"""Phase 7 deliverables: write output / critique / reasoning to _workspace/.../final/."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RoundData:
    round_num: int
    black_draft_path: Path
    rgsb_scores: dict[str, dict[str, Any]]   # {persona: {score, reason, suggestion}}
    debate_log: str
    anti_patterns: list[dict[str, Any]]


@dataclass
class SessionResult:
    session_dir: Path
    case_id: str
    case_title: str
    user_xxxxx: str
    rounds: list[RoundData]
    final_round_idx: int
    completion_status: str   # "passed" | "forced" | "user_aborted"
    output_format: str       # "md" | "html"
    slide_template_id: str | None = None


def deliver(result: SessionResult) -> Path:
    final_dir = result.session_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    final_round = result.rounds[result.final_round_idx]
    # 1. output.{ext} — copy final BLACK draft to final/
    out_ext = result.output_format
    output_path = final_dir / f"output.{out_ext}"
    if result.output_format == "html":
        try:
            from .build_slide_html import build, mode_for_case
            build(
                index_json=Path("skills/roasting/references/slide-templates/index.json"),
                template_id=result.slide_template_id or "",
                black_md=final_round.black_draft_path.read_text(encoding="utf-8"),
                output_html=output_path,
                mode=mode_for_case(result.case_id),
            )
        except Exception as e:
            # Fallback: write output.md with warning footer.
            fallback_path = final_dir / "output.md"
            black_md = final_round.black_draft_path.read_text(encoding="utf-8")
            fallback_path.write_text(
                black_md + f"\n\n> ⚠️ HTML 슬라이드 빌드 실패. Markdown 폴백으로 출력. 사유: {e}\n",
                encoding="utf-8",
            )
            return final_dir
    else:
        output_path.write_text(
            final_round.black_draft_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    # 2. critique.md — RGSB comments per round, in order
    final_dir.joinpath("critique.md").write_text(_render_critique(result), encoding="utf-8")
    # 3. reasoning.md — BLACK decision log
    final_dir.joinpath("reasoning.md").write_text(_render_reasoning(result), encoding="utf-8")
    return final_dir


def _render_critique(r: SessionResult) -> str:
    lines = [f"# {r.case_title} — 4인 평가 코멘트\n",
             f"> 케이스 `{r.case_id}` · 사용자 입력: \"{r.user_xxxxx[:80]}\"\n\n"]
    for rd in r.rounds:
        lines.append(f"## Round {rd.round_num}\n\n")
        for persona in ("RED", "SILVER", "BLUE", "GOLD"):
            entry = rd.rgsb_scores.get(persona, {})
            score = entry.get("score", "—")
            reason = entry.get("reason", "")
            suggestion = entry.get("suggestion", "")
            lines.append(f"- **{persona}**: {score} — {reason}\n")
            if suggestion:
                lines.append(f"  - 개선안: {suggestion}\n")
        if rd.debate_log:
            lines.append(f"\n### Round {rd.round_num} 토론\n\n{rd.debate_log}\n\n")
    return "".join(lines)


def _render_reasoning(r: SessionResult) -> str:
    lines = [f"# {r.case_title} — BLACK 결정 로그\n\n",
             f"종료 상태: **{r.completion_status}**, 최종 라운드: {r.rounds[r.final_round_idx].round_num}\n\n"]
    for rd in r.rounds:
        lines.append(f"## Round {rd.round_num}\n\n")
        if rd.anti_patterns:
            lines.append("### 안티패턴 검출 + 자체 수정\n\n")
            for ap in rd.anti_patterns:
                lines.append(f"- `{ap.get('name')}`: {ap.get('detail')}\n")
            lines.append("\n")
        else:
            lines.append("(안티패턴 검출 없음)\n\n")
    return "".join(lines)
