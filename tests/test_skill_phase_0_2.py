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
