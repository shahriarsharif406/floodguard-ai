"""Three-tier orchestrator: pre-computed cache → limited live Gemini → rule-based fallback."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .config import Settings, get_settings
from .gemini import (GeminiUnavailable, bump_daily, call_gemini, caps_allow, payload_to_analysis)
from .models import Analysis, Engine
from .rules import analyze_rules

CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "gemini_cache.json"


def cache_key(redacted_text: str, model: str) -> str:
    return hashlib.sha256((model + "|" + redacted_text.strip().lower()).encode("utf-8")).hexdigest()


def load_precomputed() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except ValueError:
            return {}
    return {}


def analyze(redacted_text: str, district: str | None, *, allow_live: bool, conn=None, session_calls: int = 0,
            settings: Settings | None = None) -> tuple[Analysis, str, bool]:
    """Returns (analysis, note, used_live_call)."""
    s = settings or get_settings()
    pre = load_precomputed()
    model = (pre.get("meta") or {}).get("model") or s.gemini_model
    for m in {model, s.gemini_model}:
        key = cache_key(redacted_text, m)
        item = (pre.get("items") or {}).get(key)
        if item:
            return payload_to_analysis(item, Engine.PRE, m, (pre.get("meta") or {}).get("generated_on", "")), "", False
        if conn is not None:
            row = conn.execute("SELECT payload, model, created_at FROM ai_cache WHERE key=?", (key,)).fetchone()
            if row:
                return payload_to_analysis(json.loads(row["payload"]), Engine.LIVE, row["model"], row["created_at"]), \
                    "cached live result", False
    reason = ""
    if allow_live and conn is not None:
        ok, reason = caps_allow(session_calls, conn, s)
        if ok:
            bump_daily(conn)
            try:
                a = call_gemini(redacted_text, district, s)
                conn.execute("INSERT OR REPLACE INTO ai_cache VALUES(?,?,?,?)",
                             (cache_key(redacted_text, s.gemini_model),
                              json.dumps({"category": a.category.value, "urgency": a.urgency.value, "needs": a.needs,
                                          "people_affected": a.people_affected, "summary_en": a.summary_en,
                                          "summary_bn": a.summary_bn, "location_hint": a.location_hint,
                                          "language": a.language, "confidence": a.confidence}),
                              s.gemini_model, a.created_at))
                conn.commit()
                return a, "", True
            except GeminiUnavailable as e:
                reason = str(e)
    elif not allow_live:
        reason = "live AI not requested"
    a = analyze_rules(redacted_text, district)
    a.note = reason
    return a, reason, False
