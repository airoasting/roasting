"""Test slide HTML builder with mock template + minimal Markdown."""
from __future__ import annotations

import json

import pytest

from scripts import build_slide_html as bsh


def test_md_to_slide_blocks_h1():
    md = "# Slide One\nBody A\n\n# Slide Two\n- bullet"
    blocks = bsh.black_md_to_slide_blocks(md)
    assert len(blocks) == 2
    assert "<h1>Slide One</h1>" in blocks[0]
    assert "<p>Body A</p>" in blocks[0]
    assert "<ul><li>bullet</li></ul>" in blocks[1]


def test_md_to_slide_blocks_h2_fallback():
    md = "## A\nx\n## B\ny"
    blocks = bsh.black_md_to_slide_blocks(md)
    assert len(blocks) == 2


def test_inject_slides_replaces_container():
    template = '<html><body><div class="slides"><section>OLD</section></div></body></html>'
    merged = bsh.inject_slides(template, ["<section>NEW</section>"])
    assert "OLD" not in merged
    assert "NEW" in merged


def test_load_template_meta_missing(tmp_path):
    idx = tmp_path / "index.json"
    idx.write_text(json.dumps([{"id": "tpl-1", "name": "T1",
                                "color": "dark", "formality": "formal",
                                "url": "https://example/", "slide_count": 5,
                                "keywords": []}]), encoding="utf-8")
    with pytest.raises(KeyError):
        bsh.load_template_meta(idx, "tpl-missing")


def test_load_template_meta_found(tmp_path):
    idx = tmp_path / "index.json"
    idx.write_text(json.dumps([{"id": "tpl-1", "name": "T1",
                                "color": "dark", "formality": "formal",
                                "url": "https://example/", "slide_count": 5,
                                "keywords": []}]), encoding="utf-8")
    tpl = bsh.load_template_meta(idx, "tpl-1")
    assert tpl.color == "dark"
    assert tpl.formality == "formal"
