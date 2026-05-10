"""Verify Phase 3-4 logic structure via SKILL.md content checks + StrikeCounter integration."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.anti_patterns import StrikeCounter, ConsecutiveAntiPatternError


SKILL = Path("skills/roasting/SKILL.md")


def test_phase_3_invokes_black_agent():
    body = SKILL.read_text(encoding="utf-8")
    assert "Phase 3 — BLACK DRAFT" in body
    assert "Agent(" in body or "agents/roasting-black.md" in body
    assert "black-draft" in body


def test_phase_4_uses_detect_all():
    body = SKILL.read_text(encoding="utf-8")
    assert "Phase 4 — ANTI-PATTERN CHECK" in body
    assert "detect_all" in body
    assert "StrikeCounter" in body
    assert "ConsecutiveAntiPatternError" in body or "3-strikes" in body or "3회 연속" in body


def test_phase_4_reports_user_options_on_3_strikes():
    body = SKILL.read_text(encoding="utf-8")
    assert "(1) 진행" in body
    assert "(2) 중단" in body
    assert "(3) 케이스 재선택" in body


def test_strike_counter_integration_pattern():
    """Smoke test: 3rd record raises (used in Phase 4)."""
    sc = StrikeCounter()
    sc.record("HALLUCINATED_NUMBER")
    sc.record("HALLUCINATED_NUMBER")
    with pytest.raises(ConsecutiveAntiPatternError):
        sc.record("HALLUCINATED_NUMBER")
