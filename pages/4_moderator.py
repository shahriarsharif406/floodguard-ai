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
JUDGE_OK = state.mode() == "replay"   # judge preview is offered on replay (demo) data only
if not s.moderator_pin and not JUDGE_OK:
    st.error("Moderator PIN is not configured on this deployment (set MODERATOR_PIN in secrets).")
    st.stop()

if not st.session_state["mod_ok"]:
    lock = lk["until"] - time.time()
    st.markdown(ui.banner("info", "Only a human moderator can verify or reject reports. AI can suggest, never decide."),
                unsafe_allow_html=True)
    if JUDGE_OK:
        st.markdown(ui.banner("info", "Judges and visitors: you can explore the desk on the June 2022 replay data "
                                      "(simulated reports) without a PIN. Live mode always needs the PIN."),
                    unsafe_allow_html=True)
        if st.button("Open judge preview (replay data only)"):
            st.session_state["mod_ok"] = True
            st.session_state["mod_judge"] = True
            st.rerun()
    pin = st.text_input("Moderator PIN", type="password")
    if st.button("Unlock", type="primary", disabled=lock > 0 or not s.moderator_pin):
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

if st.session_state.get("mod_judge") and state.mode() != "replay":
    st.session_state["mod_ok"] = False       # judge preview never carries over to live mode
    st.session_state["mod_judge"] = False
    st.rerun()
if st.session_state.get("mod_judge"):
    st.markdown(ui.banner("warn", "Judge preview: replay data only. Actions here are audited like real ones."),
                unsafe_allow_html=True)
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
if not st.session_state.get("mod_judge") and state.mode() == "replay":
    from floodguard.config import get_settings
    _s = get_settings()
    with st.expander("Admin · upgrade replay reports with Gemini"):
        st.caption("Re-analyses the redacted replay texts with Gemini (daily cap applies). Updates this running "
                   "instance and gives a JSON you can commit as data/gemini_cache.json.")
        if not _s.gemini_api_key:
            st.info("No Gemini key configured.")
        elif st.button("Run Gemini on replay reports"):
            import json as _json, time as _t
            from floodguard.analysis import cache_key
            from floodguard.gemini import GeminiUnavailable, bump_daily, call_gemini, caps_allow
            from floodguard.redact import redact
            items, done, failed = {}, 0, 0
            bar = st.progress(0.0)
            rows = [x for x in conn.execute("SELECT id FROM reports WHERE mode='replay'")]
            for i, row in enumerate(rows):
                rid = row["id"]
                raw_r = db.get_raw(conn, rid)
                red, _ = redact(raw_r["raw_text"])
                ok, why = caps_allow(0, conn, _s)
                if not ok:
                    st.warning(f"Stopped: {why}"); break
                bump_daily(conn)
                try:
                    a = call_gemini(red, db.get_report(conn, rid)["district"], _s)
                except GeminiUnavailable as ex:
                    failed += 1; st.caption(f"#{rid}: {ex}"); continue
                db.insert_analysis(conn, rid, a)
                db.audit(conn, rid, "ai_analyzed", Actor.AI, a.engine.value, a.summary_en)
                db.recompute_priority(conn, rid)
                items[cache_key(red, _s.gemini_model)] = {
                    "category": a.category.value, "urgency": a.urgency.value, "needs": a.needs,
                    "people_affected": a.people_affected, "summary_en": a.summary_en, "summary_bn": a.summary_bn,
                    "location_hint": a.location_hint, "language": a.language, "confidence": a.confidence}
                done += 1; bar.progress((i + 1) / len(rows)); _t.sleep(1)
            st.success(f"{done} upgraded, {failed} failed.")
            if items:
                from datetime import date as _dd
                st.session_state["gem_cache_json"] = _json.dumps(
                    {"meta": {"model": _s.gemini_model, "generated_on": _dd.today().isoformat()}, "items": items},
                    ensure_ascii=False, indent=1)
        if st.session_state.get("gem_cache_json"):
            st.download_button("Download gemini_cache.json", st.session_state["gem_cache_json"],
                               "gemini_cache.json", "application/json")
if st.button("Lock desk"):
    st.session_state["mod_ok"] = False; st.rerun()
