import streamlit as st

st.set_page_config(page_title="FloodGuard AI", page_icon="◆", layout="wide", initial_sidebar_state="expanded")

from floodguard import state, ui  # noqa: E402
from floodguard.config import get_settings  # noqa: E402

st.markdown(f"<style>{ui.GLOBAL_CSS}</style>", unsafe_allow_html=True)
state.init()
state.warm_evidence(state.conn())

pages = [
    st.Page("pages/1_command_center.py", title="Command Center", icon="🛰️", url_path="command", default=True),
    st.Page("pages/2_submit_report.py", title="Submit Report", icon="📝", url_path="submit"),
    st.Page("pages/3_report_detail.py", title="Report Detail", icon="🔎", url_path="report"),
    st.Page("pages/4_moderator.py", title="Moderator", icon="🛡️", url_path="moderator"),
    st.Page("pages/5_analytics.py", title="Analytics", icon="📊", url_path="analytics"),
    st.Page("pages/6_situation_report.py", title="Situation Report", icon="📄", url_path="sitrep"),
    st.Page("pages/7_about_limits.py", title="About & Limits", icon="ℹ️", url_path="about"),
]
nav = st.navigation(pages)

with st.sidebar:
    st.markdown('<div class="fg-logo">◆ FLOOD<b>GUARD</b> AI</div>',
                unsafe_allow_html=True)
    st.radio("Mode", ["Replay 2022", "Live (today)"], key="mode_label", horizontal=True)
    s = get_settings()
    left = max(s.live_ai_session_cap - st.session_state.get("live_calls", 0), 0)
    st.caption(f"Live AI calls left this session: {left}/{s.live_ai_session_cap}"
               if s.gemini_api_key else "Live AI: off (no API key) · rule-based + pre-computed")
    st.markdown('<div class="footer">Not a flood predictor<br>AI suggests · humans verify</div>',
                unsafe_allow_html=True)

st.markdown(ui.top_bar(state.mode()), unsafe_allow_html=True)
if state.mode() == "replay":
    from floodguard.replay import BANNER
    st.markdown(ui.banner("info", BANNER), unsafe_allow_html=True)
nav.run()
