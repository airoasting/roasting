"""Tiny Haiku-backed LLM judge wrapper. Mockable for tests via dependency injection."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol

import requests
from anthropic import Anthropic


HAIKU_MODEL = "claude-haiku-4-5-20251001"
_ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"


def _extract_json(text: str) -> dict[str, Any]:
    """Extract first JSON object from model output, handling ```json fences and trailing text."""
    t = text.strip()
    # Strip markdown code fences.
    if t.startswith("```"):
        t = t.strip("`").strip()
        if t.startswith("json"):
            t = t[4:].strip()
    # Find the first { ... } block in case there's leading/trailing prose.
    start = t.find("{")
    if start == -1:
        return json.loads(t)  # type: ignore[no-any-return]  # will raise JSONDecodeError with clear message
    # Walk to find matching closing brace.
    depth = 0
    for i, ch in enumerate(t[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(t[start:i + 1])  # type: ignore[no-any-return]
    return json.loads(t[start:])  # type: ignore[no-any-return]  # fallback — let json module raise


class JudgeFn(Protocol):
    def __call__(self, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]: ...


def _call_via_bearer(token: str, system: str, user: str, model: str, max_tokens: int,
                     retries: int = 3) -> str:
    """Call Anthropic Messages API using a Bearer OAuth token (Claude Code auth).

    Retries up to `retries` times on transient network errors (timeout, connection).
    """
    import time
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.post(
                _ANTHROPIC_MESSAGES_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                },
                timeout=90,
            )
            resp.raise_for_status()
            data = resp.json()
            return "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            last_exc = exc
            wait = 2 ** attempt  # exponential back-off: 1s, 2s, 4s
            time.sleep(wait)
    raise RuntimeError(f"All {retries} attempts failed") from last_exc


@dataclass
class HaikuJudge:
    """Real implementation backed by Anthropic Haiku.

    Tests should pass a fake JudgeFn instead of using this.
    Supports ANTHROPIC_API_KEY (SDK) or CLAUDE_CODE_OAUTH_TOKEN (Bearer).
    """
    client: Anthropic | None = None
    _oauth_token: str | None = None

    def __post_init__(self) -> None:
        if self.client is None and self._oauth_token is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
            if api_key:
                self.client = Anthropic(api_key=api_key)
            elif oauth_token:
                # Claude Code OAuth token — use raw Bearer HTTP requests.
                self._oauth_token = oauth_token
            else:
                # Fall back to SDK default (will raise AuthenticationError at call time).
                self.client = Anthropic()

    def __call__(self, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]:
        full_system = system + "\n\nReturn ONLY a JSON object matching this schema: " + json.dumps(schema)
        if self._oauth_token is not None:
            text = _call_via_bearer(self._oauth_token, full_system, user, HAIKU_MODEL, 512)
        else:
            assert self.client is not None
            msg = self.client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=512,
                system=full_system,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in msg.content if b.type == "text")
        return _extract_json(text)
