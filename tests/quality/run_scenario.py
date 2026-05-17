"""End-to-end scenario runner for /roasting quality integration tests.

Simulates the SKILL.md workflow:
  route → BLACK (Sonnet) → anti-pattern detect (Haiku) → RGSB (Sonnet/Opus parallel)
  → aggregate → loop if needed → return ScenarioResult

Auth: uses `claude` CLI subprocess with the authenticated Claude Code session.
No TeamCreate/SendMessage — these are SKILL.md runtime constructs.

Budget: ~$0.30-0.60 per scenario (1-2 rounds), ~$5-9 for all 15 scenarios.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Model IDs (via claude CLI)
# ---------------------------------------------------------------------------
BLACK_MODEL = "claude-sonnet-4-5"       # BLACK producer (Sonnet)
RED_MODEL = "claude-opus-4-5"           # RED reviewer (Opus, per agent definition)
GOLD_MODEL = "claude-opus-4-5"          # GOLD reviewer (Opus, per agent definition)
SILVER_MODEL = "claude-sonnet-4-5"      # SILVER reviewer (Sonnet)
BLUE_MODEL = "claude-sonnet-4-5"        # BLUE reviewer (Sonnet)
HAIKU_MODEL = "claude-haiku-4-5"        # Anti-pattern detection (Haiku, cheaper)

REPO_ROOT = Path(__file__).parent.parent.parent
CASES_DIR = REPO_ROOT / "skills" / "roasting" / "references" / "cases"
INDEX_PATH = REPO_ROOT / "skills" / "roasting" / "references" / "cases" / "_index.md"

# Workflow constants (from references/workflow.md)
ACCEPTANCE_THRESHOLD = 9.5  # Per-round acceptance gate (9.5 as per workflow.md)
MAX_ROUNDS = 2              # Cap at 2 for quality gate (cost budget ~$10)
QUALITY_GATE_AVG = 9.0      # PR17 gate: average across 15 scenarios

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class ReviewScore:
    role: str       # RED | SILVER | BLUE | GOLD
    score: float
    reason: str
    suggestion: str


@dataclass
class RoundResult:
    round_num: int
    black_output: str
    anti_patterns: list[str]
    scores: list[ReviewScore]
    avg_score: float   # avg of RED+SILVER+BLUE (GOLD is tiebreaker per workflow)
    sigma: float       # std dev of RED+SILVER+BLUE scores


@dataclass
class ScenarioResult:
    case_id: str
    xxxxx: str
    final_score: float
    round_count: int
    rounds: list[RoundResult] = field(default_factory=list)
    error: str | None = None
    cost_estimate_usd: float = 0.0

# ---------------------------------------------------------------------------
# Core: run claude CLI subprocess
# ---------------------------------------------------------------------------

def _run_claude(
    user_prompt: str,
    system: str = "",
    model: str = BLACK_MODEL,
    max_retries: int = 1,
    timeout: int = 150,
) -> str:
    """Run claude CLI subprocess via stdin and return text result.

    Uses --no-session-persistence to reduce cache overhead and cost.
    Pipes user_prompt via stdin to avoid arg-length limits on long critiques.
    Retries once on transient failure with exponential backoff.
    """
    cmd = [
        "claude",
        "--model", model,
        "--no-session-persistence",
        "--output-format", "json",
    ]
    if system:
        cmd += ["--system-prompt", system]

    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            result = subprocess.run(
                cmd,
                input=user_prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                stderr = result.stderr[:500] if result.stderr else "no stderr"
                raise RuntimeError(f"claude CLI exit {result.returncode}: {stderr}")
            if not result.stdout.strip():
                raise RuntimeError("claude CLI returned empty output")
            data = json.loads(result.stdout)
            if data.get("is_error"):
                raise RuntimeError(f"claude CLI error: {data.get('result', '')[:300]}")
            return data.get("result", "")
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, RuntimeError,
                json.JSONDecodeError) as exc:
            last_exc = exc
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"  [retry {attempt+1}/{max_retries}] after {wait}s: {exc}", flush=True)
                time.sleep(wait)

    raise RuntimeError(f"All {max_retries+1} attempts failed") from last_exc


def _extract_json(text: str) -> dict[str, Any]:
    """Extract first JSON object from text (tolerant of fences and trailing prose)."""
    t = text.strip()
    # Strip markdown code fences
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t).rstrip("`").strip()
    # Find first { ... } block
    start = t.find("{")
    if start == -1:
        return json.loads(t)
    depth = 0
    for i, ch in enumerate(t[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(t[start : i + 1])
    return json.loads(t[start:])


# ---------------------------------------------------------------------------
# Step 1: Load case definition
# ---------------------------------------------------------------------------

def _load_case(case_id: str) -> dict[str, str]:
    """Parse case .md and return fields: black_casting, red, silver, blue, gold, category, title."""
    path = CASES_DIR / f"{case_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Case file not found: {path}")
    text = path.read_text(encoding="utf-8")

    # Parse YAML frontmatter
    frontmatter: dict[str, str] = {}
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                frontmatter[k.strip()] = v.strip().strip('"')

    # Extract sections
    def _section(header: str) -> str:
        pattern = rf"## {re.escape(header)}.*?\n(.*?)(?=\n## |\Z)"
        m = re.search(pattern, text, re.DOTALL)
        return m.group(1).strip() if m else ""

    return {
        "case_id": case_id,
        "category": frontmatter.get("category", ""),
        "title": frontmatter.get("title", ""),
        "black_casting": _section("BLACK 캐스팅"),
        "red": _section("RED — 이성"),
        "silver": _section("SILVER — 분야 전문가"),
        "blue": _section("BLUE — 공감"),
        "gold": _section("GOLD — 독자 시나리오"),
        "full_text": text,
    }


# ---------------------------------------------------------------------------
# Step 2: Route to verify case (thin wrapper — case_id is pre-specified)
# ---------------------------------------------------------------------------

def _route_check(case_id: str) -> bool:
    """Verify the case file exists (routing is pre-specified in scenarios.json)."""
    return (CASES_DIR / f"{case_id}.md").exists()


# ---------------------------------------------------------------------------
# Step 3: BLACK draft call
# ---------------------------------------------------------------------------

def _call_black(case: dict[str, str], xxxxx: str, prev_critique: str = "") -> str:
    """Call BLACK model (Sonnet) to produce draft output."""
    system = (
        f"당신은 {case['black_casting']}이다.\n\n"
        "케이스 정의에 따라 화이트칼라 산출물을 작성한다. "
        "자평·메타 코멘트 금지. 산출물만 출력하라.\n\n"
        f"케이스: {case['title']} ({case['category']})\n"
        f"GOLD 합격선 장면: {case['gold'][:300]}\n"
    )
    user_parts = [f"사용자 요청: {xxxxx}"]
    if prev_critique:
        # Keep critique concise to avoid arg-length issues and model confusion
        user_parts.append(f"\n이전 RGSB 피드백 (반영하여 개선):\n{prev_critique[:400]}")

    return _run_claude(
        user_prompt="\n".join(user_parts),
        system=system,
        model=BLACK_MODEL,
        timeout=150,
    )


# ---------------------------------------------------------------------------
# Step 4: Anti-pattern detection (simplified, regex + single Haiku call)
# ---------------------------------------------------------------------------

def _detect_anti_patterns(
    black_output: str,
    case: dict[str, str],
    xxxxx: str,
) -> list[str]:
    """Run simplified anti-pattern detection.

    Returns list of detected pattern names.
    Uses regex for LEGAL_RISK_TERM and VAGUE_CTA (fast, no API).
    Uses Haiku for HALLUCINATED_NUMBER and TONE_MISMATCH (single call).
    """
    detected: list[str] = []

    # Regex-only: LEGAL_RISK_TERM
    legal_risk_cats = {"법무 검토·규제 대응", "외부 커뮤니케이션"}
    legal_keywords = ("보장합니다", "확실히", "절대로", "100%", "약속드립니다",
                      "반드시 한", "분명히", "당연히")
    if case["category"] in legal_risk_cats:
        found = [kw for kw in legal_keywords if kw in black_output]
        if found:
            detected.append(f"LEGAL_RISK_TERM({','.join(found)})")

    # Regex-only: VAGUE_CTA
    vague_kws = ("검토 부탁", "참고 바랍니다", "고민 부탁", "확인 부탁",
                 "양해 부탁", "하시기 바랍니다")
    clear_verbs = ("승인", "회신", "결정", "마감", "확정")
    last_50 = black_output[-50:].strip()
    if any(kw in last_50 for kw in vague_kws) and not any(v in last_50 for v in clear_verbs):
        detected.append("VAGUE_CTA")

    # Haiku call: HALLUCINATED_NUMBER + TONE_MISMATCH (combined to save cost)
    if len(black_output) > 50:
        try:
            haiku_result = _run_claude(
                user_prompt=(
                    f"산출물(앞 400자):\n{black_output[:400]}\n\n"
                    f"BLACK 캐스팅 톤: {case['black_casting'][:80]}\n"
                    f"사용자 입력: {xxxxx[:100]}\n\n"
                    "1. 출처 없는 수치가 있는가? (true/false)\n"
                    "2. 첫 문장 톤이 캐스팅 톤과 불일치 점수(1-10, 10=완벽일치)?\n"
                    "JSON만: {\"unsourced_numbers\": bool, \"tone_score\": number}"
                ),
                system="당신은 안티패턴 감지자다. JSON으로만 응답.",
                model=HAIKU_MODEL,
                timeout=60,
            )
            ap_check = _extract_json(haiku_result)
            if ap_check.get("unsourced_numbers"):
                detected.append("HALLUCINATED_NUMBER")
            tone_score = float(ap_check.get("tone_score", 10))
            if tone_score < 6.0:
                detected.append(f"TONE_MISMATCH(score={tone_score:.1f})")
        except Exception as exc:
            print(f"  [ap-detect warn] {exc}", flush=True)  # Non-fatal

    return detected


# ---------------------------------------------------------------------------
# Step 5: RGSB reviewer calls (parallel)
# ---------------------------------------------------------------------------

def _call_reviewer(
    role: str,
    persona: str,
    black_output: str,
    case: dict[str, str],
    xxxxx: str,
    model: str,
) -> ReviewScore:
    """Call one RGSB reviewer and return a ReviewScore."""
    system = (
        f"당신은 {role} 평가자다. 페르소나: {persona[:250]}\n\n"
        f"케이스: {case['title']} ({case['category']})\n"
        f"GOLD 합격선 장면: {case['gold'][:150]}\n\n"
        "BLACK 산출물을 1-10점 척도로 채점하라. "
        "점수: 10=결함없음, 9.5=합격선, 9=약간 보완, 8=v2 권장, ≤7=재작업.\n"
        "반드시 JSON만 출력: {\"score\": number, \"reason\": \"string\", \"suggestion\": \"string\"}"
    )
    user = (
        f"사용자 요청: {xxxxx}\n\n"
        f"BLACK 산출물:\n{black_output[:1500]}"
    )
    try:
        result = _run_claude(user_prompt=user, system=system, model=model, timeout=120)
        parsed = _extract_json(result)
        raw_score = parsed.get("score", 0.0)
        # Clamp to 1-10 in case model returns out-of-range
        score = max(1.0, min(10.0, float(raw_score)))
        return ReviewScore(
            role=role,
            score=score,
            reason=str(parsed.get("reason", "")),
            suggestion=str(parsed.get("suggestion", "")),
        )
    except Exception as exc:
        print(f"  [warn] {role} reviewer failed: {exc}", flush=True)
        return ReviewScore(role=role, score=0.0, reason=f"ERROR: {exc}", suggestion="")


def _call_rgsb_parallel(
    black_output: str,
    case: dict[str, str],
    xxxxx: str,
) -> list[ReviewScore]:
    """Call all 4 RGSB reviewers in parallel via ThreadPoolExecutor."""
    reviewers = [
        ("RED", case["red"], RED_MODEL),
        ("GOLD", case["gold"], GOLD_MODEL),
        ("SILVER", case["silver"], SILVER_MODEL),
        ("BLUE", case["blue"], BLUE_MODEL),
    ]

    scores: list[ReviewScore] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(
                _call_reviewer, role, persona, black_output, case, xxxxx, model
            ): role
            for role, persona, model in reviewers
        }
        for future in as_completed(futures):
            try:
                scores.append(future.result())
            except Exception as exc:
                role = futures[future]
                scores.append(ReviewScore(
                    role=role, score=0.0, reason=f"ERROR: {exc}", suggestion=""))

    # Sort by canonical order: RED, GOLD, SILVER, BLUE
    order = {"RED": 0, "GOLD": 1, "SILVER": 2, "BLUE": 3}
    scores.sort(key=lambda s: order.get(s.role, 99))
    return scores


# ---------------------------------------------------------------------------
# Step 6: Aggregate scores + sigma
# ---------------------------------------------------------------------------

def _aggregate(scores: list[ReviewScore]) -> tuple[float, float]:
    """Compute avg of RED+SILVER+BLUE (GOLD is tiebreaker per workflow.md).

    Returns (avg_analysts, sigma_analysts).
    """
    analyst_scores = [s.score for s in scores if s.role in ("RED", "SILVER", "BLUE")]
    if not analyst_scores:
        return 0.0, 0.0
    avg = sum(analyst_scores) / len(analyst_scores)
    if len(analyst_scores) < 2:
        return avg, 0.0
    variance = sum((x - avg) ** 2 for x in analyst_scores) / len(analyst_scores)
    return avg, math.sqrt(variance)


def _build_critique(scores: list[ReviewScore]) -> str:
    """Format RGSB scores as concise critique for BLACK's next round.

    Kept short (≤400 chars) to avoid overwhelming BLACK in round 2.
    """
    lines = []
    for s in scores:
        # One-line per reviewer: role, score, key suggestion only
        lines.append(f"[{s.role}] {s.score:.1f}점: {s.suggestion[:80]}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main: run_one
# ---------------------------------------------------------------------------

def run_one(case_id: str, xxxxx: str) -> ScenarioResult:
    """Run one scenario end-to-end and return ScenarioResult.

    Workflow (per references/workflow.md, adapted for quality gate):
    1. Load case definition
    2. For each round (up to MAX_ROUNDS=2 for budget):
       a. BLACK draft (Sonnet)
       b. Anti-pattern detection (Haiku + regex)
       c. RGSB parallel review (4 calls: 2 Opus + 2 Sonnet)
       d. Aggregate avg(RED+SILVER+BLUE) + sigma
       e. If avg >= 9.5 acceptance threshold: done
       f. Else if round < MAX_ROUNDS: continue with concise critique
    3. Return best-round result (not last round — best avg)
    """
    print(f"\n--- Scenario: {case_id} | {xxxxx[:50]}... ---", flush=True)

    try:
        if not _route_check(case_id):
            raise FileNotFoundError(f"Case {case_id} not found")

        case = _load_case(case_id)
        print(f"  Case: {case['title']} ({case['category']})", flush=True)

        rounds: list[RoundResult] = []
        prev_critique = ""
        best_result: RoundResult | None = None

        for round_num in range(1, MAX_ROUNDS + 1):
            print(f"  Round {round_num}/{MAX_ROUNDS}", flush=True)

            # BLACK draft
            black_output = _call_black(case, xxxxx, prev_critique)
            print(f"  BLACK done ({len(black_output)} chars)", flush=True)

            # Anti-pattern detection (non-blocking — log but don't force rewrite here)
            anti_patterns = _detect_anti_patterns(black_output, case, xxxxx)
            if anti_patterns:
                print(f"  Anti-patterns: {anti_patterns}", flush=True)

            # RGSB parallel
            scores = _call_rgsb_parallel(black_output, case, xxxxx)
            for s in scores:
                print(f"    {s.role}: {s.score:.1f}", flush=True)

            avg, sigma = _aggregate(scores)
            print(f"  avg={avg:.2f} sigma={sigma:.2f}", flush=True)

            round_result = RoundResult(
                round_num=round_num,
                black_output=black_output,
                anti_patterns=anti_patterns,
                scores=scores,
                avg_score=avg,
                sigma=sigma,
            )
            rounds.append(round_result)

            # Track best round (may not be the latest)
            if best_result is None or avg > best_result.avg_score:
                best_result = round_result

            # Acceptance gate (9.5 per workflow.md)
            if avg >= ACCEPTANCE_THRESHOLD:
                print(
                    f"  Accepted at round {round_num} (avg={avg:.2f} >= {ACCEPTANCE_THRESHOLD})",
                    flush=True,
                )
                break

            # Prepare for next round
            if round_num < MAX_ROUNDS:
                prev_critique = _build_critique(scores)
                print(f"  Continuing to round {round_num + 1}...", flush=True)
            else:
                if best_result is not None:
                    print(
                        f"  {MAX_ROUNDS}-round cap reached. "
                        f"Best avg={best_result.avg_score:.2f}.",
                        flush=True,
                    )

        assert best_result is not None
        final_score = best_result.avg_score
        print(
            f"  FINAL: {case_id} final_score={final_score:.2f} rounds={len(rounds)}",
            flush=True,
        )

        return ScenarioResult(
            case_id=case_id,
            xxxxx=xxxxx,
            final_score=final_score,
            round_count=len(rounds),
            rounds=rounds,
        )

    except Exception as exc:
        import traceback
        print(f"  ERROR in scenario {case_id}: {exc}", flush=True)
        traceback.print_exc(file=sys.stdout)
        return ScenarioResult(
            case_id=case_id,
            xxxxx=xxxxx,
            final_score=0.0,
            round_count=0,
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# CLI entry point (manual testing of a single scenario)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run one /roasting quality scenario")
    parser.add_argument("case_id", help="Case ID, e.g. c1")
    parser.add_argument("xxxxx", help="User input, e.g. '거래처 부장에게 메일'")
    args = parser.parse_args()

    result = run_one(args.case_id, args.xxxxx)
    print(f"\nResult: final_score={result.final_score:.2f}, rounds={result.round_count}")
    if result.error:
        print(f"Error: {result.error}")
