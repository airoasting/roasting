"""Anti-pattern detection for /roasting.

5 detectors run BEFORE Phase 5 RGSB scoring. Detected patterns trigger BLACK
self-correction (round counter unaffected). Three consecutive detections of
the same pattern (counted within OR across rounds) escalate to user.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .llm_judge import JudgeFn


# 시·소설·링크드인 프로필은 HALLUCINATED_NUMBER 적용 제외.
HN_EXEMPT_CASES: frozenset[str] = frozenset({"p63", "p64", "p69"})

# 단정 약속어 — LEGAL_RISK_TERM은 법무 + 외부 커뮤니케이션 일부 카테고리만 적용.
LEGAL_RISK_CATEGORIES: frozenset[str] = frozenset({"법무 검토·규제 대응", "외부 커뮤니케이션"})

LEGAL_RISK_KEYWORDS: tuple[str, ...] = (
    "보장합니다", "확실히", "절대로", "100%", "약속드립니다",
    "반드시 한", "분명히", "당연히",
)

VAGUE_CTA_KEYWORDS: tuple[str, ...] = (
    "검토 부탁", "참고 바랍니다", "고민 부탁", "확인 부탁",
    "양해 부탁", "하시기 바랍니다",
)

# 명확한 동사가 마지막 50자에 있어야 VAGUE_CTA 면제.
CLEAR_VERBS: tuple[str, ...] = ("승인", "회신", "결정", "마감", "확정")


@dataclass(frozen=True)
class AntiPattern:
    name: str
    detail: str           # short reason for BLACK rewrite prompt


def detect_all(
    black_output: str,
    case_id: str,
    case_category: str,
    case_black_tone: str,
    case_gold_scenario: str,
    user_xxxxx: str,
    judge: JudgeFn,
) -> list[AntiPattern]:
    """Run all 5 detectors. Empty list = clean output."""
    detected: list[AntiPattern] = []
    if hn := _hallucinated_number(black_output, case_id, user_xxxxx, judge):
        detected.append(hn)
    if vc := _vague_cta(black_output, judge):
        detected.append(vc)
    if mh := _missing_gold_hook(black_output, case_gold_scenario, judge):
        detected.append(mh)
    if tm := _tone_mismatch(black_output, case_black_tone, judge):
        detected.append(tm)
    if lr := _legal_risk_term(black_output, case_category):
        detected.append(lr)
    return detected


NUMBER_RE = re.compile(r"\d+(?:\.\d+)?(?:%|만|억|원|\$|개|명|배|건|회)?")


def _hallucinated_number(
    text: str,
    case_id: str,
    user_xxxxx: str,
    judge: JudgeFn,
) -> AntiPattern | None:
    if case_id in HN_EXEMPT_CASES:
        return None
    numbers = NUMBER_RE.findall(text)
    if not numbers:
        return None
    verdict = judge(
        system=(
            "당신은 화이트칼라 산출물의 환각 수치 감지자다. "
            "산출물 안의 수치가 (1) 사용자 입력에 명시된 출처 또는 (2) 산출물 안에서 출처 표기 ([출처: ...] 등)가 있는지 본다."
        ),
        user=(
            f"산출물:\n{text}\n\n사용자 입력 xxxxx:\n{user_xxxxx}\n\n"
            "출처 표기 없이 등장하는 수치를 모두 골라라."
        ),
        schema={"unsourced_numbers": ["string"]},
    )
    unsourced = verdict.get("unsourced_numbers") or []
    if not unsourced:
        return None
    return AntiPattern(
        name="HALLUCINATED_NUMBER",
        detail=f"출처 없는 수치 발견: {', '.join(unsourced[:5])}. 출처를 명시하거나 삭제하라.",
    )


def _vague_cta(text: str, judge: JudgeFn) -> AntiPattern | None:
    last_50 = text[-50:].strip()
    if not any(kw in last_50 for kw in VAGUE_CTA_KEYWORDS):
        return None
    if any(verb in last_50 for verb in CLEAR_VERBS):
        return None
    verdict = judge(
        system="당신은 임원 메시지의 명확성 감지자다. 마지막 부분에 결정 요청이 명확한 동사로 들어있는지 본다.",
        user=f"마지막 50자: {last_50}\n\n명확한 결정 요청 동사가 있는가?",
        schema={"has_clear_verb": "boolean"},
    )
    if verdict.get("has_clear_verb"):
        return None
    return AntiPattern(
        name="VAGUE_CTA",
        detail=f"마무리가 모호하다: '{last_50[-20:]}...'. 무엇을 결정해 달라는지 1동사로 다시 쓰라.",
    )


def _missing_gold_hook(text: str, gold_scenario: str, judge: JudgeFn) -> AntiPattern | None:
    if not gold_scenario:
        return None
    first_200 = text[:200]
    verdict = judge(
        system="GOLD 합격선 장면(독자가 만나는 미리보기 두 줄/첫 슬라이드)이 산출물 첫 부분에 살아있는지 평가한다.",
        user=f"GOLD 합격선 장면:\n{gold_scenario}\n\n산출물 첫 200자:\n{first_200}\n\n장면이 살아있는가?",
        schema={"gold_hook_alive": "boolean", "missing_aspect": "string"},
    )
    if verdict.get("gold_hook_alive"):
        return None
    return AntiPattern(
        name="MISSING_GOLD_HOOK",
        detail=f"GOLD 합격선 장면이 첫 200자에 안 살아있다. 누락: {verdict.get('missing_aspect', '')}. 첫 두 줄을 다시 쓰라.",
    )


def _tone_mismatch(text: str, black_tone: str, judge: JudgeFn) -> AntiPattern | None:
    if not black_tone:
        return None
    first_sentence = re.split(r"[.!?\n]", text, maxsplit=1)[0]
    if not first_sentence.strip():
        return None
    verdict = judge(
        system="BLACK 캐스팅 톤과 산출물 첫 문장 어휘 거리를 1-10으로 측정 (10 = 완벽 일치).",
        user=f"BLACK 캐스팅 톤: {black_tone}\n\n산출물 첫 문장: {first_sentence}",
        schema={"tone_match_score": "number", "reason": "string"},
    )
    score = float(verdict.get("tone_match_score", 10))
    if score >= 6.0:
        return None
    return AntiPattern(
        name="TONE_MISMATCH",
        detail=f"톤 불일치 (score={score:.1f}). 캐스팅 톤='{black_tone[:60]}...'. {verdict.get('reason','')}",
    )


def _legal_risk_term(text: str, category: str) -> AntiPattern | None:
    if category not in LEGAL_RISK_CATEGORIES:
        return None
    found = [kw for kw in LEGAL_RISK_KEYWORDS if kw in text]
    if not found:
        return None
    return AntiPattern(
        name="LEGAL_RISK_TERM",
        detail=f"단정 약속어 발견: {', '.join(found)}. 위험 회피 표현으로 대체하라.",
    )


class ConsecutiveAntiPatternError(Exception):
    """Raised when same pattern detected 3 times in a row (round-internal OR cross-round)."""
    def __init__(self, pattern_name: str):
        self.pattern_name = pattern_name
        super().__init__(f"Anti-pattern {pattern_name} hit 3-strike cap.")


@dataclass
class StrikeCounter:
    """Track consecutive detections per pattern. Counts cross all rounds."""
    counts: dict[str, int] = field(default_factory=dict)

    def record(self, pattern_name: str) -> None:
        self.counts[pattern_name] = self.counts.get(pattern_name, 0) + 1
        if self.counts[pattern_name] >= 3:
            raise ConsecutiveAntiPatternError(pattern_name)

    def reset(self, pattern_name: str) -> None:
        self.counts.pop(pattern_name, None)

    def reset_all(self) -> None:
        self.counts.clear()
