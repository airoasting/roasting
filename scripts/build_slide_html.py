"""For HTML-output cases (p41/42/43/45 PPT, p70 landing page), fetch the
slide_library template HTML and inject BLACK content.

Two modes share the same fetch + container-detection logic; only the block
shape differs:

- ``mode="slides"`` (PPT cases p41/42/43/45): split BLACK Markdown by H1
  (fallback H2) into one slide per heading, wrap as ``<section><h1>…``.
- ``mode="landing"`` (p70 web/landing): split by H2 into landing sections
  (hero, social proof, features, CTA, FAQ, footer …) and wrap as
  ``<section class="landing-{slug}"><h2>…``. We split by H2 because BLACK's
  landing skeleton uses one H1 for the page and H2 per landing section.

Strategy:
1. Pull template HTML from index.json url field.
2. Parse with BeautifulSoup, locate the slide content container (the
   slide_library convention is a wrapping element with class 'slides' or a
   data-role='slides' attribute).
3. Replace inner content with the mode-appropriate block list.
4. Write the merged HTML to output.html.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import requests
from bs4 import BeautifulSoup, Tag

BuildMode = Literal["slides", "landing"]


@dataclass
class SlideTemplate:
    id: str
    name: str
    url: str
    color: str
    formality: str


def load_template_meta(index_json: Path, template_id: str) -> SlideTemplate:
    items = json.loads(index_json.read_text(encoding="utf-8"))
    for it in items:
        if it["id"] == template_id:
            return SlideTemplate(
                id=it["id"], name=it["name"], url=it["url"],
                color=it["color"], formality=it["formality"],
            )
    raise KeyError(f"template {template_id} not in {index_json}")


def fetch_template_html(template: SlideTemplate) -> str:
    resp = requests.get(template.url, timeout=30)
    resp.raise_for_status()
    return resp.text


def black_md_to_slide_blocks(black_md: str) -> list[str]:
    """Split BLACK Markdown by H1 (or H2 fallback) into one slide per heading."""
    sections = re.split(r"(?m)^# ", black_md)
    if len(sections) <= 1:
        sections = re.split(r"(?m)^## ", black_md)
    blocks: list[str] = []
    for s in sections:
        s = s.strip()
        if not s:
            continue
        # First line = title, rest = body.
        lines = s.split("\n", 1)
        title = lines[0].strip()
        body_md = lines[1].strip() if len(lines) > 1 else ""
        blocks.append(f"<section><h1>{_escape(title)}</h1>{_md_to_html(body_md)}</section>")
    return blocks


def black_md_to_landing_sections(black_md: str) -> list[str]:
    """Split BLACK Markdown by H2 into landing sections.

    A landing page has a single visual hero, not a separate title slide, so
    the page-level H1 and any lead paragraph before the first H2 are dropped:
    BLACK is expected to put the hero copy inside the first H2 section.

    If the input has no H2s at all (rare), we fall back to splitting by H1
    so the builder always produces at least one section.
    """
    has_h2 = bool(re.search(r"(?m)^## ", black_md))
    if has_h2:
        # Keep only the H2-and-after portion.
        body = re.sub(r"(?s)\A.*?(?=^## )", "", black_md, count=1, flags=re.MULTILINE)
        parts = re.split(r"(?m)^## ", body)
    else:
        parts = re.split(r"(?m)^# ", black_md)
    blocks: list[str] = []
    for s in parts:
        s = s.strip()
        if not s:
            continue
        lines = s.split("\n", 1)
        title = lines[0].strip()
        body_md = lines[1].strip() if len(lines) > 1 else ""
        slug = _slugify(title)
        blocks.append(
            f'<section class="landing-{slug}">'
            f"<h2>{_escape(title)}</h2>{_md_to_html(body_md)}</section>"
        )
    return blocks


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9가-힣]+", "-", s)
    return s.strip("-") or "section"


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _md_to_html(md: str) -> str:
    """Minimal Markdown → HTML for v0.1. Handles paragraphs, ul, headings.

    For richer rendering, swap to a real Markdown lib in v0.2.
    """
    out: list[str] = []
    in_ul = False
    for line in md.splitlines():
        stripped = line.strip()
        if not stripped:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            continue
        if stripped.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_escape(stripped[2:])}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{_escape(stripped)}</p>")
    if in_ul:
        out.append("</ul>")
    return "".join(out)


def inject_slides(template_html: str, slide_blocks: list[str]) -> str:
    soup = BeautifulSoup(template_html, "html.parser")
    container = (
        soup.select_one("[data-role='slides']")
        or soup.select_one(".slides")
        or soup.select_one(".deck")
        or soup.select_one("main")
        or soup.body
    )
    assert container is not None, "no slide container found in template"
    # Clear existing slides.
    for child in list(container.children):
        if isinstance(child, Tag):
            child.decompose()
    container.append(BeautifulSoup("".join(slide_blocks), "html.parser"))
    return str(soup)


def build(
    index_json: Path,
    template_id: str,
    black_md: str,
    output_html: Path,
    mode: BuildMode = "slides",
) -> Path:
    tpl = load_template_meta(index_json, template_id)
    template_html = fetch_template_html(tpl)
    if mode == "landing":
        blocks = black_md_to_landing_sections(black_md)
    else:
        blocks = black_md_to_slide_blocks(black_md)
    merged = inject_slides(template_html, blocks)
    output_html.write_text(merged, encoding="utf-8")
    return output_html


LANDING_CASE_IDS: frozenset[str] = frozenset({"p70"})


def mode_for_case(case_id: str) -> BuildMode:
    """Map case_id → builder mode. Keeps the case→mode mapping in one place
    so deliver.py and tests stay in sync."""
    return "landing" if case_id in LANDING_CASE_IDS else "slides"
