"""Routing for /roasting Phase 1.

Loads references/cases/_index.md, sends xxxxx to Haiku judge, returns top-3
case_ids with confidence scores.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from .llm_judge import HaikuJudge, JudgeFn


@dataclass
class RouteResult:
    top3: list[tuple[str, float]]   # [(case_id, confidence), ...]

    @property
    def top1_id(self) -> str:
        return self.top3[0][0] if self.top3 else ""

    @property
    def top1_confidence(self) -> float:
        return self.top3[0][1] if self.top3 else 0.0


def load_index(index_path: Path) -> str:
    return index_path.read_text(encoding="utf-8")


def route(xxxxx: str, index_md: str, judge: JudgeFn | None = None) -> RouteResult:
    if judge is None:
        judge = HaikuJudge()
    verdict = judge(
        system=(
            "당신은 화이트칼라 산출물 케이스 라우터다. "
            "사용자 자연어 요청을 받아 5color 사이트의 63개 케이스 중 가장 적합한 top-3를 신뢰도와 함께 반환한다.\n\n"
            "중요: case_id는 반드시 백틱(`) 안에 표기된 p-코드(예: p1, p2, p23)를 사용한다. "
            "로마자 folio(예: I·1, II·3)가 아닌 p-코드를 반환해야 한다.\n\n"
            "케이스 인덱스:\n" + index_md
        ),
        user=f"사용자 요청 xxxxx: {xxxxx}\n\ntop-3 case_id(p-코드)를 신뢰도(0-1)와 함께 반환.",
        schema={"top3": [{"case_id": "string", "confidence": "number"}]},
    )
    items = verdict.get("top3") or []
    top3: list[tuple[str, float]] = [
        # Strip backticks that models sometimes include around p-codes (e.g. `p11` -> p11).
        (str(it.get("case_id", "")).strip("`"), float(it.get("confidence", 0)))
        for it in items[:3]
    ]
    return RouteResult(top3=top3)


def wilson_lower_bound(successes: int, total: int, z: float = 1.96) -> float:
    """Wilson score 95% lower bound for a proportion."""
    if total == 0:
        return 0.0
    p = successes / total
    denom = 1 + z * z / total
    centre = p + z * z / (2 * total)
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total)
    return (centre - margin) / denom
