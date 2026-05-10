"""Generate docs/ko/case-catalog.md from references/cases/p*.md frontmatter."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def parse_fm(text: str) -> dict:  # type: ignore[type-arg]
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    return yaml.safe_load(text[3:end]) or {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    by_cat: dict[str, list[dict]] = {}  # type: ignore[type-arg]
    for p in sorted(args.cases.glob("p*.md")):
        fm = parse_fm(p.read_text(encoding="utf-8"))
        by_cat.setdefault(fm.get("category", "기타"), []).append(fm)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# 케이스 카탈로그\n\n",
             "5color 사이트의 63개 화이트칼라 산출물 케이스 전체 목록.\n\n"]
    for cat, items in by_cat.items():
        lines.append(f"## {cat} ({len(items)}개)\n\n")
        lines.append("| Folio | ID | 제목 | 한 줄 |\n|---|---|---|---|\n")
        for it in sorted(items, key=lambda x: str(x.get("folio", ""))):
            lines.append(
                f"| {it.get('folio')} | `{it.get('id')}` | "
                f"{it.get('title')} | {it.get('subhead', '')} |\n"
            )
        lines.append("\n")
    args.out.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
