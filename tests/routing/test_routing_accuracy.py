"""Routing accuracy gate: top-1 >= 90% Wilson 95% lower bound across 189 phrasings.

Marked --slow because it calls Haiku 189 times (~$1 per full run).
"""
from __future__ import annotations


import pytest

from scripts.route import route, wilson_lower_bound
from scripts.llm_judge import HaikuJudge


pytestmark = pytest.mark.slow


def test_routing_accuracy_gate(phrasings, index_md):
    judge = HaikuJudge()
    successes = 0
    misses: list[tuple[str, str, str]] = []
    for entry in phrasings:
        expected = entry["case_id"]
        result = route(entry["phrasing"], index_md, judge=judge)
        if result.top1_id == expected:
            successes += 1
        else:
            misses.append((entry["phrasing"], expected, result.top1_id))
    total = len(phrasings)
    lower = wilson_lower_bound(successes, total)
    print(f"Top-1 accuracy: {successes}/{total} = {successes/total:.3f} "
          f"(Wilson 95% LB = {lower:.3f})")
    if misses:
        print("\nFirst 10 misses:")
        for phrasing, expected, got in misses[:10]:
            print(f"  '{phrasing}' -> expected={expected}, got={got}")
    assert lower >= 0.90, (
        f"Routing accuracy gate failed: Wilson 95% LB = {lower:.3f} < 0.90. "
        f"Successes={successes}/{total}. See misses above."
    )


def test_top3_recall_gate(phrasings, index_md):
    """Looser gate: expected case must be in top-3 >= 95% of the time."""
    judge = HaikuJudge()
    successes = 0
    for entry in phrasings:
        expected = entry["case_id"]
        result = route(entry["phrasing"], index_md, judge=judge)
        if expected in [c for c, _ in result.top3]:
            successes += 1
    lower = wilson_lower_bound(successes, len(phrasings))
    assert lower >= 0.95, f"Top-3 recall LB={lower:.3f} < 0.95"
