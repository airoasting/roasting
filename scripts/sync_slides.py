"""Sync 35 slide templates from airoasting.github.io/slide_library/ to index.json.

ACTUAL SCHEMA (differs from original plan — inspected 2026-05-10):
  The slide_library site does NOT use [data-id] HTML cards. Instead, templates
  are declared as a JS array: `const TEMPLATES = [ {...}, ... ]` inside an
  inline <script> tag. We parse this array with a bracket-counting state machine
  and extract fields using regex, mirroring the approach used in sync_cases.py.

Per-template fields in the JS source:
  slug        — unique string ID (used as `id` in output)
  name        — Korean display name
  nameEn      — English name (used as `name` in output alongside Korean)
  tagline     — Korean one-line description (stored as `subhead` in keywords)
  scheme      — color scheme: "light" | "dark" | "mixed"
                Mapped to plan's `color` vocab: light→light, dark→dark, mixed→mixed
                (no "full" value exists in live data; plan vocab adapted)
  formality   — "high" | "medium-high" | "medium" | "medium-low" | "low"
                Mapped to plan's `formality` vocab:
                  "high"        → "formal"
                  "medium-high" → "formal"   (nearest plan bucket)
                  "medium"      → "neutral"
                  "medium-low"  → "casual"
                  "low"         → "casual"
  slides      — integer slide count (mapped to `slide_count`)
  mood        — JS array of Korean strings → flattened to keywords list
  occasion    — JS array of Korean strings → appended to keywords list

Output URL pattern: {base_url}templates/{slug}/template.html
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import requests


SITE_URL = "https://airoasting.github.io/slide_library/"

# Mapping from live `scheme` values → plan's `color` vocabulary
_SCHEME_TO_COLOR: dict[str, str] = {
    "light": "light",
    "dark": "dark",
    "mixed": "mixed",
}

# Mapping from live `formality` values → plan's `formality` vocabulary
_FORMALITY_MAP: dict[str, str] = {
    "high": "formal",
    "medium-high": "formal",
    "medium": "neutral",
    "medium-low": "casual",
    "low": "casual",
}


@dataclass
class Template:
    id: str
    name: str
    color: str  # light | dark | mixed  (plan vocab; mapped from site's "scheme")
    formality: str  # formal | neutral | casual  (plan vocab; mapped from site's "formality")
    url: str
    slide_count: int
    keywords: list[str]


def fetch_html(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_templates(html: str, base_url: str) -> list[Template]:
    """Extract const TEMPLATES = [...] from the site HTML and parse each entry."""
    start_marker = "const TEMPLATES = ["
    start = html.find(start_marker)
    if start < 0:
        raise RuntimeError("Could not find 'const TEMPLATES = [' in HTML")
    i = start + len("const TEMPLATES = ")
    depth = 0
    in_str: str | None = None
    escape = False
    end = -1
    while i < len(html):
        c = html[i]
        if escape:
            escape = False
        elif c == "\\":
            escape = True
        elif in_str:
            if c == in_str:
                in_str = None
        elif c in ('"', "'"):
            in_str = c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    if end < 0:
        raise RuntimeError("Unterminated TEMPLATES array")

    array_str = html[start + len("const TEMPLATES = ") : end]
    return _parse_array(array_str, base_url)


def _parse_array(array_str: str, base_url: str) -> list[Template]:
    """Walk each top-level {...} object inside the array."""
    body = array_str.strip()
    assert body.startswith("[") and body.endswith("]"), "expected [...] array"
    body = body[1:-1].strip()

    templates: list[Template] = []
    i = 0
    while i < len(body):
        # Skip whitespace, commas, JS line comments
        while i < len(body) and body[i] in " \t\n\r,":
            i += 1
        # Skip // ... line comments
        if body[i : i + 2] == "//":
            newline = body.find("\n", i)
            i = newline + 1 if newline >= 0 else len(body)
            continue
        if i >= len(body):
            break
        if body[i] != "{":
            break

        # Find matching closing brace
        depth = 0
        in_str2: str | None = None
        escape2 = False
        j = i
        while j < len(body):
            c = body[j]
            if escape2:
                escape2 = False
            elif c == "\\":
                escape2 = True
            elif in_str2:
                if c == in_str2:
                    in_str2 = None
            elif c in ('"', "'"):
                in_str2 = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        entry = body[i:j]
        t = _parse_entry(entry, base_url)
        if t is not None:
            templates.append(t)
        i = j

    return templates


def _parse_entry(entry: str, base_url: str) -> Template | None:
    """Extract fields from one template object literal."""

    def grab(field: str) -> str:
        m = re.search(rf'{field}\s*:\s*"((?:[^"\\]|\\.)*)"', entry, re.DOTALL)
        if not m:
            return ""
        return m.group(1).replace("\\n", "\n").replace('\\"', '"')

    def grab_int(field: str) -> int:
        m = re.search(rf"{field}\s*:\s*(\d+)", entry)
        return int(m.group(1)) if m else 0

    def grab_array(field: str) -> list[str]:
        m = re.search(rf"{field}\s*:\s*\[([^\]]*)\]", entry, re.DOTALL)
        if not m:
            return []
        raw = m.group(1)
        items = re.findall(r'"((?:[^"\\]|\\.)*)"', raw)
        return [it.replace('\\"', '"') for it in items]

    slug = grab("slug")
    if not slug:
        return None

    name_ko = grab("name")
    name_en = grab("nameEn")
    display_name = f"{name_ko} ({name_en})" if name_en else name_ko

    raw_color = grab("scheme")
    color = _SCHEME_TO_COLOR.get(raw_color, "mixed")

    raw_formality = grab("formality")
    formality = _FORMALITY_MAP.get(raw_formality, "neutral")

    slide_count = grab_int("slides")

    mood = grab_array("mood")
    occasion = grab_array("occasion")
    tagline = grab("tagline")
    keywords = mood + occasion
    if tagline:
        keywords.append(tagline)

    url = f"{base_url.rstrip('/')}/templates/{slug}/template.html"

    return Template(
        id=slug,
        name=display_name,
        color=color,
        formality=formality,
        url=url,
        slide_count=slide_count,
        keywords=keywords,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=SITE_URL)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Fetching {args.source}...", file=sys.stderr)
    html = fetch_html(args.source)
    templates = parse_templates(html, args.source)
    print(f"Parsed {len(templates)} templates", file=sys.stderr)
    args.out.write_text(
        json.dumps([asdict(t) for t in templates], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
