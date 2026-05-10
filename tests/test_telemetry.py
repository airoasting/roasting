from __future__ import annotations

import json
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
