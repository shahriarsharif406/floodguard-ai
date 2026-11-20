import json
import pandas as pd
import streamlit as st
from floodguard import db, sitrep, state, ui
from floodguard.config import get_settings

conn, s = state.conn(), get_settings()
st.markdown("## Situation Report")
allr = db.list_reports(conn, mode=state.mode(), until=state.until())
districts = sorted({r["district"] for r in allr if r["district"]})
c1, c2 = st.columns([3, 1])
sel = c1.multiselect("Districts", districts, default=districts)
only_ver = c2.toggle("Only verified", value=True)
view = [r for r in allr if (not sel or r["district"] in sel) and (r["status"] == "verified" or not only_ver)]
if st.button("Generate SitRep", type="primary"):
    agg_src = [r for r in allr if (not sel or r["district"] in sel)]
    agg = sitrep.aggregate([r for r in agg_src if r["status"] == "verified"] if only_ver else agg_src)
    if only_ver:      # keep life-risk items visible, clearly marked as NOT verified
        agg["critical_unverified"] = [{"id": r["id"], "place": r["upazila"] or r["district"], "summary": r["summary_en"]}
                                      for r in agg_src if r["urgency"] == "critical" and r["status"] != "verified"]
        agg["simulated"] = any(r["is_simulated"] for r in agg_src)
    md, eng, note = sitrep.generate(agg, bool(s.gemini_api_key), conn, st.session_state["live_calls"])
    if eng.value == "gemini_live":
        st.session_state["live_calls"] += 1
    st.session_state["sitrep"] = (md, eng.value, note)
res = st.session_state.get("sitrep")
if res:
    md, eng, note = res
    if "SIMULATED" not in md and any(r["is_simulated"] for r in allr):
        md = "> **Includes SIMULATED data (event replay).**\n\n" + md
    st.markdown(ui.chip_engine("gemini_live" if eng == "gemini_live" else "rules").replace("Rule-based fallback",
                "Template (no live AI)"), unsafe_allow_html=True)
    if note:
        st.caption(f"Template used: {note}")
    with st.container(border=True):
        st.markdown(md)
    d1, d2, d3 = st.columns(3)
    d1.download_button("Download .md", md, "situation_report.md", "text/markdown")
    rows = [{"id": r["id"], "created_at": r["created_at"], "simulated": bool(r["is_simulated"]), "status": r["status"],
             "urgency": r["urgency"], "category": r["category"], "district": r["district"], "lat_public": r["lat_pub"],
             "lon_public": r["lon_pub"], "summary": r["summary_en"], "evidence": r["badge"]} for r in view]
    d2.download_button("Download .csv", pd.DataFrame(rows).to_csv(index=False), "reports.csv", "text/csv")
    gj = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [x["lon_public"], x["lat_public"]]},
         "properties": {k: v for k, v in x.items() if k not in ("lat_public", "lon_public")}} for x in rows]}
    d3.download_button("Download .geojson", json.dumps(gj, ensure_ascii=False), "reports.geojson", "application/geo+json")
    st.caption("Exports carry a `simulated` column and blurred (~500 m) coordinates.")
else:
    st.caption("Generates a ≤250-word briefing from aggregate counts only (no raw text, no personal data).")
