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


def test_landing_sections_split_by_h2():
    md = (
        "# 페이지 제목\n"
        "리드 한 줄\n\n"
        "## 히어로\nQ3 ROAS 2.1로 목표 미달함\n\n"
        "## 소셜 프루프\n- 고객 A\n- 고객 B\n\n"
        "## CTA\n지금 데모 신청하세요\n"
    )
    blocks = bsh.black_md_to_landing_sections(md)
    assert len(blocks) == 3
    assert "<h2>히어로</h2>" in blocks[0]
    assert 'class="landing-' in blocks[0]
    assert "<ul><li>고객 A</li><li>고객 B</li></ul>" in blocks[1]
    assert "<h2>CTA</h2>" in blocks[2]


def test_landing_sections_fallback_when_no_h2():
    md = "# 단일 제목\n본문\n"
    blocks = bsh.black_md_to_landing_sections(md)
    assert len(blocks) == 1
    assert "<h2>단일 제목</h2>" in blocks[0]


def test_mode_for_case_routes_p70_to_landing():
    assert bsh.mode_for_case("p70") == "landing"
    assert bsh.mode_for_case("p41") == "slides"
    assert bsh.mode_for_case("p1") == "slides"


def test_build_passes_mode_to_correct_splitter(monkeypatch, tmp_path):
    idx = tmp_path / "index.json"
    idx.write_text(json.dumps([{"id": "tpl-1", "name": "T1",
                                "color": "light", "formality": "formal",
                                "url": "https://example/", "slide_count": 5,
                                "keywords": []}]), encoding="utf-8")
    monkeypatch.setattr(
        bsh,
        "fetch_template_html",
        lambda tpl: '<html><body><div class="slides"></div></body></html>',
    )
    out = tmp_path / "out.html"
    bsh.build(idx, "tpl-1", "# Page\n\n## Hero\nbody\n", out, mode="landing")
    html = out.read_text(encoding="utf-8")
    assert "<h2>Hero</h2>" in html
    assert "landing-hero" in html
