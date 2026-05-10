"""Verify Phase 5 Agent Teams primary path + auto-fallback."""
from __future__ import annotations

from pathlib import Path



SKILL = Path("skills/roasting/SKILL.md")


def test_phase_5_has_team_create():
    body = SKILL.read_text(encoding="utf-8")
    assert "TeamCreate" in body
    assert "SendMessage" in body
    assert "TaskCreate" in body


def test_phase_5_lifecycle_single_team_per_case():
    body = SKILL.read_text(encoding="utf-8")
    assert "Round 2+에서 TeamCreate 안 함" in body or "1팀" in body
    assert "TeamDelete" in body


def test_phase_5_tiebreaker_order():
    body = SKILL.read_text(encoding="utf-8")
    assert "GOLD" in body and "RED" in body and "SILVER" in body and "BLUE" in body
    # GOLD must be highest priority in tiebreak.
    gold_pos = body.find('"GOLD": 0')
    red_pos = body.find('"RED": 1')
    silver_pos = body.find('"SILVER": 2')
    blue_pos = body.find('"BLUE": 3')
    assert 0 < gold_pos < red_pos < silver_pos < blue_pos


def test_phase_5_auto_fallback_documented():
    body = SKILL.read_text(encoding="utf-8")
    assert "NotAvailable" in body or "폴백" in body
    assert "Sub-Agent Fallback" in body


def test_models_red_gold_opus_silver_blue_sonnet():
    body = SKILL.read_text(encoding="utf-8")
    # Opus reviewers
    for line_should_contain in [
        '"name": "RED"',
        '"model": "opus"',
        '"name": "GOLD"',
    ]:
        assert line_should_contain in body
    # Sonnet reviewers
    assert '"name": "SILVER"' in body and '"model": "sonnet"' in body
    assert '"name": "BLUE"' in body
