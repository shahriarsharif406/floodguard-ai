"""Streamlit session/state helpers shared by all pages."""
from __future__ import annotations
from datetime import date, timedelta
import streamlit as st
from . import db
from .config import get_settings
from .replay import DEFAULT_DATE, REPLAY_DATES


@st.cache_resource
def conn():
    s = get_settings()
    c = db.connect(s.db_path)
    db.init_db(c)
    db.seed_if_empty(c)
    return c


def init() -> None:
    s = get_settings()
    st.session_state.setdefault("mode_label", "Replay 2022" if s.app_mode_default == "replay" else "Live")
    st.session_state.setdefault("replay_date", DEFAULT_DATE)
    st.session_state.setdefault("live_calls", 0)
    st.session_state.setdefault("playing", False)
    st.session_state.setdefault("submit_times", [])


def mode() -> str:
    return "replay" if st.session_state.get("mode_label", "Replay 2022").startswith("Replay") else "live"


def dates() -> list[str]:
    if mode() == "replay":
        return REPLAY_DATES
    t = date.today()
    return [(t - timedelta(days=i)).isoformat() for i in range(14, -1, -1)]


def current_date() -> str:
    ds = dates()
    d = st.session_state.get("replay_date", DEFAULT_DATE)
    if d not in ds:
        d = ds[len(ds) // 2] if mode() == "replay" else ds[-1]
        st.session_state["replay_date"] = d
    return d


def until() -> str | None:
    return f"{current_date()}T23:59" if mode() == "replay" else None


def goto_detail(report_id: int) -> None:
    st.session_state["detail_id"] = report_id
    st.query_params["id"] = str(report_id)
    st.switch_page("pages/3_report_detail.py")
