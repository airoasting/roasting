"""Sync 63 case definitions from airoasting.github.io/5color/ to references/cases/*.md.

Pure parsing logic — no Claude API calls. Idempotent: rerunning produces identical files.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import requests


SITE_URL = "https://airoasting.github.io/5color/"


@dataclass
class Case:
    """One case from the 5color PROMPTS object."""

    id: str  # "p1"
    folio: str  # "I·1"
    cat: str  # "외부 커뮤니케이션"
    title: str  # "이메일 (외부 비즈니스)"
    subhead: str
    black: str
    red: dict[str, str]  # {axis, watch}
    silver: dict[str, str]
    blue: dict[str, str]
    gold: str
    full_prompt: str


def fetch_html(url: str) -> str:
    """Download the 5color site HTML."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_prompts(html: str) -> list[Case]:
    """Extract the const PROMPTS = {...} object from the site's HTML.

    Uses a brace-counting state machine because the JS object contains
    nested braces, regex literals, and quoted strings.
    """
    start_marker = "const PROMPTS = {"
    start = html.find(start_marker)
    if start < 0:
        raise RuntimeError("Could not find 'const PROMPTS = {' in HTML")
    i = start + len("const PROMPTS = ")
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
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    if end < 0:
        raise RuntimeError("Unterminated PROMPTS object")
    block = html[start + len("const PROMPTS = ") : end]
    return _split_entries(block)


def _split_entries(block: str) -> list[Case]:
    """Walk top-level entries inside the PROMPTS object body and parse each."""
    # Strip outer braces.
    body = block.strip()
    assert body.startswith("{") and body.endswith("}"), "expected braced object"
    body = body[1:-1].strip()
    cases: list[Case] = []
    i = 0
    while i < len(body):
        # Skip whitespace + commas.
        while i < len(body) and body[i] in " \t\n\r,":
            i += 1
        if i >= len(body):
            break
        # Read key (until ':').
        key_end = body.find(":", i)
        if key_end < 0:
            break
        key = body[i:key_end].strip()
        # Find the matching '{...}' value.
        val_start = body.find("{", key_end)
        if val_start < 0:
            break
        depth = 0
        in_str: str | None = None
        escape = False
        j = val_start
        while j < len(body):
            c = body[j]
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif in_str:
                if c == in_str:
                    in_str = None
            elif c in ('"', "'"):
                in_str = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        entry_body = body[val_start:j]
        cases.append(_parse_entry(key, entry_body))
        i = j
    return cases


def _parse_entry(case_id: str, entry_body: str) -> Case:
    """Pull each field out of one case body using regex."""

    def grab(field: str) -> str:
        # Match field:"value" capturing through escaped quotes.
        m = re.search(rf'{field}\s*:\s*"((?:[^"\\]|\\.)*)"', entry_body, re.DOTALL)
        if not m:
            return ""
        # Unescape \n and \"
        return m.group(1).replace("\\n", "\n").replace('\\"', '"').replace("\\'", "'")

    def grab_subobj(field: str) -> dict[str, str]:
        # Match field:{axis:"...",watch:"..."}
        # Note: \{{ in rf-string = literal { for regex; closing \} matches literal }
        m = re.search(
            rf'{field}\s*:\s*\{{\s*axis\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*watch\s*:\s*"((?:[^"\\]|\\.)*)"'
            r"\s*\}",
            entry_body,
            re.DOTALL,
        )
        if not m:
            return {"axis": "", "watch": ""}
        return {
            "axis": m.group(1).replace("\\n", "\n").replace('\\"', '"'),
            "watch": m.group(2).replace("\\n", "\n").replace('\\"', '"'),
        }

    return Case(
        id=case_id,
        folio=grab("folio"),
        cat=grab("cat"),
        title=re.sub(r"</?em>", "", grab("title")),
        subhead=grab("subhead"),
        black=grab("black"),
        red=grab_subobj("red"),
        silver=grab_subobj("silver"),
        blue=grab_subobj("blue"),
        gold=grab("gold"),
        full_prompt=grab("fullPrompt"),
    )


