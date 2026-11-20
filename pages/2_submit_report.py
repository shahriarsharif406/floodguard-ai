import time
import streamlit as st
from streamlit_folium import st_folium
import folium
from floodguard import db, state, ui
from floodguard.ui import BASEMAP, BASEMAP_ATTR, BASE_CSS
from floodguard.config import get_settings
from floodguard.geo import districts, district_centroid
from floodguard.imaging import ImageRejected
from floodguard.redact import redact
from floodguard.service import submit_report

conn, mode, s = state.conn(), state.mode(), get_settings()
st.markdown('## Report a flood <span class="bn">বন্যার খবর দিন</span>', unsafe_allow_html=True)
dl = districts()
left, right = st.columns([5, 5])

with left:
    text = st.text_area("What is happening?", height=170, max_chars=1000,
                        placeholder="কী হচ্ছে? কতজন? কী দরকার? / What is happening? How many people? What is needed?")
    names = [f"{d['name_en']} · {d['name_bn']}" for d in dl]
    default_i = next((i for i, d in enumerate(dl) if d["name_en"] == "Sunamganj"), 0) if mode == "replay" else 0
    dsel = st.selectbox("District · জেলা", names, index=default_i)
    district = dl[names.index(dsel)]["name_en"]
    up = st.file_uploader("Photo (optional, PNG/JPG, up to 5 MB)", type=["png", "jpg", "jpeg"])
    consent = st.checkbox("I consent to sharing this report and photo for flood response. I will not include names or "
                          "phone numbers. Text (with personal data removed) may be processed by Google Gemini. / "
                          "আমি সম্মতি দিচ্ছি: এই রিপোর্ট ও ছবি বন্যা সাড়াদানের জন্য শেয়ার করা যাবে। আমি নাম বা ফোন নম্বর "
                          "দেব না। ব্যক্তিগত তথ্য মুছে ফেলা টেক্সট Google Gemini প্রক্রিয়া করতে পারে।")

with right:
    c_lat, c_lon = district_centroid(district)
    clicked = st.session_state.get("picked")
    if clicked and clicked.get("district") != district:
        clicked = None
        st.session_state["picked"] = None
    m = folium.Map(location=clicked["pt"] if clicked else (c_lat, c_lon), zoom_start=11, tiles=None)
    folium.TileLayer(BASEMAP, attr=BASEMAP_ATTR, className="fg-base").add_to(m)
    m.get_root().header.add_child(folium.Element(BASE_CSS))
    pt = clicked["pt"] if clicked else (c_lat, c_lon)
    folium.Marker(pt, icon=folium.Icon(icon="crosshairs", prefix="fa", color="blue")).add_to(m)
    st.caption("Click the map to place the report (otherwise the district centre is used)")
    out = st_folium(m, height=300, use_container_width=True, returned_objects=["last_clicked"], key="pick_map")
    if out and out.get("last_clicked"):
        lc = out["last_clicked"]
        new = (round(lc["lat"], 5), round(lc["lng"], 5))
        if not clicked or clicked["pt"] != new:
            st.session_state["picked"] = {"pt": new, "district": district}
            st.rerun()
    loc_src = "map_click" if clicked else "district"
    lat, lon = (clicked["pt"] if clicked else (c_lat, c_lon))
    red, counts = redact(text or "")
    leaked = sum(counts.values())
    body = (f'<div style="font-size:14px;white-space:pre-wrap">{ui.e(red) or "<i>Type a report to preview</i>"}</div>'
            f'<div class="mono" style="font-size:11px;color:#8FA3C0;margin-top:8px">removed: '
            f'{counts["phone"]} phone · {counts["email"]} email · {counts["name"]} name · {counts["id"]} id · '
            f'{counts["url"]} url</div>')
    st.markdown(ui.card("What leaves this device (to AI)", body), unsafe_allow_html=True)
    left_calls = max(s.live_ai_session_cap - st.session_state["live_calls"], 0)
    st.caption(f"Live AI calls left this session: {left_calls}/{s.live_ai_session_cap}" if s.gemini_api_key
               else "Live AI is off — pre-computed Gemini results and the rule-based fallback are used.")

valid = bool(text and 10 <= len(text.strip()) <= 1000)
if st.button("Submit report", type="primary", disabled=not (consent and valid)):
    now = time.time()
    recent = [t for t in st.session_state["submit_times"] if now - t < 600]
    if len(recent) >= 5:
        st.error("Too many reports from this session. Please wait a few minutes.")
    else:
        try:
            with st.spinner("Analysing…"):
                res = submit_report(
                    conn, text=text.strip(), district=district, lat=lat, lon=lon, location_source=loc_src,
                    photo=(up.getvalue(), up.name) if up else None, mode=mode,
                    replay_date=state.current_date() if mode == "replay" else None,
                    allow_live=bool(s.gemini_api_key), session_calls=st.session_state["live_calls"])
            if res["used_live"]:
                st.session_state["live_calls"] += 1
            st.session_state["submit_times"] = recent + [now]
            st.session_state["last_submit"] = res
        except ImageRejected as e:
            st.error(f"Photo rejected: {e}")
        except Exception as e:  # noqa: BLE001
            st.error("Could not submit right now. Please try again.")

res = st.session_state.get("last_submit")
if res:
    a = res["analysis"]
    date_lbl = a.created_at[:10] if a.engine.value == "gemini_precomputed" else None
    chips = ui.chip_urgency(a.urgency.value) + ui.chip_engine(a.engine.value, date_lbl) + \
        "".join(f'<span class="chip need">{ui.e(n.replace("_", " "))}</span>' for n in a.needs)
    dup = ""
    for mt in res["matches"]:
        if mt["kind"] == "duplicate":
            dup += f'<div>Possible duplicate of #{mt["other_id"]} ({round(mt["score"]*100)}% text match, {mt["distance_m"]/1000:.1f} km, {mt["hours"]:.0f} h)</div>'
        elif mt["kind"] == "corroborates":
            dup += f'<div>Corroborates #{mt["other_id"]} ({mt["distance_m"]/1000:.1f} km away)</div>'
        elif mt["kind"] == "same_photo":
            dup += f'<div style="color:#FF5A5F">⚠ Same photo as #{mt["other_id"]} — possible re-shared image</div>'
    note = f'<div class="mono" style="font-size:11px;color:#8FA3C0">{ui.e(res["note"])}</div>' if res["note"] else ""
    st.markdown(ui.card(f'Report #{res["id"]} received — analysis',
                        f'<div>{chips}</div><p style="margin:10px 0 4px">{ui.e(a.summary_en)}</p>'
                        f'<p class="bn" style="margin:0">{ui.e(a.summary_bn or "")}</p>{dup}{note}'
                        + ui.evidence_block(res["evidence"]["badge"], res["evidence"]["sentence"])),
                unsafe_allow_html=True)
    if st.button("View report →"):
        state.goto_detail(res["id"])
