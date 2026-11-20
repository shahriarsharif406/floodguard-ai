"""Event Replay: Sylhet-Sunamganj, June 2022. Real satellite/river data, SIMULATED community reports."""
from __future__ import annotations
import json
from pathlib import Path
from . import db
from .analysis import analyze
from .dedupe import find_matches
from .evidence import build_evidence
from .geo import DATA, blur
from .imaging import validate_and_clean
from .models import Actor
from .redact import redact

REPLAY_DATES = [f"2022-06-{d:02d}" for d in range(14, 26)]
DEFAULT_DATE = "2022-06-20"
BANNER = ("EVENT REPLAY · June 2022 Sylhet–Sunamganj floods · Satellite & river data: REAL (NASA, GloFAS) · "
          "Community reports: SIMULATED for demonstration")


def seed(conn) -> None:
    if conn.execute("SELECT COUNT(*) c FROM reports WHERE mode='replay'").fetchone()["c"] > 0:
        return
    if conn.execute("SELECT COUNT(*) c FROM shelters").fetchone()["c"] == 0:
        for s in json.loads((DATA / "shelters_demo.json").read_text(encoding="utf-8")):
            conn.execute("INSERT INTO shelters VALUES(?,?,?,?,?,?,?)",
                         (s["id"], s["name"], s["name_bn"], s["lat"], s["lon"], s["district"], 1))
        conn.commit()
    rows = json.loads((DATA / "replay_sylhet2022.json").read_text(encoding="utf-8"))
    for r in rows:
        red, counts = redact(r["text"])
        a, note, _ = analyze(red, r["district"], allow_live=False, conn=conn)
        photo, ah = None, None
        if r.get("photo"):
            p = DATA / r["photo"]
            photo, ah = validate_and_clean(p.read_bytes(), p.name)
        lat_p, lon_p = blur(r["lat"], r["lon"])
        rid = db.insert_report(conn, {
            "created_at": r["created_at"], "mode": "replay", "is_simulated": 1, "raw_text": r["text"],
            "redacted_text": red, "redaction_counts": json.dumps(counts), "language": a.language,
            "lat": r["lat"], "lon": r["lon"], "lat_pub": lat_p, "lon_pub": lon_p, "district": r["district"],
            "upazila": r["upazila"], "location_source": "district", "photo": photo, "photo_ahash": ah,
            "status": "pending"})
        db.insert_analysis(conn, rid, a)
        cands = db.candidates(conn, "replay")
        me = next(c for c in cands if c["id"] == rid)
        me["category"] = a.category.value
        db.save_links(conn, rid, find_matches(me, cands))
        ev = build_evidence({"lat": lat_p, "lon": lon_p, "created_at": r["created_at"]}, live=False,
                            cache_key=f"{r['id']}|{r['created_at'][:10]}")
        db.save_evidence(conn, rid, ev)
        db.audit(conn, rid, "created", Actor.SYSTEM, "seed", "SIMULATED seed report")
        db.audit(conn, rid, "ai_analyzed", Actor.AI, a.engine.value, a.summary_en)
        if r["status"] != "pending":
            db.set_status(conn, rid, __import__("floodguard.models", fromlist=["Status"]).Status(r["status"]),
                          Actor.HUMAN, r.get("mod_note") or "Seeded moderator decision (simulated)", "seed")
    for rid in [x["id"] for x in conn.execute("SELECT id FROM reports")]:
        db.recompute_priority(conn, rid)
