"""Phase 6 + Phase 7 verification."""
from __future__ import annotations

from pathlib import Path


from scripts.deliver import RoundData, SessionResult, deliver


SKILL = Path("skills/roasting/SKILL.md")


def test_phase_6_documents_three_branches():
    body = SKILL.read_text(encoding="utf-8")
    assert "Phase 6 — LOOP" in body
    assert "round_count < 4" in body
    assert "round_count == 4" in body
    assert "9.5 미달" in body


def test_phase_7_lists_three_outputs():
    body = SKILL.read_text(encoding="utf-8")
    assert "output.{html|md}" in body or "output." in body
    assert "critique.md" in body
    assert "reasoning.md" in body


def test_phase_7_telemetry_optin_no_content():
    body = SKILL.read_text(encoding="utf-8")
    assert "telemetry" in body.lower()
    assert "콘텐츠" in body and ("절대" in body or "안 됨" in body or "0" in body)


def test_deliver_writes_three_files(tmp_path):
    session = tmp_path / "test-session"
    rd1 = session / "round-1"
    rd1.mkdir(parents=True)
    draft = rd1 / "black-draft.md"
    draft.write_text("# Test Output\nbody", encoding="utf-8")
    result = SessionResult(
        session_dir=session,
        case_id="p1",
        case_title="이메일 (외부 비즈니스)",
        user_xxxxx="거래처에 답신 안 오는 메일",
        rounds=[
            RoundData(
                round_num=1,
                black_draft_path=draft,
                rgsb_scores={
                    "RED": {"score": 9.4, "reason": "의도 명확", "suggestion": ""},
                    "SILVER": {"score": 9.3, "reason": "구조 OK", "suggestion": ""},
                    "BLUE": {"score": 9.5, "reason": "톤 적정", "suggestion": ""},
                    "GOLD": {"score": 9.5, "reason": "미리보기 살아있음", "suggestion": ""},
                },
                debate_log="",
                anti_patterns=[],
            ),
        ],
        final_round_idx=0,
        completion_status="passed",
        output_format="md",
    )
    final = deliver(result)
    assert (final / "output.md").exists()
    assert (final / "critique.md").exists()
    assert (final / "reasoning.md").exists()
    critique = (final / "critique.md").read_text(encoding="utf-8")
    assert "RED" in critique and "GOLD" in critique
    assert "9.5" in critique
