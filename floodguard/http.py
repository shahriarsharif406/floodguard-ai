"""Single network wrapper. Never raises; returns (status, payload, error). Mock point for tests."""
from __future__ import annotations
import os
import requests


def _offline() -> bool:
    return os.environ.get("FG_OFFLINE") == "1"


def http_get(url: str, params: dict | None = None, timeout: float = 10, as_bytes: bool = False,
             headers: dict | None = None):
    if _offline():
        return 0, None, "offline"
    try:
        r = requests.get(url, params=params, timeout=timeout, headers=headers)
        if r.status_code != 200:
            return r.status_code, None, f"http {r.status_code}"
        return 200, (r.content if as_bytes else r.json()), None
    except Exception as e:  # noqa: BLE001
        return 0, None, type(e).__name__


def http_post(url: str, json_body: dict, headers: dict | None = None, timeout: float = 8):
    if _offline():
        return 0, None, "offline"
    try:
        r = requests.post(url, json=json_body, headers=headers, timeout=timeout)
        if r.status_code != 200:
            return r.status_code, None, f"http {r.status_code}"
        return 200, r.json(), None
    except Exception as e:  # noqa: BLE001
        return 0, None, type(e).__name__
