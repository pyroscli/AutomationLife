from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from typing import Any

from daily.config import load_env
from daily.store import DayLog

WEBHOOK_ENV = "ACTIVEPIECES_WEBHOOK_URL"
# Cloudflare in front of hooks.activepieces.com blocks Python-urllib's default signature.
_BROWSER_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
}


class SheetSyncError(RuntimeError):
    pass


def resolve_webhook_url() -> str:
    env = {**load_env(), **os.environ}
    return env.get(WEBHOOK_ENV, "").strip()


def day_payload(log: DayLog) -> dict[str, Any]:
    """Flat JSON that Activepieces can map onto one Google Sheet row."""
    return {
        "event": "day_logged",
        "date": log.date,
        "calories": "" if log.calories is None else log.calories,
        "steps": "" if log.steps is None else log.steps,
        "pages": "" if log.pages is None else log.pages,
        "book": log.book or "",
        "med_morning": "yes" if log.meds.get("morning") else "no",
        "med_night": "yes" if log.meds.get("night") else "no",
        "notes": log.notes or "",
        "updated_at": log.updated_at,
    }


def post_webhook(url: str, payload: dict[str, Any], *, timeout: float = 20) -> None:
    body = json.dumps(payload).encode("utf-8")
    try:
        _post_urllib(url, body, timeout=timeout)
    except SheetSyncError as exc:
        if "1010" not in str(exc) and "browser_signature" not in str(exc):
            raise
        _post_curl(url, body, timeout=timeout)


def _post_urllib(url: str, body: bytes, *, timeout: float) -> None:
    request = urllib.request.Request(url, data=body, method="POST", headers=_BROWSER_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read()
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        hint = ""
        if exc.code == 404:
            hint = " Publish the Activepieces flow, then use the Catch Webhook Live URL (not /test)."
        raise SheetSyncError(f"Activepieces returned HTTP {exc.code}: {text[:400]}{hint}") from exc
    except urllib.error.URLError as exc:
        raise SheetSyncError(f"Could not reach Activepieces: {exc.reason}") from exc


def _post_curl(url: str, body: bytes, *, timeout: float) -> None:
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "-f",
            "-X",
            "POST",
            url,
            "-H",
            "Content-Type: application/json",
            "-H",
            f"User-Agent: {_BROWSER_HEADERS['User-Agent']}",
            "--max-time",
            str(int(timeout)),
            "--data-binary",
            "@-",
        ],
        input=body,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout).decode("utf-8", errors="replace")
        raise SheetSyncError(f"Activepieces webhook failed: {err[:400]}")


def sync_day(log: DayLog, *, url: str | None = None) -> str:
    """POST one day to Activepieces. Returns the webhook URL used."""
    webhook = url if url is not None else resolve_webhook_url()
    if not webhook:
        raise SheetSyncError(
            f"{WEBHOOK_ENV} is not set. Add the Catch Webhook URL from Activepieces to .env."
        )
    post_webhook(webhook, day_payload(log))
    return webhook
