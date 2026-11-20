from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from .config import Settings
from .http import http_post
from .models import ANALYSIS_JSON_SCHEMA, NEEDS, Analysis, Category, Engine, Urgency
from .redact import redact

SYSTEM_PROMPT = """You are a triage assistant for a community flood-reporting tool in Bangladesh. You receive ONE citizen flood report that may be in Bangla (বাংলা), English, or a mix, possibly with spelling errors or Banglish (Bangla in Latin letters). Personal data has already been replaced with tokens like [PHONE], [NAME], [EMAIL]; never try to reconstruct them.
Your job is to STRUCTURE the report, not to judge whether it is true. You never verify reports; a human moderator does.
Rules:
- Output ONLY JSON matching the provided schema.
- category: the single most important need. If anyone is trapped, on a roof, drowning or missing → "rescue_needed".
- urgency: critical = immediate risk to life (trapped people, drowning, missing person, injured with no access); high = vulnerable people (children, elderly, pregnant, sick) without food/water/shelter, or homes submerged; medium = property/infrastructure damage, roads cut, power out, rising water without direct life risk; low = general information or recovered situations.
- people_affected: an integer only if the text states or clearly implies a number (e.g. "5 families" → estimate 5 families × 5 = 25 and state "approx." in summary). Otherwise null.
- summary_en: one neutral English sentence, max 30 words, no speculation. summary_bn: the same in Bangla if the input was Bangla or mixed, else null.
- location_hint: a place name mentioned in the text (village/union/upazila), or null. Do not invent places.
- Do NOT give medical advice, do NOT predict floods, do NOT add facts not in the report.
- confidence: 0–1, how clearly the text supports your category and urgency."""

USER_TEMPLATE = 'District (approximate, user-selected): {district}\nReport text (redacted):\n"""{text}"""'


class GeminiUnavailable(Exception):
    pass


def build_prompt(redacted_text: str, district: str | None) -> dict:
    return {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": USER_TEMPLATE.format(
            district=district or "unknown", text=redacted_text)}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048, "responseMimeType": "application/json",
                             "responseSchema": ANALYSIS_JSON_SCHEMA},
    }


def validate_payload(obj: dict) -> dict:
    if not isinstance(obj, dict):
        raise ValueError("payload is not an object")
    cat = str(obj.get("category", "")).strip().lower()
    urg = str(obj.get("urgency", "")).strip().lower()
    if cat not in {c.value for c in Category}:
        raise ValueError(f"bad category {cat!r}")
    if urg not in {u.value for u in Urgency}:
        raise ValueError(f"bad urgency {urg!r}")
    needs: list[str] = []
    for n in obj.get("needs") or []:
        n = str(n).strip().lower()
        if n in NEEDS and n not in needs:
            needs.append(n)
    needs = needs[:6]
    pa = obj.get("people_affected")
    pa = pa if isinstance(pa, int) and not isinstance(pa, bool) and 0 <= pa <= 100000 else None
    se = str(obj.get("summary_en") or "").strip()
    if len(se) < 10:
        raise ValueError("summary_en too short")
    se = se[:240]
    sb = obj.get("summary_bn")
    sb = str(sb).strip()[:240] if sb else None
    lh = obj.get("location_hint")
    lh = redact(str(lh).strip()[:80])[0] if lh else None
    lang = str(obj.get("language", "en")).lower()
    lang = lang if lang in ("bn", "en", "mixed") else "en"
    try:
        conf = max(0.0, min(1.0, float(obj.get("confidence", 0.5))))
    except (TypeError, ValueError):
        conf = 0.5
    # any "status"/"verified" keys in the payload are deliberately ignored
    return {"category": cat, "urgency": urg, "needs": needs, "people_affected": pa, "summary_en": se,
            "summary_bn": sb, "location_hint": lh, "language": lang, "confidence": round(conf, 2)}


def payload_to_analysis(p: dict, engine: Engine, model: str | None, created: str = "") -> Analysis:
    return Analysis(category=Category(p["category"]), urgency=Urgency(p["urgency"]), needs=p["needs"],
                    people_affected=p["people_affected"], summary_en=p["summary_en"], summary_bn=p["summary_bn"],
                    location_hint=p["location_hint"], language=p["language"], confidence=p["confidence"],
                    engine=engine, model=model, created_at=created)


FALLBACK_MODELS = ("gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash", "gemini-3.1-flash-lite")
_WORKING: dict = {}   # remembers the (model, thinking-variant) that last worked


def model_chain(s: Settings) -> list[str]:
    out = [s.gemini_model]
    out += [m for m in FALLBACK_MODELS if m not in out]
    return out


def generate_content(s: Settings, body: dict, timeout: float):
    """POST to generateContent. Gemini 2.5 is closed to new keys, so try the configured model, then current
    fallbacks. Thinking is kept minimal (thinkingLevel), with a retry without thinkingConfig if rejected.
    Returns (status, data, err, model_used)."""
    hdr = {"x-goog-api-key": s.gemini_api_key}
    chain = model_chain(s)
    if _WORKING.get("model") in chain:
        chain.remove(_WORKING["model"]); chain.insert(0, _WORKING["model"])
    status, data, err = 0, None, "no model"
    for model in chain:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for think in ({"thinkingLevel": "minimal"}, {"thinkingLevel": "low"}, None):
            b = json.loads(json.dumps(body))
            if think:
                b["generationConfig"]["thinkingConfig"] = think
            status, data, err = http_post(url, b, headers=hdr, timeout=timeout)
            if status == 200 and data:
                _WORKING["model"] = model
                return status, data, err, model
            if status in (429,) or status >= 500 or status in (401, 403):
                return status, data, err, model     # not a model problem: stop here
            # 400/404: bad thinking value or model unavailable to this key -> next variant / next model
    return status, data, err, chain[-1]


def _text_of(data: dict) -> str:
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def call_gemini(redacted_text: str, district: str | None, s: Settings) -> Analysis:
    if not s.gemini_api_key:
        raise GeminiUnavailable("no API key")
    body = build_prompt(redacted_text, district)
    status, data, err, model = generate_content(s, body, s.gemini_timeout_s)
    if status in (429,) or status >= 500:
        raise GeminiUnavailable("rate-limited")
    if status != 200 or not data:
        raise GeminiUnavailable(err or "timeout")
    try:
        payload = validate_payload(json.loads(_text_of(data)))
    except (KeyError, IndexError, ValueError, TypeError) as e:
        raise GeminiUnavailable("invalid response") from e
    return payload_to_analysis(payload, Engine.LIVE, model,
                               datetime.now(timezone.utc).isoformat(timespec="seconds"))


def today_pt() -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=8)).strftime("%Y-%m-%d")   # PT ≈ UTC-8 (reset ≈ midnight PT)


def caps_allow(session_calls: int, conn, s: Settings) -> tuple[bool, str]:
    if not s.gemini_api_key:
        return False, "no API key"
    if session_calls >= s.live_ai_session_cap:
        return False, f"session cap reached ({session_calls}/{s.live_ai_session_cap})"
    row = conn.execute("SELECT live_calls FROM usage_counters WHERE day=?", (today_pt(),)).fetchone()
    if row and row["live_calls"] >= s.live_ai_daily_cap:
        return False, "daily cap reached"
    return True, ""


def bump_daily(conn) -> None:
    conn.execute("INSERT INTO usage_counters(day,live_calls) VALUES(?,1) ON CONFLICT(day) DO UPDATE SET "
                 "live_calls=live_calls+1", (today_pt(),))
    conn.commit()
