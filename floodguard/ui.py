"""Design system ("ops room at night, printed like a field manual") and shared UI helpers."""
from __future__ import annotations
import html
import folium
from .evidence import FOOTER, LABEL
from .gibs import LAYERS, tile_url
from .models import CATEGORY_LABEL

BASEMAP = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"   # darkened with a CSS filter (class fg-base)
BASEMAP_ATTR = "© OpenStreetMap contributors"
BASE_CSS = ("<style>.fg-base{filter:invert(1) hue-rotate(190deg) brightness(.82) contrast(.95) saturate(.55)}"
            ".leaflet-container{background:#0b1220}</style>")
URGENCY_COLOR = {"critical": "#FF5A5F", "high": "#FF9F43", "medium": "#F4D35E", "low": "#7FB7A4"}
URGENCY_RADIUS = {"critical": 11, "high": 9, "medium": 7, "low": 6}

GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Noto+Sans+Bengali:wght@400;600&display=swap');
:root{--ink-950:#060B14;--ink-900:#0B1422;--ink-800:#13203A;--line:#22324F;--text:#E6EDF7;--muted:#8FA3C0;
--cyan:#3FD0E0;--amber:#FFB547;--crit:#FF5A5F;--high:#FF9F43;--med:#F4D35E;--low:#7FB7A4;--ok:#4ADE9A;--rej:#9AA4B2;}
html,body,[data-testid="stAppViewContainer"]{background:var(--ink-950);color:var(--text);
  font-family:'IBM Plex Sans','Noto Sans Bengali',system-ui,sans-serif;}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stSidebar"]{background:var(--ink-900);border-right:1px solid var(--line);}
h1,h2,h3,.fg-display{font-family:'Chakra Petch',sans-serif;letter-spacing:.02em;color:var(--text);}
.block-container{padding-top:1.2rem;max-width:1440px;}
.bn{font-family:'Noto Sans Bengali',sans-serif;color:var(--muted);font-size:.9em;margin-left:.4em;}
.mono{font-family:'IBM Plex Mono',monospace;}
.fg-bar{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;border:1px solid var(--line);
  border-radius:6px;background:var(--ink-900);margin-bottom:16px;}
.fg-logo{font-family:'Chakra Petch';font-weight:700;font-size:20px;letter-spacing:.12em;}
.fg-logo b{color:var(--cyan);}
.fg-kpi{border:1px solid var(--line);border-left:3px solid var(--cyan);background:var(--ink-900);border-radius:6px;padding:14px 18px;}
.fg-kpi .v{font-family:'IBM Plex Mono';font-size:34px;font-weight:500;line-height:1;}
.fg-kpi .l{font-family:'IBM Plex Mono';font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:6px;}
.fg-kpi.amber{border-left-color:var(--amber);} .fg-kpi.crit{border-left-color:var(--crit);} .fg-kpi.ok{border-left-color:var(--ok);}
.fg-card{background:var(--ink-900);border:1px solid var(--line);border-radius:6px;padding:16px 18px;margin-bottom:12px;}
.fg-card h4{font-family:'Chakra Petch';font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 10px;}
.chip{display:inline-block;font-family:'IBM Plex Mono';font-size:11px;font-weight:500;letter-spacing:.06em;text-transform:uppercase;
  padding:3px 8px;border-radius:3px;border:1px solid currentColor;margin-right:6px;line-height:16px;}
.u-critical{color:var(--crit);background:rgba(255,90,95,.12);} .u-high{color:var(--high);background:rgba(255,159,67,.10);}
.u-medium{color:var(--med);background:rgba(244,211,94,.08);} .u-low{color:var(--low);background:rgba(127,183,164,.08);}
.eng{color:var(--cyan);border-style:dashed;}
.sim{color:var(--text);background:#2A3550;border-color:#2A3550;}
.need{color:var(--muted);border-color:var(--line);}
.stamp{display:inline-block;font-family:'Chakra Petch';font-weight:700;font-size:12px;letter-spacing:.14em;padding:2px 10px;
  border:2px solid currentColor;border-radius:3px;transform:rotate(-2deg);text-transform:uppercase;}
.s-verified{color:var(--ok);} .s-rejected{color:var(--rej);text-decoration:line-through;}
.s-pending{color:var(--amber);border-style:dashed;} .s-under_review{color:var(--cyan);border-style:dashed;}
.ev{display:flex;gap:10px;align-items:flex-start;padding:10px 12px;border-radius:6px;border:1px solid var(--line);background:var(--ink-800);}
.ev .dot{width:10px;height:10px;border-radius:50%;margin-top:6px;flex:none;}
.ev-supports .dot{background:var(--cyan);box-shadow:0 0 0 4px rgba(63,208,224,.18);}
.ev-no_signal .dot{background:var(--muted);} .ev-inconclusive .dot{background:transparent;border:2px dashed var(--muted);}
.ev-unavailable .dot{background:var(--line);}
.ev b{font-family:'Chakra Petch';letter-spacing:.08em;}
.ev-foot{font-size:12px;color:var(--muted);margin-top:8px;border-top:1px solid var(--line);padding-top:8px;}
.banner{padding:8px 14px;border-radius:6px;font-size:13px;margin-bottom:12px;border:1px solid;}
.banner.info{color:var(--cyan);border-color:rgba(63,208,224,.4);background:rgba(63,208,224,.06);}
.banner.warn{color:var(--amber);border-color:rgba(255,181,71,.4);background:rgba(255,181,71,.06);}
.banner.bad{color:var(--crit);border-color:rgba(255,90,95,.4);background:rgba(255,90,95,.06);}
.stButton>button{font-family:'Chakra Petch';font-weight:600;letter-spacing:.08em;text-transform:uppercase;border-radius:4px;
  border:1px solid var(--line);background:var(--ink-800);color:var(--text);}
.stButton>button[kind="primary"]{background:var(--amber);color:#1A1203;border-color:var(--amber);}
.stButton>button:focus-visible{outline:2px solid var(--cyan);outline-offset:2px;}
.q-row{display:flex;gap:10px;align-items:center;padding:6px 0;border-bottom:1px solid var(--line);font-size:13px;}
.q-row .score{font-family:'IBM Plex Mono';font-size:18px;margin-left:auto;}
.legend span{display:inline-block;width:12px;height:12px;margin-right:6px;vertical-align:middle;border-radius:2px;}
.footer{font-family:'IBM Plex Mono';font-size:11px;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;text-align:center;padding:16px 0;}
.pitch{color:var(--muted);font-size:14px;margin-top:8px;}
"""


def e(s) -> str:
    return html.escape(str(s if s is not None else ""))


def chip_urgency(u: str) -> str:
    return f'<span class="chip u-{e(u)}">{e(u)}</span>'


def chip_engine(engine: str, date: str | None = None) -> str:
    label = {"gemini_live": "Gemini (live)", "gemini_precomputed": f"Gemini (pre-computed{' · ' + date if date else ''})",
             "rules": "Rule-based fallback"}.get(engine, engine)
    return f'<span class="chip eng">{e(label)}</span>'


def chip_sim() -> str:
    return '<span class="chip sim">SIMULATED</span>'


def stamp(status: str) -> str:
    return f'<span class="stamp s-{e(status)}">{e(status.replace("_", " "))}</span>'


def evidence_block(badge: str, sentence: str) -> str:
    return (f'<div class="ev ev-{e(badge)}"><span class="dot"></span><div><b>{e(LABEL.get(badge, badge))}</b><br>'
            f'<span style="font-size:14px">{e(sentence)}</span></div></div>'
            f'<div class="ev-foot">{e(FOOTER)}</div>')


def kpi(value, label: str, variant: str = "") -> str:
    return f'<div class="fg-kpi {variant}"><div class="v">{e(value)}</div><div class="l">{e(label)}</div></div>'


def banner(kind: str, text: str) -> str:
    return f'<div class="banner {kind}">{e(text)}</div>'


def card(title: str, body_html: str) -> str:
    return f'<div class="fg-card"><h4>{e(title)}</h4>{body_html}</div>'


def top_bar(mode: str) -> str:
    badge = ('<span class="chip sim">REPLAY · SYLHET JUN 2022 · SIMULATED REPORTS</span>' if mode == "replay"
             else '<span class="chip eng">LIVE</span>')
    return (f'<div class="fg-bar"><div class="fg-logo">◆ FLOOD<b>GUARD</b> AI</div>'
            f'<div>{badge}</div></div>')


def category_label(c: str) -> str:
    return CATEGORY_LABEL.get(c, c)


def build_map(reports: list[dict], *, date: str, layers: dict[str, bool], shelters: list[dict] | None = None,
              exact: bool = False, center=(24.95, 91.65), zoom: int = 9) -> folium.Map:
    m = folium.Map(location=center, zoom_start=zoom, tiles=None, control_scale=True)
    folium.TileLayer(BASEMAP, name="Base (dark)", attr=BASEMAP_ATTR, className="fg-base").add_to(m)
    m.get_root().header.add_child(folium.Element(BASE_CSS))
    for key, on in layers.items():
        if on and key in LAYERS:
            L = LAYERS[key]
            folium.TileLayer(tiles=tile_url(key, date), attr="NASA GIBS (MODIS / IMERG)", name=L["label"], overlay=True,
                             control=True, opacity=L["opacity"], max_native_zoom=L["max_native"], max_zoom=12).add_to(m)
    for r in reports:
        lat, lon = (r["lat"], r["lon"]) if exact else (r["lat_pub"], r["lon_pub"])
        col = URGENCY_COLOR.get(r["urgency"], "#999")
        st_ = r["status"]
        if st_ == "verified":
            kw = dict(color="#4ADE9A", weight=3, fill_opacity=0.85)
        elif st_ == "pending":
            kw = dict(color="#FFB547", weight=2, dash_array="4 3", fill_opacity=0.85)
        elif st_ == "under_review":
            kw = dict(color="#3FD0E0", weight=2, dash_array="4 3", fill_opacity=0.85)
        else:
            kw = dict(color="#9AA4B2", weight=0, fill_opacity=0.35)
        sim = '<span style="background:#2A3550;padding:1px 6px;border-radius:3px;font-size:10px">SIMULATED</span> ' \
            if r["is_simulated"] else ""
        pop = (f"{sim}<b>#{r['id']}</b> · {e(st_.replace('_', ' '))} · <b style='color:{col}'>{e(r['urgency'])}</b>"
               f"<br>{e(r['summary_en'])}<br><i>{e(LABEL.get(r['badge'] or 'unavailable'))}</i> · score {r['priority']}"
               f"<br><span style='color:#888'>Open it from “Open report” (right panel).</span>")
        folium.CircleMarker((lat, lon), radius=URGENCY_RADIUS.get(r["urgency"], 6), fill=True, fill_color=col,
                            popup=folium.Popup(pop, max_width=260), tooltip=f"#{r['id']} {r['urgency']}", **kw).add_to(m)
    for s in (shelters or []):
        folium.Marker((s["lat"], s["lon"]), icon=folium.Icon(icon="home", prefix="fa", color="lightgray"),
                      popup=folium.Popup(f"<b>{e(s['name'])}</b><br>DEMO location — not an official shelter list.",
                                         max_width=240), tooltip="DEMO shelter").add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m


def style_fig(fig, height: int = 320):
    fig.update_layout(paper_bgcolor="#0B1422", plot_bgcolor="#0B1422", height=height,
                      font=dict(family="IBM Plex Sans, sans-serif", color="#E6EDF7", size=12),
                      margin=dict(l=40, r=20, t=40, b=36), legend=dict(orientation="h", y=-0.2),
                      title=dict(font=dict(family="Chakra Petch, sans-serif", size=15)))
    fig.update_xaxes(gridcolor="#22324F", zerolinecolor="#22324F")
    fig.update_yaxes(gridcolor="#22324F", zerolinecolor="#22324F")
    return fig
