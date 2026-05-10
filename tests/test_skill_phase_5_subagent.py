"""Verify Phase 5 sub-agent fallback structure in SKILL.md."""
from __future__ import annotations

import statistics
from pathlib import Path



SKILL = Path("skills/roasting/SKILL.md")


def test_phase_5_subagent_section():
    body = SKILL.read_text(encoding="utf-8")
    assert "Phase 5 — RGSB REVIEW" in body
    assert "run_in_background" in body or "Sub-Agent" in body
    for who in ("RED", "SILVER", "BLUE", "GOLD"):
        assert who in body


def test_phase_5_score_aggregation_via_sigma():
    body = SKILL.read_text(encoding="utf-8")
    assert "σ" in body or "표준편차" in body
    assert "0.5" in body
    assert "9.5" in body  # 합격선


def test_phase_5_fallback_disables_debate():
    body = SKILL.read_text(encoding="utf-8")
    # Sub-agent path explicitly mentions debate is unavailable.
    assert "토론 불가" in body or "토론 SKIP" in body or "debate" in body.lower()


def test_sigma_calculation_smoke():
    """Standard deviation logic — guard against future drift."""
    scores = [9.4, 8.7, 9.1, 7.8]
    sigma = statistics.stdev(scores)
    assert sigma > 0.5  # this exact set should trigger debate per spec
