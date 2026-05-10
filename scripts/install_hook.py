"""Append /roasting pointer block to CLAUDE.md.

Idempotent: detects existing block via marker comments and replaces it.
Falls back to creating CLAUDE.md if absent.
"""
from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path


MARKER_BEGIN = "<!-- roasting:begin -->"
MARKER_END = "<!-- roasting:end -->"


def block(version: str = "0.1.0") -> str:
    today = datetime.date.today().isoformat()
    return (
        f"{MARKER_BEGIN}\n"
        f"## 하네스: /roasting (airoasting/roasting v{version})\n\n"
        "**트리거**: 화이트칼라 산출물 작성 요청 (이메일·보고서·PPT·메모 등) 시 `roasting` 스킬 사용. xxxxx에서 도메인 자동 라우팅.\n\n"
        "**산출 위치**: ~/.claude/roasting/_workspace/\n\n"
        "**변경 이력**:\n"
        "| 날짜 | 변경 | 사유 |\n"
        "|------|------|------|\n"
        f"| {today} | 초기 설치 (v{version}) | - |\n"
        f"{MARKER_END}\n"
    )


def install(claude_md: Path, version: str = "0.1.0") -> str:
    """Insert or replace the roasting block. Returns 'inserted' or 'replaced'."""
    new_block = block(version)
    if not claude_md.exists():
        claude_md.write_text(new_block + "\n", encoding="utf-8")
        return "inserted"
    body = claude_md.read_text(encoding="utf-8")
    if MARKER_BEGIN in body and MARKER_END in body:
        # Replace existing block.
        before = body.split(MARKER_BEGIN, 1)[0]
        after = body.split(MARKER_END, 1)[1]
        new_body = before + new_block + after
        claude_md.write_text(new_body, encoding="utf-8")
        return "replaced"
    # Append.
    sep = "\n" if body.endswith("\n") else "\n\n"
    claude_md.write_text(body + sep + new_block + "\n", encoding="utf-8")
    return "inserted"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True, type=Path,
                    help="Path to CLAUDE.md (e.g. ~/.claude/CLAUDE.md or ./CLAUDE.md)")
    ap.add_argument("--version", default="0.1.0")
    args = ap.parse_args()
    action = install(args.target, args.version)
    print(f"{action} roasting pointer in {args.target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
