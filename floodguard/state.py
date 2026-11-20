"""Streamlit session/state helpers shared by all pages."""
from __future__ import annotations
from datetime import date, timedelta
import streamlit as st
from . import db
from .config import get_settings
from .replay import DEFAULT_DATE, REPLAY_DATES


import os
import threading
from concurrent.futures import ThreadPoolExecutor

_warm: dict = {"started": False, "results": {}, "applied": set()}


def _warm_worker(rows):
    from .evidence import build_evidence

    def one(r):
        try:
            _warm["results"][r["id"]] = build_evidence(
                {"lat": r["lat_pub"], "lon": r["lon_pub"], "created_at": r["created_at"]}, live=True)
        except Exception:  # noqa: BLE001
            pass
    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(one, rows))


def warm_evidence(c) -> None:
    """Replay evidence (real NASA/GloFAS) is fetched once in the background if not cached in data/."""
    if os.environ.get("FG_OFFLINE") == "1":
        return
    if not _warm["started"]:
        rows = [dict(r) for r in c.execute(
            "SELECT r.id, r.lat_pub, r.lon_pub, r.created_at FROM reports r JOIN evidence e ON e.report_id=r.id "
            "WHERE r.mode='replay' AND e.badge='unavailable'")]
        _warm["started"] = True
        if rows:
            threading.Thread(target=_warm_worker, args=(rows,), daemon=True).start()
    for rid, ev in list(_warm["results"].items()):
        if rid not in _warm["applied"]:
            if ev["badge"] != "unavailable":
                db.save_evidence(c, rid, ev)
                db.recompute_priority(c, rid)
            _warm["applied"].add(rid)


@st.cache_resource
def conn():
    s = get_settings()
    c = db.connect(s.db_path)
    db.init_db(c)
    db.seed_if_empty(c)
    return c


def init() -> None:
    s = get_settings()
    st.session_state.setdefault("mode_label", "Replay 2022" if s.app_mode_default == "replay" else "Live (today)")
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
    return [(t - timedelta(days=i)).isoformat() for i in range(15, 0, -1)]


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
    st.switch_page("pages/3_report_detail.py")
