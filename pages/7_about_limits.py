import streamlit as st
from floodguard import ui
from floodguard.config import get_settings

s = get_settings()
st.markdown("## About & Limits")
a, b = st.columns(2)
with a:
    st.markdown(ui.card("What it is",
        "FloodGuard AI turns community flood reports (Bangla or English) into structured incidents, sets each one "
        "against NASA satellite flood imagery and GloFAS river-discharge context, and lets human moderators verify "
        "or reject. Responders get one prioritised map and a one-click situation report."), unsafe_allow_html=True)
    st.markdown(ui.card("What it is NOT",
        "• Not a flood predictor or warning system.<br>• Not an official channel — in an emergency in Bangladesh call 999.<br>"
        "• AI does not verify reports; humans do.<br>• Satellite evidence is context, never proof: ~250 m pixels, clouds, "
        "and flash/under-canopy flooding are often missed."), unsafe_allow_html=True)
    st.markdown(ui.card("Data",
        "<b>Real:</b> NASA GIBS MODIS flood product (MCDWD) and Terra true colour; GloFAS v4 modelled river discharge via "
        "Open-Meteo.<br><b>Simulated:</b> all Event Replay community reports and all shelters (tagged SIMULATED / DEMO)."),
        unsafe_allow_html=True)
with b:
    st.markdown(ui.card("Privacy",
        "No accounts, no contact fields. Phone numbers, emails, names, ID numbers and links are removed before any AI "
        "sees the text. Public map locations are blurred to ~500 m; photo EXIF/GPS is stripped. The Gemini free tier may "
        "use submitted content to improve Google products and may be read by human reviewers, so only redacted text is "
        "sent — never photos or coordinates. Demo deployment: submissions are not permanent."), unsafe_allow_html=True)
    st.markdown(ui.card("AI disclosure",
        f"<b>In the product:</b> Google Gemini (<span class='mono'>{ui.e(s.gemini_model)}</span>, free tier) structures "
        "redacted text and drafts situation reports. Every result is labelled: <i>Gemini (live)</i>, <i>Gemini "
        "(pre-computed)</i> or <i>Rule-based fallback</i>.<br><b>In building it:</b> Anthropic's Claude (Claude Code) "
        "helped plan and write the code under the author's direction."), unsafe_allow_html=True)
    st.markdown(ui.card("Credits",
        "NASA GIBS / LANCE · GloFAS (Copernicus) via Open-Meteo · Esri World Dark Gray Base (© Esri, HERE, Garmin, OpenStreetMap contributors) · Google Fonts. "
        "Event facts: UN RCO Bangladesh (22 Jun 2022), IFRC MDRBD028."), unsafe_allow_html=True)
st.markdown('<div class="footer">Evidence is context, never proof. A human moderator decides.</div>', unsafe_allow_html=True)
