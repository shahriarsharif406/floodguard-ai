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
    agg_src = [r for r in allr if (not sel or r["district"] in sel)]     # unverified-critical stays visible, labelled
    agg = sitrep.aggregate(agg_src if not only_ver else agg_src)
    md, eng, note = sitrep.generate(agg, bool(s.gemini_api_key), conn, st.session_state["live_calls"])
    if eng.value == "gemini_live":
        st.session_state["live_calls"] += 1
    st.session_state["sitrep"] = (md, eng.value, note)
res = st.session_state.get("sitrep")
if res:
    md, eng, note = res
    st.markdown(ui.chip_engine("gemini_live" if eng == "gemini_live" else "rules").replace("Rule-based fallback",
                "Template (no live AI)"), unsafe_allow_html=True)
    if note:
        st.caption(f"Template used: {note}")
    st.markdown(f'<div class="fg-card">', unsafe_allow_html=True)
    st.markdown(md)
    st.markdown('</div>', unsafe_allow_html=True)
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
