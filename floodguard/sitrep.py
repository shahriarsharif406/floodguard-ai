from __future__ import annotations
import json
from collections import Counter
from .config import get_settings
from .http import http_post
from .models import CATEGORY_LABEL, Engine


def aggregate(reports: list[dict]) -> dict:
    sim = any(r["is_simulated"] for r in reports)
    by_status = Counter(r["status"] for r in reports)
    by_cat = Counter(r["category"] for r in reports)
    by_dist = Counter(r["district"] or "unknown" for r in reports)
    needs = Counter(n for r in reports for n in r["needs"])
    top = sorted([r for r in reports if r["status"] not in ("verified", "rejected")],
                 key=lambda r: -r["priority"])[:5]
    verified = [r for r in reports if r["status"] == "verified"]
    crit_unver = [r for r in reports if r["urgency"] == "critical" and r["status"] != "verified"]
    badges = Counter(r["badge"] or "unavailable" for r in reports)
    return {"total": len(reports), "simulated": sim, "by_status": dict(by_status), "by_category": dict(by_cat),
            "by_district": dict(by_dist), "needs": dict(needs.most_common(6)), "badges": dict(badges),
            "hotspots": [{"id": r["id"], "place": r["upazila"] or r["district"], "urgency": r["urgency"],
                          "summary": r["summary_en"], "priority": r["priority"]} for r in top],
            "verified": [{"id": r["id"], "place": r["upazila"] or r["district"], "summary": r["summary_en"]}
                         for r in verified],
            "critical_unverified": [{"id": r["id"], "place": r["upazila"] or r["district"],
                                     "summary": r["summary_en"]} for r in crit_unver]}


def template(agg: dict) -> str:
    tag = " (SIMULATED data)" if agg["simulated"] else ""
    L = [f"# Situation Report{tag}", "", "## Overview",
         f"{agg['total']} reports in view · {agg['by_status'].get('verified', 0)} verified by humans · "
         f"{len(agg['critical_unverified'])} critical not yet verified · "
         f"{agg['by_status'].get('pending', 0)} pending review.", "", "## Open hotspots (not yet decided, top 5 by priority)"]
    L += [f"- #{h['id']} {h['place']} — {h['urgency'].upper()} (score {h['priority']}): {h['summary']}"
          for h in agg["hotspots"]] or ["- none"]
    L += ["", "## Needs summary"]
    L += [f"- {k.replace('_', ' ')}: {v}" for k, v in agg["needs"].items()] or ["- none"]
    cats = ", ".join(f"{CATEGORY_LABEL.get(k, k)} {v}" for k, v in sorted(agg["by_category"].items(),
                                                                          key=lambda kv: -kv[1]))
    L += ["", f"Categories: {cats or 'none'}.", "", "## Verified incidents"]
    L += [f"- #{v['id']} {v['place']}: {v['summary']}" for v in agg["verified"]] or ["- none yet"]
    L += ["", "## Unverified but critical (NOT confirmed)"]
    L += [f"- #{v['id']} {v['place']}: {v['summary']}" for v in agg["critical_unverified"]] or ["- none"]
    b = agg["badges"]
    L += ["", "## Evidence context",
          f"Satellite/river context: {b.get('supports', 0)} supports, {b.get('no_signal', 0)} no signal, "
          f"{b.get('inconclusive', 0)} inconclusive, {b.get('unavailable', 0)} unavailable. "
          "Evidence is context, never proof.", "", "## Data caveats",
          "AI analysis only structures text; it never verifies. Satellite flood pixels are ~250 m and can miss "
          "small or under-canopy flooding. This tool does not predict floods."]
    if agg["simulated"]:
        L.append("Community reports in this view are SIMULATED for demonstration.")
    return "\n".join(L)


def generate(agg: dict, allow_live: bool, conn=None, session_calls: int = 0) -> tuple[str, Engine, str]:
    """Returns (markdown, engine, note). Gemini gets aggregates only."""
    from .gemini import bump_daily, caps_allow
    s = get_settings()
    reason = "live AI not requested"
    if allow_live and conn is not None:
        ok, reason = caps_allow(session_calls, conn, s)
        if ok:
            bump_daily(conn)
            prompt = ("Write a concise situation report (≤250 words) for humanitarian coordinators from this JSON. "
                      "Keep counts exactly as given. Mark simulated data as SIMULATED. Do not predict, do not give "
                      "medical advice. Use markdown headings.\n" + json.dumps(agg, ensure_ascii=False))
            from .gemini import generate_content
            st, data, err, _m = generate_content(s, {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                                                     "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2500}},
                                                 max(s.gemini_timeout_s, 15))
            if st == 200 and data:
                try:
                    from .gemini import _text_of
                    return _text_of(data), Engine.LIVE, ""
                except (KeyError, IndexError):
                    reason = "invalid response"
            else:
                reason = err or "timeout"
    return template(agg), Engine.RULES, reason