def _read_existing_enrich(path: Path) -> str | None:
    """If the existing case .md has an enrich: block, return it as a YAML snippet."""
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm = text[3:end]
    # Simple line-based extraction: capture from "enrich:" to next top-level key
    lines = fm.splitlines()
    capturing = False
    out: list[str] = []
    for line in lines:
        if line.startswith("enrich:"):
            capturing = True
            out.append(line)
            continue
        if capturing:
            if line and not line.startswith(("  ", "-", "\t")):
                # Hit next top-level key
                break
            out.append(line)
    return "\n".join(out) if out else None


def write_case_files(cases: list[Case], out_dir: Path) -> None:
    """Write one .md per case with YAML frontmatter + body."""
    for case in cases:
        path = out_dir / f"{case.id}.md"
        existing_enrich = _read_existing_enrich(path)
        path.write_text(_render_case(case, existing_enrich=existing_enrich), encoding="utf-8")


def _render_case(c: Case, existing_enrich: str | None = None) -> str:
    enrich_block = f"{existing_enrich}\n" if existing_enrich else ""
    fm = (
        "---\n"
        f"id: {c.id}\n"
        f'folio: "{c.folio}"\n'
        f'category: "{c.cat}"\n'
        f'title: "{c.title}"\n'
        f'subhead: "{_yaml_escape(c.subhead)}"\n'
        "tier: beta\n"
        f"{enrich_block}"
        "---\n\n"
    )
    body = (
        f"# {c.title}\n\n"
        f"> {c.subhead}\n\n"
        "## BLACK 캐스팅\n\n"
        f"{c.black}\n\n"
        "## RED — 이성\n\n"
        f"**평가축:** {c.red['axis']}\n\n"
        f"**감시 포인트:** {c.red['watch']}\n\n"
        "## SILVER — 분야 전문가\n\n"
        f"**평가축:** {c.silver['axis']}\n\n"
        f"**감시 포인트:** {c.silver['watch']}\n\n"
        "## BLUE — 공감\n\n"
        f"**평가축:** {c.blue['axis']}\n\n"
        f"**감시 포인트:** {c.blue['watch']}\n\n"
        "## GOLD — 독자 시나리오\n\n"
        f"{c.gold}\n\n"
        "## 합격선\n\n"
        "- 분석가 3인 평균 ≥ 9.5\n"
        "- GOLD 체류도 별도 보고\n"
        "- 권장 최대 4라운드\n\n"
        "## Full Prompt (5color 사이트 원본 — 참고용)\n\n"
        "```\n"
        f"{c.full_prompt}\n"
        "```\n"
    )
    return fm + body


def _yaml_escape(s: str) -> str:
    return s.replace('"', '\\"').replace("\n", " ").strip()


def write_index(cases: list[Case], path: Path) -> None:
    """Generate _index.md — 1-line summary per case for routing LLM judge."""
    lines = [
        "# 5-Color Cases — Routing Index\n",
        "1줄 요약 (folio · category · title · subhead). LLM judge가 xxxxx → top-3 매칭에 사용.\n\n",
    ]
    by_cat: dict[str, list[Case]] = {}
    for c in cases:
        by_cat.setdefault(c.cat, []).append(c)
    for cat, items in by_cat.items():
        lines.append(f"## {cat} ({len(items)}개)\n\n")
        for c in sorted(items, key=lambda x: x.folio):
            lines.append(f"- **{c.folio}** `{c.id}` — **{c.title}** · {c.subhead}\n")
        lines.append("\n")
    path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=SITE_URL)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Fetching {args.source}...", file=sys.stderr)
    html = fetch_html(args.source)
    cases = parse_prompts(html)
    print(f"Parsed {len(cases)} cases", file=sys.stderr)
    write_case_files(cases, args.out)
    write_index(cases, args.out / "_index.md")
    print(f"Wrote {len(cases)} case files + _index.md to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
