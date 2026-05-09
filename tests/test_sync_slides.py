"""End-to-end test for slide_library scraper.

Schema note: the live slide_library site stores templates in a JS array
`const TEMPLATES = [...]` (not [data-id] HTML cards as originally planned).
Color vocab is {light, dark, mixed} (no "full"); formality vocab is
{formal, neutral, casual} (mapped from site's high/medium/low buckets).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.network
def test_sync_slides_produces_index(tmp_path: Path) -> None:
    out = tmp_path / "index.json"
    subprocess.run(
        [sys.executable, "-m", "scripts.sync_slides", "--out", str(out)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 30, f"expected ≥ 30 templates, got {len(data)}"
    sample = data[0]
    for key in ("id", "name", "color", "formality", "url", "slide_count", "keywords"):
        assert key in sample, f"missing key {key} in template entry"
    # Verify color and formality values are from expected vocab.
    # Note: live site uses scheme∈{light,dark,mixed} → color; no "full" value exists.
    valid_color = {"light", "dark", "mixed"}
    valid_formality = {"formal", "neutral", "casual"}
    for t in data:
        assert t["color"] in valid_color, f"unexpected color {t['color']}"
        assert t["formality"] in valid_formality, f"unexpected formality {t['formality']}"
    # Verify URL pattern
    for t in data:
        assert t["url"].startswith("https://"), f"invalid URL {t['url']}"
        assert "/templates/" in t["url"], f"URL missing /templates/ path: {t['url']}"
    # Verify slide_count is numeric
    for t in data:
        assert isinstance(t["slide_count"], int), f"slide_count not int: {t['slide_count']}"
        assert t["slide_count"] >= 0
