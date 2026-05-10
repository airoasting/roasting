"""/roasting --feedback handler. Builds a prefilled GitHub Issue URL.

Includes session_id (anonymous UUID) so author can correlate with telemetry,
but no content.
"""
from __future__ import annotations

import urllib.parse

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
