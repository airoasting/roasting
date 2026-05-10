from __future__ import annotations


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
