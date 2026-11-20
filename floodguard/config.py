from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_model: str
    live_ai_session_cap: int
    live_ai_daily_cap: int
    gemini_timeout_s: float
    moderator_pin: str
    db_path: str
    app_mode_default: str


def _secret(name: str) -> str | None:
    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.environ.get(name)


def get_settings() -> Settings:
    on_cloud = os.path.exists("/mount/src") or os.environ.get("HOME") == "/home/appuser"
    default_db = "/tmp/floodguard.db" if on_cloud else "./floodguard.db"
    return Settings(
        gemini_api_key=_secret("GEMINI_API_KEY") or None,
        gemini_model=_secret("GEMINI_MODEL") or "gemini-2.5-flash",
        live_ai_session_cap=int(_secret("LIVE_AI_SESSION_CAP") or 3),
        live_ai_daily_cap=int(_secret("LIVE_AI_DAILY_CAP") or 150),
        gemini_timeout_s=float(_secret("GEMINI_TIMEOUT_S") or 8),
        moderator_pin=_secret("MODERATOR_PIN") or "2468",
        db_path=_secret("DB_PATH") or default_db,
        app_mode_default=_secret("APP_MODE_DEFAULT") or "replay",
    )
