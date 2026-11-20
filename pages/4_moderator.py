import hmac
import time
import pandas as pd
import streamlit as st
from floodguard import db, state, ui
from floodguard.config import get_settings
from floodguard.models import Actor, Status
from floodguard.priority import breakdown
from floodguard.redact import redact

conn, s = state.conn(), get_settings()
st.markdown("## Moderator desk")
@st.cache_resource
def _lockout() -> dict:       # server-wide, survives page reloads
    return {"fail": 0, "until": 0.0}


lk = _lockout()
st.session_state.setdefault("mod_ok", False)
if not s.moderator_pin:
    st.error("Moderator PIN is not configured on this deployment (set MODERATOR_PIN in secrets).")
    st.stop()

if not st.session_state["mod_ok"]:
    lock = lk["until"] - time.time()
    st.markdown(ui.banner("info", "Only a human moderator can verify or reject reports. AI can suggest, never decide."),
                unsafe_allow_html=True)
    pin = st.text_input("Moderator PIN", type="password")
    if st.button("Unlock", type="primary", disabled=lock > 0):
        if hmac.compare_digest(pin.encode(), s.moderator_pin.encode()):
            st.session_state["mod_ok"] = True
            lk["fail"] = 0
            st.rerun()
        else:
            lk["fail"] += 1
            if lk["fail"] >= 5:
                lk["until"] = time.time() + 60
                lk["fail"] = 0
            st.error("Wrong PIN.")
    if lock > 0:
        st.warning(f"Too many attempts. Try again in {int(lock)} s.")
    st.stop()

reports = db.list_reports(conn, mode=state.mode(), until=state.until())
f1, f2 = st.columns(2)
fs = f1.multiselect("Status", [x.value for x in Status], default=["pending", "under_review"])
fu = f2.multiselect("Urgency", ["critical", "high", "medium", "low"], default=["critical", "high", "medium", "low"])
view = [r for r in reports if r["status"] in fs and r["urgency"] in fu]
df = pd.DataFrame([{"score": r["priority"], "#": r["id"], "SIM": "SIM" if r["is_simulated"] else "",
                    "urgency": r["urgency"], "category": r["category"], "place": r["upazila"] or r["district"],
                    "badge": r["badge"], "links": r["n_links"] + (1 if r["photo_match"] else 0), "status": r["status"]}
                   for r in view])
st.dataframe(df, width="stretch", hide_index=True, height=260)
if not view:
    st.info("Nothing matches these filters."); st.stop()

pick = st.selectbox("Select a report", [r["id"] for r in view],
                    format_func=lambda i: next(f"#{r['id']} · {r['urgency']} · {r['upazila'] or r['district']} · {r['status']}"
                                               for r in view if r["id"] == i))
r = db.get_report(conn, pick)
raw = db.get_raw(conn, pick)
L, R = st.columns([6, 4])
with L:
    st.markdown(f'### #{pick} {ui.stamp(r["status"])} {ui.chip_sim() if r["is_simulated"] else ""}', unsafe_allow_html=True)
    st.markdown(ui.card("Moderator-only view",
                        f'<div class="mono" style="font-size:12px;color:#8FA3C0">exact: {raw["lat"]:.5f}, {raw["lon"]:.5f}</div>'
                        f'<div style="white-space:pre-wrap;margin-top:6px">{ui.e(raw["raw_text"])}</div>'), unsafe_allow_html=True)
    st.markdown(ui.evidence_block(r["badge"] or "unavailable", r["ev_sentence"] or "Evidence not available."),
                unsafe_allow_html=True)
    u, c, e = breakdown(r["urgency"], r["n_links"], r["badge"] or "unavailable")
    st.caption(f"Priority {r['priority']} = U {u:.2f} × C {c:.2f} × E {e:.2f}")
    st.caption(f"AI suggestion: {r['category']}/{r['urgency']} — suggestion only ({r['engine']})")
with R:
    with st.form(f"decide_{pick}", clear_on_submit=True):
        note = st.text_area("Note (required for Verify / Reject, 5–200 chars)", max_chars=200, height=90)
        b1, b2, b3 = st.columns(3)
        rev = b1.form_submit_button("Under review", width="stretch")
        ver = b2.form_submit_button("Verify", type="primary", width="stretch")
        rej = b3.form_submit_button("Reject", width="stretch")
    ok_note = 5 <= len(note.strip()) <= 200
    if (ver or rej) and not ok_note:
        st.error("A note of 5–200 characters is required to verify or reject.")
    elif rev or ver or rej:
        new = Status.REVIEW if rev else (Status.VERIFIED if ver else Status.REJECTED)
        db.set_status(conn, pick, new, Actor.HUMAN, note, "moderator")
        st.rerun()
    st.markdown("**Audit trail**")
    for a in reversed(db.get_audit(conn, pick)):
        arrow = f" {a['from_status']}→{a['to_status']}" if a["to_status"] else ""
        st.markdown(f'<div class="mono" style="font-size:12px;border-bottom:1px solid #22324F;padding:4px 0">'
                    f'{ui.e(a["ts"][:19])} · {ui.e(a["actor"])} · {ui.e(a["action"])}{ui.e(arrow)}'
                    f'<br><span style="color:#8FA3C0">{ui.e(a["note"] or "")}</span></div>', unsafe_allow_html=True)
if st.button("Lock desk"):
    st.session_state["mod_ok"] = False; st.rerun()
