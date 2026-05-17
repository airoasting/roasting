"""End-to-end test that sync_cases parses the live site to 64 cases."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.network
def test_sync_produces_64_cases(tmp_path: Path) -> None:
    out = tmp_path / "cases"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.sync_cases", "--out", str(out)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Parsed 64 cases" in result.stderr
    md_files = sorted(out.glob("p*.md"))
    assert len(md_files) == 64
    index = out / "_index.md"
    assert index.exists()
    body = index.read_text(encoding="utf-8")
    # Spot-check 5 expected cases incl. the two new marketing cases (c73 웹사이트, c74 이미지).
    for marker in ["c1", "c23", "c65", "c73", "c74"]:
        assert f"`{marker}`" in body
