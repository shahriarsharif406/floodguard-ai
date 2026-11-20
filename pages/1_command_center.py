import time
import streamlit as st
from streamlit_folium import st_folium
from floodguard import db, state, ui
from floodguard.replay import REPLAY_DATES

conn, mode = state.conn(), state.mode()
date = state.current_date()
reports = db.list_reports(conn, mode=mode, until=state.until())

verified = sum(1 for r in reports if r["status"] == "verified")
crit = sum(1 for r in reports if r["urgency"] == "critical" and r["status"] in ("pending", "under_review"))
k1, k2, k3 = st.columns(3)
k1.markdown(ui.kpi(len(reports), "Reports in view"), unsafe_allow_html=True)
k2.markdown(ui.kpi(verified, "Verified by humans", "ok"), unsafe_allow_html=True)
k3.markdown(ui.kpi(crit, "Critical pending", "crit"), unsafe_allow_html=True)
st.write("")

left, right = st.columns([7, 3])
with right:
    if mode == "replay":
        playing = st.session_state.get("playing")
        if st.button("❚❚ Pause" if playing else "▶ Replay Sylhet 2022", type="primary", width="stretch"):
            if playing:
                st.session_state["playing"] = False
            else:
                st.session_state["replay_date"] = REPLAY_DATES[0]
                st.session_state["playing"] = True
            st.rerun()
    else:
        st.button("▶ Switch to Replay", type="primary", width="stretch", on_click=lambda: st.session_state.update(
            mode_label="Replay 2022"))
    ds = state.dates()
    c1, c2 = st.columns(2)
    i = ds.index(date)
    if c1.button("◀ Day", width="stretch", disabled=i == 0):
        st.session_state["replay_date"] = ds[i - 1]; st.session_state["playing"] = False; st.rerun()
    if c2.button("Day ▶", width="stretch", disabled=i == len(ds) - 1):
        st.session_state["replay_date"] = ds[i + 1]; st.session_state["playing"] = False; st.rerun()
    chosen = st.select_slider("Date", options=ds, value=date)
    if chosen != date:
        st.session_state["replay_date"] = chosen
        st.session_state["playing"] = False
        st.rerun()
    st.caption(f"Flood layer = composite of {date} and the day before (NASA MODIS, ~250 m)")
    layers = {
        "flood2": st.checkbox("Flood 2-day", True), "flood3": st.checkbox("Flood 3-day", False),
        "truecolor": st.checkbox("True colour", False),
        "imerg": st.checkbox("Rainfall (IMERG)", False)}
    show_sh = st.checkbox("Shelters (DEMO)", True)
    st.markdown('<div class="legend" style="font-size:12px;color:#8FA3C0;margin:6px 0">'
                '<div><span style="background:#ff2b2b"></span>Flood (unusual water)</div>'
                '<div><span style="background:#2bd4ff"></span>Normal surface water</div>'
                '<div><span style="background:#9aa4b2"></span>Insufficient data / cloud</div>'
                '<div style="margin-top:4px">~250 m pixels · cloud shadows can cause false flood pixels</div></div>',
                unsafe_allow_html=True)
    rows = "".join(
        f'<div class="q-row">{ui.chip_urgency(r["urgency"])}<span>#{r["id"]} {ui.e(r["upazila"] or r["district"])}</span>'
        f'<span class="score">{r["priority"]}</span></div>'
        for r in [x for x in reports if x["status"] not in ("verified", "rejected")][:5])
    st.markdown(ui.card("Priority queue (top 5)", rows or "<i>No open reports</i>"), unsafe_allow_html=True)
    if reports:
        by_id = {x["id"]: x for x in reports}
        pick = st.selectbox("Open report", [x["id"] for x in reports],
                            format_func=lambda i: f"#{i} · {by_id[i]['urgency']} · {by_id[i]['upazila'] or by_id[i]['district']}")
        if st.button("Open details →", width="stretch"):
            state.goto_detail(pick)

with left:
    m = ui.build_map(reports, date=date, layers=layers,
                     shelters=db.get_shelters(conn) if show_sh else None)
    st_folium(m, height=620, use_container_width=True, returned_objects=[], key="cc_map")
    st.markdown('<div class="pitch">Satellites see the water; people see the damage. FloodGuard connects both, '
                'with a human in the loop.</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">Not a flood predictor · AI suggests, humans verify · '
            'Data: NASA GIBS, GloFAS/Open-Meteo</div>', unsafe_allow_html=True)

if st.session_state.get("playing"):
    ds = state.dates()
    time.sleep(1.2)
    j = ds.index(st.session_state["replay_date"])
    if j < len(ds) - 1:
        st.session_state["replay_date"] = ds[j + 1]
    else:
        st.session_state["playing"] = False
    st.rerun()
