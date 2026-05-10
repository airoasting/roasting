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
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def _save_config(cfg: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def is_enabled() -> bool:
    return _load_config().get("telemetry", False)  # type: ignore[no-any-return]


def get_or_create_user_id() -> str:
    cfg = _load_config()
    if "user_id" not in cfg:
        cfg["user_id"] = str(uuid.uuid4())
        _save_config(cfg)
    return cfg["user_id"]  # type: ignore[no-any-return]


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
