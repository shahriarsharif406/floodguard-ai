from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from .models import Actor, Analysis, Status
from .priority import priority as prio
from .redact import redact

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
  mode TEXT NOT NULL CHECK(mode IN ('live','replay')), is_simulated INTEGER NOT NULL DEFAULT 0,
  raw_text TEXT NOT NULL, redacted_text TEXT NOT NULL, redaction_counts TEXT NOT NULL, language TEXT NOT NULL,
  lat REAL NOT NULL, lon REAL NOT NULL, lat_pub REAL NOT NULL, lon_pub REAL NOT NULL,
  district TEXT, upazila TEXT, location_source TEXT, photo BLOB, photo_ahash TEXT,
  consent INTEGER NOT NULL CHECK(consent=1),
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','under_review','verified','rejected')),
  priority INTEGER NOT NULL DEFAULT 0, user_during_replay INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS analyses (
  report_id INTEGER PRIMARY KEY REFERENCES reports(id), category TEXT NOT NULL, urgency TEXT NOT NULL,
  needs TEXT NOT NULL, people_affected INTEGER, summary_en TEXT NOT NULL, summary_bn TEXT, location_hint TEXT,
  confidence REAL NOT NULL, engine TEXT NOT NULL, model TEXT, created_at TEXT NOT NULL, note TEXT);
CREATE TABLE IF NOT EXISTS links (report_id INTEGER, other_id INTEGER,
  kind TEXT CHECK(kind IN ('duplicate','corroborates','same_photo')), score REAL, distance_m REAL, hours REAL,
  PRIMARY KEY(report_id, other_id, kind));
CREATE TABLE IF NOT EXISTS evidence (
  report_id INTEGER PRIMARY KEY, sat_class TEXT, flood_frac REAL, nodata_frac REAL, sat_date TEXT, river_class TEXT,
  q REAL, clim_median REAL, ratio REAL, pctl REAL, badge TEXT NOT NULL, sentence TEXT NOT NULL, source TEXT,
  fetched_at TEXT);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, report_id INTEGER, action TEXT NOT NULL,
  from_status TEXT, to_status TEXT, actor TEXT NOT NULL, actor_label TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS shelters (id INTEGER PRIMARY KEY, name TEXT, name_bn TEXT, lat REAL, lon REAL,
  district TEXT, is_demo INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS usage_counters (day TEXT PRIMARY KEY, live_calls INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS ai_cache (key TEXT PRIMARY KEY, payload TEXT NOT NULL, model TEXT, created_at TEXT);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def seed_if_empty(conn: sqlite3.Connection) -> None:
    from .replay import seed
    seed(conn)


def audit(conn, report_id, action, actor: Actor, actor_label="", note="", from_status=None, to_status=None):
    safe_note, _ = redact(note or "")
    conn.execute("INSERT INTO audit_log(ts,report_id,action,from_status,to_status,actor,actor_label,note) "
                 "VALUES(?,?,?,?,?,?,?,?)",
                 (now_iso(), report_id, action, from_status, to_status, actor.value, actor_label, safe_note))


def insert_report(conn, r: dict) -> int:
    cur = conn.execute(
        "INSERT INTO reports(created_at,mode,is_simulated,raw_text,redacted_text,redaction_counts,language,lat,lon,"
        "lat_pub,lon_pub,district,upazila,location_source,photo,photo_ahash,consent,status,priority,user_during_replay)"
        " VALUES(:created_at,:mode,:is_simulated,:raw_text,:redacted_text,:redaction_counts,:language,:lat,:lon,"
        ":lat_pub,:lon_pub,:district,:upazila,:location_source,:photo,:photo_ahash,:consent,:status,:priority,"
        ":user_during_replay)",
        {"upazila": None, "photo": None, "photo_ahash": None, "status": "pending", "priority": 0,
         "user_during_replay": 0, "is_simulated": 0, "consent": 1, **r})
    conn.commit()
    return int(cur.lastrowid)


def insert_analysis(conn, report_id: int, a: Analysis) -> None:
    conn.execute("INSERT OR REPLACE INTO analyses VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 (report_id, a.category.value, a.urgency.value, json.dumps(a.needs), a.people_affected, a.summary_en,
                  a.summary_bn, a.location_hint, a.confidence, a.engine.value, a.model, a.created_at or now_iso(),
                  a.note))
    conn.commit()


def save_links(conn, report_id: int, matches: list[dict]) -> None:
    for m in matches:
        conn.execute("INSERT OR REPLACE INTO links VALUES(?,?,?,?,?,?)",
                     (report_id, m["other_id"], m["kind"], m["score"], m["distance_m"], m["hours"]))
    conn.commit()


def save_evidence(conn, report_id: int, ev: dict) -> None:
    conn.execute("INSERT OR REPLACE INTO evidence VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 (report_id, ev.get("sat_class"), ev.get("flood_frac"), ev.get("nodata_frac"), ev.get("sat_date"),
                  ev.get("river_class"), ev.get("q"), ev.get("clim_median"), ev.get("ratio"), ev.get("pctl"),
                  ev["badge"], ev["sentence"], ev.get("source"), now_iso()))
    conn.commit()


