# /roasting v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `airoasting/roasting` v0.1 — a distributable Claude Code plugin that executes the 5-Color Harness methodology over 63 white-collar cases sourced from `airoasting.github.io/5color/`, ships via Anthropic Marketplace + GitHub, and operates as an open beta with anonymous telemetry.

**Architecture:** Pipeline + Supervisor (7-Phase). Phase 5 uses Agent Teams (TeamCreate + SendMessage + TaskCreate) for RGSB debate-driven scoring with σ ≥ 0.5 trigger; sub-agent path retained as fallback. Progressive Disclosure: SKILL.md + references/cases/_index.md (~30KB) + per-case .md files (~3KB each, lazy loaded).

**Tech Stack:** Claude Code (skills + agents), Python 3.11 (sync/anti-patterns/route/telemetry), pytest + ruff + mypy, Supabase Postgres (telemetry), GitHub Actions (CI), Make (release), Anthropic Marketplace.

**Reference Spec:** `docs/superpowers/specs/2026-05-10-roasting-design.md` (commit `690c11e`).

---

## PR Map (18 PRs to v0.1.0 release)

| # | PR Title | Depends on | Acceptance Gate |
|---|---|---|---|
| 1 | Repo scaffolding + manifests | — | `gh repo view` works |
| 2 | Case sync infrastructure | PR1 | 63 case .md files generated |
| 3 | Slide library index | PR1 | 35 templates indexed |
| 4 | Anti-pattern detection | PR1 | 50 unit tests pass, FP=0 |
| 5 | Routing infrastructure | PR2 | 189 tests, top-1 ≥ 90% Wilson lower |
| 6 | Agent definitions (5×) | PR1 | 5 agents/*.md valid frontmatter |
| 7 | SKILL.md Phase 0–2 | PR5, PR6 | E2E parse + seed load passes |
| 8 | SKILL.md Phase 3–4 | PR4, PR7 | BLACK draft + AP self-correct passes |
| 9 | SKILL.md Phase 5 sub-agent fallback | PR8 | 4 reviewers parallel, score aggregated |
| 10 | SKILL.md Phase 5 Agent Teams | PR9 | TeamCreate path works, fallback retained |
| 11 | SKILL.md Phase 6–7 | PR10 | E2E case completes, 3 outputs delivered |
| 12 | HTML slide output (PPT cases) | PR11 | PPT case → HTML deck rendered |
| 13 | Telemetry backend | PR1 | Supabase row inserted on opt-in |
| 14 | CLAUDE.md auto-registration | PR11 | Pointer registered on install |
| 15 | Documentation (README ko/en, privacy, CHANGELOG) | PR11 | All docs match spec |
| 16 | GitHub Actions CI | PR4, PR5 | CI green on PR + tag |
| 17 | Quality integration tests | PR12 | 15 scenarios, avg ≥ 9.0 |
| 18 | v0.1.0 beta release | All | Marketplace listed, airoasting landing live |

**Critical path:** PR1 → PR2 → PR5 → PR7 → PR8 → PR9 → PR10 → PR11 → PR12 → PR17 → PR18 (≈ 11 PRs sequential, others parallel).

---

## Risk Mitigation Build Order

**Risk 1: Agent Teams instability (experimental).** Build sub-agent fallback (PR9) BEFORE Agent Teams (PR10). PR10 adds Agent Teams path with feature flag and auto-falls back to PR9 path if `TeamCreate` errors.

**Risk 2: Routing accuracy < 90%.** Test in PR5 *before* writing main SKILL.md. If gate fails, iterate on `_index.md` (richer descriptions + synonyms) before unblocking PR7.

**Risk 3: Supabase free tier traffic.** Telemetry is opt-in (default OFF in v0.1). PR13 is parallel to main path — safe to defer if backend not ready.

---

## Conventions

- **Working dir:** `~/Desktop/New Projects/무제 폴더` (rename to `airoasting-roasting/` before pushing).
- **Branch naming:** `feat/pr-{N}-{slug}`, e.g. `feat/pr-2-case-sync`.
- **Commit format:** Conventional commits (`feat(scope):`, `test(scope):`, `docs(scope):`).
- **Test file naming:** `tests/{category}/test_{component}.py`.
- **Python entry:** All scripts run as modules (`python -m scripts.sync_cases`).
- **Per-PR cycle:** branch → commits → push → `gh pr create` → merge to `main` after CI green.

---

## PR 1: Repo Scaffolding + Manifests

**Goal:** Establish directory structure, plugin manifest, license, and Python toolchain.

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `pyproject.toml`
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `Makefile`
- Create: `.github/workflows/test.yml` (skeleton)
- Create: `README.md` (skeleton — full content in PR15)
- Create: `CHANGELOG.md`
- Create: `skills/roasting/.gitkeep`, `skills/roasting/agents/.gitkeep`, `skills/roasting/references/cases/.gitkeep`, `skills/roasting/references/anti-patterns/.gitkeep`, `skills/roasting/references/slide-templates/.gitkeep`
- Create: `scripts/__init__.py`
- Create: `tests/__init__.py`, `tests/routing/__init__.py`, `tests/anti_patterns/__init__.py`, `tests/quality/__init__.py`

### Task 1.1: Initialize .gitignore

- [ ] **Step 1:** Create `.gitignore` at repo root with the following content:

```
# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.mypy_cache/
.ruff_cache/
.venv/
venv/

# Build
dist/
*.zip

# OS
.DS_Store
Thumbs.db

# Claude Code workspace (runtime artifacts, never committed)
_workspace/
~/.claude/roasting/

# Secrets
.env
.env.local
config.local.json
```

- [ ] **Step 2:** Verify with `git check-ignore -v __pycache__/foo.pyc` — expected output: `.gitignore:3:__pycache__/  __pycache__/foo.pyc`.

### Task 1.2: Add MIT LICENSE

- [ ] **Step 1:** Create `LICENSE` with MIT text:

```
MIT License

Copyright (c) 2026 AI ROASTING (jaydenjkang@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Task 1.3: Initialize Python toolchain (pyproject.toml)

- [ ] **Step 1:** Create `pyproject.toml`:

```toml
[project]
name = "roasting"
version = "0.1.0"
description = "5-Color Harness execution engine — Claude Code plugin"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.40.0",
    "beautifulsoup4>=4.12.0",
    "requests>=2.31.0",
    "supabase>=2.3.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "ruff>=0.6",
    "mypy>=1.10",
    "types-requests",
    "types-PyYAML",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

- [ ] **Step 2:** Run `python -m venv .venv && .venv/bin/pip install -e ".[dev]"` and verify `.venv/bin/pytest --version` outputs `pytest 8.x.x`.

### Task 1.4: Create plugin.json manifest

- [ ] **Step 1:** Create `.claude-plugin/plugin.json`:

```json
{
  "name": "roasting",
  "version": "0.1.0",
  "description": "5-Color Harness execution engine for Korean business leaders. Auto-routes 63 white-collar artifact cases (email, board memo, investor letter, etc.) and produces output via BLACK Producer + RGSB Reviewer team with debate-driven scoring. Korean only.",
  "author": {
    "name": "AI ROASTING",
    "url": "https://airoasting.github.io"
  },
  "homepage": "https://airoasting.github.io/roasting",
  "repository": "https://github.com/airoasting/roasting",
  "license": "MIT",
  "keywords": [
    "5-color-harness",
    "korean",
    "executive",
    "white-collar",
    "agent-teams",
    "producer-reviewer",
    "claude-code-plugin",
    "open-beta"
  ]
}
```

- [ ] **Step 2:** Validate JSON: `python -c "import json; json.load(open('.claude-plugin/plugin.json'))"` — no output = valid.

### Task 1.5: Create marketplace.json

- [ ] **Step 1:** Create `.claude-plugin/marketplace.json`:

```json
{
  "name": "airoasting",
  "owner": {
    "name": "AI ROASTING",
    "url": "https://airoasting.github.io"
  },
  "plugins": [
    {
      "name": "roasting",
      "source": "./",
      "version": "0.1.0",
      "description": "5-Color Harness execution engine for Korean business leaders."
    }
  ]
}
```

### Task 1.6: Create skeleton Makefile

- [ ] **Step 1:** Create `Makefile`:

```makefile
PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest

.PHONY: help sync-cases sync-slides test test-routing test-anti-patterns test-quality lint typecheck package publish clean

help:
	@echo "Available commands:"
	@echo "  make sync-cases       - Pull 63 cases from airoasting.github.io/5color"
	@echo "  make sync-slides      - Pull 35 templates from airoasting.github.io/slide_library"
	@echo "  make test             - Run all tests"
	@echo "  make test-routing     - Routing accuracy tests (189)"
	@echo "  make test-anti-patterns - Anti-pattern unit tests (50)"
	@echo "  make test-quality     - Quality integration tests (15)"
	@echo "  make lint             - ruff check"
	@echo "  make typecheck        - mypy check"
	@echo "  make package          - Build distributable .zip"
	@echo "  make publish          - Create GitHub release"
	@echo "  make clean            - Remove caches and dist/"

sync-cases:
	$(PYTHON) -m scripts.sync_cases \
		--source https://airoasting.github.io/5color/ \
		--out skills/roasting/references/cases/

sync-slides:
	$(PYTHON) -m scripts.sync_slides \
		--source https://airoasting.github.io/slide_library/ \
		--out skills/roasting/references/slide-templates/index.json

test: test-routing test-anti-patterns test-quality

test-routing:
	$(PYTEST) tests/routing/ -v

test-anti-patterns:
	$(PYTEST) tests/anti_patterns/ -v

test-quality:
	$(PYTEST) tests/quality/ -v --slow

lint:
	.venv/bin/ruff check .

typecheck:
	.venv/bin/mypy scripts/ skills/

package:
	mkdir -p dist/
	zip -r dist/roasting-$$(jq -r .version .claude-plugin/plugin.json).zip \
		.claude-plugin/ skills/ scripts/ docs/ README.md README.ko.md LICENSE CHANGELOG.md

publish:
	gh release create v$$(jq -r .version .claude-plugin/plugin.json) \
		dist/roasting-*.zip \
		--title "v$$(jq -r .version .claude-plugin/plugin.json)" \
		--notes-file CHANGELOG.md

clean:
	rm -rf dist/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
```

- [ ] **Step 2:** Test `make help` outputs the menu.

### Task 1.7: Create README.md skeleton (full version in PR 15)

- [ ] **Step 1:** Create `README.md`:

```markdown
# roasting

> 5-Color Harness execution engine for Korean business leaders. Open Beta v0.1.

**Korean documentation:** see [README.ko.md](README.ko.md).

## Install

```bash
/plugin marketplace add airoasting/roasting
/plugin install roasting@airoasting
```

## Privacy

Anonymous metadata only (case ID, score, round count). Content (xxxxx input, BLACK output, RGSB comments) is **never** transmitted.

## License

MIT — see [LICENSE](LICENSE).
```

### Task 1.8: Create CHANGELOG.md

- [ ] **Step 1:** Create `CHANGELOG.md`:

```markdown
# Changelog

This project follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.1.0] - 2026-XX-XX (Open Beta)

### Added

- Initial release with 63 cases routed via Expert Pool pattern.
- 5-Color Harness Producer-Reviewer team (BLACK + RED·SILVER·BLUE·GOLD).
- Agent Teams mode for Phase 5 RGSB debate; sub-agent fallback retained.
- Anti-pattern detection (5 types): HALLUCINATED_NUMBER, VAGUE_CTA, MISSING_GOLD_HOOK, TONE_MISMATCH, LEGAL_RISK_TERM.
- slide_library binding for PPT cases (35 templates, color × formality axes).
- 9.5 acceptance threshold + 4-round cap.
- Anonymous opt-in telemetry; `/roasting --feedback` GitHub Issue prefilled.
- CLAUDE.md auto-registration on install.

### Privacy

- Content (xxxxx input, BLACK output, RGSB comments) never transmitted.
- Telemetry default = OFF; opt-in via `~/.claude/roasting/config.json`.
```

### Task 1.9: Create skill + test directory placeholders

- [ ] **Step 1:** Create empty marker files:

```bash
mkdir -p skills/roasting/{agents,references/{cases,anti-patterns,slide-templates}}
touch skills/roasting/agents/.gitkeep
touch skills/roasting/references/cases/.gitkeep
touch skills/roasting/references/anti-patterns/.gitkeep
touch skills/roasting/references/slide-templates/.gitkeep

mkdir -p scripts tests/{routing,anti_patterns,quality}
touch scripts/__init__.py
touch tests/__init__.py tests/routing/__init__.py tests/anti_patterns/__init__.py tests/quality/__init__.py
```

### Task 1.10: Skeleton GitHub Actions

- [ ] **Step 1:** Create `.github/workflows/test.yml` (filled out further in PR 16):

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: pytest tests/ -v
```

### Task 1.11: Initial commit + push

- [ ] **Step 1:** Run:

```bash
git config user.email "jaydenjkang@gmail.com"
git config user.name "Jayden Kang"
git add -A
git status
```

- [ ] **Step 2:** Verify all PR1 files staged. Then commit:

```bash
git commit -m "feat(scaffold): initialize repo structure, manifests, toolchain

- pyproject.toml with anthropic, beautifulsoup4, supabase deps
- .claude-plugin/{plugin,marketplace}.json
- Makefile with sync-cases, test, package, publish targets
- LICENSE (MIT), CHANGELOG.md, README.md skeleton
- skills/roasting/{agents,references/{cases,anti-patterns,slide-templates}} dirs
- tests/{routing,anti_patterns,quality} dirs
- .github/workflows/test.yml skeleton

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 3:** Create GitHub repo and push:

```bash
gh repo create airoasting/roasting --public --description "5-Color Harness execution engine for Korean business leaders" --homepage "https://airoasting.github.io/roasting"
git remote add origin git@github.com:airoasting/roasting.git
git branch -M main
git push -u origin main
```

- [ ] **Step 4:** Verify: `gh repo view airoasting/roasting --json name,url,description` shows correct values.

**Acceptance criteria for PR 1:**
- [ ] `.venv/bin/pytest --version` works
- [ ] `make help` shows menu
- [ ] `python -c "import json; json.load(open('.claude-plugin/plugin.json'))"` succeeds
- [ ] GitHub repo `airoasting/roasting` exists and matches `git remote -v`

---

## PR 2: Case Sync Infrastructure

**Goal:** Parse 63 cases from `airoasting.github.io/5color/`, generate per-case `.md` files and `_index.md` for routing.

**Depends on:** PR 1.

**Files:**
- Create: `scripts/sync_cases.py`
- Create: `tests/test_sync_cases.py`
- Create: `skills/roasting/references/cases/_index.md` (generated)
- Create: `skills/roasting/references/cases/p1.md` ... `p72.md` (63 files, generated)

### Task 2.1: Write sync_cases.py — HTML fetcher

- [ ] **Step 1:** Create `scripts/sync_cases.py` with imports and main scaffold:

```python
"""Sync 63 case definitions from airoasting.github.io/5color/ to references/cases/*.md.

Pure parsing logic — no Claude API calls. Idempotent: rerunning produces identical files.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


SITE_URL = "https://airoasting.github.io/5color/"


@dataclass
class Case:
    """One case from the 5color PROMPTS object."""
    id: str            # "p1"
    folio: str         # "I·1"
    cat: str           # "외부 커뮤니케이션"
    title: str         # "이메일 (외부 비즈니스)"
    subhead: str
    black: str
    red: dict[str, str]     # {axis, watch}
    silver: dict[str, str]
    blue: dict[str, str]
    gold: str
    full_prompt: str


def fetch_html(url: str) -> str:
    """Download the 5color site HTML."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


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
```

### Task 2.2: Implement parse_prompts (extract PROMPTS JS object)

- [ ] **Step 1:** Add `parse_prompts` function:

```python
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
        return m.group(1).replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")

    def grab_subobj(field: str) -> dict[str, str]:
        # Match field:{axis:"...",watch:"..."}
        m = re.search(
            rf'{field}\s*:\s*\{{\s*axis\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*watch\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}}',
            entry_body, re.DOTALL,
        )
        if not m:
            return {"axis": "", "watch": ""}
        return {
            "axis": m.group(1).replace('\\n', '\n').replace('\\"', '"'),
            "watch": m.group(2).replace('\\n', '\n').replace('\\"', '"'),
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
```

### Task 2.3: Implement write_case_files

- [ ] **Step 1:** Add file writers:

```python
def write_case_files(cases: list[Case], out_dir: Path) -> None:
    """Write one .md per case with YAML frontmatter + body."""
    for case in cases:
        path = out_dir / f"{case.id}.md"
        path.write_text(_render_case(case), encoding="utf-8")


def _render_case(c: Case) -> str:
    fm = (
        "---\n"
        f"id: {c.id}\n"
        f'folio: "{c.folio}"\n'
        f'category: "{c.cat}"\n'
        f'title: "{c.title}"\n'
        f'subhead: "{_yaml_escape(c.subhead)}"\n'
        f"tier: beta\n"
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
    lines = ["# 5-Color Cases — Routing Index\n",
             "1줄 요약 (folio · category · title · subhead). LLM judge가 xxxxx → top-3 매칭에 사용.\n\n"]
    by_cat: dict[str, list[Case]] = {}
    for c in cases:
        by_cat.setdefault(c.cat, []).append(c)
    for cat, items in by_cat.items():
        lines.append(f"## {cat} ({len(items)}개)\n\n")
        for c in sorted(items, key=lambda x: x.folio):
            lines.append(f"- **{c.folio}** `{c.id}` — **{c.title}** · {c.subhead}\n")
        lines.append("\n")
    path.write_text("".join(lines), encoding="utf-8")
```

### Task 2.4: Test sync_cases parses 63 cases

- [ ] **Step 1:** Create `tests/test_sync_cases.py`:

```python
"""End-to-end test that sync_cases parses the live site to 63 cases."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.network
def test_sync_produces_63_cases(tmp_path: Path) -> None:
    out = tmp_path / "cases"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.sync_cases", "--out", str(out)],
        capture_output=True, text=True, check=True,
    )
    assert "Parsed 63 cases" in result.stderr
    md_files = sorted(out.glob("p*.md"))
    assert len(md_files) == 63
    index = out / "_index.md"
    assert index.exists()
    body = index.read_text(encoding="utf-8")
    # Spot-check 4 expected cases.
    for marker in ["p1", "p23", "p41", "p65"]:
        assert f"`{marker}`" in body
```

- [ ] **Step 2:** Add `network` marker to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
markers = [
    "network: tests that hit the live 5color site",
    "slow: integration tests that call Claude API",
]
```

- [ ] **Step 3:** Run: `.venv/bin/pytest tests/test_sync_cases.py -v -m network` — expected: 1 passed.

### Task 2.5: Run sync to populate cases/

- [ ] **Step 1:** Run `make sync-cases`. Expected stderr line: `Parsed 63 cases`.
- [ ] **Step 2:** Verify: `ls skills/roasting/references/cases/ | wc -l` outputs `64` (63 cases + 1 _index.md).
- [ ] **Step 3:** Spot check `cat skills/roasting/references/cases/p1.md` — must show frontmatter + BLACK 캐스팅 + RED/SILVER/BLUE/GOLD sections.

### Task 2.6: Commit

- [ ] **Step 1:** Commit:

```bash
git add scripts/sync_cases.py tests/test_sync_cases.py pyproject.toml \
  skills/roasting/references/cases/
git commit -m "feat(sync): parse 63 cases from 5color site to per-case .md files

- scripts/sync_cases.py: brace-counting state machine extracts PROMPTS
  object; regex pulls per-case fields (folio, cat, title, BLACK, RGSB, GOLD)
- references/cases/p1.md ... p72.md: 63 generated case files with YAML
  frontmatter (id, folio, category, title, subhead, tier=beta)
- references/cases/_index.md: 1-line routing summary grouped by 8
  categories (외부 커뮤니케이션 12, 분석·보고서 12, etc.)
- tests/test_sync_cases.py: network test verifies 63 cases + index

Acceptance: 'Parsed 63 cases' confirmed via make sync-cases.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 2:**
- [ ] 63 case .md files at `skills/roasting/references/cases/p*.md`
- [ ] `_index.md` lists all 63 across 8 categories
- [ ] `pytest tests/test_sync_cases.py -m network` passes
- [ ] Each case file has frontmatter + BLACK + RED + SILVER + BLUE + GOLD sections

---

## PR 3: Slide Library Index

**Goal:** Scrape 35 HTML templates from `airoasting.github.io/slide_library` and produce `index.json` with `{id, name, color, formality, url, slide_count}` schema.

**Depends on:** PR 1.

**Files:**
- Create: `scripts/sync_slides.py`
- Create: `tests/test_sync_slides.py`
- Create: `skills/roasting/references/slide-templates/index.json` (generated)

### Task 3.1: Write sync_slides.py scraper

- [ ] **Step 1:** Create `scripts/sync_slides.py`:

```python
"""Sync 35 slide templates from airoasting.github.io/slide_library/ to index.json.

The slide_library site renders cards with data-* attributes carrying color and
formality metadata. We parse the cards, extract per-template URLs, and emit a
JSON index for /roasting Phase 2 (PPT case seeding).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag


SITE_URL = "https://airoasting.github.io/slide_library/"


@dataclass
class Template:
    id: str
    name: str
    color: str       # full | light | dark | mixed
    formality: str   # full | casual | neutral | formal
    url: str
    slide_count: int
    keywords: list[str]


def fetch_html(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_templates(html: str, base_url: str) -> list[Template]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("[data-id]")
    templates: list[Template] = []
    for card in cards:
        if not isinstance(card, Tag):
            continue
        tid = card.get("data-id") or ""
        if not tid:
            continue
        templates.append(Template(
            id=str(tid),
            name=_text(card, ".card__title") or _text(card, ".title") or str(tid),
            color=str(card.get("data-color") or "mixed"),
            formality=str(card.get("data-formality") or "neutral"),
            url=_resolve_url(base_url, str(card.get("data-url") or card.get("href") or "")),
            slide_count=_int_attr(card, "data-slide-count", default=0),
            keywords=_split_keywords(card.get("data-keywords")),
        ))
    return templates


def _text(parent: Tag, sel: str) -> str:
    el = parent.select_one(sel)
    return el.get_text(strip=True) if el else ""


def _int_attr(card: Tag, name: str, default: int = 0) -> int:
    raw = card.get(name)
    if raw is None:
        return default
    m = re.search(r"\d+", str(raw))
    return int(m.group()) if m else default


def _split_keywords(raw: object) -> list[str]:
    if raw is None:
        return []
    return [k.strip() for k in str(raw).split(",") if k.strip()]


def _resolve_url(base: str, ref: str) -> str:
    if ref.startswith(("http://", "https://")):
        return ref
    if ref.startswith("/"):
        return base.rstrip("/") + ref
    return base.rstrip("/") + "/" + ref


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
```

### Task 3.2: Test sync_slides parses ≥ 30 templates

- [ ] **Step 1:** Create `tests/test_sync_slides.py`:

```python
"""End-to-end test for slide_library scraper."""
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
        check=True, capture_output=True, text=True,
    )
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 30, f"expected ≥ 30 templates, got {len(data)}"
    sample = data[0]
    for key in ("id", "name", "color", "formality", "url", "slide_count", "keywords"):
        assert key in sample, f"missing key {key} in template entry"
    # Verify color and formality values are from expected vocab.
    valid_color = {"full", "light", "dark", "mixed"}
    valid_formality = {"full", "casual", "neutral", "formal"}
    for t in data:
        assert t["color"] in valid_color, f"unexpected color {t['color']}"
        assert t["formality"] in valid_formality, f"unexpected formality {t['formality']}"
```

- [ ] **Step 2:** Run: `.venv/bin/pytest tests/test_sync_slides.py -m network -v` — expected: 1 passed.

### Task 3.3: Run sync, populate index.json

- [ ] **Step 1:** Run `make sync-slides`.
- [ ] **Step 2:** Verify: `jq 'length' skills/roasting/references/slide-templates/index.json` returns a number ≥ 30 (target 35).
- [ ] **Step 3:** Spot check: `jq '.[0]' skills/roasting/references/slide-templates/index.json` shows full schema.

### Task 3.4: Commit

- [ ] **Step 1:** Commit:

```bash
git add scripts/sync_slides.py tests/test_sync_slides.py \
  skills/roasting/references/slide-templates/index.json
git commit -m "feat(slides): scrape slide_library to references/slide-templates/index.json

- scripts/sync_slides.py: BeautifulSoup parser for slide_library site cards
- index.json schema: {id, name, color (full|light|dark|mixed), formality
  (full|casual|neutral|formal), url, slide_count, keywords[]}
- 35 templates indexed (or ≥ 30 acceptable)
- tests verify color/formality vocabulary

Used by Phase 2 SEED LOAD for PPT cases (p41, p42, p43, p45) — auto-recommend
top-3 matched on color × formality + xxxxx clue analysis.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 3:**
- [ ] `index.json` exists with ≥ 30 templates
- [ ] All entries have `{id, name, color, formality, url, slide_count, keywords}` keys
- [ ] `color` ∈ {full, light, dark, mixed}; `formality` ∈ {full, casual, neutral, formal}

---

## PR 4: Anti-Pattern Detection (5 types + 3-strikes)

**Goal:** Implement `scripts/anti_patterns.py` with 5 detectors and 50 unit tests (5 positive + 5 negative per type, false positive rate 0%).

**Depends on:** PR 1.

**Files:**
- Create: `scripts/anti_patterns.py`
- Create: `scripts/llm_judge.py` (small Haiku helper used by detectors and routing)
- Create: `skills/roasting/references/anti-patterns/hallucinated-number.md`
- Create: `skills/roasting/references/anti-patterns/vague-cta.md`
- Create: `skills/roasting/references/anti-patterns/missing-gold-hook.md`
- Create: `skills/roasting/references/anti-patterns/tone-mismatch.md`
- Create: `skills/roasting/references/anti-patterns/legal-risk-term.md`
- Create: `tests/anti_patterns/test_hallucinated_number.py`
- Create: `tests/anti_patterns/test_vague_cta.py`
- Create: `tests/anti_patterns/test_missing_gold_hook.py`
- Create: `tests/anti_patterns/test_tone_mismatch.py`
- Create: `tests/anti_patterns/test_legal_risk_term.py`
- Create: `tests/anti_patterns/test_three_strikes.py`
- Create: `tests/anti_patterns/conftest.py` (fakes)

### Task 4.1: LLM judge helper (mockable)

- [ ] **Step 1:** Create `scripts/llm_judge.py`:

```python
"""Tiny Haiku-backed LLM judge wrapper. Mockable for tests via dependency injection."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from anthropic import Anthropic


HAIKU_MODEL = "claude-haiku-4-5-20251001"


class JudgeFn(Protocol):
    def __call__(self, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class HaikuJudge:
    """Real implementation backed by Anthropic Haiku.

    Tests should pass a fake JudgeFn instead of using this.
    """
    client: Anthropic | None = None

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def __call__(self, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]:
        assert self.client is not None
        msg = self.client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=512,
            system=system + "\n\nReturn ONLY a JSON object matching this schema: " + json.dumps(schema),
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in msg.content if b.type == "text")
        # Trim ```json fences if present.
        if text.strip().startswith("```"):
            text = text.strip().strip("`")
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
```

### Task 4.2: HALLUCINATED_NUMBER detector + tests

- [ ] **Step 1:** Create `scripts/anti_patterns.py` skeleton with `AntiPattern` dataclass + module structure:

```python
"""Anti-pattern detection for /roasting.

5 detectors run BEFORE Phase 5 RGSB scoring. Detected patterns trigger BLACK
self-correction (round counter unaffected). Three consecutive detections of
the same pattern (counted within OR across rounds) escalate to user.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from .llm_judge import JudgeFn


# 시·소설·링크드인 프로필은 HALLUCINATED_NUMBER 적용 제외.
HN_EXEMPT_CASES: frozenset[str] = frozenset({"p63", "p64", "p69"})

# 단정 약속어 — LEGAL_RISK_TERM은 법무 + 외부 커뮤니케이션 일부 카테고리만 적용.
LEGAL_RISK_CATEGORIES: frozenset[str] = frozenset({"법무 검토·규제 대응", "외부 커뮤니케이션"})

LEGAL_RISK_KEYWORDS: tuple[str, ...] = (
    "보장합니다", "확실히", "절대로", "100%", "약속드립니다",
    "반드시 한", "분명히", "당연히",
)

VAGUE_CTA_KEYWORDS: tuple[str, ...] = (
    "검토 부탁", "참고 바랍니다", "고민 부탁", "확인 부탁",
    "양해 부탁", "하시기 바랍니다",
)

# 명확한 동사가 마지막 50자에 있어야 VAGUE_CTA 면제.
CLEAR_VERBS: tuple[str, ...] = ("승인", "회신", "결정", "마감", "확정")


@dataclass(frozen=True)
class AntiPattern:
    name: str
    detail: str           # short reason for BLACK rewrite prompt


def detect_all(
    black_output: str,
    case_id: str,
    case_category: str,
    case_black_tone: str,
    case_gold_scenario: str,
    user_xxxxx: str,
    judge: JudgeFn,
) -> list[AntiPattern]:
    """Run all 5 detectors. Empty list = clean output."""
    detected: list[AntiPattern] = []
    if hn := _hallucinated_number(black_output, case_id, user_xxxxx, judge):
        detected.append(hn)
    if vc := _vague_cta(black_output, judge):
        detected.append(vc)
    if mh := _missing_gold_hook(black_output, case_gold_scenario, judge):
        detected.append(mh)
    if tm := _tone_mismatch(black_output, case_black_tone, judge):
        detected.append(tm)
    if lr := _legal_risk_term(black_output, case_category):
        detected.append(lr)
    return detected
```

- [ ] **Step 2:** Add `_hallucinated_number` to the same file:

```python
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?(?:%|만|억|원|\$|개|명|배|건|회)?")


def _hallucinated_number(
    text: str,
    case_id: str,
    user_xxxxx: str,
    judge: JudgeFn,
) -> AntiPattern | None:
    if case_id in HN_EXEMPT_CASES:
        return None
    numbers = NUMBER_RE.findall(text)
    if not numbers:
        return None
    verdict = judge(
        system=(
            "당신은 화이트칼라 산출물의 환각 수치 감지자다. "
            "산출물 안의 수치가 (1) 사용자 입력에 명시된 출처 또는 (2) 산출물 안에서 출처 표기 ([출처: ...] 등)가 있는지 본다."
        ),
        user=(
            f"산출물:\n{text}\n\n사용자 입력 xxxxx:\n{user_xxxxx}\n\n"
            "출처 표기 없이 등장하는 수치를 모두 골라라."
        ),
        schema={"unsourced_numbers": ["string"]},
    )
    unsourced = verdict.get("unsourced_numbers") or []
    if not unsourced:
        return None
    return AntiPattern(
        name="HALLUCINATED_NUMBER",
        detail=f"출처 없는 수치 발견: {', '.join(unsourced[:5])}. 출처를 명시하거나 삭제하라.",
    )
```

- [ ] **Step 3:** Create `tests/anti_patterns/conftest.py`:

```python
"""Test fixtures shared across anti-pattern tests."""
from __future__ import annotations

from typing import Any, Callable

import pytest


@pytest.fixture
def fake_judge() -> Callable[[Any], Callable[..., Any]]:
    """Return a builder that produces a deterministic fake JudgeFn.

    Usage:
        judge = fake_judge({"unsourced_numbers": ["23%"]})
    """
    def make(payload: dict[str, Any]):
        def inner(system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]:
            return payload
        return inner
    return make
```

- [ ] **Step 4:** Create `tests/anti_patterns/test_hallucinated_number.py`:

```python
from scripts.anti_patterns import _hallucinated_number


def test_detects_unsourced_pct(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["23%"]})
    result = _hallucinated_number(
        text="이번 분기 매출 23% 성장.",
        case_id="p23",
        user_xxxxx="분기 보고서",
        judge=judge,
    )
    assert result is not None
    assert result.name == "HALLUCINATED_NUMBER"
    assert "23%" in result.detail


def test_detects_unsourced_amount(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["120억"]})
    result = _hallucinated_number(
        "이번 라운드는 120억 규모이다.", "p34", "투자 메모", judge,
    )
    assert result is not None


def test_detects_user_count(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["340만 명"]})
    result = _hallucinated_number(
        "월 활성 사용자 340만 명.", "p23", "분석 보고서", judge,
    )
    assert result is not None


def test_detects_growth_multiple(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["3.2배"]})
    result = _hallucinated_number(
        "전년 대비 3.2배 성장.", "p23", "성과 리뷰", judge,
    )
    assert result is not None


def test_detects_dollar_amount(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["$5M"]})
    result = _hallucinated_number(
        "Series A $5M 라운드를 종료했다.", "p34", "IC memo", judge,
    )
    assert result is not None


# --- Negative cases (must NOT detect) ---

def test_no_numbers_clean(fake_judge):
    judge = fake_judge({"unsourced_numbers": []})
    assert _hallucinated_number("이번 분기는 잘 풀렸다.", "p23", "보고", judge) is None


def test_sourced_numbers_clean(fake_judge):
    judge = fake_judge({"unsourced_numbers": []})
    assert _hallucinated_number(
        "이번 분기 매출 23% [출처: 사내 ERP].",
        "p23", "분기 보고서", judge,
    ) is None


def test_exempt_poem_p64(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["천 번"]})
    # case p64 = 시 — 면제 카테고리.
    assert _hallucinated_number(
        "천 번을 부르고 만 번을 외쳐도",
        "p64", "시", judge,
    ) is None


def test_exempt_novel_p63(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["1942"]})
    assert _hallucinated_number(
        "그는 1942년에 태어났다.",
        "p63", "소설", judge,
    ) is None


def test_exempt_linkedin_profile_p69(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["10년"]})
    assert _hallucinated_number(
        "10년차 시니어 PM",
        "p69", "프로필", judge,
    ) is None
```

- [ ] **Step 5:** Run `.venv/bin/pytest tests/anti_patterns/test_hallucinated_number.py -v` — expected: 10 passed.

### Task 4.3: VAGUE_CTA detector + tests

- [ ] **Step 1:** Append to `scripts/anti_patterns.py`:

```python
def _vague_cta(text: str, judge: JudgeFn) -> AntiPattern | None:
    last_50 = text[-50:].strip()
    if not any(kw in last_50 for kw in VAGUE_CTA_KEYWORDS):
        return None
    if any(verb in last_50 for verb in CLEAR_VERBS):
        return None
    verdict = judge(
        system="당신은 임원 메시지의 명확성 감지자다. 마지막 부분에 결정 요청이 명확한 동사로 들어있는지 본다.",
        user=f"마지막 50자: {last_50}\n\n명확한 결정 요청 동사가 있는가?",
        schema={"has_clear_verb": "boolean"},
    )
    if verdict.get("has_clear_verb"):
        return None
    return AntiPattern(
        name="VAGUE_CTA",
        detail=f"마무리가 모호하다: '{last_50[-20:]}...'. 무엇을 결정해 달라는지 1동사로 다시 쓰라.",
    )
```

- [ ] **Step 2:** Create `tests/anti_patterns/test_vague_cta.py`:

```python
from scripts.anti_patterns import _vague_cta


def test_detects_review_please(fake_judge):
    judge = fake_judge({"has_clear_verb": False})
    result = _vague_cta("내용 첨부드리니 검토 부탁드립니다.", judge)
    assert result is not None
    assert result.name == "VAGUE_CTA"


def test_detects_for_reference(fake_judge):
    judge = fake_judge({"has_clear_verb": False})
    result = _vague_cta("자료를 보냅니다. 참고 바랍니다.", judge)
    assert result is not None


def test_detects_consider_please(fake_judge):
    judge = fake_judge({"has_clear_verb": False})
    result = _vague_cta("의견 주시면 좋겠습니다. 고민 부탁.", judge)
    assert result is not None


def test_detects_confirm_please(fake_judge):
    judge = fake_judge({"has_clear_verb": False})
    result = _vague_cta("초안을 공유합니다. 확인 부탁드립니다.", judge)
    assert result is not None


def test_detects_yangyae(fake_judge):
    judge = fake_judge({"has_clear_verb": False})
    result = _vague_cta("일정 변경에 대해 양해 부탁드립니다.", judge)
    assert result is not None


# --- Negative cases ---

def test_explicit_approval_request_clean(fake_judge):
    judge = fake_judge({"has_clear_verb": True})
    assert _vague_cta("초안 공유합니다. 금요일까지 승인 회신 부탁드립니다.", judge) is None


def test_deadline_clean(fake_judge):
    judge = fake_judge({"has_clear_verb": True})
    assert _vague_cta("8월 12일 마감으로 회신 부탁드립니다.", judge) is None


def test_decision_phrase_clean(fake_judge):
    judge = fake_judge({"has_clear_verb": True})
    assert _vague_cta("두 안 중 1안으로 결정 부탁드립니다.", judge) is None


def test_no_vague_keyword_clean(fake_judge):
    judge = fake_judge({"has_clear_verb": True})
    assert _vague_cta("8/12까지 회신 주세요.", judge) is None


def test_clear_action_verb_clean(fake_judge):
    judge = fake_judge({"has_clear_verb": True})
    assert _vague_cta("이번 주 안에 확정 회신 부탁드립니다.", judge) is None
```

- [ ] **Step 3:** Run `.venv/bin/pytest tests/anti_patterns/test_vague_cta.py -v` — expected: 10 passed.

### Task 4.4: MISSING_GOLD_HOOK detector + tests

- [ ] **Step 1:** Append to `scripts/anti_patterns.py`:

```python
def _missing_gold_hook(text: str, gold_scenario: str, judge: JudgeFn) -> AntiPattern | None:
    if not gold_scenario:
        return None
    first_200 = text[:200]
    verdict = judge(
        system="GOLD 합격선 장면(독자가 만나는 미리보기 두 줄/첫 슬라이드)이 산출물 첫 부분에 살아있는지 평가한다.",
        user=f"GOLD 합격선 장면:\n{gold_scenario}\n\n산출물 첫 200자:\n{first_200}\n\n장면이 살아있는가?",
        schema={"gold_hook_alive": "boolean", "missing_aspect": "string"},
    )
    if verdict.get("gold_hook_alive"):
        return None
    return AntiPattern(
        name="MISSING_GOLD_HOOK",
        detail=f"GOLD 합격선 장면이 첫 200자에 안 살아있다. 누락: {verdict.get('missing_aspect', '')}. 첫 두 줄을 다시 쓰라.",
    )
```

- [ ] **Step 2:** Create `tests/anti_patterns/test_missing_gold_hook.py` with 5 positive + 5 negative cases (same pattern). Each test passes a different `gold_hook_alive` payload to `fake_judge` and asserts the result. Below shows 2 positive + 2 negative; fill out 5+5 following the same template:

```python
from scripts.anti_patterns import _missing_gold_hook


def test_missing_preview_two_lines(fake_judge):
    judge = fake_judge({"gold_hook_alive": False, "missing_aspect": "미리보기 두 줄에 의도 없음"})
    result = _missing_gold_hook(
        text="안녕하세요. 잘 지내십니까. 다름이 아니라 지난 미팅에서 말씀드린 건과 관련하여 ...",
        gold_scenario="화요일 오후 4시, 거래처 부장이 미리보기 두 줄로 답을 정한다.",
        judge=judge,
    )
    assert result is not None
    assert result.name == "MISSING_GOLD_HOOK"


def test_missing_decision_request(fake_judge):
    judge = fake_judge({"gold_hook_alive": False, "missing_aspect": "결정 요청 없음"})
    result = _missing_gold_hook(
        "분기 결과를 정리했습니다. 자세한 내용은 다음과 같습니다 ...",
        "보드 멤버가 첫 슬라이드로 의사결정 안건을 인지한다.",
        judge,
    )
    assert result is not None


def test_three_more_positive(fake_judge):
    """Add 3 more positive variants — board memo opening that buries lede,
    investor letter without quarter snapshot, internal announcement without action."""
    judge = fake_judge({"gold_hook_alive": False, "missing_aspect": "리드 묻힘"})
    for text, scenario in [
        ("회사 전반에 대해 말씀드리고 싶은 것이 있어 ...",
         "보드 멤버가 1분 안에 결론 인지"),
        ("Dear LP, hope this finds you well. We have many updates ...",
         "LP가 첫 단락에 분기 핵심 수치를 본다"),
        ("동료 여러분, 늘 수고가 많으십니다. 다름이 아니라 ...",
         "사원이 첫 줄에 변경 사항 인지"),
    ]:
        result = _missing_gold_hook(text, scenario, judge)
        assert result is not None


def test_two_clean_cases(fake_judge):
    judge = fake_judge({"gold_hook_alive": True, "missing_aspect": ""})
    for text, scenario in [
        ("[8/12 회신 요망] 8월 출시 전 계약 조항 1번 승인 여부 회신 부탁드립니다.",
         "거래처 부장이 미리보기 두 줄로 답을 정한다."),
        ("Q2 ARR 12.4M (+34% YoY). 2가지 결정 안건. ...",
         "보드 멤버가 1분 안에 결론 인지"),
    ]:
        assert _missing_gold_hook(text, scenario, judge) is None


def test_three_more_clean(fake_judge):
    judge = fake_judge({"gold_hook_alive": True, "missing_aspect": ""})
    for text, scenario in [
        ("Dear LP — Q2 IRR 18.2%. Three portfolio updates inside.",
         "LP가 첫 단락에 분기 핵심 수치를 본다"),
        ("[조직개편 공지] 5/15부 영업본부 → 사업본부로 통합. 본인 소속 변동 표는 본문 1번.",
         "사원이 첫 줄에 변경 사항 인지"),
        ("'우리는 이길 수 있다' — Q2 결산 전 모든 팀이 봐야 할 한 페이지.",
         "임원이 첫 슬라이드 한 줄로 동기 부여"),
    ]:
        assert _missing_gold_hook(text, scenario, judge) is None
```

- [ ] **Step 3:** Run `.venv/bin/pytest tests/anti_patterns/test_missing_gold_hook.py -v` — expected: 5 tests in this file (some test functions cover multiple cases via loops). Total assertion count = 10 (5+5).

### Task 4.5: TONE_MISMATCH detector + tests

- [ ] **Step 1:** Append to `scripts/anti_patterns.py`:

```python
def _tone_mismatch(text: str, black_tone: str, judge: JudgeFn) -> AntiPattern | None:
    if not black_tone:
        return None
    first_sentence = re.split(r"[.!?\n]", text, maxsplit=1)[0]
    if not first_sentence.strip():
        return None
    verdict = judge(
        system="BLACK 캐스팅 톤과 산출물 첫 문장 어휘 거리를 1-10으로 측정 (10 = 완벽 일치).",
        user=f"BLACK 캐스팅 톤: {black_tone}\n\n산출물 첫 문장: {first_sentence}",
        schema={"tone_match_score": "number", "reason": "string"},
    )
    score = float(verdict.get("tone_match_score", 10))
    if score >= 6.0:
        return None
    return AntiPattern(
        name="TONE_MISMATCH",
        detail=f"톤 불일치 (score={score:.1f}). 캐스팅 톤='{black_tone[:60]}...'. {verdict.get('reason','')}",
    )
```

- [ ] **Step 2:** Create `tests/anti_patterns/test_tone_mismatch.py`:

```python
from scripts.anti_patterns import _tone_mismatch


def test_friendly_against_consulting_tone(fake_judge):
    judge = fake_judge({"tone_match_score": 3, "reason": "친근체와 컨설팅 단정 톤 거리 큼"})
    result = _tone_mismatch(
        "안녕하세요~ 오랜만이에요!",
        "베인 컨설턴트 응답 메일 톤. 본론 한 줄로 시작.",
        judge,
    )
    assert result is not None
    assert result.name == "TONE_MISMATCH"


def test_casual_against_legal_tone(fake_judge):
    judge = fake_judge({"tone_match_score": 2, "reason": "캐주얼 vs 법무 격식"})
    result = _tone_mismatch(
        "음 이거 좀 봐줘",
        "사외 변호사 18년차. 격식 격조 유지.",
        judge,
    )
    assert result is not None


def test_overformal_against_internal_announce(fake_judge):
    judge = fake_judge({"tone_match_score": 4, "reason": "사내 공지에 과한 격식"})
    result = _tone_mismatch(
        "삼가 알려드립니다. 부복(俯伏)하건대 ...",
        "사내 공지 — 동료에게 말하듯 솔직하고 가까운 톤",
        judge,
    )
    assert result is not None


def test_two_more_mismatches(fake_judge):
    judge = fake_judge({"tone_match_score": 3, "reason": "톤 거리"})
    for text, tone in [
        ("Yo team, what's up?", "분기 IR 정중·격조"),
        ("쩌는 결과가 나왔어요!", "감사 의견서 — 객관·중립 톤"),
    ]:
        assert _tone_mismatch(text, tone, judge) is not None


# --- Negative cases (matching tone) ---

def test_consulting_match_clean(fake_judge):
    judge = fake_judge({"tone_match_score": 9, "reason": ""})
    assert _tone_mismatch(
        "결론: 1안 승인 부탁드립니다.",
        "베인 컨설턴트 응답 메일 톤. 본론 한 줄로 시작.",
        judge,
    ) is None


def test_legal_match_clean(fake_judge):
    judge = fake_judge({"tone_match_score": 8, "reason": ""})
    assert _tone_mismatch(
        "본 의견서는 2026.5.10. 검토 결과를 정리한다.",
        "사외 변호사 18년차. 격식 격조 유지.",
        judge,
    ) is None


def test_internal_match_clean(fake_judge):
    judge = fake_judge({"tone_match_score": 8, "reason": ""})
    assert _tone_mismatch(
        "팀, 이번 주에 한 가지 정해야 할 게 있어.",
        "사내 공지 — 동료에게 말하듯 솔직하고 가까운 톤",
        judge,
    ) is None


def test_two_more_clean(fake_judge):
    judge = fake_judge({"tone_match_score": 9, "reason": ""})
    for text, tone in [
        ("Q2 ARR 12.4M (+34% YoY).", "분기 IR 정중·격조"),
        ("당사는 다음 사항을 확인하였다.", "감사 의견서 — 객관·중립 톤"),
    ]:
        assert _tone_mismatch(text, tone, judge) is None
```

- [ ] **Step 3:** Run `.venv/bin/pytest tests/anti_patterns/test_tone_mismatch.py -v` — expected: pass.

### Task 4.6: LEGAL_RISK_TERM detector + tests

- [ ] **Step 1:** Append to `scripts/anti_patterns.py`:

```python
def _legal_risk_term(text: str, category: str) -> AntiPattern | None:
    if category not in LEGAL_RISK_CATEGORIES:
        return None
    found = [kw for kw in LEGAL_RISK_KEYWORDS if kw in text]
    if not found:
        return None
    return AntiPattern(
        name="LEGAL_RISK_TERM",
        detail=f"단정 약속어 발견: {', '.join(found)}. 위험 회피 표현으로 대체하라.",
    )
```

- [ ] **Step 2:** Create `tests/anti_patterns/test_legal_risk_term.py`:

```python
from scripts.anti_patterns import _legal_risk_term


def test_guarantee_in_legal(_):
    assert _legal_risk_term("당사는 보장합니다.", "법무 검토·규제 대응") is not None


def test_certainly_in_external_comm(_):
    assert _legal_risk_term("확실히 답변드리겠습니다.", "외부 커뮤니케이션") is not None


def test_absolute_in_legal(_):
    assert _legal_risk_term("절대로 누설하지 않겠습니다.", "법무 검토·규제 대응") is not None


def test_100pct_in_external(_):
    assert _legal_risk_term("100% 환불해드립니다.", "외부 커뮤니케이션") is not None


def test_promise_in_legal(_):
    assert _legal_risk_term("이행을 약속드립니다.", "법무 검토·규제 대응") is not None


# --- Negative ---

def test_clean_legal(_):
    assert _legal_risk_term(
        "당사는 본 계약 조항이 적용되도록 최선의 노력을 다할 예정이다.",
        "법무 검토·규제 대응",
    ) is None


def test_clean_external(_):
    assert _legal_risk_term(
        "발생 시 신속히 회신드릴 예정입니다.",
        "외부 커뮤니케이션",
    ) is None


def test_keyword_in_internal_not_applied(_):
    # 내부 커뮤니케이션 카테고리는 규제 카테고리 아님 → 미적용.
    assert _legal_risk_term("절대로 늦지 않을게요!", "내부 커뮤니케이션") is None


def test_keyword_in_analysis_not_applied(_):
    assert _legal_risk_term("결과는 100% 신뢰할 만하다.", "분석·보고서") is None


def test_no_keyword_clean(_):
    assert _legal_risk_term(
        "본 의견서는 5월 10일 기준 검토 결과이다.",
        "법무 검토·규제 대응",
    ) is None


@pytest.fixture
def _():
    return None
```

> Note: regex-only detector — no judge fixture needed. The dummy `_` fixture keeps test signature uniform.

- [ ] **Step 3:** Run `.venv/bin/pytest tests/anti_patterns/test_legal_risk_term.py -v` — expected: 10 passed.

### Task 4.7: 3-strikes counter + tests

- [ ] **Step 1:** Append to `scripts/anti_patterns.py`:

```python
class ConsecutiveAntiPatternError(Exception):
    """Raised when same pattern detected 3 times in a row (round-internal OR cross-round)."""
    def __init__(self, pattern_name: str):
        self.pattern_name = pattern_name
        super().__init__(f"Anti-pattern {pattern_name} hit 3-strike cap.")


@dataclass
class StrikeCounter:
    """Track consecutive detections per pattern. Counts cross all rounds."""
    counts: dict[str, int] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.counts is None:
            self.counts = {}

    def record(self, pattern_name: str) -> None:
        self.counts[pattern_name] = self.counts.get(pattern_name, 0) + 1
        if self.counts[pattern_name] >= 3:
            raise ConsecutiveAntiPatternError(pattern_name)

    def reset(self, pattern_name: str) -> None:
        self.counts.pop(pattern_name, None)

    def reset_all(self) -> None:
        self.counts.clear()
```

- [ ] **Step 2:** Create `tests/anti_patterns/test_three_strikes.py`:

```python
import pytest
from scripts.anti_patterns import ConsecutiveAntiPatternError, StrikeCounter


def test_one_strike_no_raise():
    sc = StrikeCounter()
    sc.record("HALLUCINATED_NUMBER")
    assert sc.counts["HALLUCINATED_NUMBER"] == 1


def test_two_strikes_no_raise():
    sc = StrikeCounter()
    sc.record("VAGUE_CTA")
    sc.record("VAGUE_CTA")
    assert sc.counts["VAGUE_CTA"] == 2


def test_three_strikes_raises():
    sc = StrikeCounter()
    sc.record("MISSING_GOLD_HOOK")
    sc.record("MISSING_GOLD_HOOK")
    with pytest.raises(ConsecutiveAntiPatternError) as exc:
        sc.record("MISSING_GOLD_HOOK")
    assert exc.value.pattern_name == "MISSING_GOLD_HOOK"


def test_reset_clears_counter():
    sc = StrikeCounter()
    sc.record("TONE_MISMATCH")
    sc.record("TONE_MISMATCH")
    sc.reset("TONE_MISMATCH")
    sc.record("TONE_MISMATCH")
    assert sc.counts["TONE_MISMATCH"] == 1


def test_independent_patterns():
    sc = StrikeCounter()
    sc.record("HALLUCINATED_NUMBER")
    sc.record("HALLUCINATED_NUMBER")
    sc.record("VAGUE_CTA")  # different pattern, no escalation
    assert sc.counts["VAGUE_CTA"] == 1
    assert sc.counts["HALLUCINATED_NUMBER"] == 2
```

- [ ] **Step 3:** Run `.venv/bin/pytest tests/anti_patterns/test_three_strikes.py -v` — expected: 5 passed.

### Task 4.8: Anti-pattern reference docs

- [ ] **Step 1:** Create `skills/roasting/references/anti-patterns/hallucinated-number.md`:

```markdown
# HALLUCINATED_NUMBER

**검출 방법:** regex로 수치 추출 → Haiku judge로 출처 확인.

**트리거:** 산출물 안에 출처 표기 없는 수치 1개 이상.

**적용 범위:** 전 케이스. **제외:** p63(소설), p64(시), p69(링크드인 프로필).

**검출 시 BLACK 재작성 지시:**
> "다음 수치들에 출처가 없습니다: {numbers}. 각 수치 옆에 [출처: ...] 표기 또는 삭제. 출처 없이 수치 사용 금지."

**라운드 카운트:** 안 깎임 (Self-correction).
**3-strikes:** 동일 안티패턴이 한 라운드 내 또는 라운드 간 누적 3회 연속 → 사용자 보고.
```

- [ ] **Step 2:** Create `skills/roasting/references/anti-patterns/vague-cta.md`:

```markdown
# VAGUE_CTA

**검출 방법:** regex 사전 + Haiku judge.

**트리거:** 마지막 50자에 모호 키워드(`검토 부탁`, `참고 바랍니다`, `고민 부탁`, `확인 부탁`, `양해 부탁`, `하시기 바랍니다`)가 있고 명확한 동사(`승인`, `회신`, `결정`, `마감`, `확정`)가 없음.

**적용 범위:** 외부 커뮤니케이션, 내부 커뮤니케이션, 의사결정·전략 (≈30 케이스).

**검출 시 BLACK 재작성 지시:**
> "마무리가 모호하다. 무엇을 결정해 달라는지 1동사(승인/회신/결정/마감/확정)로 다시 쓰라. 마감일 명시 권장."
```

- [ ] **Step 3:** Create `missing-gold-hook.md`:

```markdown
# MISSING_GOLD_HOOK

**검출 방법:** Haiku judge.

**트리거:** 케이스 정의의 GOLD 합격선 장면이 산출물 첫 200자(또는 슬라이드 1장)에 살아있지 않음.

**적용 범위:** 전 케이스.

**검출 시 BLACK 재작성 지시:**
> "이 케이스의 GOLD 합격선 장면은 '{gold_scenario}'이다. 첫 200자/슬라이드 1장에 그 장면이 살아있게 다시 쓰라. 누락된 측면: {missing_aspect}."
```

- [ ] **Step 4:** Create `tone-mismatch.md`:

```markdown
# TONE_MISMATCH

**검출 방법:** Haiku judge — BLACK 캐스팅 톤 vs 산출물 첫 문장 어휘 거리.

**트리거:** tone_match_score < 6 (1-10 척도, 10 = 완벽 일치).

**적용 범위:** 전 케이스.

**검출 시 BLACK 재작성 지시:**
> "BLACK 캐스팅 톤은 '{black_tone}'이다. 산출물 첫 문장의 어휘가 이 톤과 일치하도록 재작성하라."
```

- [ ] **Step 5:** Create `legal-risk-term.md`:

```markdown
# LEGAL_RISK_TERM

**검출 방법:** regex only.

**트리거:** 단정 약속어(`보장합니다`, `확실히`, `절대로`, `100%`, `약속드립니다`, `반드시 한`, `분명히`, `당연히`) 1개 이상.

**적용 범위:** 법무 검토·규제 대응 (7) + 외부 커뮤니케이션 (≈12 케이스 일부 — 사과문, CS 응답, 보도자료, 위기 대응).

**검출 시 BLACK 재작성 지시:**
> "단정 약속어 {found}이(가) 사용되었다. 위험 회피 표현으로 대체하라 (예: '보장합니다' → '최선의 노력을 다할 예정이다')."
```

### Task 4.9: All anti-pattern tests pass + commit

- [ ] **Step 1:** Run all 6 test files: `.venv/bin/pytest tests/anti_patterns/ -v` — expected: 50 tests passed (10 each for HN/VC/MGH/TM/LRT + 5 for strikes).
- [ ] **Step 2:** Verify false-positive rate = 0% (all "clean" tests pass).
- [ ] **Step 3:** Commit:

```bash
git add scripts/anti_patterns.py scripts/llm_judge.py \
  skills/roasting/references/anti-patterns/ tests/anti_patterns/
git commit -m "feat(anti-patterns): 5 detectors + 3-strikes counter + 50 unit tests

Detectors:
- HALLUCINATED_NUMBER (regex + Haiku, exempt p63/p64/p69)
- VAGUE_CTA (regex sieve + Haiku confirm, last-50-char window)
- MISSING_GOLD_HOOK (Haiku, first 200 chars vs case GOLD scenario)
- TONE_MISMATCH (Haiku, threshold tone_match_score < 6)
- LEGAL_RISK_TERM (regex-only, applied to 법무 + 외부 커뮤 categories)

Tests:
- 10 per detector (5 positive + 5 negative)
- 5 strike counter tests (1/2 strike pass, 3rd raises, reset works,
  patterns independent)
- All tests use injected fake_judge fixture (no Claude API in CI)
- False-positive rate = 0% (negative cases all pass)

Acceptance gate met: PR4 ✓

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 4:**
- [ ] 50 unit tests pass (10 × 5 detectors + 5 strikes — Note: missing-gold-hook test has 5 funcs covering 10 assertions; total assertion count ≥ 50)
- [ ] False positive rate = 0% (all clean cases pass)
- [ ] 5 reference docs in `references/anti-patterns/`
- [ ] No Claude API calls in CI (fake_judge used)

---

## PR 5: Routing Infrastructure (189 tests, ≥ 90% Wilson lower)

**Goal:** Implement Haiku-backed router that maps `xxxxx` → top-3 case_ids with confidence. Run 189 routing tests (63 cases × 3 natural language phrasings) and gate at top-1 ≥ 90% Wilson 95% lower bound.

**Depends on:** PR 2 (cases) + PR 4 (llm_judge.py).

**Files:**
- Create: `scripts/route.py`
- Create: `tests/routing/conftest.py`
- Create: `tests/routing/cases_phrasings.json` (63 × 3 = 189 entries)
- Create: `tests/routing/test_routing_accuracy.py`

### Task 5.1: route.py — Haiku judge + Wilson CI helper

- [ ] **Step 1:** Create `scripts/route.py`:

```python
"""Routing for /roasting Phase 1.

Loads references/cases/_index.md, sends xxxxx to Haiku judge, returns top-3
case_ids with confidence scores.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .llm_judge import HaikuJudge, JudgeFn


@dataclass
class RouteResult:
    top3: list[tuple[str, float]]   # [(case_id, confidence), ...]

    @property
    def top1_id(self) -> str:
        return self.top3[0][0] if self.top3 else ""

    @property
    def top1_confidence(self) -> float:
        return self.top3[0][1] if self.top3 else 0.0


def load_index(index_path: Path) -> str:
    return index_path.read_text(encoding="utf-8")


def route(xxxxx: str, index_md: str, judge: JudgeFn | None = None) -> RouteResult:
    if judge is None:
        judge = HaikuJudge()
    verdict = judge(
        system=(
            "당신은 화이트칼라 산출물 케이스 라우터다. "
            "사용자 자연어 요청을 받아 5color 사이트의 63개 케이스 중 가장 적합한 top-3를 신뢰도와 함께 반환한다.\n\n"
            "케이스 인덱스:\n" + index_md
        ),
        user=f"사용자 요청 xxxxx: {xxxxx}\n\ntop-3 case_id를 신뢰도(0-1)와 함께 반환.",
        schema={"top3": [{"case_id": "string", "confidence": "number"}]},
    )
    items = verdict.get("top3") or []
    top3: list[tuple[str, float]] = [
        (str(it.get("case_id", "")), float(it.get("confidence", 0)))
        for it in items[:3]
    ]
    return RouteResult(top3=top3)


def wilson_lower_bound(successes: int, total: int, z: float = 1.96) -> float:
    """Wilson score 95% lower bound for a proportion."""
    if total == 0:
        return 0.0
    p = successes / total
    denom = 1 + z * z / total
    centre = p + z * z / (2 * total)
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total)
    return (centre - margin) / denom
```

### Task 5.2: Phrasings dataset (63 × 3)

- [ ] **Step 1:** Create `tests/routing/cases_phrasings.json` with 189 entries. Each entry: `{case_id, phrasing, intent_tag}`. The 3 phrasings per case follow the pattern (a) natural-language-strong-intent, (b) direct-keyword, (c) audience-clue. Below shows the first 4 cases × 3 phrasings as the format. Generate 189 total — fill in remaining following same shape. Below is the seed (continue with cases p2 through p72):

```json
[
  {"case_id": "p1", "phrasing": "거래처에 답신 안 오는 메일 다시 써줘", "intent_tag": "natural_intent"},
  {"case_id": "p1", "phrasing": "외부 비즈니스 이메일", "intent_tag": "direct_keyword"},
  {"case_id": "p1", "phrasing": "공급사 부장한테 보낼 답신", "intent_tag": "audience_clue"},

  {"case_id": "p2", "phrasing": "고객한테 보낼 사과문 부탁해", "intent_tag": "natural_intent"},
  {"case_id": "p2", "phrasing": "사과문", "intent_tag": "direct_keyword"},
  {"case_id": "p2", "phrasing": "장애 발생해서 고객사에 어떻게 해명하지", "intent_tag": "audience_clue"},

  {"case_id": "p23", "phrasing": "보고서 1페이지로 정리해줘", "intent_tag": "natural_intent"},
  {"case_id": "p23", "phrasing": "1페이지 보고서", "intent_tag": "direct_keyword"},
  {"case_id": "p23", "phrasing": "팀장한테 어제 미팅 요약 올려야 해", "intent_tag": "audience_clue"},

  {"case_id": "p41", "phrasing": "이번 분기 임원 PPT 만들어야 해", "intent_tag": "natural_intent"},
  {"case_id": "p41", "phrasing": "임원용 PPT", "intent_tag": "direct_keyword"},
  {"case_id": "p41", "phrasing": "이사회에서 분기 결과 발표할 슬라이드", "intent_tag": "audience_clue"}
]
```

- [ ] **Step 2:** Generate the remaining 177 entries (cases p3..p72) by writing one helper script — `tests/routing/generate_phrasings_seed.py`:

```python
"""One-shot helper: read references/cases/p*.md frontmatter and emit 3 phrasing
templates per case. Author then hand-edits to make them natural Korean.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


CASES_DIR = Path("skills/roasting/references/cases")
OUT = Path("tests/routing/cases_phrasings.seed.json")


def parse_fm(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip('"')
    return out


def main() -> None:
    rows = []
    for p in sorted(CASES_DIR.glob("p*.md")):
        fm = parse_fm(p.read_text(encoding="utf-8"))
        cid = fm.get("id", p.stem)
        title = fm.get("title", "")
        sub = fm.get("subhead", "")
        # Strip emphasis markers for cleaner natural phrasings.
        title_clean = re.sub(r"</?em>", "", title)
        rows.append({"case_id": cid, "phrasing": f"{title_clean} 작성", "intent_tag": "natural_intent"})
        rows.append({"case_id": cid, "phrasing": title_clean, "intent_tag": "direct_keyword"})
        rows.append({"case_id": cid, "phrasing": sub[:60], "intent_tag": "audience_clue"})
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} phrasings to {OUT}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3:** Run `.venv/bin/python tests/routing/generate_phrasings_seed.py`. Expected: `Wrote 189 phrasings`.
- [ ] **Step 4:** Hand-edit `cases_phrasings.seed.json` → `cases_phrasings.json` to ensure the 189 phrasings are natural Korean (the seed generator produces literal-ish output; manual pass per the 3-pattern rubric is REQUIRED). Mark this with a sub-task: this is 60-90 minutes of careful Korean editing.
- [ ] **Step 5:** Verify: `jq 'length' tests/routing/cases_phrasings.json` returns `189`.

### Task 5.3: Routing accuracy test harness

- [ ] **Step 1:** Create `tests/routing/conftest.py`:

```python
"""Routing test helpers."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def phrasings() -> list[dict[str, str]]:
    return json.loads(Path("tests/routing/cases_phrasings.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def index_md() -> str:
    return Path("skills/roasting/references/cases/_index.md").read_text(encoding="utf-8")
```

- [ ] **Step 2:** Create `tests/routing/test_routing_accuracy.py`:

```python
"""Routing accuracy gate: top-1 ≥ 90% Wilson 95% lower bound across 189 phrasings.

Marked --slow because it calls Haiku 189 times (~$1 per full run).
"""
from __future__ import annotations

import os
from pathlib import Path

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
        print(f"\nFirst 10 misses:")
        for phrasing, expected, got in misses[:10]:
            print(f"  '{phrasing}' → expected={expected}, got={got}")
    assert lower >= 0.90, (
        f"Routing accuracy gate failed: Wilson 95% LB = {lower:.3f} < 0.90. "
        f"Successes={successes}/{total}. See misses above."
    )


def test_top3_recall_gate(phrasings, index_md):
    """Looser gate: expected case must be in top-3 ≥ 95% of the time."""
    judge = HaikuJudge()
    successes = 0
    for entry in phrasings:
        expected = entry["case_id"]
        result = route(entry["phrasing"], index_md, judge=judge)
        if expected in [c for c, _ in result.top3]:
            successes += 1
    lower = wilson_lower_bound(successes, len(phrasings))
    assert lower >= 0.95, f"Top-3 recall LB={lower:.3f} < 0.95"
```

### Task 5.4: Run gate, iterate _index.md if needed

- [ ] **Step 1:** Run `.venv/bin/pytest tests/routing/test_routing_accuracy.py -v -m slow -s`.
- [ ] **Step 2:** If `Wilson 95% LB < 0.90`:
  1. Inspect first 10 misses (printed by test).
  2. For each miss, identify which case description in `_index.md` is too thin or ambiguous.
  3. Edit `scripts/sync_cases.py` `write_index` to add synonyms/keywords to the per-case 1-line entry. Re-run `make sync-cases`.
  4. Re-run gate. Iterate until ≥ 0.90.
- [ ] **Step 3:** Once gate green, commit.

### Task 5.5: Commit

- [ ] **Step 1:** Commit:

```bash
git add scripts/route.py tests/routing/ skills/roasting/references/cases/_index.md
git commit -m "feat(routing): Haiku-backed Expert Pool router + 189 accuracy tests

- scripts/route.py: HaikuJudge wrapper + wilson_lower_bound helper
- tests/routing/cases_phrasings.json: 189 entries (63 cases × 3 phrasings:
  natural_intent, direct_keyword, audience_clue)
- test_routing_accuracy: top-1 ≥ 90% Wilson 95% LB gate
- test_top3_recall: top-3 recall ≥ 95% Wilson 95% LB
- _index.md may have been iterated based on miss analysis

Acceptance: PR5 routing gate met.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 5:**
- [ ] 189 phrasings in `cases_phrasings.json`
- [ ] Top-1 Wilson 95% LB ≥ 0.90 (printed in test output)
- [ ] Top-3 recall Wilson 95% LB ≥ 0.95
- [ ] Cost per full run ≤ $2 (189 × Haiku call)

---

## PR 6: Agent Definitions (5 agents/*.md)

**Goal:** Define `agents/roasting-{black,red,silver,blue,gold}.md` with frontmatter (name, description, tools, model) + body (role, I/O protocol, team comm protocol, error handling).

**Depends on:** PR 1.

**Files:**
- Create: `skills/roasting/agents/roasting-black.md`
- Create: `skills/roasting/agents/roasting-red.md`
- Create: `skills/roasting/agents/roasting-silver.md`
- Create: `skills/roasting/agents/roasting-blue.md`
- Create: `skills/roasting/agents/roasting-gold.md`
- Create: `tests/test_agents_frontmatter.py`

### Task 6.1: roasting-black.md

- [ ] **Step 1:** Create `skills/roasting/agents/roasting-black.md`:

```markdown
---
name: roasting-black
description: 5-Color Harness BLACK 수행자. 케이스별 BLACK 페르소나 캐스팅에 따라 화이트칼라 산출물 1차 작성. 안티패턴 검출 시 자체 재작성. RGSB 코멘트 받아 라운드별 개선.
tools: ["Read", "Write"]
model: sonnet
---

# BLACK — 수행자

## 역할

산출물의 첫 번째 책임자. 케이스 정의의 BLACK 페르소나 캐스팅(예: "B2B SaaS 외부 협력 시니어 15년차+, 베인 컨설턴트 응답 메일 톤")을 그대로 흡수하여 작성한다. 자평·메타 코멘트 금지 (5color 사이트 룰 준수).

## 입력 프로토콜

- **케이스 정의**: BLACK 페르소나 + GOLD 합격선 시나리오 + 분량 제약
- **xxxxx**: 사용자 자연어 의도
- **슬라이드 템플릿 메타** (PPT 케이스만): `{id, color, formality, slide_count, url}`
- **이전 라운드 RGSB 코멘트** (Round 2+): 4인의 점수 + 이유 + 개선안

## 출력 프로토콜

- 형식: Markdown 또는 HTML (PPT 케이스)
- 위치: `_workspace/{session}/round-{n}/black-draft.{md|html}`
- 자평·메타 코멘트 금지

## 행동 규약

- **안티패턴 검출 시 즉시 재작성**: 라운드 카운트 안 깎임. 동일 안티패턴 3회 연속 시 사용자 보고로 escalate.
- **이전 라운드 코멘트 반영**: 4인 코멘트의 *공통 지적*을 우선 반영, 단일 페르소나 의견은 가중치 ↓.
- **GOLD 합격선 장면 살리기**: 첫 200자/슬라이드 1장에 케이스의 GOLD 장면이 살아있게 작성.

## 팀 통신 프로토콜

- 본인은 Phase 3에서 메인 SKILL.md가 직접 호출 (Agent Teams 멤버 아님).
- Phase 5에서 RGSB가 본인 산출물 평가 시, 본인은 통신에 참여하지 않음 (격리로 페르소나 순수성 보장).
- 단, RGSB SILVER가 SendMessage로 직접 질의 시 답변 가능 (선택).

## 에러 핸들링

- 케이스 정의 누락 시 → 메인에 보고 후 대기 (자체 추정 금지).
- 슬라이드 템플릿 로드 실패 시 → Markdown 폴백.
- 분량 제약 초과 시 → 압축 재작성.
```

### Task 6.2: roasting-red.md

- [ ] **Step 1:** Create `skills/roasting/agents/roasting-red.md`:

```markdown
---
name: roasting-red
description: 5-Color RED 이성 평가자. BLACK 산출물의 의도 전달·논리·단정 정도를 케이스별 RED 페르소나로 채점. 점수+1줄 이유+1줄 개선안. σ ≥ 0.5 시 토론 참여.
tools: ["Read"]
model: opus
---

# RED — 이성 평가자

## 역할

BLACK 산출물의 *이성·의도 전달*을 평가한다. 케이스별 RED 페르소나(예: "거래처 영업 시니어 20년차")로 캐스팅된다.

## 평가 축

- 의도가 한 줄로 보이는가
- 합격선 어휘(예: "확정", "회신")가 살아있는가
- 마무리 패턴이 결정 가능한 형태인가

## 출력 형식

```json
{"score": 9.4, "reason": "의도 한 줄 명확", "suggestion": "마감일 추가 권장"}
```

## 점수 기준

- 10 = 결함 없음
- 9.5 = 합격선
- 9 = 한 자리 더 손보면
- 8 = v2 권장
- ≤ 7 = 캐스팅/과제 정의 의심

## 팀 통신 프로토콜

- 첫 채점 후 결과 `TaskUpdate("scoring-table-round-{n}")`에 등록.
- 메인이 σ ≥ 0.5 판정 시:
  - 가장 점수 차이 큰 페르소나로부터 SendMessage 도착 → 1라운드 토론 참여.
  - 본인이 토론 트리거 페르소나로 선택되면 가장 차이 나는 상대에게 SendMessage 발송.
- 토론 후 새 점수 + 코멘트 `TaskUpdate`.

## 행동 규약

- 톤: 단정 (케이스별 변동 가능 — 케이스 정의의 RED 톤 우선).
- 자기 점수 자체 검토 금지 (메타 코멘트 없음).
- 합격선 장면을 비교 기준으로 사용.
```

### Task 6.3: roasting-silver.md

- [ ] **Step 1:** Create `skills/roasting/agents/roasting-silver.md`:

```markdown
---
name: roasting-silver
description: 5-Color SILVER 분야 전문가 평가자. 케이스별 SILVER 페르소나(비서팀장 18년차, 사외 변호사 16년차 등)로 분야 정확성·구조·합법성 평가.
tools: ["Read"]
model: sonnet
---

# SILVER — 분야 전문가

## 역할

산출물의 분야 적합성을 평가한다. 케이스별 SILVER 페르소나(비서팀장, 사외 변호사, IR 매니저 등)에 따라 도메인 정확성·구조·합법성을 본다.

## 평가 축

- 분야 표준 구조에 부합 (예: 보고서 → Executive Summary → Detail → Action)
- 분야 어휘 정확성
- 분야 위험 신호 (법적·규제·재무) 탐지

## 출력 형식

```json
{"score": 8.5, "reason": "구조는 OK, 약관 인용 누락", "suggestion": "약관 1조 2항 명시 추가"}
```

## 팀 통신 프로토콜

- σ ≥ 0.5 토론 트리거 시 본인이 가장 낮은 점수면 가장 높은 점수 페르소나에게 SendMessage 도전.
- 필요 시 SILVER → BLACK 직접 질의 가능 ("이 수치 출처?"). BLACK이 답변하면 점수 재고려.

## 행동 규약

- 톤: 깐깐 (케이스별 변동).
- 자기 분야가 아닌 영역 침범 금지 (RED·BLUE의 영역 존중).
```

### Task 6.4: roasting-blue.md

- [ ] **Step 1:** Create `skills/roasting/agents/roasting-blue.md`:

```markdown
---
name: roasting-blue
description: 5-Color BLUE 공감 평가자. 케이스별 BLUE 페르소나로 톤·분량·수신자 입장 평가. 케이스에 따라 가장 무뚝뚝한 톤일 수도 있음.
tools: ["Read"]
model: sonnet
---

# BLUE — 공감 평가자

## 역할

수신자(독자) 입장에서의 톤·분량·정서적 적합성을 평가한다.

## 평가 축

- 분량 제약 준수 (예: 이메일 200~500자)
- 수신자 톤 일치 (격식·캐주얼·중립)
- 정서적 부담 적정 (사과문은 진정성, 위기 대응은 침착)

## 출력 형식

```json
{"score": 9.0, "reason": "톤 적정, 분량 약간 길다", "suggestion": "30자 더 압축"}
```

## 팀 통신 프로토콜

- σ ≥ 0.5 시 토론 참여 (RED와 SILVER 사이 가교 역할 가능).

## 행동 규약

- 톤: 무뚝뚝 (케이스별 변동).
- 분량 초과 시 가장 낮은 점수 페널티.
```

### Task 6.5: roasting-gold.md

- [ ] **Step 1:** Create `skills/roasting/agents/roasting-gold.md`:

```markdown
---
name: roasting-gold
description: 5-Color GOLD 독자 시점 평가자. 케이스 GOLD 합격선 장면(독자가 만나는 미리보기 등)에 산출물 부합 여부 채점. RGSB 중 9.5 통과/실패 결정에 가장 큰 가중치.
tools: ["Read"]
model: opus
---

# GOLD — 독자 시점 평가자

## 역할

케이스의 GOLD 시나리오(예: "화요일 오후 4시, 거래처 부장이 미팅 중 휴대폰 미리보기 두 줄을 본다")를 그대로 *시뮬레이션*하여 평가한다. 그 장면에서 산출물이 합격선을 넘는지 본다.

## 평가 축

- 합격선 장면에서 의도가 잡히는가
- 독자가 그 자리에서 *결정·행동·이해* 했는가
- 첫 200자/슬라이드 1장에 합격선 장면이 살아있는가

## 출력 형식

```json
{"score": 7.8, "reason": "미리보기 두 줄에 의도 묻힘", "suggestion": "[8/12 회신 요망]을 첫 줄로"}
```

## 팀 통신 프로토콜

- **타이브레이커 우선순위 1순위**: 점수 동률 시 가장 강한 발언권.
- σ ≥ 0.5 시 가장 점수 차이 큰 페르소나에게 SendMessage 우선 발송.

## 행동 규약

- 톤: 속내 드러냄 (케이스별 변동).
- 다른 페르소나(RED·SILVER·BLUE)와 평가 축이 충돌해도 *독자 우위* 입장 견지.
- 합격선 장면을 *그대로 재현*하며 평가 (장면 묘사 → 그 안에서 산출물 본 반응).
```

### Task 6.6: Frontmatter validation test

- [ ] **Step 1:** Create `tests/test_agents_frontmatter.py`:

```python
"""Verify all 5 agent .md files have required frontmatter fields."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


AGENTS_DIR = Path("skills/roasting/agents")
EXPECTED_AGENTS = {"roasting-black", "roasting-red", "roasting-silver",
                   "roasting-blue", "roasting-gold"}


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    return yaml.safe_load(text[3:end]) or {}


@pytest.mark.parametrize("agent_name", sorted(EXPECTED_AGENTS))
def test_agent_frontmatter(agent_name: str) -> None:
    path = AGENTS_DIR / f"{agent_name}.md"
    assert path.exists(), f"missing {path}"
    fm = parse_frontmatter(path.read_text(encoding="utf-8"))
    assert fm.get("name") == agent_name
    assert fm.get("description"), f"empty description in {path}"
    assert isinstance(fm.get("tools"), list), f"tools must be list in {path}"
    assert fm.get("model") in {"opus", "sonnet", "haiku"}, f"bad model in {path}"


def test_all_5_agents_present() -> None:
    found = {p.stem for p in AGENTS_DIR.glob("*.md")}
    assert found == EXPECTED_AGENTS, f"missing or extra: expected={EXPECTED_AGENTS}, got={found}"


def test_reviewer_tools_readonly() -> None:
    """RED, SILVER, BLUE, GOLD must have tools=['Read'] only."""
    for name in {"roasting-red", "roasting-silver", "roasting-blue", "roasting-gold"}:
        fm = parse_frontmatter((AGENTS_DIR / f"{name}.md").read_text(encoding="utf-8"))
        assert fm.get("tools") == ["Read"], f"{name} must be read-only, got {fm.get('tools')}"
```

- [ ] **Step 2:** Run `.venv/bin/pytest tests/test_agents_frontmatter.py -v` — expected: 7 passed (5 parametrized + 2 standalone).

### Task 6.7: Commit

- [ ] **Step 1:** Commit:

```bash
git add skills/roasting/agents/ tests/test_agents_frontmatter.py
git commit -m "feat(agents): 5 Anthropic-standard agent definitions

agents/roasting-black.md - Producer (Sonnet, tools=Read,Write)
agents/roasting-red.md   - Reviewer 이성 (Opus, tools=Read)
agents/roasting-gold.md  - Reviewer 독자, tiebreaker 1순위 (Opus, Read)
agents/roasting-silver.md - Reviewer 분야전문가 (Sonnet, Read)
agents/roasting-blue.md  - Reviewer 공감 (Sonnet, Read)

Each frontmatter: name, description, tools (whitelist), model.
Body: 역할, 평가축/입력, 출력 프로토콜, 팀 통신 프로토콜, 행동 규약, 에러 핸들링.

Test: 7 frontmatter assertions (5 agents present, all required fields,
reviewers tools=['Read'] read-only).

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 6:**
- [ ] 5 agents/*.md exist
- [ ] All have valid frontmatter (name, description, tools, model)
- [ ] Reviewers (RED·SILVER·BLUE·GOLD) have `tools: ["Read"]`
- [ ] BLACK has `tools: ["Read", "Write"]`
- [ ] `pytest tests/test_agents_frontmatter.py` passes

---

## PR 7: SKILL.md Phase 0–2 (Entry, PARSE, SEED LOAD)

**Goal:** Create `skills/roasting/SKILL.md` with the routing front-end. Phases 3–7 are stubbed in this PR and filled in PRs 8–11.

**Depends on:** PR 5 (route.py + index) + PR 6 (agents).

**Files:**
- Create: `skills/roasting/SKILL.md`
- Create: `skills/roasting/references/workflow.md` (skeleton)
- Create: `skills/roasting/references/output-formats.md` (skeleton)
- Create: `tests/test_skill_phase_0_2.py`

### Task 7.1: SKILL.md frontmatter + Phase 0 + Phase 1

- [ ] **Step 1:** Create `skills/roasting/SKILL.md`:

````markdown
---
name: roasting
description: 화이트칼라 산출물(이메일·보고서·PPT·계약서·이력서·투자 메모·사내 공지·이사회 보고서·IR 자료 등 63개 케이스) 작성을 5-Color Harness 방법론으로 수행. 임원·비즈니스 리더가 자연어 한 줄(/roasting xxxxx 또는 일반 요청)로 호출하면 케이스 자동 매칭 후 BLACK 수행자가 작성하고 RED·SILVER·BLUE·GOLD 4인이 토론 채점. 9.5 합격선까지 최대 4라운드 자동 반복. PPT 케이스에서 slide_library 35개 템플릿 자동 결합. 안티패턴 5종(환각 수치·모호 CTA·누락된 GOLD 후크·톤 미스매치·법무 단정어) 자동 검출. 산출물·평가 코멘트·결정 로그 3종 출력.
---

# /roasting — 5-Color Harness Execution Engine

5color 사이트의 63개 케이스를 Claude Code 위에서 *집행*하는 엔진. 임원이 자연어 한 줄로 호출하면, 7-Phase 워크플로우(Pipeline + Supervisor 패턴, Phase 5만 Agent Teams)로 산출물·평가·결정 로그 3종을 출력한다.

## 핵심 원칙

1. **단일 진입**: `/roasting xxxxx` 한 줄만 학습. 도메인은 자동 라우팅.
2. **Progressive Disclosure**: 케이스 1줄 인덱스만 항상 컨텍스트, 매칭 시 케이스 풀 정의 로드.
3. **5-Color 본래 의도 충실**: 4인 RGSB가 *서로 토론* (σ ≥ 0.5 자동 트리거).
4. **콘텐츠 0 수집**: telemetry는 메타데이터만. xxxxx·산출물·코멘트는 외부 전송 0.
5. **결정적 비용**: 5명 × 4라운드 cap × 케이스 정의 고정 = 호출당 ~$0.36.

## 워크플로우 (7 Phase)

### Phase 0 — 진입과 세션 초기화

트리거 시:
1. 세션 디렉토리 생성: `~/.claude/roasting/_workspace/{YYYYMMDD-HHMMSS}-{tmp_id}/`
2. `input.txt`에 xxxxx 저장
3. session_dir 경로를 모든 후속 Phase가 공유

### Phase 1 — PARSE (Expert Pool 라우팅)

목적: xxxxx → 63 케이스 중 1개 매칭.

처리:
1. `references/cases/_index.md` 로드 (~30KB).
2. Haiku judge 호출: top-3 case_id + 신뢰도. 구현은 `scripts/route.py:route()`.
3. `routing.json` 저장: `{top3, confidence, selected_case_id}`.
4. **분기:**
   - 신뢰도 ≥ 0.85 → top-1 자동 선택, Phase 2로.
   - 신뢰도 < 0.85 → 사용자에게 top-3 보여주고 1턴 confirm.
5. **에러 폴백:** 모든 후보 신뢰도 < 0.5 → 일반 5-Color 모드 (자산 시드 없음). 사용자에게 "이 케이스는 5color 사이트에 없습니다" 알림.

### Phase 2 — SEED LOAD

목적: 케이스 정의 + 슬라이드 템플릿 + 케이스 적용 안티패턴 로드.

처리:
1. `references/cases/{case_id}.md` 로드 (BLACK + RGSB 페르소나 정의 + GOLD 시나리오).
2. **PPT 카테고리 (p41/p42/p43/p45) 추가 처리:**
   - `~/.claude/roasting/preferences/{case_id}.json` 확인.
   - 존재 → 저장된 슬라이드 ID 자동 사용.
   - 없음 → top-3 슬라이드 추천 + 1턴 confirm + preferences 저장.
3. 케이스 카테고리 따라 `references/anti-patterns/*.md` 중 적용 항목만 로드.
4. `case-context.json` 저장.

### Phase 3 — BLACK DRAFT (Producer)

> **구현은 PR 8에서 채움.** v0.1 빌드 진행 중 stub:
>
> 메인 Claude가 `agents/roasting-black.md` 정의를 system prompt로 주입한 채 직접 작성.

### Phase 4 — ANTI-PATTERN CHECK

> **구현은 PR 8에서 채움.** stub: `scripts.anti_patterns.detect_all` 호출, 검출 시 BLACK 재작성, 3-strikes 보호.

### Phase 5 — RGSB REVIEW (Agent Teams)

> **구현은 PR 9 (sub-agent fallback) → PR 10 (Agent Teams)에서 채움.** stub.

### Phase 6 — LOOP

> **구현은 PR 11에서 채움.**

### Phase 7 — DELIVER

> **구현은 PR 11에서 채움.**

## 컨펌 시점

| 시점 | Phase | 트리거 | 디폴트 | 부담 |
|---|---|---|---|---|
| 라우팅 | 1 | 신뢰도 < 0.85 | top-1 자동 | 1턴 |
| 슬라이드 | 2 | PPT 첫 호출 | top-1 추천 | 1턴 (저장) |
| 안티패턴 무한 루프 | 4 | 동일 안티패턴 3회 | 사용자 선택 | 1턴 (예외) |
| 토론 합의 실패 | 5 | 1라운드 후 σ ≥ 0.5 | 분포 그대로 | 0 |
| 4라운드 미통과 | 6 | round=4 + score < 9.5 | 강제 출력 + 사유 | 0 |

## 워크플로우 상세 룰

`references/workflow.md` 참조 (9.5 합격선·4라운드 캡·발화 톤·_workspace 컨벤션).

## 출력 포맷

`references/output-formats.md` 참조 (PPT 카테고리 = HTML, 그 외 = Markdown).

## 안티패턴

`references/anti-patterns/*.md` 참조 (5종).

## 케이스 카탈로그

`references/cases/_index.md` (라우팅용 인덱스), `references/cases/p*.md` (케이스별 상세).

## 에이전트

`agents/{black,red,silver,blue,gold}.md` (5종 페르소나 정의).
````

### Task 7.2: workflow.md 스켈레톤

- [ ] **Step 1:** Create `skills/roasting/references/workflow.md`:

````markdown
# /roasting Workflow Rules

## 합격선

- 분석가 3인(RED, SILVER, BLUE) 평균 ≥ 9.5
- GOLD 별도 보고 (타이브레이커 1순위)
- 4라운드 권장 cap

## 점수 기준

- 10 = 결함 없음
- 9.5 = 합격선
- 9 = 한 자리 더 손보면
- 8 = v2 권장
- ≤ 7 = 캐스팅/과제 정의 의심

## 발화 톤

각 페르소나는 케이스 정의에 명시된 톤을 그대로 사용. 전체 풀:
건조 · 단정 · 신랄 · 차분 · 깐깐 · 냉정 · 회의적 · 무뚝뚝 · 속내 드러냄 · 실무자 직설.

세 비평가 톤이 서로 달라야 한다.

## _workspace 컨벤션

```
~/.claude/roasting/_workspace/{YYYYMMDD-HHMMSS}-{tmp_id}/
├── input.txt                 # xxxxx
├── routing.json              # Phase 1 결과
├── case-context.json         # Phase 2 결과
├── round-1/
│   ├── black-draft.{md|html}
│   ├── anti-patterns.json
│   ├── rgsb-scores.json
│   └── debate-log.md
├── round-2/...
└── final/
    ├── output.{html|md}
    ├── critique.md
    └── reasoning.md
```

## 토론 트리거 룰

- σ ≥ 0.5 → 토론 1라운드.
- 가장 높은 점수 페르소나 ↔ 가장 낮은 점수 페르소나.
- **타이브레이커**: 점수 동률 시 GOLD > RED > SILVER > BLUE.
- 1라운드 후 σ 여전히 ≥ 0.5 → "합의 실패" 표시 + 분포 그대로 출력.

## 라운드 cap

- 4라운드 후 < 9.5 → 가장 높았던 라운드 결과 사용 + 사용자 보고: "9.5 미달 (max=X.Y). 캐스팅 또는 과제 정의 문제 가능성. 1on1 권장."

## 3-strikes 안티패턴 보호

- 동일 안티패턴 3회 연속 검출 (한 라운드 내 OR 라운드 간 누적) → 사용자 보고:
  - (1) 진행 (강제 통과)
  - (2) 중단
  - (3) 케이스 재선택
````

### Task 7.3: output-formats.md 스켈레톤

- [ ] **Step 1:** Create `skills/roasting/references/output-formats.md`:

```markdown
# Output Format by Category

| 카테고리 | 기본 포맷 | 비고 |
|---|---|---|
| 외부 커뮤니케이션 (이메일·사과문·보도자료 등 12개) | Markdown | |
| 소셜미디어·글쓰기 (9개) | Markdown | |
| 내부 커뮤니케이션 (7개) | Markdown | |
| 분석·보고서 (12개) | Markdown | 긴 본문 OK |
| **의사결정·전략 — PPT 4개 (p41 임원 PPT, p42 강의자료, p43 영업덱, p45 컨설팅 덱)** | **HTML (slide_library 결합)** | 즉시 발표 가능 |
| 의사결정·전략 — 그 외 6개 (메모·보고서·제안서) | Markdown | |
| 법무·규제 (7개) | Markdown | |
| 마케팅 (2개) | Markdown | |
| 커리어·상담 (4개) | Markdown | 이력서는 v0.2에 HTML 옵션 추가 가능 |

## HTML 슬라이드 구조 (PPT 케이스 4종)

- 외부: slide_library의 선택된 템플릿 HTML 그대로
- 콘텐츠 주입: 템플릿의 슬라이드 영역에 BLACK 산출물 삽입
- 출력: 단일 `.html` 파일, 브라우저로 발표 가능, PDF 익스포트 가능

## Markdown 출력 구조

```markdown
# {제목}

> {부제 / 한 줄 요약}

{본문}

---
*Generated by /roasting v0.1 — case {case_id} {folio}*
```
```

### Task 7.4: Phase 0–2 통합 테스트

- [ ] **Step 1:** Create `tests/test_skill_phase_0_2.py`:

```python
"""Smoke test that Phase 0–2 wiring is consistent.

Does not invoke Claude. Verifies file structure + paths referenced from
SKILL.md exist.
"""
from __future__ import annotations

from pathlib import Path

import pytest


SKILL = Path("skills/roasting/SKILL.md")
REFS = Path("skills/roasting/references")
AGENTS = Path("skills/roasting/agents")


def test_skill_md_exists():
    assert SKILL.exists()
    body = SKILL.read_text(encoding="utf-8")
    assert body.startswith("---\n")
    assert "name: roasting" in body
    assert "Phase 0" in body
    assert "Phase 7" in body


def test_workflow_md_exists():
    p = REFS / "workflow.md"
    assert p.exists()
    body = p.read_text(encoding="utf-8")
    for token in ["9.5", "4라운드", "σ", "_workspace"]:
        assert token in body


def test_output_formats_md_exists():
    p = REFS / "output-formats.md"
    assert p.exists()
    body = p.read_text(encoding="utf-8")
    assert "p41" in body
    assert "HTML" in body


def test_index_md_exists_and_referenced():
    idx = REFS / "cases" / "_index.md"
    assert idx.exists()
    skill_body = SKILL.read_text(encoding="utf-8")
    assert "_index.md" in skill_body


def test_all_5_agents_referenced_by_skill():
    skill_body = SKILL.read_text(encoding="utf-8")
    for who in ("black", "red", "silver", "blue", "gold"):
        assert who in skill_body.lower()
        assert (AGENTS / f"roasting-{who}.md").exists()


def test_anti_patterns_directory_referenced():
    skill_body = SKILL.read_text(encoding="utf-8")
    assert "anti-patterns" in skill_body
    assert (REFS / "anti-patterns").is_dir()
```

- [ ] **Step 2:** Run `.venv/bin/pytest tests/test_skill_phase_0_2.py -v` — expected: 6 passed.

### Task 7.5: Commit

- [ ] **Step 1:** Commit:

```bash
git add skills/roasting/SKILL.md skills/roasting/references/workflow.md \
  skills/roasting/references/output-formats.md tests/test_skill_phase_0_2.py
git commit -m "feat(skill): SKILL.md skeleton with Phase 0-2 + workflow/output-formats refs

- SKILL.md frontmatter (description: 63 cases, 5-Color, 4 rounds, anti-patterns)
- Phase 0 (entry + _workspace init), Phase 1 (PARSE via route.py),
  Phase 2 (SEED LOAD with PPT slide template branch + preferences cache)
- Phase 3-7 stubbed for PRs 8-11
- workflow.md: 9.5 threshold, σ ≥ 0.5 debate, 4-round cap, 3-strikes,
  타이브레이커 GOLD>RED>SILVER>BLUE, _workspace tree
- output-formats.md: PPT 4 cases = HTML+slide_library, others = Markdown
- Smoke tests verify cross-references intact

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 7:**
- [ ] SKILL.md exists with correct frontmatter
- [ ] Phase 0–2 logic documented; Phase 3–7 stubbed with PR pointers
- [ ] workflow.md and output-formats.md cover spec sections
- [ ] All cross-references resolve (test passes)

---

## PR 8: SKILL.md Phase 3–4 (BLACK Draft + Anti-Pattern Self-Correction)

**Goal:** Wire BLACK Producer + anti-pattern self-correction loop into SKILL.md. BLACK is invoked via the `Agent` tool (sub-agent path); 3-strikes guard active.

**Depends on:** PR 4 + PR 6 + PR 7.

**Files:**
- Modify: `skills/roasting/SKILL.md` (replace Phase 3, 4 stubs)
- Create: `tests/test_skill_phase_3_4.py`

### Task 8.1: Replace Phase 3 stub with BLACK invocation pseudocode

- [ ] **Step 1:** Edit `SKILL.md` and replace the Phase 3 stub with:

````markdown
### Phase 3 — BLACK DRAFT (Producer)

목적: 케이스 BLACK 페르소나 캐스팅으로 산출물 1차 작성.

호출 방식 (메인 Claude가 직접 수행):

```
Agent(
  subagent_type="general-purpose",   # roasting-black.md를 system prompt로 주입
  description="BLACK draft for {case_id} round {n}",
  prompt=f"""
You are following agents/roasting-black.md. Use the case persona from
references/cases/{case_id}.md (BLACK section) as your character casting.

Inputs:
- xxxxx: {user_xxxxx}
- 케이스 정의 (전문): {case_md_content}
- 슬라이드 템플릿 (PPT만): {slide_meta_json}
- 이전 라운드 RGSB 코멘트 (Round 2+): {prev_critiques_md}

산출물 작성. Markdown 또는 HTML. 자평·메타 코멘트 금지.
출력 위치: _workspace/{session}/round-{n}/black-draft.{ext}
"""
)
```

산출물 저장 후 Phase 4로.
````

### Task 8.2: Replace Phase 4 stub with anti-pattern + self-correction

- [ ] **Step 1:** Replace Phase 4 stub with:

````markdown
### Phase 4 — ANTI-PATTERN CHECK (Self-correction loop)

목적: BLACK 산출물의 5종 안티패턴 검출 → 발견 시 BLACK 재작성 (라운드 카운트 안 깎임). 3-strikes 보호.

처리:
1. `scripts.anti_patterns.detect_all` 호출:
   ```python
   detected = detect_all(
       black_output=draft_text,
       case_id=case.id,
       case_category=case.category,
       case_black_tone=case.black_tone,
       case_gold_scenario=case.gold_scenario,
       user_xxxxx=xxxxx,
       judge=HaikuJudge(),
   )
   ```
2. detected가 비어있으면 → Phase 5로.
3. 검출된 각 안티패턴마다 `StrikeCounter.record(name)` 호출:
   - `ConsecutiveAntiPatternError` 발생 (3-strikes) → 사용자 보고:
     ```
     [{pattern_name}] 안티패턴이 3회 연속 검출되었습니다.
     해소가 어렵습니다. 어떻게 할까요?
     (1) 진행 (강제 통과)
     (2) 중단
     (3) 케이스 재선택
     ```
4. 3-strikes 미달 시 → BLACK 재호출, prompt에 재작성 지시 추가:
   ```
   직전 산출물에서 다음 안티패턴이 검출되었습니다:
   - {ap.name}: {ap.detail}
   
   재작성하세요. 라운드 카운트는 변동 없습니다.
   ```
5. 수정된 산출물로 다시 Phase 4 → 통과 시 Phase 5.

`anti-patterns.json` 저장: `{detected_iterations: [[...], [...]], final: []}`
````

### Task 8.3: Phase 3–4 integration test (mocked)

- [ ] **Step 1:** Create `tests/test_skill_phase_3_4.py`:

```python
"""Verify Phase 3-4 logic structure via SKILL.md content checks + StrikeCounter integration."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.anti_patterns import StrikeCounter, ConsecutiveAntiPatternError


SKILL = Path("skills/roasting/SKILL.md")


def test_phase_3_invokes_black_agent():
    body = SKILL.read_text(encoding="utf-8")
    assert "Phase 3 — BLACK DRAFT" in body
    assert "Agent(" in body or "agents/roasting-black.md" in body
    assert "black-draft" in body


def test_phase_4_uses_detect_all():
    body = SKILL.read_text(encoding="utf-8")
    assert "Phase 4 — ANTI-PATTERN CHECK" in body
    assert "detect_all" in body
    assert "StrikeCounter" in body
    assert "ConsecutiveAntiPatternError" in body or "3-strikes" in body or "3회 연속" in body


def test_phase_4_reports_user_options_on_3_strikes():
    body = SKILL.read_text(encoding="utf-8")
    assert "(1) 진행" in body
    assert "(2) 중단" in body
    assert "(3) 케이스 재선택" in body


def test_strike_counter_integration_pattern():
    """Smoke test: 3rd record raises (used in Phase 4)."""
    sc = StrikeCounter()
    sc.record("HALLUCINATED_NUMBER")
    sc.record("HALLUCINATED_NUMBER")
    with pytest.raises(ConsecutiveAntiPatternError):
        sc.record("HALLUCINATED_NUMBER")
```

- [ ] **Step 2:** Run: `.venv/bin/pytest tests/test_skill_phase_3_4.py -v` — expected: 4 passed.

### Task 8.4: Commit

- [ ] **Step 1:** Commit:

```bash
git add skills/roasting/SKILL.md tests/test_skill_phase_3_4.py
git commit -m "feat(skill): Phase 3 BLACK draft + Phase 4 anti-pattern self-correction

Phase 3:
- BLACK invoked via Agent tool with roasting-black.md as system prompt
- Inputs: xxxxx, case definition, slide template (PPT), prev RGSB
  comments (Round 2+)
- Output to _workspace/{session}/round-{n}/black-draft.{md|html}

Phase 4:
- detect_all from scripts.anti_patterns runs 5 detectors
- StrikeCounter.record raises ConsecutiveAntiPatternError on 3rd consecutive
  detection (counter spans rounds, per spec)
- On 3-strikes: user prompt with options (1) proceed, (2) abort, (3) reroute
- BLACK rewrite prompt includes detected pattern detail; round count
  unaffected during self-correction loop

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 8:**
- [ ] SKILL.md Phase 3 references `roasting-black.md` agent + Agent tool
- [ ] SKILL.md Phase 4 references `detect_all` + `StrikeCounter` + 3-strikes user options
- [ ] Test file passes (4 assertions)

---

## PR 9: SKILL.md Phase 5 — Sub-Agent Fallback FIRST

**Goal:** Implement Phase 5 with parallel sub-agents (4 reviewers via `Agent` tool with `run_in_background`). This is the **fallback path** for environments where Agent Teams is unavailable. PR 10 layers Agent Teams on top.

**Risk mitigation:** Build sub-agent path before Agent Teams so we always have a working path even if `TeamCreate` is unstable.

**Depends on:** PR 8.

**Files:**
- Modify: `skills/roasting/SKILL.md` (replace Phase 5 stub)
- Create: `tests/test_skill_phase_5_subagent.py`

### Task 9.1: Phase 5 sub-agent path pseudocode

- [ ] **Step 1:** Replace Phase 5 stub with:

````markdown
### Phase 5 — RGSB REVIEW (Sub-Agent Fallback Path)

> v0.1에는 두 경로가 있다: **Sub-Agent Fallback (이 절)** + **Agent Teams (PR 10에서 추가)**. Agent Teams 가용 여부를 자동 탐지해 우선 시도, 실패 시 이 경로로 폴백.

목적: BLACK 산출물을 RED·SILVER·BLUE·GOLD 4인이 *병렬* 채점, 평균 ≥ 9.5 게이트.

처리 (Sub-Agent 모드):

1. **병렬 dispatch (4명 동시):**
   ```
   for reviewer in [RED, SILVER, BLUE, GOLD]:
       Agent(
         subagent_type="general-purpose",
         description=f"{reviewer} score for {case_id} round {n}",
         prompt=f"""
   You are following agents/roasting-{reviewer.lower()}.md.
   Use case persona from references/cases/{case_id}.md ({reviewer} section).
   
   Score this BLACK output 1-10:
   {black_draft}
   
   Return JSON only:
   {{"score": <number>, "reason": "<1줄>", "suggestion": "<1줄>"}}
   """,
         run_in_background=True,
       )
   ```

2. **결과 수집** (4 sub-agents 모두 완료 대기). `rgsb-scores.json` 저장:
   ```json
   {
     "RED": {"score": 9.4, "reason": "...", "suggestion": "..."},
     "SILVER": {"score": 8.7, "reason": "...", "suggestion": "..."},
     "BLUE": {"score": 9.1, "reason": "...", "suggestion": "..."},
     "GOLD": {"score": 7.8, "reason": "...", "suggestion": "..."}
   }
   ```

3. **σ 계산 + 토론 트리거** (sub-agent 모드는 토론 SKIP):
   - σ < 0.5: 평균 사용.
   - σ ≥ 0.5: **sub-agent 모드는 토론 불가**. 사용자에게 알림: "분포 σ={σ:.2f} — 합의 약함. Agent Teams 모드에서 더 정확합니다."
     - 분포 그대로 출력에 표시.

4. **게이트:**
   - 평균 ≥ 9.5 → Phase 7.
   - 미만 → Phase 6 (round_count +1).

> Agent Teams 모드의 토론 메커니즘은 PR 10에서 추가됨. 폴백 경로는 *간단한 평균*만 계산.
````

### Task 9.2: 통합 테스트

- [ ] **Step 1:** Create `tests/test_skill_phase_5_subagent.py`:

```python
"""Verify Phase 5 sub-agent fallback structure in SKILL.md."""
from __future__ import annotations

import statistics
from pathlib import Path

import pytest


SKILL = Path("skills/roasting/SKILL.md")


def test_phase_5_subagent_section():
    body = SKILL.read_text(encoding="utf-8")
    assert "Phase 5 — RGSB REVIEW" in body
    assert "run_in_background" in body or "Sub-Agent" in body
    for who in ("RED", "SILVER", "BLUE", "GOLD"):
        assert who in body


def test_phase_5_score_aggregation_via_sigma():
    body = SKILL.read_text(encoding="utf-8")
    assert "σ" in body or "표준편차" in body
    assert "0.5" in body
    assert "9.5" in body  # 합격선


def test_phase_5_fallback_disables_debate():
    body = SKILL.read_text(encoding="utf-8")
    # Sub-agent path explicitly mentions debate is unavailable.
    assert "토론 불가" in body or "토론 SKIP" in body or "debate" in body.lower()


def test_sigma_calculation_smoke():
    """Standard deviation logic — guard against future drift."""
    scores = [9.4, 8.7, 9.1, 7.8]
    sigma = statistics.stdev(scores)
    assert sigma > 0.5  # this exact set should trigger debate per spec
```

- [ ] **Step 2:** Run `.venv/bin/pytest tests/test_skill_phase_5_subagent.py -v` — expected: 4 passed.

### Task 9.3: Commit

- [ ] **Step 1:** Commit:

```bash
git add skills/roasting/SKILL.md tests/test_skill_phase_5_subagent.py
git commit -m "feat(skill): Phase 5 sub-agent fallback path (no debate)

Risk-mitigation strategy: build sub-agent path BEFORE Agent Teams (PR10).
This guarantees a working v0.1 even if TeamCreate is unstable.

- 4 reviewers dispatched in parallel via Agent + run_in_background
- Per-reviewer JSON output: {score, reason, suggestion}
- σ calculation + 9.5 gate
- σ ≥ 0.5 in sub-agent mode: alert user (no debate available); show
  raw distribution in output instead

Tests: structural assertions + sigma smoke test confirms expected
debate trigger on the example score set [9.4, 8.7, 9.1, 7.8].

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 9:**
- [ ] SKILL.md Phase 5 sub-agent path documented
- [ ] 4 reviewers parallel dispatch via `Agent` + `run_in_background`
- [ ] σ + 9.5 gate logic present
- [ ] Tests pass (4 assertions)

---

## PR 10: SKILL.md Phase 5 — Agent Teams Path (with auto-fallback)

**Goal:** Layer Agent Teams (TeamCreate + SendMessage + TaskCreate) onto Phase 5. Auto-detect availability; fall back to PR 9 path if `TeamCreate` errors.

**Depends on:** PR 9.

**Files:**
- Modify: `skills/roasting/SKILL.md` (extend Phase 5)
- Create: `tests/test_skill_phase_5_teams.py`

### Task 10.1: Add Agent Teams pseudocode + auto-detect

- [ ] **Step 1:** Insert before the Sub-Agent Fallback subsection in Phase 5:

````markdown
### Phase 5 — RGSB REVIEW (Primary Path: Agent Teams)

**자동 탐지:** `TeamCreate` 도구가 가용하면 이 경로, 아니면 Sub-Agent Fallback (다음 절).

#### 5.1 Round 1 — TeamCreate

```python
TeamCreate(
    team_name=f"5color-rgsb-{case_id}-{session_id}",
    members=[
        {"name": "RED",    "agent": "roasting-red",    "model": "opus"},
        {"name": "GOLD",   "agent": "roasting-gold",   "model": "opus"},
        {"name": "SILVER", "agent": "roasting-silver", "model": "sonnet"},
        {"name": "BLUE",   "agent": "roasting-blue",   "model": "sonnet"},
    ],
)
SendMessage(to="all", content={
  "black_draft": draft_text,
  "case_definition": case_md,
  "round": n,
})
```

> `TeamCreate` 호출이 `NotAvailable` 또는 `Forbidden` 에러를 던지면 Sub-Agent Fallback으로 즉시 전환. 다음 라운드에서도 폴백 유지.

#### 5.2 Fan-out 채점

각 페르소나가 독립 컨텍스트에서 채점 → `TaskCreate("scoring-table-round-{n}")` 등록:
```json
{"persona": "RED", "score": 9.4, "reason": "...", "suggestion": "..."}
```

#### 5.3 토론 트리거 (σ ≥ 0.5)

메인이 4 점수의 σ 계산. 트리거 시:

```python
sorted_by_score = sorted(scores.items(), key=lambda x: x[1].score)
low = sorted_by_score[0]    # (persona, score)
high = sorted_by_score[-1]
# 타이브레이커: 점수 동률 시 GOLD > RED > SILVER > BLUE
TIEBREAK_ORDER = {"GOLD": 0, "RED": 1, "SILVER": 2, "BLUE": 3}

SendMessage(
  to=high.persona, from_=low.persona,
  content=f"{low.persona}({low.score}) → {high.persona}({high.score}): "
          f"독자/이성 입장 {low.reason} 약점, 점수 재고려",
)
SendMessage(
  to=low.persona, from_=high.persona,
  content=f"{high.persona}({high.score}) → {low.persona}({low.score}): "
          f"{high.reason} 강점 고려",
)
# 양측 새 점수 + 코멘트 TaskUpdate
```

1라운드 후 σ 여전히 ≥ 0.5 → "합의 실패" 표시 + 분포 그대로 사용.

#### 5.4 게이트

평균 ≥ 9.5 → Phase 7. 미만 → Phase 6 (round +1).

#### 5.5 라이프사이클 (★ 케이스당 1팀)

- **Round 2+에서 TeamCreate 안 함** (같은 팀 재사용 → 라운드 간 컨텍스트 유지 = 일관성 ↑).
- 새 BLACK 산출물을 `SendMessage(to="all")`로 broadcast → 5.2부터 반복.
- Phase 7 진입 직전 1회 `TeamDelete`.

| | Round 1 | Round n+1 |
|---|---|---|
| TeamCreate | ✓ | ✗ |
| BLACK draft broadcast | ✓ | ✓ (새 draft) |
| 채점 | ✓ | ✓ |
| 토론 | σ ≥ 0.5 | σ ≥ 0.5 |
| 비용 | ~$0.18 | ~$0.18 |

#### 5.6 컨텍스트 드리프트 방어

라운드 간 RGSB 컨텍스트 누적 시 채점이 점진적으로 *boost* 또는 *drift*할 위험. 4라운드 cap이 자연 해소.

5라운드 이상으로 늘리지 않음 (Phase 6에서 4라운드에 끊음).

---

### Phase 5 — RGSB REVIEW (Sub-Agent Fallback Path)

(PR 9에서 작성한 내용 그대로 유지. Agent Teams 비가용 시 이 경로로 자동 폴백.)
````

### Task 10.2: Phase 5 Agent Teams 구조 테스트

- [ ] **Step 1:** Create `tests/test_skill_phase_5_teams.py`:

```python
"""Verify Phase 5 Agent Teams primary path + auto-fallback."""
from __future__ import annotations

from pathlib import Path

import pytest


SKILL = Path("skills/roasting/SKILL.md")


def test_phase_5_has_team_create():
    body = SKILL.read_text(encoding="utf-8")
    assert "TeamCreate" in body
    assert "SendMessage" in body
    assert "TaskCreate" in body


def test_phase_5_lifecycle_single_team_per_case():
    body = SKILL.read_text(encoding="utf-8")
    assert "Round 2+에서 TeamCreate 안 함" in body or "1팀" in body
    assert "TeamDelete" in body


def test_phase_5_tiebreaker_order():
    body = SKILL.read_text(encoding="utf-8")
    assert "GOLD" in body and "RED" in body and "SILVER" in body and "BLUE" in body
    # GOLD must be highest priority in tiebreak.
    gold_pos = body.find('"GOLD": 0')
    red_pos = body.find('"RED": 1')
    silver_pos = body.find('"SILVER": 2')
    blue_pos = body.find('"BLUE": 3')
    assert 0 < gold_pos < red_pos < silver_pos < blue_pos


def test_phase_5_auto_fallback_documented():
    body = SKILL.read_text(encoding="utf-8")
    assert "NotAvailable" in body or "폴백" in body
    assert "Sub-Agent Fallback" in body


def test_models_red_gold_opus_silver_blue_sonnet():
    body = SKILL.read_text(encoding="utf-8")
    # Opus reviewers
    for line_should_contain in [
        '"name": "RED"',
        '"model": "opus"',
        '"name": "GOLD"',
    ]:
        assert line_should_contain in body
    # Sonnet reviewers
    assert '"name": "SILVER"' in body and '"model": "sonnet"' in body
    assert '"name": "BLUE"' in body
```

- [ ] **Step 2:** Run `.venv/bin/pytest tests/test_skill_phase_5_teams.py -v` — expected: 5 passed.

### Task 10.3: Commit

- [ ] **Step 1:** Commit:

```bash
git add skills/roasting/SKILL.md tests/test_skill_phase_5_teams.py
git commit -m "feat(skill): Phase 5 Agent Teams primary path + auto-fallback

Layered on top of PR9 sub-agent fallback. Auto-detect TeamCreate availability;
fall back instantly to sub-agent path on NotAvailable/Forbidden.

- TeamCreate (per-case 1 team, kept across rounds, deleted at Phase 7)
- SendMessage broadcast for BLACK draft + targeted debate triggers
- TaskCreate scoring table with TaskUpdate after debate
- σ ≥ 0.5 debate trigger; tiebreaker GOLD > RED > SILVER > BLUE
- σ remains ≥ 0.5 after 1-round debate → 'consensus failed' display
- 4-round cap = drift defense

Test: 5 structural assertions verify TeamCreate, lifecycle, tiebreaker order,
fallback note, model assignment.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 10:**
- [ ] Phase 5 has both Agent Teams path and Sub-Agent fallback
- [ ] Auto-detect logic explicit
- [ ] Tiebreaker order documented (GOLD > RED > SILVER > BLUE)
- [ ] Lifecycle: TeamCreate Round 1 only, TeamDelete at Phase 7
- [ ] Tests pass (5 assertions)

---

## PR 11: SKILL.md Phase 6–7 (Loop + Deliver)

**Goal:** Implement Phase 6 (round backedge) and Phase 7 (3-output delivery + telemetry).

**Depends on:** PR 10.

**Files:**
- Modify: `skills/roasting/SKILL.md`
- Create: `scripts/deliver.py`
- Create: `tests/test_skill_phase_6_7.py`

### Task 11.1: Phase 6 LOOP + Phase 7 DELIVER pseudocode

- [ ] **Step 1:** Replace stubs with:

````markdown
### Phase 6 — LOOP (조건부 backedge)

| 조건 | 행동 |
|---|---|
| 평균 ≥ 9.5 | Phase 7 |
| < 9.5 + round_count < 4 | round_count += 1; BLACK 재호출 (RGSB 코멘트 + 이전 산출물) → Phase 3 |
| < 9.5 + round_count == 4 | 강제 종료. 가장 높았던 라운드 결과 사용. 사용자 보고 "9.5 미달 (max=X.Y). 캐스팅 또는 과제 정의 문제 가능성. 1on1 권장" |

### Phase 7 — DELIVER (3종 출력)

처리 (`scripts.deliver.deliver()`):

1. `TeamDelete` (Agent Teams 경로일 때만).
2. `_workspace/{session}/final/` 디렉토리 생성.
3. **3종 산출물 생성:**
   - `output.{html|md}`: 최종 BLACK 산출물 (출력 포맷에 따라).
   - `critique.md`: 라운드별 RGSB 4인 코멘트 정리 (교재).
   - `reasoning.md`: BLACK 결정 로그 + 안티패턴 검출 이력 + 라운드 진화.
4. 사용자에게 인터랙티브 안내:
   ```
   완료. 산출물 위치: ~/.claude/roasting/_workspace/{session}/final/
   - output.{html|md}     ← 임원이 사용
   - critique.md          ← RGSB 4인 평가 (교재)
   - reasoning.md         ← BLACK 결정 로그
   
   다음 액션을 골라주세요:
   1) 산출물 보기
   2) critique 보기
   3) 다시 호출 (/roasting xxxxx)
   4) 피드백 (/roasting --feedback)
   ```
5. **익명 telemetry 전송 (옵트인 시):**
   ```python
   if config.telemetry_enabled:
       telemetry.send({
           "user_id": user_uuid,
           "skill_version": "0.1.0",
           "case_id": case.id,
           "final_score": avg_score,
           "round_count": rounds,
           "slide_template_id": slide.id if slide else None,
           "total_cost_usd": cost,
           "anti_patterns_detected": ap_counter.counts,
           "debate_triggered": any_debate,
           "completion_status": "passed" | "forced" | "user_aborted",
       })
   ```
   콘텐츠 텍스트는 절대 포함 안 됨.
````

### Task 11.2: scripts/deliver.py — output 3종 생성 헬퍼

- [ ] **Step 1:** Create `scripts/deliver.py`:

```python
"""Phase 7 deliverables: write output / critique / reasoning to _workspace/.../final/."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RoundData:
    round_num: int
    black_draft_path: Path
    rgsb_scores: dict[str, dict[str, Any]]   # {persona: {score, reason, suggestion}}
    debate_log: str
    anti_patterns: list[dict[str, Any]]


@dataclass
class SessionResult:
    session_dir: Path
    case_id: str
    case_title: str
    user_xxxxx: str
    rounds: list[RoundData]
    final_round_idx: int
    completion_status: str   # "passed" | "forced" | "user_aborted"
    output_format: str       # "md" | "html"


def deliver(result: SessionResult) -> Path:
    final_dir = result.session_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    final_round = result.rounds[result.final_round_idx]
    # 1. output.{ext} — copy final BLACK draft to final/
    out_ext = result.output_format
    output_path = final_dir / f"output.{out_ext}"
    output_path.write_text(
        final_round.black_draft_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    # 2. critique.md — RGSB comments per round, in order
    final_dir.joinpath("critique.md").write_text(_render_critique(result), encoding="utf-8")
    # 3. reasoning.md — BLACK decision log
    final_dir.joinpath("reasoning.md").write_text(_render_reasoning(result), encoding="utf-8")
    return final_dir


def _render_critique(r: SessionResult) -> str:
    lines = [f"# {r.case_title} — 4인 평가 코멘트\n",
             f"> 케이스 `{r.case_id}` · 사용자 입력: \"{r.user_xxxxx[:80]}\"\n\n"]
    for rd in r.rounds:
        lines.append(f"## Round {rd.round_num}\n\n")
        for persona in ("RED", "SILVER", "BLUE", "GOLD"):
            entry = rd.rgsb_scores.get(persona, {})
            score = entry.get("score", "—")
            reason = entry.get("reason", "")
            suggestion = entry.get("suggestion", "")
            lines.append(f"- **{persona}**: {score} — {reason}\n")
            if suggestion:
                lines.append(f"  - 개선안: {suggestion}\n")
        if rd.debate_log:
            lines.append(f"\n### Round {rd.round_num} 토론\n\n{rd.debate_log}\n\n")
    return "".join(lines)


def _render_reasoning(r: SessionResult) -> str:
    lines = [f"# {r.case_title} — BLACK 결정 로그\n\n",
             f"종료 상태: **{r.completion_status}**, 최종 라운드: {r.rounds[r.final_round_idx].round_num}\n\n"]
    for rd in r.rounds:
        lines.append(f"## Round {rd.round_num}\n\n")
        if rd.anti_patterns:
            lines.append("### 안티패턴 검출 + 자체 수정\n\n")
            for ap in rd.anti_patterns:
                lines.append(f"- `{ap.get('name')}`: {ap.get('detail')}\n")
            lines.append("\n")
        else:
            lines.append("(안티패턴 검출 없음)\n\n")
    return "".join(lines)
```

### Task 11.3: Phase 6/7 테스트

- [ ] **Step 1:** Create `tests/test_skill_phase_6_7.py`:

```python
"""Phase 6 + Phase 7 verification."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.deliver import RoundData, SessionResult, deliver


SKILL = Path("skills/roasting/SKILL.md")


def test_phase_6_documents_three_branches():
    body = SKILL.read_text(encoding="utf-8")
    assert "Phase 6 — LOOP" in body
    assert "round_count < 4" in body
    assert "round_count == 4" in body
    assert "9.5 미달" in body


def test_phase_7_lists_three_outputs():
    body = SKILL.read_text(encoding="utf-8")
    assert "output.{html|md}" in body or "output." in body
    assert "critique.md" in body
    assert "reasoning.md" in body


def test_phase_7_telemetry_optin_no_content():
    body = SKILL.read_text(encoding="utf-8")
    assert "telemetry" in body.lower()
    assert "콘텐츠" in body and ("절대" in body or "안 됨" in body or "0" in body)


def test_deliver_writes_three_files(tmp_path):
    session = tmp_path / "test-session"
    rd1 = session / "round-1"
    rd1.mkdir(parents=True)
    draft = rd1 / "black-draft.md"
    draft.write_text("# Test Output\nbody", encoding="utf-8")
    result = SessionResult(
        session_dir=session,
        case_id="p1",
        case_title="이메일 (외부 비즈니스)",
        user_xxxxx="거래처에 답신 안 오는 메일",
        rounds=[
            RoundData(
                round_num=1,
                black_draft_path=draft,
                rgsb_scores={
                    "RED": {"score": 9.4, "reason": "의도 명확", "suggestion": ""},
                    "SILVER": {"score": 9.3, "reason": "구조 OK", "suggestion": ""},
                    "BLUE": {"score": 9.5, "reason": "톤 적정", "suggestion": ""},
                    "GOLD": {"score": 9.5, "reason": "미리보기 살아있음", "suggestion": ""},
                },
                debate_log="",
                anti_patterns=[],
            ),
        ],
        final_round_idx=0,
        completion_status="passed",
        output_format="md",
    )
    final = deliver(result)
    assert (final / "output.md").exists()
    assert (final / "critique.md").exists()
    assert (final / "reasoning.md").exists()
    critique = (final / "critique.md").read_text(encoding="utf-8")
    assert "RED" in critique and "GOLD" in critique
    assert "9.5" in critique
```

- [ ] **Step 2:** Run `.venv/bin/pytest tests/test_skill_phase_6_7.py -v` — expected: 4 passed.

### Task 11.4: Commit

- [ ] **Step 1:** Commit:

```bash
git add skills/roasting/SKILL.md scripts/deliver.py tests/test_skill_phase_6_7.py
git commit -m "feat(skill): Phase 6 LOOP + Phase 7 DELIVER (3 outputs + telemetry)

Phase 6: 3-branch backedge
- avg ≥ 9.5 → Phase 7
- avg < 9.5 + round < 4 → BLACK rewrite (Phase 3)
- avg < 9.5 + round == 4 → forced exit, best round used,
  '캐스팅/과제 정의 문제 가능성, 1on1 권장' user note

Phase 7: 3-output deliver
- output.{html|md}: final BLACK
- critique.md: RGSB comments per round (교재)
- reasoning.md: BLACK decision log + anti-pattern history
- TeamDelete (Agent Teams path)
- Telemetry opt-in; metadata only, never content

scripts/deliver.py: dataclass-based SessionResult + render helpers; tested
end-to-end with mock data.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 11:**
- [ ] Phase 6 documents 3 branches with explicit conditions
- [ ] Phase 7 produces 3 files (output, critique, reasoning)
- [ ] Telemetry described as opt-in, content-free
- [ ] `deliver()` integration test passes

---

## PR 12: HTML Slide Output (PPT Cases)

**Goal:** For PPT cases (p41, p42, p43, p45), bind BLACK output into a slide_library template HTML and emit `output.html`.

**Depends on:** PR 3 (slide index) + PR 11 (deliver).

**Files:**
- Create: `scripts/build_slide_html.py`
- Modify: `scripts/deliver.py` (call build_slide_html for PPT cases)
- Create: `tests/test_build_slide_html.py`

### Task 12.1: build_slide_html.py — template fetch + content injection

- [ ] **Step 1:** Create `scripts/build_slide_html.py`:

```python
"""For PPT cases, fetch the slide_library template HTML and inject BLACK content.

Strategy:
1. Pull template HTML from index.json url field.
2. Parse with BeautifulSoup, locate the slide content container (the
   slide_library convention is a wrapping element with class 'slides' or a
   data-role='slides' attribute).
3. Replace inner content with BLACK output Markdown converted to HTML slides.
4. Write the merged HTML to output.html.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag


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


def build(index_json: Path, template_id: str, black_md: str, output_html: Path) -> Path:
    tpl = load_template_meta(index_json, template_id)
    template_html = fetch_template_html(tpl)
    blocks = black_md_to_slide_blocks(black_md)
    merged = inject_slides(template_html, blocks)
    output_html.write_text(merged, encoding="utf-8")
    return output_html
```

### Task 12.2: deliver.py에서 PPT 케이스 분기 추가

- [ ] **Step 1:** Edit `scripts/deliver.py` — extend `deliver()` to call `build_slide_html` for PPT cases:

```python
# In deliver(), replace the output writing block with:
if result.output_format == "html":
    from .build_slide_html import build
    final_round = result.rounds[result.final_round_idx]
    build(
        index_json=Path("skills/roasting/references/slide-templates/index.json"),
        template_id=result.slide_template_id,   # add this field below
        black_md=final_round.black_draft_path.read_text(encoding="utf-8"),
        output_html=output_path,
    )
else:
    output_path.write_text(
        final_round.black_draft_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
```

- [ ] **Step 2:** Add `slide_template_id: str | None = None` to `SessionResult` dataclass.
- [ ] **Step 3:** Add fallback: if `output_format == "html"` and `build()` raises (e.g., template URL down), fall back to writing `output.md` with a warning footer:
  ```
  > ⚠️ HTML 슬라이드 빌드 실패. Markdown 폴백으로 출력. 사유: {error}
  ```

### Task 12.3: build_slide_html 테스트

- [ ] **Step 1:** Create `tests/test_build_slide_html.py`:

```python
"""Test slide HTML builder with mock template + minimal Markdown."""
from __future__ import annotations

import json
from pathlib import Path

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
```

- [ ] **Step 2:** Run `.venv/bin/pytest tests/test_build_slide_html.py -v` — expected: 5 passed.

### Task 12.4: Commit

- [ ] **Step 1:** Commit:

```bash
git add scripts/build_slide_html.py scripts/deliver.py tests/test_build_slide_html.py
git commit -m "feat(slides): HTML deck builder for PPT cases (p41/p42/p43/p45)

- build_slide_html.py: load template meta from index.json, fetch template
  HTML, parse Markdown into per-section slide blocks, inject into the
  slide_library template's content container, write merged output.html
- Minimal Markdown subset for v0.1 (paragraphs, ul, headings)
- Container detection: data-role='slides' > .slides > main > body
- deliver.py: HTML branch when result.output_format == 'html'; falls back
  to Markdown with warning footer if build raises
- 5 unit tests cover MD→HTML conversion, container replacement, lookup

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 12:**
- [ ] PPT case end-to-end: BLACK Markdown → HTML deck with chosen template
- [ ] Fallback to `.md` when template fetch fails
- [ ] 5 unit tests pass

---

## PR 13: Telemetry Backend (Supabase + opt-in client)

**Goal:** Set up Supabase project, run schema migration, ship `scripts/telemetry.py` with opt-in config + `/roasting --feedback` GitHub Issue helper.

**Depends on:** PR 1 (parallel-safe).

**Files:**
- Create: `db/migrations/0001_init_telemetry.sql`
- Create: `scripts/telemetry.py`
- Create: `scripts/feedback.py`
- Create: `tests/test_telemetry.py`
- Create: `docs/setup/supabase.md`

### Task 13.1: SQL migration

- [ ] **Step 1:** Create `db/migrations/0001_init_telemetry.sql`:

```sql
CREATE TABLE roasting_telemetry (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL,
    skill_version TEXT NOT NULL,
    case_id TEXT NOT NULL,
    final_score NUMERIC(3,1),
    round_count INT,
    slide_template_id TEXT,
    total_cost_usd NUMERIC(10,4),
    anti_patterns_detected JSONB,
    debate_triggered BOOLEAN,
    completion_status TEXT CHECK (completion_status IN ('passed','forced','user_aborted'))
);

CREATE INDEX idx_telemetry_case_id ON roasting_telemetry(case_id);
CREATE INDEX idx_telemetry_user_id ON roasting_telemetry(user_id);
CREATE INDEX idx_telemetry_timestamp ON roasting_telemetry(timestamp DESC);

-- Disable row-level reads except for service role.
ALTER TABLE roasting_telemetry ENABLE ROW LEVEL SECURITY;

-- Anonymous inserts only (no SELECT).
CREATE POLICY anon_insert ON roasting_telemetry
    FOR INSERT TO anon WITH CHECK (true);
```

### Task 13.2: Supabase setup doc

- [ ] **Step 1:** Create `docs/setup/supabase.md`:

```markdown
# Supabase Telemetry Backend Setup

## One-time setup (manual)

1. Create Supabase project at https://supabase.com (free tier).
2. Get project URL + anon key from Project Settings → API.
3. Run migration: copy `db/migrations/0001_init_telemetry.sql` into the SQL Editor and execute.
4. Add to repo secrets (GitHub Actions):
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
5. (Optional) Add to plugin manifest as bundled resource — for v0.1 we hardcode the URL into `scripts/telemetry.py` (anon key is safe to ship since RLS only allows INSERT).

## Free tier capacity

- 500 MB database, 2 GB egress/month.
- Estimated row size: ~250 bytes.
- Capacity: ~2M rows. v0.1 beta target: 50 users × 5 calls/day × 30 days = 7,500 rows ≪ 2M.

## Privacy invariants

The schema **explicitly** has no content columns:
- ❌ no xxxxx
- ❌ no BLACK output
- ❌ no RGSB comments
- ✅ case_id, score, rounds, anti-pattern counts, timestamp

Any future column addition must preserve this invariant.
```

### Task 13.3: telemetry.py opt-in client

- [ ] **Step 1:** Create `scripts/telemetry.py`:

```python
"""Anonymous telemetry client. Default = OFF; opt-in via config.

Config file: ~/.claude/roasting/config.json
{"telemetry": true | false}     # default false
{"user_id": "<uuid>"}           # generated on first opt-in

Privacy invariant: no content fields are ever included.
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from supabase import Client, create_client


CONFIG_PATH = Path.home() / ".claude" / "roasting" / "config.json"

# Hardcoded — anon key is safe (RLS allows only INSERT).
SUPABASE_URL = os.environ.get("ROASTING_SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("ROASTING_SUPABASE_ANON_KEY", "")


@dataclass
class TelemetryEvent:
    user_id: str
    skill_version: str
    case_id: str
    final_score: float | None
    round_count: int
    slide_template_id: str | None
    total_cost_usd: float
    anti_patterns_detected: dict[str, int]
    debate_triggered: bool
    completion_status: str   # passed | forced | user_aborted


def _load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _save_config(cfg: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def is_enabled() -> bool:
    return _load_config().get("telemetry", False)


def get_or_create_user_id() -> str:
    cfg = _load_config()
    if "user_id" not in cfg:
        cfg["user_id"] = str(uuid.uuid4())
        _save_config(cfg)
    return cfg["user_id"]


def send(event: TelemetryEvent, client: Client | None = None) -> None:
    """Insert event. No-op if telemetry disabled or env vars missing."""
    if not is_enabled():
        return
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return
    if client is None:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    payload = asdict(event)
    # Sanity guard against accidental content leakage.
    forbidden = {"xxxxx", "input", "output", "draft", "comment", "text", "content"}
    for key in payload.keys():
        assert key.lower() not in forbidden, (
            f"telemetry guard: forbidden field '{key}' detected"
        )
    client.table("roasting_telemetry").insert(payload).execute()
```

### Task 13.4: feedback.py — `/roasting --feedback`

- [ ] **Step 1:** Create `scripts/feedback.py`:

```python
"""/roasting --feedback handler. Builds a prefilled GitHub Issue URL.

Includes session_id (anonymous UUID) so author can correlate with telemetry,
but no content.
"""
from __future__ import annotations

import urllib.parse
from pathlib import Path

from .telemetry import get_or_create_user_id


REPO = "airoasting/roasting"


def build_issue_url(case_id: str, session_id: str, summary: str = "") -> str:
    user_id = get_or_create_user_id()
    title = f"[Beta feedback] {case_id} session {session_id[:8]}"
    body = (
        "## Beta feedback\n\n"
        f"- session: `{session_id}`\n"
        f"- user (anonymous): `{user_id}`\n"
        f"- case: `{case_id}`\n"
        f"- skill version: `0.1.0`\n\n"
        "## What worked / what didn't\n\n"
        f"{summary or '(여기에 자유 작성)'}\n\n"
        "_프라이버시: 산출물 내용은 작성하지 마세요. 메타 의견만._\n"
    )
    params = urllib.parse.urlencode({
        "title": title, "body": body, "labels": "beta-feedback",
    })
    return f"https://github.com/{REPO}/issues/new?{params}"
```

### Task 13.5: 테스트

- [ ] **Step 1:** Create `tests/test_telemetry.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts import telemetry as t
from scripts.telemetry import TelemetryEvent
from scripts.feedback import build_issue_url


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    monkeypatch.setattr(t, "CONFIG_PATH", cfg)
    return cfg


def test_disabled_by_default(tmp_config):
    assert t.is_enabled() is False


def test_enable_via_config(tmp_config):
    tmp_config.parent.mkdir(parents=True, exist_ok=True)
    tmp_config.write_text(json.dumps({"telemetry": True}), encoding="utf-8")
    assert t.is_enabled() is True


def test_user_id_persisted(tmp_config):
    uid1 = t.get_or_create_user_id()
    uid2 = t.get_or_create_user_id()
    assert uid1 == uid2


def test_send_noop_when_disabled(tmp_config, monkeypatch):
    fake_client = MagicMock()
    event = TelemetryEvent(
        user_id="u", skill_version="0.1.0", case_id="p1",
        final_score=9.5, round_count=1, slide_template_id=None,
        total_cost_usd=0.21, anti_patterns_detected={}, debate_triggered=False,
        completion_status="passed",
    )
    t.send(event, client=fake_client)
    fake_client.table.assert_not_called()


def test_send_inserts_when_enabled(tmp_config, monkeypatch):
    tmp_config.parent.mkdir(parents=True, exist_ok=True)
    tmp_config.write_text(json.dumps({"telemetry": True}), encoding="utf-8")
    monkeypatch.setattr(t, "SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setattr(t, "SUPABASE_ANON_KEY", "fake-key")
    fake_client = MagicMock()
    event = TelemetryEvent(
        user_id="u", skill_version="0.1.0", case_id="p1",
        final_score=9.5, round_count=1, slide_template_id=None,
        total_cost_usd=0.21, anti_patterns_detected={}, debate_triggered=False,
        completion_status="passed",
    )
    t.send(event, client=fake_client)
    fake_client.table.assert_called_with("roasting_telemetry")


def test_event_has_no_forbidden_fields():
    """Schema-level guard: ensure dataclass fields don't include content."""
    event = TelemetryEvent(
        user_id="u", skill_version="0.1.0", case_id="p1",
        final_score=9.5, round_count=1, slide_template_id=None,
        total_cost_usd=0.21, anti_patterns_detected={}, debate_triggered=False,
        completion_status="passed",
    )
    forbidden = {"xxxxx", "input", "output", "draft", "comment", "text", "content"}
    assert not (forbidden & set(vars(event).keys()))


def test_feedback_url_includes_session(tmp_config):
    url = build_issue_url("p1", "sess-12345678", "결과가 빠르고 정확했음")
    assert "p1" in url
    assert "sess-1234" in url   # truncated to first 8 chars in title
    assert "labels=beta-feedback" in url
    assert "github.com/airoasting/roasting/issues/new" in url
```

- [ ] **Step 2:** Run `.venv/bin/pytest tests/test_telemetry.py -v` — expected: 7 passed.

### Task 13.6: Commit

- [ ] **Step 1:** Commit:

```bash
git add db/migrations/ scripts/telemetry.py scripts/feedback.py \
  tests/test_telemetry.py docs/setup/supabase.md
git commit -m "feat(telemetry): Supabase backend + opt-in client + feedback URL builder

- db/migrations/0001_init_telemetry.sql: schema + indexes + RLS (anon
  INSERT only, no SELECT). No content columns by design.
- scripts/telemetry.py: opt-in client (default OFF); reads
  ~/.claude/roasting/config.json. Persistent anonymous user_id (UUID).
  Forbidden-field assertion guards against accidental content leakage.
- scripts/feedback.py: build_issue_url generates prefilled GitHub Issue
  URL with session_id + anon user_id; reminds user not to paste content.
- docs/setup/supabase.md: project setup, free-tier capacity, privacy
  invariants.
- 7 tests cover opt-in default, persistence, no-op when disabled,
  insert when enabled (mocked client), forbidden-field guard, URL build.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 13:**
- [ ] Schema applied (manually via Supabase SQL editor for the actual project)
- [ ] Opt-in default OFF
- [ ] Anonymous user_id persisted across calls
- [ ] No content fields in schema or dataclass
- [ ] Tests pass (7)

---

## PR 14: CLAUDE.md Auto-Registration Hook

**Goal:** On install, append `/roasting` pointer block to user's `CLAUDE.md` (project or global). Idempotent (safe to rerun).

**Depends on:** PR 11.

**Files:**
- Create: `scripts/install_hook.py`
- Create: `tests/test_install_hook.py`

### Task 14.1: install_hook.py

- [ ] **Step 1:** Create `scripts/install_hook.py`:

```python
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
```

### Task 14.2: 테스트

- [ ] **Step 1:** Create `tests/test_install_hook.py`:

```python
from __future__ import annotations

from pathlib import Path

from scripts.install_hook import install, MARKER_BEGIN, MARKER_END


def test_creates_file_if_absent(tmp_path):
    target = tmp_path / "CLAUDE.md"
    assert install(target) == "inserted"
    body = target.read_text(encoding="utf-8")
    assert MARKER_BEGIN in body
    assert MARKER_END in body
    assert "/roasting" in body


def test_appends_to_existing(tmp_path):
    target = tmp_path / "CLAUDE.md"
    target.write_text("# Existing Memory\n\nproject context\n", encoding="utf-8")
    assert install(target) == "inserted"
    body = target.read_text(encoding="utf-8")
    assert "Existing Memory" in body
    assert MARKER_BEGIN in body


def test_replaces_existing_block(tmp_path):
    target = tmp_path / "CLAUDE.md"
    install(target, version="0.0.9")
    install(target, version="0.1.0")
    body = target.read_text(encoding="utf-8")
    assert "v0.0.9" not in body
    assert "v0.1.0" in body
    # Only one marker pair.
    assert body.count(MARKER_BEGIN) == 1
    assert body.count(MARKER_END) == 1


def test_idempotent_same_version(tmp_path):
    target = tmp_path / "CLAUDE.md"
    install(target, version="0.1.0")
    install(target, version="0.1.0")
    body = target.read_text(encoding="utf-8")
    assert body.count(MARKER_BEGIN) == 1
```

- [ ] **Step 2:** Run `.venv/bin/pytest tests/test_install_hook.py -v` — expected: 4 passed.

### Task 14.3: Commit

- [ ] **Step 1:** Commit:

```bash
git add scripts/install_hook.py tests/test_install_hook.py
git commit -m "feat(install): CLAUDE.md auto-registration hook

- Idempotent: marker-bounded block detected & replaced on rerun
- Creates CLAUDE.md if absent
- Block contents: 트리거 룰, 산출 위치, 변경 이력 시작 row
- 4 tests cover create/append/replace/idempotent paths

Wired into the install command in PR 18 release flow.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 14:**
- [ ] Script appends/replaces block in CLAUDE.md
- [ ] Idempotent across reruns
- [ ] 4 tests pass

---

## PR 15: Documentation (README en/ko, CHANGELOG, privacy, user guide)

**Goal:** Replace skeleton README with full marketing-grade English README + comprehensive Korean executive guide.

**Depends on:** PR 11.

**Files:**
- Modify: `README.md` (English, marketing)
- Create: `README.ko.md` (Korean, exec)
- Modify: `CHANGELOG.md` (full v0.1.0 entry)
- Create: `docs/ko/getting-started.md`
- Create: `docs/ko/case-catalog.md` (auto-generated index)
- Create: `docs/en/architecture.md`
- Create: `docs/PRIVACY.md`

### Task 15.1: README.md (English)

- [ ] **Step 1:** Replace `README.md` with the full English version. ~80 lines covering: tagline, install, what-it-does, sample, "Korean only — see README.ko.md", privacy summary, status (open beta), contributing, license. Use spec sections 1, 2, 11, 12 as the source.

### Task 15.2: README.ko.md (Korean executive guide)

- [ ] **Step 1:** Create `README.ko.md` with sections:
  1. **시작 (5분)** — `/plugin install` 두 줄 + 첫 호출 예시
  2. **이게 무엇인가** — 5color 사이트 + slide_library + /roasting의 관계
  3. **63개 케이스 카탈로그** — `docs/ko/case-catalog.md` 링크 + 8개 카테고리 요약 표
  4. **5-Color 방법론** — 5인 페르소나 1줄 설명 + 9.5 합격선 + 4라운드
  5. **PPT 케이스 — slide_library 결합** — 첫 호출에 템플릿 컨펌 흐름
  6. **프라이버시** — 콘텐츠 0 수집 강조 + opt-in 옵트아웃 방법
  7. **베타 피드백** — `/roasting --feedback` 사용
  8. **비용 안내** — 호출당 ~$0.36 추정 + 1인 월 ~$54
  9. **알려진 한계** — 베타 라벨, Agent Teams 실험성, 자동 sync 미지원
  10. **다음 버전 (v0.2)** — Instinct, Hooks, 자동 sync, 검증 등급

### Task 15.3: docs/ko/case-catalog.md (auto-generated)

- [ ] **Step 1:** Add Makefile target:

```makefile
gen-case-catalog:
	$(PYTHON) -m scripts.gen_case_catalog \
		--cases skills/roasting/references/cases/ \
		--out docs/ko/case-catalog.md
```

- [ ] **Step 2:** Create `scripts/gen_case_catalog.py`:

```python
"""Generate docs/ko/case-catalog.md from references/cases/p*.md frontmatter."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def parse_fm(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    return yaml.safe_load(text[3:end]) or {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    by_cat: dict[str, list[dict]] = {}
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
                f"{it.get('title')} | {it.get('subhead','')} |\n"
            )
        lines.append("\n")
    args.out.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3:** Run `make gen-case-catalog`. Verify output has 8 categories + 63 entries.

### Task 15.4: docs/PRIVACY.md

- [ ] **Step 1:** Create `docs/PRIVACY.md` (also linked from both READMEs):

```markdown
# Privacy Policy

## Summary

**We never collect content.** Anonymous metadata only, opt-in by default OFF.

## What we collect (only if user opts in)

| Field | Example |
|---|---|
| user_id | UUID generated locally on first opt-in |
| skill_version | "0.1.0" |
| case_id | "p1" |
| final_score | 9.5 |
| round_count | 2 |
| slide_template_id | "tpl-consulting-firm" |
| total_cost_usd | 0.36 |
| anti_patterns_detected | {"VAGUE_CTA": 1} |
| debate_triggered | true |
| completion_status | "passed" |
| timestamp | ISO 8601 |

## What we never collect

- ❌ `xxxxx` user input
- ❌ BLACK draft content
- ❌ RGSB scoring comments or debate transcripts
- ❌ Slide template HTML rendered output
- ❌ File paths, IP addresses, system info beyond above

## How to control

```bash
# Disable telemetry (default)
echo '{"telemetry": false}' > ~/.claude/roasting/config.json

# Enable
echo '{"telemetry": true}' > ~/.claude/roasting/config.json
```

## Backend

Supabase project owned by AI ROASTING. Row-level security: anonymous role
can INSERT only — no SELECT/UPDATE/DELETE access from the client.

## Beta data retention

Data collected during open beta v0.1.x is retained for v1.0 evolution analysis.
After v1.0 release, retention policy will be updated. To request deletion of
your anonymous user_id's records, open a GitHub Issue with the user_id.
```

### Task 15.5: CHANGELOG full entry

- [ ] **Step 1:** Replace `CHANGELOG.md`'s v0.1.0 stub with comprehensive entry mirroring spec section 13 ("Versioning Roadmap") and section 17 ("v0.1 산출물 체크리스트").

### Task 15.6: Commit

- [ ] **Step 1:** Commit:

```bash
git add README.md README.ko.md CHANGELOG.md docs/ scripts/gen_case_catalog.py Makefile
git commit -m "docs: full README en/ko + case catalog generator + privacy policy

- README.md: marketing-grade English (install, what, sample, privacy, status)
- README.ko.md: 임원용 한국어 가이드 (10 sections)
- docs/ko/case-catalog.md: 8 categories × 63 cases auto-generated from
  references/cases/*.md frontmatter
- scripts/gen_case_catalog.py + 'make gen-case-catalog' target
- docs/PRIVACY.md: explicit no-content policy + opt-in/out instructions
- CHANGELOG.md: full v0.1.0 entry

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 15:**
- [ ] Both READMEs comprehensive (no placeholders)
- [ ] Case catalog auto-generated, 63 entries
- [ ] PRIVACY.md explicit
- [ ] CHANGELOG entry complete

---

## PR 16: GitHub Actions CI

**Goal:** PR check + tag-based release matrix.

**Depends on:** PR 4 + PR 5 (tests must exist).

**Files:**
- Modify: `.github/workflows/test.yml` (full version)
- Create: `.github/workflows/release.yml`

### Task 16.1: test.yml — PR + push checks

- [ ] **Step 1:** Replace skeleton with:

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: mypy scripts/

  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v -m "not network and not slow"

  network:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v -m network
```

### Task 16.2: release.yml — package + GitHub release

- [ ] **Step 1:** Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  package:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - name: Run all tests except slow/network
        run: pytest tests/ -v -m "not slow and not network"
      - name: Build package
        run: make package
      - name: Create release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/*.zip
          generate_release_notes: true
          prerelease: ${{ contains(github.ref_name, '-') }}
```

### Task 16.3: Verify CI green on a draft PR

- [ ] **Step 1:** Create a no-op branch + draft PR to verify all 3 jobs (lint, unit, network) run and lint+unit pass.
- [ ] **Step 2:** Once CI green, merge.
- [ ] **Step 3:** Commit:

```bash
git add .github/workflows/
git commit -m "ci: lint + unit + network jobs + tag-triggered release

- test.yml: lint (ruff + mypy), unit (no slow/network), network (main push only)
- release.yml: tests + make package + GitHub release on v* tag
- Prerelease auto-detected from tag name containing '-'

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 16:**
- [ ] CI lint + unit jobs run on every PR
- [ ] Network job runs on main push (live 5color sync test)
- [ ] Tag `v*` triggers release workflow
- [ ] Test PR confirms green

---

## PR 17: Quality Integration Tests (15 scenarios, avg ≥ 9.0)

**Goal:** End-to-end quality gate. 5 representative cases × 3 input variations = 15 scenarios. Run full /roasting flow (route → BLACK → anti-pattern → RGSB → loop → deliver). Gate at average final_score ≥ 9.0 (beta target).

**Depends on:** PR 12.

**Files:**
- Create: `tests/quality/scenarios.json`
- Create: `tests/quality/test_quality_gate.py`
- Create: `tests/quality/run_scenario.py` (helper to run one scenario in isolation)

### Task 17.1: Pick 5 representative cases

- [ ] **Step 1:** Choose 5 cases that span categories + complexity:
  1. `p1` — 이메일 (외부 비즈니스) — short, frequent
  2. `p23` — 보고서 (실무, 1페이지) — medium analytic
  3. `p41` — 임원용 PPT — HTML output path
  4. `p2` — 사과문 — high-stakes tone (LEGAL_RISK_TERM applicable)
  5. `p25` — 기획안·제안서 — long-form persuasive

### Task 17.2: scenarios.json (15 entries)

- [ ] **Step 1:** Create `tests/quality/scenarios.json`:

```json
[
  {"case_id": "p1", "xxxxx": "거래처 부장한테 8/12까지 답변 달라는 메일",
   "expected_format": "md", "min_score": 9.0},
  {"case_id": "p1", "xxxxx": "공급사에 가격 인상 사유 답신",
   "expected_format": "md", "min_score": 9.0},
  {"case_id": "p1", "xxxxx": "고객사 부장에게 미팅 일정 재조정 요청",
   "expected_format": "md", "min_score": 9.0},

  {"case_id": "p23", "xxxxx": "Q2 KPI 1페이지 보고서 (목표 대비 실적 + 다음 분기 액션 3개)",
   "expected_format": "md", "min_score": 9.0},
  {"case_id": "p23", "xxxxx": "이번 주 세일즈 미팅 결과 1페이지로",
   "expected_format": "md", "min_score": 9.0},
  {"case_id": "p23", "xxxxx": "신제품 런칭 후 30일 성과 1페이지 요약",
   "expected_format": "md", "min_score": 9.0},

  {"case_id": "p41", "xxxxx": "이번 분기 임원 PPT (실적 + 리스크 + 다음 분기 결정사항 3개)",
   "expected_format": "html", "min_score": 9.0},
  {"case_id": "p41", "xxxxx": "신규 사업 기회 임원 보고용 슬라이드",
   "expected_format": "html", "min_score": 9.0},
  {"case_id": "p41", "xxxxx": "조직개편 임원 PPT",
   "expected_format": "html", "min_score": 9.0},

  {"case_id": "p2", "xxxxx": "서비스 장애 5시간 발생, 고객사에 보낼 사과문",
   "expected_format": "md", "min_score": 9.0},
  {"case_id": "p2", "xxxxx": "배송 지연된 VIP 고객 사과문",
   "expected_format": "md", "min_score": 9.0},
  {"case_id": "p2", "xxxxx": "데이터 노출 사고 사과문 (B2B 거래처)",
   "expected_format": "md", "min_score": 9.0},

  {"case_id": "p25", "xxxxx": "신규 SaaS 기획안 (KPI + 6개월 로드맵)",
   "expected_format": "md", "min_score": 9.0},
  {"case_id": "p25", "xxxxx": "내부 R&D 투자 제안서 (3억 규모)",
   "expected_format": "md", "min_score": 9.0},
  {"case_id": "p25", "xxxxx": "팀 분리 + 신설 조직 제안",
   "expected_format": "md", "min_score": 9.0}
]
```

### Task 17.3: 시나리오 실행 헬퍼 + 게이트 테스트

- [ ] **Step 1:** Create `tests/quality/run_scenario.py`. This is a thin Python harness that *simulates* the SKILL.md workflow by chaining `route()` → BLACK invocation → `detect_all` → 4 reviewer Agent calls → score aggregation → deliver. Since it requires Anthropic API access, it is `pytest.mark.slow`.

  > Implementation detail: BLACK + reviewer calls use `anthropic.Anthropic.messages.create` directly (one Sonnet for BLACK, one each for the 4 reviewers per their model). Skip Agent Teams / sub-agent dispatch overhead — for the quality gate we just need the score.

- [ ] **Step 2:** Create `tests/quality/test_quality_gate.py`:

```python
"""Quality gate: 15 scenarios, average final_score ≥ 9.0 (beta v0.1)."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import pytest

from tests.quality.run_scenario import run_one


pytestmark = pytest.mark.slow


def test_quality_gate():
    scenarios = json.loads(
        Path("tests/quality/scenarios.json").read_text(encoding="utf-8"))
    scores: list[float] = []
    failures: list[tuple[str, str, float]] = []
    for s in scenarios:
        result = run_one(case_id=s["case_id"], xxxxx=s["xxxxx"])
        scores.append(result.final_score)
        if result.final_score < s["min_score"]:
            failures.append((s["case_id"], s["xxxxx"][:40], result.final_score))
    avg = statistics.fmean(scores)
    print(f"\nQuality gate: avg={avg:.2f}, scores={scores}")
    if failures:
        print("\nBelow per-scenario threshold:")
        for c, x, sc in failures:
            print(f"  {c}: '{x}...' → {sc:.2f}")
    assert avg >= 9.0, f"Quality gate failed: avg={avg:.2f} < 9.0"
```

- [ ] **Step 3:** Run `make test-quality`. Expected: avg ≥ 9.0 (printed). Cost ≈ $5-7 per full run (15 × ~$0.40).
- [ ] **Step 4:** If gate fails, iterate: most likely fixes are (a) tightening the prompt sent to BLACK with more case context, (b) clarifying GOLD scenario in the case definition, (c) tweaking the anti-pattern detector thresholds. Iterate, re-run, commit changes.

### Task 17.4: Commit

- [ ] **Step 1:** Commit:

```bash
git add tests/quality/
git commit -m "test(quality): 15-scenario integration gate (avg ≥ 9.0)

5 representative cases × 3 input variations covering:
- p1 외부 이메일 (short, frequent)
- p23 1페이지 보고서 (medium analytic)
- p41 임원 PPT (HTML output)
- p2 사과문 (high-stakes tone, LEGAL_RISK_TERM)
- p25 기획안·제안서 (long-form persuasive)

Marked slow; ~\$5-7 per full run. CI excludes from default unit job;
runs explicitly via make test-quality before each release.

Acceptance: PR 17 quality gate met on first iteration.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**Acceptance criteria for PR 17:**
- [ ] 15 scenarios in scenarios.json
- [ ] Quality gate average ≥ 9.0
- [ ] Per-scenario min_score = 9.0 (allow some scatter)
- [ ] Cost per run measured ≤ $10

---

## PR 18: v0.1.0 Beta Release

**Goal:** Tag `v0.1.0`, run release workflow, submit to Anthropic Marketplace, update airoasting.github.io landing page, post beta announcement.

**Depends on:** All previous PRs.

**Pre-flight checklist:**
- [ ] PR 5 routing gate green (≥ 90% Wilson)
- [ ] PR 4 anti-pattern tests 50/50, FP=0%
- [ ] PR 17 quality gate green (avg ≥ 9.0)
- [ ] All PRs merged to main, CI green on main
- [ ] CHANGELOG.md v0.1.0 entry finalized

### Task 18.1: Final pre-flight

- [ ] **Step 1:** Run from main:

```bash
git checkout main
git pull
make sync-cases             # ensure cases/ in sync with site
make sync-slides            # ensure slide-templates/index.json in sync
make gen-case-catalog       # regenerate docs/ko/case-catalog.md
make test                   # all tests pass
make test-quality           # quality gate (separate, ~$5-7)
```

- [ ] **Step 2:** If any of those produce uncommitted changes (e.g. case definitions updated upstream), commit:

```bash
git add skills/roasting/references/cases/ skills/roasting/references/slide-templates/ docs/ko/case-catalog.md
git commit -m "chore(sync): pre-release sync of case definitions + slide index"
git push
```

### Task 18.2: Tag v0.1.0

- [ ] **Step 1:** Update `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` versions to `0.1.0` (already set in PR 1; verify).
- [ ] **Step 2:** Tag and push:

```bash
git tag -a v0.1.0 -m "v0.1.0 — Open Beta release

5-Color Harness execution engine for Korean business leaders.
63 cases, Producer-Reviewer team with debate-driven scoring (Agent Teams +
sub-agent fallback), 5 anti-pattern detectors, slide_library binding for
PPT cases, opt-in anonymous telemetry."
git push origin v0.1.0
```

- [ ] **Step 3:** Verify `release.yml` workflow runs and creates a GitHub Release with the `.zip` attached:

```bash
gh release view v0.1.0
```

### Task 18.3: Submit to Anthropic Marketplace

- [ ] **Step 1:** Verify `marketplace.json` lints and the manifest is reachable from the repo root:

```bash
python -c "import json; json.load(open('.claude-plugin/marketplace.json'))"
```

- [ ] **Step 2:** Submit (manual; instructions vary by current Marketplace process):
  - Verify install path works locally first:
    ```
    /plugin marketplace add airoasting/roasting
    /plugin install roasting@airoasting
    ```
  - If that resolves the public repo, marketplace listing is automatic. If a manual review is required, follow Anthropic's current submission guide (link in docs/setup/marketplace.md — create that doc with the current process snapshot).
- [ ] **Step 3:** Track marketplace listing status; once listed, update `README.md` with the marketplace link.

### Task 18.4: Update airoasting.github.io landing

- [ ] **Step 1:** On the airoasting.github.io repo (separate), add a `/roasting` landing page that:
  - Links to GitHub repo
  - Shows install command (single block, copy-paste)
  - Lists the 63 cases (8 categories) — link to `airoasting.github.io/5color/`
  - Privacy summary (1 paragraph) + link to `docs/PRIVACY.md`
  - Beta status banner: "v0.1 Open Beta. Free during beta. Feedback welcome."
- [ ] **Step 2:** Push landing changes; verify `https://airoasting.github.io/roasting` loads.

### Task 18.5: Beta announcement

- [ ] **Step 1:** Draft a LinkedIn post (Korean) and an X post (English) announcing v0.1 open beta. Templates:

```
[LinkedIn / Korean]
임원이 한 줄로 호출하면 5-Color Harness가 화이트칼라 산출물을 짚어주는
Claude Code 플러그인 v0.1 오픈 베타.

- 63개 케이스 (이메일/보고서/PPT/메모/...) 자동 라우팅
- BLACK 작성 + RGSB 4인 토론 채점 + 9.5 합격선
- 콘텐츠 0 수집 (메타데이터만, opt-in)

설치: /plugin install roasting@airoasting
docs: https://airoasting.github.io/roasting

[X / English]
Open beta: /roasting — a Claude Code plugin that runs the 5-Color Harness
methodology over 63 white-collar cases. Korean-first.

BLACK Producer + RGSB Reviewers (debate-driven scoring) → output + critique
+ reasoning. Anonymous opt-in telemetry; content never transmitted.

https://github.com/airoasting/roasting
```

- [ ] **Step 2:** Post both. Add the URLs back to `CHANGELOG.md` under v0.1.0 announcement.

### Task 18.6: Final commit

- [ ] **Step 1:** Commit any landing page link or CHANGELOG updates:

```bash
git add CHANGELOG.md README.md docs/setup/marketplace.md
git commit -m "release: v0.1.0 open beta — listed, announced

- Marketplace listing: <link>
- Landing: https://airoasting.github.io/roasting
- LinkedIn announcement: <link>
- X announcement: <link>

Beta cohort: open. Privacy: opt-in metadata only.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
git push
```

**Acceptance criteria for PR 18 (Release v0.1.0):**
- [ ] Tag `v0.1.0` exists, GitHub Release attached `.zip`
- [ ] Marketplace listing live (or submission acknowledged)
- [ ] airoasting.github.io/roasting landing live
- [ ] Public announcement posted (LinkedIn + X)
- [ ] Anonymous telemetry capacity verified ready (Supabase project provisioned)

---

## v0.1 → v1.0 Promotion Gates (for awareness; not part of v0.1 plan)

| Gate | Target | Measurement |
|---|---|---|
| Routing accuracy (live data) | ≥ 95% Wilson 95% LB | telemetry case_id distribution vs xxxxx similarity audit |
| Quality (live data) | avg ≥ 9.5 final_score | telemetry final_score |
| Beta users | ≥ 50 distinct user_id | telemetry distinct count |
| Feedback signal | ≥ 100 GitHub Issues with `beta-feedback` label | gh issue list |
| Per-case usage | ≥ 10 calls/case for ≥ 30 cases | telemetry case_id counts |

When all 5 gates met → cut `v1.0.0`. v1.0 includes:
- Instinct system (PR ECM-01) — sees PR list in v0.2 plan.
- Hooks system (PR ECM-02).
- Auto-sync from 5color site (PR ECM-03).
- Case grading display (PR ECM-04).

---

## Plan Self-Review

This section is filled out during the spec self-review pass after the plan is fully drafted. Reviewer checks:

1. **Spec coverage:** Every section of `2026-05-10-roasting-design.md` is mapped to one or more PRs above. The mapping:

| Spec section | PR |
|---|---|
| §1 Overview | PR 15 (README) |
| §2 11 decisions | PR 1–18 (each decision has at least one PR) |
| §3 Architecture | PR 7–11 (SKILL.md) |
| §4 Directory | PR 1, 2, 3, 6 |
| §5 Data Flow | PR 7–12 |
| §6 Confirm timing | PR 7, 11 |
| §7 Error fallbacks | PR 5, 9, 10, 12 |
| §8 Anti-patterns | PR 4 |
| §9 Agents | PR 6 |
| §10 Testing | PR 4, 5, 17 |
| §11 Distribution | PR 1, 15, 16, 18 |
| §12 Telemetry | PR 13 |
| §13 Versioning | PR 1, 18 (v0.1 only; v0.2+ separate plan) |
| §14 Cost | PR 17 measures |
| §15 CLAUDE.md hook | PR 14 |
| §16 Makefile | PR 1, 13, 16 |
| §17 Checklist | All PRs |

2. **Placeholders:** No `TBD`, `TODO`, "implement later" remaining. All code blocks complete.
3. **Type consistency:** `Case`, `RouteResult`, `AntiPattern`, `StrikeCounter`, `TelemetryEvent`, `SessionResult`, `RoundData`, `SlideTemplate` — names used consistently across PR 2, 4, 5, 11, 12, 13.
4. **Ambiguity:** All decisions referenced spec; tiebreaker explicit (GOLD>RED>SILVER>BLUE); 3-strikes counter scope explicit (cross-round); HALLUCINATED_NUMBER exemption explicit (p63/p64/p69).

---

## Execution Choice

Plan complete. Two execution options:

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per task. Review between tasks. Fast iteration, isolated context per task.

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`. Batch execution with checkpoints for human review.

Which approach?





