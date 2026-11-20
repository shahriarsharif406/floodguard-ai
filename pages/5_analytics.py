import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from floodguard import db, state, ui
from floodguard.river import _load_cache

conn = state.conn()
reports = db.list_reports(conn, mode=state.mode(), until=state.until())
st.markdown("## Analytics")
if not reports:
    st.info("No reports in view yet."); st.stop()
df = pd.DataFrame(reports)
df["day"] = df["created_at"].str[:10]
k = st.columns(4)
k[0].markdown(ui.kpi(len(df), "Reports"), unsafe_allow_html=True)
k[1].markdown(ui.kpi(int((df.status == "verified").sum()), "Verified", "ok"), unsafe_allow_html=True)
k[2].markdown(ui.kpi(int(((df.urgency == "critical") & df.status.isin(["pending", "under_review"])).sum()),
                     "Critical pending", "crit"), unsafe_allow_html=True)
k[3].markdown(ui.kpi(int(df.n_links.sum() > 0 and (df.n_links > 0).sum()), "With corroboration", "amber"),
              unsafe_allow_html=True)
st.write("")
COL = ui.URGENCY_COLOR
a, b = st.columns(2)
with a:
    g = df.groupby(["day", "urgency"]).size().reset_index(name="n")
    fig = px.bar(g, x="day", y="n", color="urgency", color_discrete_map=COL, title="Reports per day by urgency",
                 category_orders={"urgency": ["critical", "high", "medium", "low"]})
    st.plotly_chart(ui.style_fig(fig), width="stretch")
with b:
    c = df.category.map(ui.category_label).value_counts().reset_index()
    c.columns = ["category", "n"]
    fig = px.bar(c.sort_values("n"), x="n", y="category", orientation="h", title="Category share",
                 color_discrete_sequence=["#3FD0E0"])
    st.plotly_chart(ui.style_fig(fig), width="stretch")
a, b = st.columns(2)
with a:
    n_pending = int((df.status == "pending").sum()); n_rev = int((df.status == "under_review").sum())
    n_ver = int((df.status == "verified").sum()); n_rej = int((df.status == "rejected").sum())
    fig = go.Figure(go.Bar(x=["Pending", "Under review", "Verified", "Rejected"], y=[n_pending, n_rev, n_ver, n_rej],
                           marker_color=["#FFB547", "#3FD0E0", "#4ADE9A", "#9AA4B2"]))
    fig.update_layout(title="Status funnel")
    st.plotly_chart(ui.style_fig(fig), width="stretch")
with b:
    anchors = (_load_cache().get("anchors") or {})
    ser = anchors.get("sunamganj_surma")
    fig = go.Figure()
    if ser and state.mode() == "replay":
        t, q = ser["time"], ser["q"]
        lo = [i for i, x in enumerate(t) if x >= "2022-06-01"][:1]
        sel = [(x, v) for x, v in zip(t, q) if "2022-06-01" <= x <= "2022-06-30"]
        fig.add_trace(go.Scatter(x=[x for x, _ in sel], y=[v for _, v in sel], name="GloFAS discharge (m³/s)",
                                 line=dict(color="#3FD0E0", width=2)))
        cnt = df.groupby("day").size().reset_index(name="n")
        fig.add_trace(go.Scatter(x=cnt.day, y=cnt.n, mode="markers", name="Reports", yaxis="y2",
                                 marker=dict(color="#FFB547", size=10)))
        fig.update_layout(title="River discharge vs reports (Sunamganj)", yaxis2=dict(overlaying="y", side="right",
                                                                                      showgrid=False))
    else:
        fig.update_layout(title="River discharge vs reports",
                          annotations=[dict(text="Run scripts/precompute_evidence.py to cache GloFAS data",
                                            showarrow=False, font=dict(color="#8FA3C0"))])
    st.plotly_chart(ui.style_fig(fig), width="stretch")
    st.caption("Correlation shown for context; reports are simulated." if state.mode() == "replay" else "Context only.")
eng = df.engine.value_counts().to_dict()
st.caption("Analyses: " + ", ".join(f"{v} {ui.chip_engine(k).split('>')[1].split('<')[0]}" for k, v in eng.items()))