def n_corroborations(conn, report_id: int) -> int:
    row = conn.execute("SELECT COUNT(*) c FROM links WHERE (report_id=? OR other_id=?) AND kind IN "
                       "('corroborates','duplicate')", (report_id, report_id)).fetchone()
    return int(row["c"])


def recompute_priority(conn, report_id: int) -> int:
    row = conn.execute("SELECT r.status, a.urgency, e.badge FROM reports r JOIN analyses a ON a.report_id=r.id "
                       "LEFT JOIN evidence e ON e.report_id=r.id WHERE r.id=?", (report_id,)).fetchone()
    if not row:
        return 0
    p = prio(row["urgency"], n_corroborations(conn, report_id), row["badge"] or "unavailable", row["status"])
    conn.execute("UPDATE reports SET priority=? WHERE id=?", (p, report_id))
    conn.commit()
    return p


def set_status(conn, report_id: int, new: Status, actor: Actor, note: str, actor_label: str) -> None:
    if actor != Actor.HUMAN and new in (Status.VERIFIED, Status.REJECTED):
        raise PermissionError("Only a human moderator can verify or reject a report.")
    row = conn.execute("SELECT status FROM reports WHERE id=?", (report_id,)).fetchone()
    old = row["status"] if row else None
    conn.execute("UPDATE reports SET status=? WHERE id=?", (new.value, report_id))
    audit(conn, report_id, "status_change", actor, actor_label, note, old, new.value)
    conn.commit()
    recompute_priority(conn, report_id)


_LIST_SQL = """
SELECT r.id, r.created_at, r.mode, r.is_simulated, r.redacted_text, r.language, r.lat, r.lon, r.lat_pub, r.lon_pub,
       r.district, r.upazila, r.status, r.priority, r.user_during_replay, (r.photo IS NOT NULL) AS has_photo,
       r.photo_ahash, a.category, a.urgency, a.needs, a.people_affected, a.summary_en, a.summary_bn, a.location_hint,
       a.confidence, a.engine, a.model, a.created_at AS analysed_at, a.note AS analysis_note,
       e.badge, e.sentence AS ev_sentence, e.sat_class, e.river_class, e.ratio, e.pctl,
       (SELECT COUNT(*) FROM links l WHERE (l.report_id=r.id OR l.other_id=r.id) AND l.kind IN
        ('corroborates','duplicate')) AS n_links,
       (SELECT COUNT(*) FROM links l WHERE l.report_id=r.id AND l.kind='same_photo') AS photo_match
FROM reports r JOIN analyses a ON a.report_id=r.id LEFT JOIN evidence e ON e.report_id=r.id
WHERE r.mode=?"""


def list_reports(conn, *, mode: str, until: str | None = None) -> list[dict]:
    sql, args = _LIST_SQL, [mode]
    if until:
        sql += " AND r.created_at<=?"
        args.append(until)
    sql += " ORDER BY r.priority DESC, r.created_at ASC"
    rows = [dict(x) for x in conn.execute(sql, args).fetchall()]
    for r in rows:
        r["needs"] = json.loads(r["needs"] or "[]")
    return rows


def get_report(conn, report_id: int) -> dict | None:
    row = conn.execute(_LIST_SQL.replace("WHERE r.mode=?", "WHERE r.id=?"), (report_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["needs"] = json.loads(d["needs"] or "[]")
    return d


def get_raw(conn, report_id: int) -> dict:
    return dict(conn.execute("SELECT raw_text, redaction_counts, photo, lat, lon FROM reports WHERE id=?",
                             (report_id,)).fetchone())


def get_links(conn, report_id: int) -> list[dict]:
    rows = conn.execute("SELECT report_id, other_id, kind, score, distance_m, hours FROM links "
                        "WHERE report_id=? OR other_id=?", (report_id, report_id)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        if d["other_id"] == report_id:      # show from this report's perspective
            d["other_id"] = d["report_id"]
        out.append(d)
    return out


def get_audit(conn, report_id: int) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM audit_log WHERE report_id=? ORDER BY id", (report_id,))]


def get_shelters(conn) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM shelters")]


def candidates(conn, mode: str) -> list[dict]:
    return [dict(r) for r in conn.execute(
        "SELECT r.id, r.created_at, r.lat, r.lon, r.redacted_text, r.photo_ahash, a.category FROM reports r "
        "JOIN analyses a ON a.report_id=r.id WHERE r.mode=?", (mode,))]
