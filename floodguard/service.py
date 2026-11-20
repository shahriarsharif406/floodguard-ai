"""Orchestrates report submission and evidence refresh (used by UI and tests)."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from . import db
from .analysis import analyze
from .dedupe import find_matches
from .evidence import build_evidence
from .geo import blur
from .imaging import validate_and_clean
from .models import Actor
from .redact import redact


def submit_report(conn, *, text: str, district: str | None, lat: float, lon: float, location_source: str,
                  photo: tuple[bytes, str] | None, mode: str, replay_date: str | None, allow_live: bool,
                  session_calls: int = 0, live_evidence: bool = True) -> dict:
    red, counts = redact(text)
    a, note, used_live = analyze(red, district, allow_live=allow_live, conn=conn, session_calls=session_calls)
    pbytes, ah = (validate_and_clean(*photo) if photo else (None, None))
    now = datetime.now(timezone.utc)
    if mode == "replay" and replay_date:
        created = f"{replay_date}T{now.strftime('%H:%M')}"
    else:
        created = now.strftime("%Y-%m-%dT%H:%M")
    lat_p, lon_p = blur(lat, lon)
    rid = db.insert_report(conn, {
        "created_at": created, "mode": mode, "is_simulated": 0, "raw_text": text, "redacted_text": red,
        "redaction_counts": json.dumps(counts), "language": a.language, "lat": lat, "lon": lon, "lat_pub": lat_p,
        "lon_pub": lon_p, "district": district, "location_source": location_source, "photo": pbytes,
        "photo_ahash": ah, "user_during_replay": 1 if mode == "replay" else 0})
    db.insert_analysis(conn, rid, a)
    db.audit(conn, rid, "created", Actor.SYSTEM, "submit", "")
    db.audit(conn, rid, "ai_analyzed", Actor.AI, a.engine.value, a.summary_en)
    cands = db.candidates(conn, mode)
    me = next(c for c in cands if c["id"] == rid)
    me["category"] = a.category.value
    matches = find_matches(me, cands)
    db.save_links(conn, rid, matches)
    ev = build_evidence({"lat": lat, "lon": lon, "created_at": created}, live=live_evidence)
    db.save_evidence(conn, rid, ev)
    for m in matches:
        db.recompute_priority(conn, m["other_id"])
    db.recompute_priority(conn, rid)
    return {"id": rid, "analysis": a, "note": note, "used_live": used_live, "matches": matches, "evidence": ev,
            "redacted": red, "counts": counts}


def refresh_evidence(conn, report_id: int) -> dict:
    r = db.get_report(conn, report_id)
    ev = build_evidence({"lat": r["lat"], "lon": r["lon"], "created_at": r["created_at"]}, live=True)
    db.save_evidence(conn, report_id, ev)
    db.audit(conn, report_id, "evidence_refreshed", Actor.SYSTEM, "evidence", ev["badge"])
    db.recompute_priority(conn, report_id)
    return ev
