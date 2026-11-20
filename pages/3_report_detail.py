import plotly.graph_objects as go
import streamlit as st
from floodguard import db, state, ui
from floodguard.geo import nearest_shelter
from floodguard.river import anomaly, series_for, sparkline_data
from floodguard.service import refresh_evidence
from streamlit_folium import st_folium
import folium

conn = state.conn()
qid = st.query_params.get("id") or st.session_state.get("detail_id")
ids = [r["id"] for r in db.list_reports(conn, mode=state.mode())] or []
if not qid:
    if not ids:
        st.info("No reports yet."); st.stop()
    qid = st.selectbox("Choose a report", ids, format_func=lambda i: f"#{i}")
rid = int(qid)
r = db.get_report(conn, rid)
if not r:
    st.error("Report not found."); st.stop()

if (r["badge"] in (None, "unavailable")) and not st.session_state.get(f"ev_tried_{rid}"):
    st.session_state[f"ev_tried_{rid}"] = True
    with st.spinner("Fetching satellite & river context…"):
        try:
            refresh_evidence(conn, rid)
            r = db.get_report(conn, rid)
        except Exception:  # noqa: BLE001
            pass

head = f'## #{rid} &nbsp;{ui.stamp(r["status"])} {ui.chip_sim() if r["is_simulated"] else ""}' \
       f'{ui.chip_urgency(r["urgency"])}{ui.chip_engine(r["engine"], (r["analysed_at"] or "")[:10])}'
st.markdown(head, unsafe_allow_html=True)
if r["user_during_replay"]:
    st.caption("USER-SUBMITTED DURING REPLAY (not historical)")
if st.button("← Back to Command Center"):
    st.switch_page("pages/1_command_center.py")

L, R = st.columns([6, 4])
with L:
    needs = "".join(f'<span class="chip need">{ui.e(n.replace("_", " "))}</span>' for n in r["needs"])
    pa = r["people_affected"] if r["people_affected"] is not None else "unknown"
    body = (f'<div class="mono" style="color:#8FA3C0">{ui.e(ui.category_label(r["category"]))} · '
            f'{ui.e(r["upazila"] or r["district"])}</div>'
            f'<p style="margin:8px 0">{ui.e(r["summary_en"])}</p><p class="bn" style="margin:0 0 8px">{ui.e(r["summary_bn"] or "")}</p>'
            f'<div>{needs}</div><div class="mono" style="font-size:12px;margin-top:8px">people affected: {pa} · '
            f'confidence {r["confidence"]:.2f} · location hint: {ui.e(r["location_hint"] or "—")}</div>'
            f'<div style="background:#13203A;height:6px;border-radius:3px;margin-top:8px"><div style="width:{int(r["confidence"]*100)}%;'
            f'height:6px;background:#3FD0E0;border-radius:3px"></div></div>')
    if r["analysis_note"]:
        body += f'<div class="mono" style="font-size:11px;color:#8FA3C0;margin-top:6px">fallback reason: {ui.e(r["analysis_note"])}</div>'
    st.markdown(ui.card("Analysis", body), unsafe_allow_html=True)
    st.markdown(ui.card("Report text (personal data removed)",
                        f'<div style="white-space:pre-wrap">{ui.e(r["redacted_text"])}</div>'), unsafe_allow_html=True)
    raw = db.get_raw(conn, rid)
    if raw["photo"]:
        st.image(raw["photo"], width=480)
    if r["photo_match"]:
        st.markdown(ui.banner("bad", "⚠ Same photo as another report — possible re-shared image. Moderator to check."),
                    unsafe_allow_html=True)
    links = db.get_links(conn, rid)
    lb = ""
    for l in links:
        if l["kind"] == "duplicate":
            lb += f'<div>Possible duplicate of #{l["other_id"]} ({round((l["score"] or 0)*100)}% text match, {l["distance_m"]/1000:.1f} km, {l["hours"]:.0f} h)</div>'
        elif l["kind"] == "corroborates":
            lb += f'<div>Corroborated by #{l["other_id"]} ({l["distance_m"]/1000:.1f} km)</div>'
        elif l["kind"] == "same_photo":
            lb += f'<div style="color:#FF5A5F">⚠ Same photo as #{l["other_id"]}</div>'
    st.markdown(ui.card("Links (suggestions for the moderator)", lb or "<i>No related reports</i>"), unsafe_allow_html=True)

with R:
    sat = {"flood_seen": "FLOOD SEEN", "clear_no_flood": "CLEAR", "clouded": "CLOUDED", "unavailable": "UNAVAILABLE",
           None: "UNAVAILABLE"}[r["sat_class"]]
    riv = {"above_normal": "ABOVE NORMAL", "normal": "NORMAL", "no_river_cell": "NO RIVER CELL",
           "unavailable": "UNAVAILABLE", None: "UNAVAILABLE"}[r["river_class"]]
    ratio = f' · {r["ratio"]}× typical (higher than {r["pctl"]:.0f}% of days)' if r["ratio"] else ""
    ev_html = (ui.evidence_block(r["badge"] or "unavailable", r["ev_sentence"] or "Evidence not available.") +
               f'<div style="margin-top:10px"><span class="chip eng">SAT · {sat}</span>'
               f'<span class="chip eng">RIVER · {riv}</span></div>'
               f'<div class="mono" style="font-size:11px;color:#8FA3C0;margin-top:6px">MODIS 2-day · {r["created_at"][:10]}{ratio}'
               f'<br>GloFAS = modelled discharge, not a gauge reading.</div>')
    st.markdown(ui.card("Satellite & river evidence", ev_html), unsafe_allow_html=True)
    date = r["created_at"][:10]
    ser = series_for(r["lat"], r["lon"], date, live=True)
    sp = sparkline_data(ser, date) if ser else None
    if sp:
        fig = go.Figure()
        if sp["p10"] is not None:
            fig.add_hrect(y0=sp["p10"], y1=sp["p90"], fillcolor="#3FD0E0", opacity=0.12, line_width=0)
        fig.add_trace(go.Scatter(x=sp["time"], y=sp["q"], mode="lines", line=dict(color="#3FD0E0", width=2),
                                 name="m³/s"))
        fig.add_vline(x=date, line_color="#FFB547", line_dash="dot")
        st.plotly_chart(ui.style_fig(fig, 160).update_layout(margin=dict(l=30, r=10, t=10, b=20), showlegend=False),
                        width="stretch")
        st.caption("River discharge (m³/s) ±30 days; band = typical 10–90th percentile for this time of year.")
    shelters = db.get_shelters(conn)
    if shelters:
        sh, km = nearest_shelter(r["lat_pub"], r["lon_pub"], shelters)
        st.markdown(ui.card("Nearest shelter (DEMO data)", f'{ui.e(sh["name"])} — {km:.1f} km straight-line'),
                    unsafe_allow_html=True)
    m = folium.Map(location=(r["lat_pub"], r["lon_pub"]), zoom_start=11, tiles=None)
    folium.TileLayer("CartoDB dark_matter", attr="© OpenStreetMap contributors © CARTO").add_to(m)
    folium.CircleMarker((r["lat_pub"], r["lon_pub"]), radius=ui.URGENCY_RADIUS[r["urgency"]], fill=True,
                        fill_color=ui.URGENCY_COLOR[r["urgency"]], color="#FFB547").add_to(m)
    st_folium(m, height=220, use_container_width=True, returned_objects=[], key=f"mini_{rid}")
    st.caption("Public location is blurred to ~500 m.")
