# FloodGuard AI — Build Specification (v1.0, 2026-11-20)

> Audience: the implementing engineer. Build exactly this. Where a choice exists it has been made; the one-line "why" follows it.
> Hackathon: STEM2Connect AI Hackathon 2026 · Track: **Community Impact** (Sustainability flavour) · Deadline **Nov 22 2026 10:59 BST (UTC+6)** · Demo Day Nov 24.
> Items marked **[UNVERIFIED]** could not be confirmed from the planning sandbox; the code must handle them defensively, and the owner checks them with `scripts/check_sources.py`.

---

## 0. TL;DR for the engineer

- Streamlit multipage app (`st.navigation`), SQLite, Folium map, Plotly charts.
- **AI never verifies.** Only a human with the moderator PIN can set `verified`/`rejected`.
- AI comes in three tiers: **pre-computed Gemini cache → limited live Gemini → rule-based fallback**. Every analysis shows a chip naming the engine that produced it.
- The hero is **Event Replay: Sylhet–Sunamganj, June 2022**. It uses real NASA GIBS tiles and real GloFAS discharge (both pre-cached in the repo), plus **SIMULATED** reports that carry a tag wherever they appear.
- The app must work with **zero network access** in replay mode. All external evidence for replay comes from committed JSON/PNG caches. Live calls are a bonus.
- Never claim to predict floods. The copy uses "evidence", "context" and "signal", never "forecast" or "prediction".

---

## 1. Pitch, landing view, demo storyline

### 1.1 Pitch (Devpost + README first paragraph)
**FloodGuard AI** is a community-powered flood intelligence tool, built Bangladesh-first and ready to be used elsewhere. Anyone can send a flood report in Bangla or English, with an optional photo and a map location. AI turns the free text into a structured incident: category, urgency, needs, people affected and a summary. It removes personal data before any text leaves the app and flags duplicate or corroborating reports. Each report is then set against **NASA satellite flood imagery** and **GloFAS river-discharge** context for its place and date. A human moderator verifies or rejects every report, and AI is never allowed to. Responders see one prioritised map and can produce a situation report in one click.
**"Satellites see the water; people see the damage. FloodGuard connects both, with a human in the loop."**

### 1.2 The 10-second landing view (Command Center, first paint)
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ◆ FLOODGUARD AI  বন্যা সতর্কতা        [REPLAY · SYLHET JUN 2022 · SIMULATED REPORTS]  │
├──────────────────────────────────────────────────────────────────────────────┤
│  KPI: 18 REPORTS     KPI: 6 VERIFIED BY HUMANS     KPI: 4 CRITICAL PENDING    │
├───────────────────────────────────────────────┬──────────────────────────────┤
│                                               │  [ ▶ REPLAY SYLHET 2022 ]    │ ← primary CTA (amber)
│   MAP (Folium): CARTO dark base +             │  Date ◀ 2022-06-20 ▶         │
│   MODIS flood 2-day overlay + incident pins   │  Layers: ☑ Flood ☐ TrueColor │
│   (urgency colour, verification ring)         │  ── Priority queue (top 5) ──│
│                                               │  ● CRIT  Companiganj  92     │
│                                               │  ...                         │
└───────────────────────────────────────────────┴──────────────────────────────┘
  Footer strip: "Not a flood predictor · AI suggests, humans verify · Data: NASA GIBS, GloFAS/Open-Meteo"
```
On a fresh session the app **auto-loads replay mode at 2022-06-20**, so judges see a populated map at once. The CTA restarts an animated walk-through from 06-14 to 06-25 (see §5.6).

### 1.3 Six-minute demo video storyboard
| Time | Segment | What is on screen | Criterion |
|---|---|---|---|
| 0:00–0:35 | Hook | Real 2022 MODIS flood layer over Sylhet. VO: "June 2022, 7.2 million people affected. Satellites saw the water. They couldn't see who was on a roof." | Problem & Impact |
| 0:35–1:05 | Landing | Command Center: 3 KPIs, priority queue, pitch line | Presentation |
| 1:05–2:05 | Submit | Bangla report + photo + map click → redaction preview (phone masked) → analysis card with "Gemini (live)" chip | Use of AI, Functionality |
| 2:05–2:45 | Duplicates + photo hash | Second near-identical report → "Corroborates #7" and "Same photo as #7" | Use of AI |
| 2:45–3:35 | Evidence card | Satellite chip "FLOOD SEEN", river chip "ABOVE NORMAL · 2.4× typical", GloFAS sparkline, wording: "context, not proof" | Use of AI, Functionality |
| 3:35–4:20 | Moderator | PIN → queue sorted by priority → Verify with note → audit trail row. Show that an AI suggestion cannot verify. | Functionality, Impact |
| 4:20–4:50 | Replay + Analytics | Press ▶, map steps through the days; charts react | Presentation |
| 4:50–5:15 | Situation report | One click → SitRep (Gemini or template) → download .md | Impact |
| 5:15–5:45 | Honesty | About & Limits page: not a predictor, simulated reports, free-tier privacy, evaluation accuracy (if A6 done) | Learning & Growth |
| 5:45–6:00 | Learning + close | 3 bullets on what was learned and how Claude was used; pitch line | Learning & Growth |

Hard cap 5:55. Record at 1920×1080, browser zoom 90%.

---

## 2. Scope

| ID | Feature | Tier | Note |
|---|---|---|---|
| F1 | Report submission (text, photo, location by map click or district dropdown, consent) | MUST | No contact fields at all; we drop even the optional one to avoid PII. |
| F2 | AI analysis, 3-tier (cache / live Gemini / rules) | MUST | |
| F3 | Duplicate/corroboration detection (geo + time + text) | MUST | |
| F4 | Incident map (urgency colour, verification styling) | MUST | |
| F5 | Moderator workflow + audit trail, PIN | MUST | |
| F6 | Analytics dashboard (Plotly) | MUST | |
| S1 | GIBS MODIS flood overlay + true-colour, date selector | MUST | |
| S2 | GloFAS discharge context per report | MUST | |
| S3 | Satellite Evidence badge | MUST | |
| R1 | Event Replay Sylhet 2022 | MUST | The hero feature. |
| A1 | Situation Report generator | MUST | |
| A2 | Privacy: ~500 m public blur, redaction before Gemini | MUST | |
| A3 | Duplicate-photo aHash | MUST | About 30 lines of code. |
| A4 | Nearest DEMO shelter + distance | MUST | |
| A5 | Priority score → moderator queue order | MUST | |
| A6 | 30-report bilingual eval set + honest accuracy | STRETCH (do it) | Cheap, and it strengthens "Use of AI" and "Learning". |
| A7 | GeoJSON/CSV export | STRETCH | About 20 lines; carries the DEMO tag. |
| S4 | IMERG rainfall layer | STRETCH, last | Layer ID [UNVERIFIED]. |
| — | Voice, native app, SMS gateway, own SAR processing, Groundsource, any prediction | CUT | |

Adjustments made to the brief: (1) the contact-info field is removed completely, because no field means no PII risk; (2) the **VIIRS flood product is not used**, because the MODIS product is verified to cover June 2022 and VIIRS coverage is unverified; (3) replay evidence is **pre-cached in the repo** because Streamlit Cloud cold starts and the free APIs must not break the demo.

---

## 3. Architecture

### 3.1 Folder tree
```
floodguard-ai/
├─ app.py                        # entry: st.set_page_config, CSS inject, init_db, seed, st.navigation
├─ pages/
│  ├─ 1_command_center.py
│  ├─ 2_submit_report.py
│  ├─ 3_report_detail.py         # reads st.query_params["id"]
│  ├─ 4_moderator.py
│  ├─ 5_analytics.py
│  ├─ 6_situation_report.py
│  └─ 7_about_limits.py
├─ floodguard/
│  ├─ __init__.py
│  ├─ config.py        # Settings dataclass from env/secrets
│  ├─ db.py            # sqlite connection, schema, CRUD
│  ├─ models.py        # Enums, dataclasses, JSON schema
│  ├─ redact.py        # PII redaction
│  ├─ lexicon.py       # EN+BN keyword lists
│  ├─ rules.py         # rule-based analyser
│  ├─ gemini.py        # REST client, prompt, validation, caps
│  ├─ analysis.py      # 3-tier orchestrator
│  ├─ dedupe.py        # text/geo/time duplicate + corroboration
│  ├─ imaging.py       # upload validation, EXIF strip, aHash
│  ├─ geo.py           # haversine, blur, districts, nearest shelter
│  ├─ gibs.py          # tile URLs, pixel sampling
│  ├─ river.py         # Open-Meteo GloFAS fetch + anomaly
│  ├─ evidence.py      # badge decision
│  ├─ priority.py
│  ├─ sitrep.py
│  ├─ replay.py        # replay state + seed loader
│  ├─ http.py          # single http_get/http_post wrapper (mock point)
│  └─ ui.py            # CSS, chips, cards, KPI, map builder
├─ data/
│  ├─ districts_bd.json          # 64 districts: name_en, name_bn, lat, lon
│  ├─ replay_sylhet2022.json     # 18 SIMULATED reports (§5.7)
│  ├─ shelters_demo.json         # DEMO shelters (§5.8)
│  ├─ gemini_cache.json          # pre-computed analyses {sha256: {...}}
│  ├─ glofas_cache.json          # per-point discharge series (§5.3)
│  ├─ gibs_samples.json          # pre-sampled pixel classes per replay report per date
│  ├─ gibs_tiles/                # optional: cached PNG tiles for offline replay (z6–9 bbox)
│  └─ eval_set.json              # A6
├─ scripts/
│  ├─ precompute_gemini.py       # owner runs locally with key
│  ├─ precompute_evidence.py     # fetch GloFAS + GIBS samples → caches
│  ├─ check_sources.py           # probe GIBS layer/matrix set, colormap, Open-Meteo
│  └─ run_eval.py                # A6 → prints + writes docs/eval_results.md
├─ tests/ (see §7)
├─ .streamlit/config.toml
├─ .streamlit/secrets.toml.example
├─ requirements.txt
├─ README.md  CREDITS.md  LICENSE (MIT)
└─ docs/ SPEC.md architecture.md threat_model.md eval_results.md screenshots/
```

### 3.2 Data flow
```
 user ─► Submit form ─► validate ─► imaging.validate+strip_exif+ahash
                         │
                         ▼
                   redact.redact(text) ──► redacted_text, flags
                         │
        analysis.analyze(redacted_text, district)
          ├─1 cache hit? (sha256(redacted_text|lang|model)) ─► engine=gemini_precomputed
          ├─2 caps ok & key? gemini.call() ─validate─► engine=gemini_live (write cache row)
          └─3 rules.analyze() ─────────────────────────► engine=rules
                         │
                   db.insert_report + insert_analysis (status=pending)
                         │
     dedupe.find_matches(report) ─► links (duplicate|corroborates), photo match
     evidence.build(lat,lon,date) ─► gibs.sample + river.anomaly ─► badge
     priority.score(...) ─► reports.priority
                         │
   Command Center map ◄──┼──► Moderator queue (PIN) ─► set_status() ─► audit_log
                         └──► Analytics, SitRep (aggregates only, no raw PII)
```

### 3.3 Module signatures (implement exactly; type hints required)
```python
# config.py
@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None; gemini_model: str; live_ai_session_cap: int
    live_ai_daily_cap: int; gemini_timeout_s: float; moderator_pin: str
    db_path: str; app_mode_default: str   # "replay" | "live"
def get_settings() -> Settings            # st.secrets first, then os.environ, then defaults

# models.py
class Category(str, Enum): RESCUE="rescue_needed"; MEDICAL="medical"; FOOD_WATER="food_water"; SHELTER="shelter"; INFRA="infrastructure"; POWER_TELECOM="power_telecom"; WATER_LEVEL="water_level"; LIVELIHOOD="livestock_crops"; OTHER="other"
class Urgency(str, Enum): CRITICAL="critical"; HIGH="high"; MEDIUM="medium"; LOW="low"
class Status(str, Enum): PENDING="pending"; REVIEW="under_review"; VERIFIED="verified"; REJECTED="rejected"
class Engine(str, Enum): LIVE="gemini_live"; PRE="gemini_precomputed"; RULES="rules"
class Badge(str, Enum): SUPPORTS="supports"; NO_SIGNAL="no_signal"; INCONCLUSIVE="inconclusive"; UNAVAILABLE="unavailable"
class SatClass(str, Enum): FLOOD="flood_seen"; CLEAR="clear_no_flood"; CLOUD="clouded"; NA="unavailable"
class RiverClass(str, Enum): HIGH="above_normal"; NORMAL="normal"; NO_CELL="no_river_cell"; NA="unavailable"
class Actor(str, Enum): HUMAN="human_moderator"; SYSTEM="system"; AI="ai"
@dataclass class Analysis: category: Category; urgency: Urgency; needs: list[str]; people_affected: int|None; summary_en: str; summary_bn: str|None; location_hint: str|None; language: str; confidence: float; engine: Engine; model: str|None; created_at: str
ANALYSIS_JSON_SCHEMA: dict      # §4.1

# redact.py
def normalize_digits(text: str) -> str                       # Bangla digits ০-৯ → 0-9
def redact(text: str) -> tuple[str, dict[str,int]]           # (redacted, {"phone":n,"email":n,"name":n,"id":n,"url":n})

# rules.py
def detect_language(text: str) -> str                        # "bn" if ≥30% chars in U+0980–U+09FF else "en"
def analyze_rules(text: str, district: str|None) -> Analysis

# gemini.py
class GeminiUnavailable(Exception): ...
def build_prompt(redacted_text: str, district: str|None) -> dict   # REST body
def call_gemini(redacted_text: str, district: str|None, s: Settings) -> Analysis   # raises GeminiUnavailable
def validate_payload(obj: dict) -> dict                      # raises ValueError
def caps_allow(session_state, db) -> tuple[bool, str]        # (ok, reason)

# analysis.py
def cache_key(redacted_text: str, model: str) -> str         # sha256(model+"|"+redacted_text.strip().lower())
def analyze(redacted_text: str, district: str|None, *, allow_live: bool) -> tuple[Analysis, str]  # (analysis, note e.g. "live cap reached")

# dedupe.py
def tokens(text: str) -> set[str]
def jaccard(a: set[str], b: set[str]) -> float
def find_matches(report: dict, candidates: list[dict]) -> list[dict]   # [{"other_id","kind","score","distance_m","hours"}]

# imaging.py
class ImageRejected(Exception): ...
def validate_and_clean(raw: bytes, filename: str) -> tuple[bytes, str]   # (clean_jpeg_bytes, ahash_hex)
def ahash(img: Image.Image) -> str                           # 64-bit hex
def hamming(h1: str, h2: str) -> int

# geo.py
def haversine_m(lat1, lon1, lat2, lon2) -> float
def blur(lat: float, lon: float, cell_m: int = 500) -> tuple[float, float]  # snap to grid centre
def district_centroid(name_en: str) -> tuple[float,float]
def nearest_shelter(lat, lon, shelters: list[dict]) -> tuple[dict, float]   # (shelter, km)

# gibs.py
LAYERS: dict[str, dict]                                       # §5.1
def tile_url(layer_key: str, date: str) -> str                # Folium template with {z}/{y}/{x}
def sample_flood(lat: float, lon: float, date: str) -> dict   # {"class": SatClass, "flood_frac","water_frac","nodata_frac","source":"live|cache"}

# river.py
def fetch_series(lat, lon, start: str, end: str) -> dict      # {"time":[...],"q":[...],"lat","lon"}
def anomaly(series: dict, date: str) -> dict                  # §5.3 → {"class":RiverClass,"q","clim_median","ratio","pctl","window"}

# evidence.py
def decide_badge(sat: dict, river: dict) -> tuple[Badge, str] # (badge, honest sentence)
def build_evidence(report: dict) -> dict

# priority.py
def priority(urgency: Urgency, n_corroborations: int, badge: Badge, status: Status) -> int

# sitrep.py
def aggregate(reports: list[dict]) -> dict
def generate(agg: dict, allow_live: bool) -> tuple[str, Engine]   # markdown

# db.py
def connect(path: str) -> sqlite3.Connection                  # check_same_thread=False, WAL off (Cloud), row_factory=Row
def init_db(conn) -> None
def seed_if_empty(conn) -> None                               # loads replay + shelters
def insert_report(conn, r: dict) -> int
def set_status(conn, report_id: int, new: Status, actor: Actor, note: str, actor_label: str) -> None
#   → raise PermissionError if actor != HUMAN and new in {VERIFIED, REJECTED}
def list_reports(conn, *, mode: str, until: str|None = None) -> list[dict]
```
Use `@st.cache_resource` for the connection and `@st.cache_data(ttl=3600)` for GIBS/river fetches.

### 3.4 SQLite schema
```sql
CREATE TABLE reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,              -- ISO8601 UTC; replay rows use 2022 dates
  mode TEXT NOT NULL CHECK(mode IN ('live','replay')),
  is_simulated INTEGER NOT NULL DEFAULT 0,  -- 1 → DEMO/SIMULATED tag everywhere
  raw_text TEXT NOT NULL,                -- moderator-only view; never sent to AI or logged
  redacted_text TEXT NOT NULL,
  redaction_counts TEXT NOT NULL,        -- JSON
  language TEXT NOT NULL,                -- 'bn'|'en'
  lat REAL NOT NULL, lon REAL NOT NULL,  -- exact (moderator only)
  lat_pub REAL NOT NULL, lon_pub REAL NOT NULL,  -- 500 m blurred
  district TEXT, location_source TEXT CHECK(location_source IN ('map_click','district')),
  photo BLOB, photo_ahash TEXT,
  consent INTEGER NOT NULL CHECK(consent=1),
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','under_review','verified','rejected')),
  priority INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE analyses (
  report_id INTEGER PRIMARY KEY REFERENCES reports(id),
  category TEXT NOT NULL, urgency TEXT NOT NULL, needs TEXT NOT NULL,  -- JSON list
  people_affected INTEGER, summary_en TEXT NOT NULL, summary_bn TEXT, location_hint TEXT,
  confidence REAL NOT NULL, engine TEXT NOT NULL, model TEXT, created_at TEXT NOT NULL
);
CREATE TABLE links (report_id INTEGER, other_id INTEGER, kind TEXT CHECK(kind IN ('duplicate','corroborates','same_photo')), score REAL, PRIMARY KEY(report_id,other_id,kind));
CREATE TABLE evidence (report_id INTEGER PRIMARY KEY, sat_class TEXT, flood_frac REAL, nodata_frac REAL, sat_date TEXT,
  river_class TEXT, q REAL, clim_median REAL, ratio REAL, pctl REAL, badge TEXT NOT NULL, sentence TEXT NOT NULL, source TEXT, fetched_at TEXT);
CREATE TABLE audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, report_id INTEGER, action TEXT NOT NULL,
  from_status TEXT, to_status TEXT, actor TEXT NOT NULL, actor_label TEXT, note TEXT);  -- no PII in note (redact() before insert)
CREATE TABLE shelters (id INTEGER PRIMARY KEY, name TEXT, name_bn TEXT, lat REAL, lon REAL, district TEXT, is_demo INTEGER NOT NULL DEFAULT 1);
CREATE TABLE usage_counters (day TEXT PRIMARY KEY, live_calls INTEGER NOT NULL DEFAULT 0);  -- day in America/Los_Angeles
CREATE TABLE ai_cache (key TEXT PRIMARY KEY, payload TEXT NOT NULL, model TEXT, created_at TEXT);
```
Audit actions: `created`, `ai_analyzed`, `status_change`, `note`, `evidence_refreshed`, `ai_suggestion` (AI may *suggest* "likely_valid" only as a note, never as a status).

### 3.5 Config / secrets
| Key | Default | Where |
|---|---|---|
| `GEMINI_API_KEY` | none → live tier disabled | secrets/env only; never committed |
| `GEMINI_MODEL` | `gemini-2.5-flash` | env; **[UNVERIFIED as current]**: owner sets it to the newest free-tier Flash model listed in AI Studio |
| `LIVE_AI_SESSION_CAP` | 3 | |
| `LIVE_AI_DAILY_CAP` | 150 | sits well under free-tier RPD; the real limits are per project and not guaranteed |
| `GEMINI_TIMEOUT_S` | 8 | |
| `MODERATOR_PIN` | `2468` (local demo only; README says to change it) | secrets |
| `DB_PATH` | `/tmp/floodguard.db` on Cloud, `./floodguard.db` locally | |
| `APP_MODE_DEFAULT` | `replay` | |
`.streamlit/secrets.toml.example` lists the keys with placeholder values. Add `.streamlit/secrets.toml` and `*.db` to `.gitignore`.

---

## 4. AI layer

### 4.1 Analysis JSON schema (Gemini `responseSchema` and local validator)
```json
{"type":"object","required":["category","urgency","needs","people_affected","summary_en","language","confidence"],
 "properties":{
  "category":{"type":"string","enum":["rescue_needed","medical","food_water","shelter","infrastructure","power_telecom","water_level","livestock_crops","other"]},
  "urgency":{"type":"string","enum":["critical","high","medium","low"]},
  "needs":{"type":"array","maxItems":6,"items":{"type":"string","enum":["boat_rescue","drinking_water","food","dry_shelter","medical_help","baby_supplies","power","phone_network","road_access","animal_shelter","sanitation","information"]}},
  "people_affected":{"type":"integer","nullable":true},
  "summary_en":{"type":"string"}, "summary_bn":{"type":"string","nullable":true},
  "location_hint":{"type":"string","nullable":true},
  "language":{"type":"string","enum":["bn","en","mixed"]},
  "confidence":{"type":"number"}}}
```
Validation in `validate_payload`: enums exact (lower-case first); `needs` deduplicated, unknown items dropped; `people_affected` 0–100000, otherwise null; `summary_en` 10–240 chars, truncated to 240 if longer; `summary_bn` ≤ 240; `location_hint` ≤ 80 and passed through `redact()` again; `confidence` clamped to 0–1. **Any key named `status`, `verified` or similar is ignored.** A payload that fails validation goes to the rules tier, with the note "Gemini response invalid → rule-based".

### 4.2 Gemini call (REST via `requests`, no SDK; this keeps dependencies small)
`POST https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent`
Header `x-goog-api-key: <key>`. Body:
```json
{"systemInstruction":{"parts":[{"text":"<SYSTEM>"}]},
 "contents":[{"role":"user","parts":[{"text":"<USER>"}]}],
 "generationConfig":{"temperature":0.1,"maxOutputTokens":512,"responseMimeType":"application/json","responseSchema":<4.1 schema>}}
```
Parse `candidates[0].content.parts[0].text` → `json.loads`. Timeout 8 s, no retries; a 429 or 5xx raises `GeminiUnavailable("rate-limited")`. Never log the request body.

**SYSTEM prompt (verbatim):**
```
You are a triage assistant for a community flood-reporting tool in Bangladesh. You receive ONE citizen flood report that may be in Bangla (বাংলা), English, or a mix, possibly with spelling errors or Banglish (Bangla in Latin letters). Personal data has already been replaced with tokens like [PHONE], [NAME], [EMAIL]; never try to reconstruct them.
Your job is to STRUCTURE the report, not to judge whether it is true. You never verify reports; a human moderator does.
Rules:
- Output ONLY JSON matching the provided schema.
- category: the single most important need. If anyone is trapped, on a roof, drowning or missing → "rescue_needed".
- urgency: critical = immediate risk to life (trapped people, drowning, missing person, injured with no access); high = vulnerable people (children, elderly, pregnant, sick) without food/water/shelter, or homes submerged; medium = property/infrastructure damage, roads cut, power out, rising water without direct life risk; low = general information or recovered situations.
- people_affected: an integer only if the text states or clearly implies a number (e.g. "5 families" → estimate 5 families × 5 = 25 and state "approx." in summary). Otherwise null.
- summary_en: one neutral English sentence, max 30 words, no speculation. summary_bn: the same in Bangla if the input was Bangla or mixed, else null.
- location_hint: a place name mentioned in the text (village/union/upazila), or null. Do not invent places.
- Do NOT give medical advice, do NOT predict floods, do NOT add facts not in the report.
- confidence: 0–1, how clearly the text supports your category and urgency.
```
**USER prompt template:**
```
District (approximate, user-selected): {district or "unknown"}
Report text (redacted):
"""{redacted_text}"""
```
Only the redacted text and the district name are sent. **No photo, no coordinates, no IDs.**

### 4.3 Three tiers and caps
1. **Pre-computed cache**: `data/gemini_cache.json` = `{"meta":{"model":"...","generated_on":"YYYY-MM-DD"},"items":{key: payload}}`. On load it is merged into the `ai_cache` table. Engine chip: **"Gemini (pre-computed · <date>)"**. `scripts/precompute_gemini.py` reads the key from the environment, iterates `replay_sylhet2022.json` + `eval_set.json`, applies `redact()`, calls `call_gemini`, sleeps 6 s between calls, and writes the file. Run locally only.
2. **Live**: allowed when the key is present, `st.session_state.live_calls < LIVE_AI_SESSION_CAP`, and `usage_counters[today_PT].live_calls < LIVE_AI_DAILY_CAP`. Increment both before the call. Successes are written to `ai_cache`. Chip: **"Gemini (live)"**.
3. **Rules** (§4.6): always available. Chip: **"Rule-based fallback"**, with a tooltip giving the reason (`no API key` / `session cap reached (3/3)` / `daily cap reached` / `timeout` / `invalid response`).
The Submit page shows a small line "Live AI calls left this session: 2/3".

### 4.4 Redaction (`redact.py`), applied to `normalize_digits(text)`, in this order
```python
EMAIL = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"                       → "[EMAIL]"
URL   = r"https?://\S+|www\.\S+"                                               → "[URL]"
BD_PHONE = r"(?<!\d)(?:\+?88[\s-]?)?0?1[3-9]\d{2}[\s-]?\d{3}[\s-]?\d{3}(?!\d)" → "[PHONE]"
INTL_PHONE = r"(?<!\d)\+\d[\d\s-]{8,14}\d(?!\d)"                               → "[PHONE]"
LONG_ID = r"(?<!\d)(?:\d{17}|\d{13}|\d{10})(?!\d)"   # NID formats             → "[ID]"
NAME_EN = r"(?i)\b(my name is|i am|this is|name:)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"  → r"\1 [NAME]"
HONORIFIC_EN = r"\b(Mr|Mrs|Ms|Md|Mohammad|Dr)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?"      → "[NAME]"
NAME_BN = r"(আমার নাম|নাম[:：]?)\s*([ঀ-৿]+(?:\s+[ঀ-৿]+){0,2})"       → r"\1 [NAME]"
HONORIFIC_BN = r"(জনাব|মোঃ|মো\.|মোছাঃ|বেগম)\s*[ঀ-৿]+(?:\s+[ঀ-৿]+)?"  → "[NAME]"
```
Rationale: bare 10-digit numbers can collide with counts, but flood reports seldom contain them, so over-redaction is the safe failure. The Submit page shows a **"What leaves this device"** preview of the redacted text before analysis. Logs never contain raw_text: use `logging` with a filter that drops records containing `raw_text`.

### 4.5 Error handling
Every external call goes through `floodguard/http.py` (`http_get(url, params, timeout)` / `http_post`). These return `(status, json|bytes|None, err)` and never raise. UI banners (component `banner(kind, text)`):
- Gemini down: amber — "Live AI unavailable (rate limit/timeout). Using rule-based analysis — results are less nuanced."
- GIBS down: amber — "Satellite tiles unavailable right now. Showing cached replay imagery / evidence marked 'unavailable'."
- Open-Meteo down: amber — "River data unavailable. River context hidden; satellite context still shown."
- Replay mode with cache: cyan info — "Replay uses real 2022 NASA & GloFAS data (cached) and SIMULATED community reports."

### 4.6 Rule-based analyser (`lexicon.py`, `rules.py`)
Matching: text lower-cased, `normalize_digits`, then substring match for BN and word-boundary match for EN. Each category scores the number of hits. Ties break by the category order listed below (most life-critical first). With zero hits the category is `other`.

| Category | English keywords | Bangla keywords |
|---|---|---|
| rescue_needed | trapped, stuck, on the roof, rooftop, rescue, save us, help us, drowning, drowned, missing, boat needed, need boat, swept away, can't get out, stranded | আটকা, আটকে, ছাদে, চালে, উদ্ধার, বাঁচান, বাঁচাও, ডুবে যাচ্ছে, ডুবছে, নিখোঁজ, ভেসে গেছে, ভেসে যাচ্ছে, নৌকা দরকার, নৌকা লাগবে, বের হতে পারছি না |
| medical | injured, sick, fever, diarrhea, diarrhoea, snake bite, snakebite, pregnant, labour, labor pain, medicine, unconscious, bleeding | আহত, অসুস্থ, জ্বর, ডায়রিয়া, পাতলা পায়খানা, সাপে কাটা, সাপের কামড়, গর্ভবতী, প্রসব, ওষুধ, ঔষধ, অজ্ঞান, রক্ত |
| food_water | food, hungry, rice, drinking water, clean water, safe water, dry food, baby food, milk, starving | খাবার, খাদ্য, ক্ষুধা, না খেয়ে, চাল, বিশুদ্ধ পানি, খাবার পানি, খাওয়ার পানি, শুকনো খাবার, শিশুখাদ্য, দুধ, চিড়া, মুড়ি |
| shelter | shelter, homeless, house collapsed, house submerged, nowhere to stay, evacuate, evacuation, school shelter | আশ্রয়, আশ্রয়কেন্দ্র, ঘর ভেঙে, ঘর ডুবে, ঘরে পানি, থাকার জায়গা নেই, সরিয়ে নিতে, বাড়ি ডুবে |
| infrastructure | road, bridge, embankment, dam breach, culvert, highway, road cut, washed out, school flooded | রাস্তা, সড়ক, সেতু, ব্রিজ, বাঁধ, বেড়িবাঁধ, কালভার্ট, ভেঙে গেছে, যোগাযোগ বিচ্ছিন্ন |
| power_telecom | electricity, power cut, no power, blackout, network, no signal, mobile network, transformer | বিদ্যুৎ, কারেন্ট নেই, বিদ্যুৎ নেই, নেটওয়ার্ক, মোবাইল নেটওয়ার্ক, ট্রান্সফরমার |
| livestock_crops | cattle, cow, goat, livestock, crops, paddy, harvest, fish farm, poultry | গরু, ছাগল, গবাদি, হাঁস, মুরগি, ফসল, ধান, বোরো, মাছের ঘের, পুকুর |
| water_level | water rising, rising fast, knee deep, waist deep, chest deep, overflowing, danger level, flash flood, river overflow | পানি বাড়ছে, পানি বাড়ছে দ্রুত, হাঁটু পানি, কোমর পানি, বুক পানি, গলা পানি, বিপদসীমা, ঢল, পাহাড়ি ঢল, উপচে, বন্যা |

Note: bare "পানি"/"water" is **not** a food_water keyword, because nearly every report contains it.

**Urgency rules** (the first rule that matches wins):
1. CRITICAL if category=rescue_needed, or any of: `drowning, unconscious, missing, swept away, snake bite, bleeding, labour, ডুবে যাচ্ছে, নিখোঁজ, ভেসে গেছে, অজ্ঞান, সাপে কাটা, প্রসব, গলা পানি`.
2. HIGH if a vulnerable-group word appears (`child, children, baby, infant, elderly, old, pregnant, disabled, শিশু, বাচ্চা, বৃদ্ধ, বয়স্ক, গর্ভবতী, প্রতিবন্ধী`) together with medical/food_water/shelter; or `chest deep, বুক পানি, house submerged, ঘর ডুবে`.
3. MEDIUM if category in {infrastructure, power_telecom, shelter, food_water, livestock_crops, medical} or water_level hits ≥ 1.
4. Otherwise LOW.

**people_affected**: regex `(\d{1,5})\s*(people|persons|families|family|জন|পরিবার|লোক|মানুষ)`. Families → ×5. Take the maximum. **needs**: map category hits to needs (rescue→boat_rescue, food_water→drinking_water/food, medical→medical_help, shelter→dry_shelter, infra→road_access, power→power/phone_network, livestock→animal_shelter). **summary_en** template: `"{Urgency} {category label} report{ near {location_hint}}{: ~N people affected}."`. **location_hint**: the first matching upazila/district name from `districts_bd.json` + the replay upazila list (EN or BN). **confidence** = min(0.9, 0.3 + 0.15×hits).

### 4.7 Duplicate and corroboration detection (`dedupe.py`)
Candidates are reports in the same mode created within ±72 h. `tokens()` lower-cases, strips punctuation (including `।`), drops a stopword list of 40 EN + 40 BN words (`the, a, is, we, are, ... / এবং, আমরা, আছে, হয়, না, এই, যে, ...`), and keeps tokens of ≥ 2 characters.
| Kind | Rule | Why |
|---|---|---|
| `duplicate` | distance ≤ 1.0 km AND Δt ≤ 24 h AND jaccard ≥ 0.45 | Same incident, re-sent or forwarded. 1 km fits the coarse map click and 500 m blur. |
| `corroborates` | NOT duplicate AND distance ≤ 3.0 km AND Δt ≤ 48 h AND same category | Independent people describing the same situation; 3 km roughly matches a union. |
| `same_photo` | hamming(aHash) ≤ 5 (of 64) | Re-shared or slightly recompressed image, which is a misinformation signal. |
The UI shows: "Possible duplicate of #7 (92% text match, 0.4 km, 2 h)", "Corroborated by 3 nearby reports", and in red "⚠ Same photo as #7 — possible re-shared image". Links are **suggestions** for the moderator. They never change status.

### 4.8 Priority score (`priority.py`)
```
U = {critical:1.00, high:0.75, medium:0.45, low:0.20}[urgency]
C = 1 + 0.15 * min(n_corroborations, 4)          # max 1.6
E = {supports:1.20, inconclusive:1.00, unavailable:1.00, no_signal:0.85}[badge]
if urgency == critical: E = max(E, 1.0)          # satellites miss roof-level/flash/under-canopy floods; never down-rank life risk
score = round(100 * U * C * E / 1.92)            # 1.92 = max product → 0–100
if status in (verified, rejected): score = 0 for queue ordering (shown as "done")
```
The queue sorts by score desc, then created_at asc. The score's breakdown appears on hover as `U 1.00 × C 1.30 × E 1.20`.

---

## 5. Space and river evidence

### 5.1 GIBS (verified pattern, see §10)
REST template (EPSG:3857):
`https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{Layer}/default/{YYYY-MM-DD}/{TileMatrixSet}/{z}/{y}/{x}.{ext}`
```python
LAYERS = {
 "flood2": {"id":"MODIS_Combined_Flood_2-Day", "ext":"png", "matrix":"GoogleMapsCompatible_Level9", "max_native":9,
            "label":"MODIS Flood (2-day composite, ~250 m)", "opacity":0.75},
 "flood3": {"id":"MODIS_Combined_Flood_3-Day", "ext":"png", "matrix":"GoogleMapsCompatible_Level9", "max_native":9,
            "label":"MODIS Flood (3-day, fewer false positives)", "opacity":0.75},   # ID [UNVERIFIED], probe
 "truecolor": {"id":"MODIS_Terra_CorrectedReflectance_TrueColor", "ext":"jpg", "matrix":"GoogleMapsCompatible_Level9", "max_native":9,
            "label":"MODIS Terra true colour", "opacity":1.0},
}
```
- Tile matrix sets are **[UNVERIFIED]**: Level9 is the expected value for 250 m layers. `scripts/check_sources.py` fetches one tile per candidate (`Level9, Level8, Level7`) at z=6, y=27, x=48 (this tile covers Sylhet) for 2022-06-20 and prints which return HTTP 200 + image. The owner writes the result into `LAYERS`.
- Terra true colour is used instead of VIIRS SNPP: GIBS metadata says the SNPP true-colour layer is "not ongoing". Terra also matches the flood product's sensors.
- Folium:
```python
folium.TileLayer(tiles=gibs.tile_url("flood2", date), attr="NASA GIBS / LANCE MODIS MCDWD", name=label,
                 overlay=True, control=True, opacity=0.75, max_native_zoom=9, max_zoom=12)
```
  Base: `CartoDB dark_matter` (attr "© OpenStreetMap contributors © CARTO"). Use `folium.LayerControl(collapsed=False)`. Map: `location=(24.95,91.65), zoom_start=9, tiles=None`, then add the base layer explicitly.
- **Date control**: on Command Center, a `st.select_slider` over dates 2022-06-10…2022-06-30 in replay mode, and over today−14…today in live mode. Flood layers have a **1-day lag** (`date_for_layer = date`, and the caption says "composite of {date−1} and {date}").
- **Legend** (custom HTML in the side panel): red ■ "Flood (unusual water)", cyan ■ "Normal surface water", grey ▨ "Insufficient data / cloud", plus the caption "~250 m pixels · cloud shadows can cause false flood pixels (NASA user guide)".
- **Pixel sampling** (`sample_flood`): fetch the z=9 tile containing the point, decode with Pillow (RGBA), and take a 7×7 pixel window (≈ ±1 km at lat 25; z9 ≈ 270 m/px). Classify each pixel: `alpha<20` → none; R≥150 and G<110 and B<110 → flood; G≥150 and B≥150 and R<120 → water; else (light/grey, alpha>0) → nodata. **[UNVERIFIED colours]**: `check_sources.py` prints the unique RGBA values of the Sylhet tile so the owner can confirm. Output fractions over the 49 pixels. `class`: flood_frac ≥ 0.04 (≥2 px) → FLOOD; elif nodata_frac ≥ 0.5 → CLOUD; else CLEAR. A fetch failure gives NA. In replay mode, read `data/gibs_samples.json` first (key `"{report_id}|{date}"`).
- Offline replay tiles (optional, if time allows): `precompute_evidence.py` downloads z6–9 tiles for the bbox lat 24.4–25.4, lon 90.9–92.5 for 3 dates (06-14, 06-20, 06-24) into `data/gibs_tiles/`. That is about 130 tiles/layer/date, under 15 MB total. Skip this unless live GIBS proves flaky during testing.

### 5.2 Open-Meteo Flood API (verified)
```
GET https://flood-api.open-meteo.com/v1/flood
    ?latitude={lat}&longitude={lon}&daily=river_discharge
    &start_date=2003-01-01&end_date=2022-07-15
```
- GloFAS v4 Seamless (default), 0.05° (~5 km), historical from 1984-01-01. `cell_selection` defaults to the nearest cell. Response: `daily.time[]`, `daily.river_discharge[]` (m³/s).
- The statistical variables (`river_discharge_median` and the rest) apply **only to forecasts**, so we compute the climatology ourselves.
- Free for non-commercial use without a key. Attribution goes in CREDITS.
- **River-cell snapping**: the docs warn that the nearest cell may not be the river. They suggest shifting the coordinates by about 0.1°. `precompute_evidence.py` therefore tests the 9 points (lat±0.05, lon±0.05) around each **anchor**, then keeps the one with the highest mean discharge. Anchors are listed below. Each report uses the series of its nearest anchor within 25 km, else RiverClass.NO_CELL.

| Anchor | River | Start lat, lon |
|---|---|---|
| sylhet_surma | Surma at Sylhet | 24.89, 91.87 |
| sunamganj_surma | Surma at Sunamganj | 25.07, 91.40 |
| companiganj_piyain | Piyain/Dhalai, Companiganj | 25.05, 91.78 |
| kanaighat_surma | Surma at Kanaighat | 25.00, 92.26 |
| sheola_kushiyara | Kushiyara near Sheola/Beanibazar | 24.86, 92.18 |
| derai_kalni | Kalni-Kushiyara near Derai | 24.79, 91.35 |
Cache format (`data/glofas_cache.json`): `{"anchors":{"sylhet_surma":{"lat":..,"lon":..,"time":[...],"q":[...]}},"meta":{"fetched_on":"..","source":"Open-Meteo Flood API, GloFAS v4"}}`. Store only 2003-01-01…2022-07-15 (about 7,100 floats per anchor, under 1 MB total).

### 5.3 Anomaly method (simple and defensible)
For target date `d` (day-of-year `j`), the **climatology window** is every value from years 2003–2021 whose day-of-year lies within j±15 (about 589 values). The event year is excluded so it does not bias its own baseline.
```
clim_median = median(window); p90 = percentile(window, 90)
q = discharge on d; ratio = q / clim_median
pctl = percent of window values < q
class = HIGH if (pctl >= 90 or ratio >= 1.5) else NORMAL;  NA if q missing
```
Card wording: "River discharge here was **2.4×** the typical mid-June level (higher than **97%** of June days 2003–2021). Modelled by GloFAS — not a gauge reading." In live mode, fetch `start_date = d−20y` to `end_date = d` the same way, cached with `ttl=6h`.

### 5.4 Evidence badge decision table (`decide_badge`)
| Satellite | River | Badge | Sentence shown |
|---|---|---|---|
| FLOOD | any | **SUPPORTS** | "Satellite imagery shows unusual water within ~1 km of this report." (+ river clause) |
| CLEAR | HIGH | **SUPPORTS** | "River flow nearby was well above normal; satellite saw no flood pixels (it can miss small or under-canopy flooding)." |
| CLEAR | NORMAL / NO_CELL / NA | **NO_SIGNAL** | "No flood signal from satellite or river data. This does NOT mean the report is false — flash and street flooding are often too small to see." |
| CLOUD | HIGH | **INCONCLUSIVE** | "Clouds blocked the satellite; river flow nearby was well above normal." |
| CLOUD | other | **INCONCLUSIVE** | "Clouds blocked the satellite view for this date." |
| NA | HIGH | **SUPPORTS** | "River flow nearby was well above normal (satellite data unavailable)." |
| NA | NORMAL/NO_CELL | **INCONCLUSIVE** | "Satellite unavailable; river flow normal." |
| NA | NA | **UNAVAILABLE** | "Evidence services unavailable — judge on report content." |
Every evidence card carries this fixed footer: **"Evidence is context, never proof. A human moderator decides."** Badge labels are "SUPPORTS" / "NO SIGNAL" / "INCONCLUSIVE · CLOUD" / "UNAVAILABLE", never "confirmed" or "verified".

### 5.5 Nearest shelter (A4)
`geo.nearest_shelter` uses haversine. The report detail shows "Nearest shelter (DEMO data): Sunamganj Govt. High School — 2.3 km straight-line." Shelter markers on the map are a small white house icon (`folium.Icon(icon="home", prefix="fa", color="lightgray")`) with "DEMO" in the popup.

### 5.6 Event Replay
- Window: **2022-06-14 → 2022-06-25**. Default landing date: **2022-06-20**.
- `st.session_state.replay_date` drives three things: the GIBS date, reports with `created_at ≤ replay_date 23:59` (BST), and the evidence lookup.
- ▶ CTA runs `for d in dates: set state; st.rerun()` with `time.sleep(1.2)` per frame, using a `replay_playing` flag and a "❚❚ Pause" button. Simpler fallback if rerun loops flicker: ◀ / ▶ step buttons plus the slider.
- A banner appears on every page in replay: **"EVENT REPLAY · June 2022 Sylhet–Sunamganj floods · Satellite & river data: REAL (NASA, GloFAS) · Community reports: SIMULATED for demonstration"**.
- Mode switch in the sidebar: `Replay 2022` / `Live (today)`. Live mode shows only user-submitted live reports.
- `seed_if_empty` inserts the 18 replay reports with `is_simulated=1, mode='replay'`. Statuses come as listed below, and the audit_log rows say `actor_label='seed'`. Each report gets its pre-computed Gemini analysis from cache if present, else rules. Evidence comes from `gibs_samples.json`/`glofas_cache.json`.

### 5.7 Simulated replay reports (data/replay_sylhet2022.json). Every row: `"simulated": true`
Coordinates are approximate (±3 km) and sit at or near upazila centres. Times are BST.
| # | created_at | District / place | lat, lon | Text | Cat | Urg | Status |
|---|---|---|---|---|---|---|---|
| 1 | 06-15 21:10 | Sylhet / Companiganj | 25.06, 91.76 | পাহাড়ি ঢলে পানি খুব দ্রুত বাড়ছে, রাস্তা ডুবে গেছে। বাজারে হাঁটু পানি। | water_level | medium | verified |
| 2 | 06-16 07:40 | Sunamganj / Chhatak | 25.04, 91.67 | Water entered our homes overnight, chest deep now. 6 families with small children need dry food and drinking water. | food_water | high | verified |
| 3 | 06-16 09:05 | Sunamganj / Sadar | 25.07, 91.40 | আমরা ৪ জন ছাদে আটকা পড়েছি, নৌকা লাগবে, বৃদ্ধ মা অসুস্থ। | rescue_needed | critical | verified |
| 4 | 06-16 09:30 | Sunamganj / Sadar | 25.07, 91.41 | ৪ জন ছাদে আটকা, নৌকা দরকার, বয়স্ক মা আছেন। দয়া করে উদ্ধার করুন। | rescue_needed | critical | under_review (duplicate of #3) |
| 5 | 06-16 13:20 | Sylhet / Gowainghat | 25.10, 91.98 | Bridge on the Gowainghat road washed out, no vehicles can pass. | infrastructure | medium | verified |
| 6 | 06-17 06:15 | Sylhet / Kanaighat | 25.00, 92.26 | Surma overflowing, whole village under water. Around 30 people at the school, no food since yesterday. | shelter | high | pending |
| 7 | 06-17 10:00 | Sylhet / Sylhet city (Upashahar) | 24.89, 91.88 | শহরের উপশহর এলাকায় বুক পানি, বিদ্যুৎ নেই দুই দিন, মোবাইল নেটওয়ার্ক বন্ধ। | power_telecom | high | verified |
| 8 | 06-17 11:45 | Sunamganj / Dowarabazar | 25.08, 91.57 | A child is missing after being swept away near the river bank. Need boat search urgently. | rescue_needed | critical | pending |
| 9 | 06-17 16:30 | Sunamganj / Tahirpur | 25.12, 91.18 | হাওরে বোরো ধান আগেই তোলা হয়েছিল, কিন্তু গরু-ছাগল রাখার জায়গা নেই, সব ডুবে গেছে। | livestock_crops | medium | pending |
| 10 | 06-18 08:20 | Sylhet / Companiganj | 25.05, 91.78 | Pregnant woman in labour pain, all roads under water, need boat to hospital. | medical | critical | under_review |
| 11 | 06-18 12:10 | Sylhet / Zakiganj | 24.88, 92.37 | কুশিয়ারার বাঁধ ভেঙে গ্রামে পানি ঢুকছে। ৫০ পরিবার আশ্রয়কেন্দ্রে যেতে চায়। | shelter | high | pending |
| 12 | 06-18 18:40 | Sunamganj / Jagannathpur | 24.77, 91.55 | Shelter at the primary school is overcrowded, need clean drinking water and baby food. | food_water | high | verified |
| 13 | 06-19 09:00 | Sylhet / Bishwanath | 24.83, 91.72 | পানি একটু কমছে কিন্তু টিউবওয়েল ডুবে আছে, বিশুদ্ধ পানির অভাব, ডায়রিয়া শুরু হয়েছে। | medical | high | pending |
| 14 | 06-19 14:30 | Sunamganj / Derai | 24.79, 91.35 | Snake bite case in our village, no transport, water everywhere. | medical | critical | pending |
| 15 | 06-20 10:15 | Moulvibazar / Kulaura | 24.51, 92.04 | Hakaluki haor side villages flooded, road to Kulaura cut. | infrastructure | medium | pending |
| 16 | 06-20 15:50 | Sylhet / Sylhet city (Zindabazar) | 24.90, 91.87 | Shops flooded on Zindabazar road, knee deep water. Situation information only. | water_level | low | rejected (note: "Photo re-shared from 2019 event") |
| 17 | 06-21 08:30 | Netrakona / Kalmakanda | 25.08, 90.88 | কলমাকান্দায় নদীর পানি বিপদসীমার উপরে, অনেক ঘরে পানি, শুকনো খাবার দরকার। | food_water | high | pending |
| 18 | 06-23 11:00 | Sunamganj / Bishwambharpur | 25.10, 91.29 | Water receding slowly. 12 families still on the embankment, need tarpaulins and rice. | shelter | medium | pending |
Notes: #4 tests duplicate detection (BN↔BN, 0.9 km, 25 min). #16 has the same seeded photo as #7 to test `same_photo`: ship two tiny generated PNGs in `data/seed_photos/`, made with Pillow by a script as plain abstract shapes (water-blue rectangles), so no real photos. #10/#14 test medical wording; the analysis must not give medical advice. These 18 rows also become the first 18 eval items.

### 5.8 DEMO shelters (data/shelters_demo.json). Name suffix always " (DEMO)"
Sunamganj Govt. High School 25.068,91.402 · Chhatak Pilot School 25.040,91.672 · Companiganj Upazila Complex 25.058,91.770 · Gowainghat College 25.103,91.975 · Kanaighat Govt. Primary School 25.002,92.258 · Sylhet MC College 24.906,91.898 · Zakiganj Govt. College 24.880,92.365 · Jagannathpur High School 24.770,91.548 · Derai Upazila Complex 24.787,91.350 · Kalmakanda Upazila Complex 25.080,90.880. All `is_demo=1`. The popup reads "DEMO location — not an official shelter list."

---

## 6. Design system and screens

### 6.1 Direction: "Ops room at night, printed like a field manual"
A deep navy-ink field, crisp hairline borders, **cyan = data/satellite**, **amber = action/attention**, and red reserved for life-critical only. Status reads like stamps on a case file. No gradients, no purple, no glassmorphism.

### 6.2 Palette (all text pairs meet WCAG AA on `--ink-900`)
| Token | Hex | Use |
|---|---|---|
| `--ink-950` | `#060B14` | app background |
| `--ink-900` | `#0B1422` | cards |
| `--ink-800` | `#13203A` | raised / hover |
| `--line` | `#22324F` | 1px borders |
| `--text` | `#E6EDF7` | body (15.6:1) |
| `--muted` | `#8FA3C0` | secondary (6.9:1) |
| `--cyan` | `#3FD0E0` | satellite/data accents, links (10.2:1) |
| `--amber` | `#FFB547` | primary CTA, pending (10.6:1) |
| `--crit` | `#FF5A5F` | critical urgency only (5.6:1) |
| `--high` | `#FF9F43` | high |
| `--med` | `#F4D35E` | medium |
| `--low` | `#7FB7A4` | low |
| `--ok` | `#4ADE9A` | verified stamp |
| `--rej` | `#9AA4B2` | rejected (desaturated) |
| `--sim-bg` | `#2A3550` (text `#E6EDF7`) | SIMULATED/DEMO tag (neutral, so it isn't mistaken for status) |

### 6.3 Type
Google Fonts: **Chakra Petch** (display, 600/700), a squared technical face that reads as instruments, unlike Inter or Poppins. **IBM Plex Sans** (UI, 400/500/600). **IBM Plex Mono** (numbers, IDs, coordinates). **Noto Sans Bengali** (400/600) for Bangla.
Scale (px): display 34/40 · h1 26/32 · h2 20/28 · h3 16/24 (Chakra, uppercase, letter-spacing .06em) · body 15/24 · small 13/20 · micro 11/16 (mono, uppercase, .08em). Spacing scale: 4, 8, 12, 16, 24, 32, 48. Radius 6 px for cards and 3 px for chips/stamps.

### 6.4 CSS (`ui.py: GLOBAL_CSS`, injected once in app.py via `st.markdown(..., unsafe_allow_html=True)`)
```css
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
/* top bar */
.fg-bar{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;border:1px solid var(--line);
  border-radius:6px;background:var(--ink-900);margin-bottom:16px;}
.fg-logo{font-family:'Chakra Petch';font-weight:700;font-size:20px;letter-spacing:.12em;}
.fg-logo b{color:var(--cyan);}
/* KPI */
.fg-kpi{border:1px solid var(--line);border-left:3px solid var(--cyan);background:var(--ink-900);border-radius:6px;padding:14px 18px;}
.fg-kpi .v{font-family:'IBM Plex Mono';font-size:34px;font-weight:500;line-height:1;}
.fg-kpi .l{font-family:'IBM Plex Mono';font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:6px;}
.fg-kpi.amber{border-left-color:var(--amber);} .fg-kpi.crit{border-left-color:var(--crit);}
/* card */
.fg-card{background:var(--ink-900);border:1px solid var(--line);border-radius:6px;padding:16px 18px;margin-bottom:12px;}
.fg-card h4{font-family:'Chakra Petch';font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 10px;}
/* chips */
.chip{display:inline-block;font-family:'IBM Plex Mono';font-size:11px;font-weight:500;letter-spacing:.06em;text-transform:uppercase;
  padding:3px 8px;border-radius:3px;border:1px solid currentColor;margin-right:6px;line-height:16px;}
.u-critical{color:var(--crit);background:rgba(255,90,95,.12);} .u-high{color:var(--high);background:rgba(255,159,67,.10);}
.u-medium{color:var(--med);background:rgba(244,211,94,.08);} .u-low{color:var(--low);background:rgba(127,183,164,.08);}
.eng{color:var(--cyan);border-style:dashed;}
.sim{color:var(--text);background:#2A3550;border-color:#2A3550;}
/* stamps (verification) */
.stamp{display:inline-block;font-family:'Chakra Petch';font-weight:700;font-size:12px;letter-spacing:.14em;padding:2px 10px;
  border:2px solid currentColor;border-radius:3px;transform:rotate(-2deg);}
.s-verified{color:var(--ok);} .s-rejected{color:var(--rej);text-decoration:line-through;}
.s-pending{color:var(--amber);border-style:dashed;} .s-under_review{color:var(--cyan);border-style:dashed;}
/* evidence badge */
.ev{display:flex;gap:10px;align-items:center;padding:10px 12px;border-radius:6px;border:1px solid var(--line);background:var(--ink-800);}
.ev .dot{width:10px;height:10px;border-radius:50%;}
.ev-supports .dot{background:var(--cyan);box-shadow:0 0 0 4px rgba(63,208,224,.18);}
.ev-no_signal .dot{background:var(--muted);} .ev-inconclusive .dot{background:transparent;border:2px dashed var(--muted);}
.ev-unavailable .dot{background:var(--line);}
.ev-foot{font-size:12px;color:var(--muted);margin-top:8px;border-top:1px solid var(--line);padding-top:8px;}
/* banners */
.banner{padding:8px 14px;border-radius:6px;font-size:13px;margin-bottom:12px;border:1px solid;}
.banner.info{color:var(--cyan);border-color:rgba(63,208,224,.4);background:rgba(63,208,224,.06);}
.banner.warn{color:var(--amber);border-color:rgba(255,181,71,.4);background:rgba(255,181,71,.06);}
/* buttons */
.stButton>button{font-family:'Chakra Petch';font-weight:600;letter-spacing:.08em;text-transform:uppercase;border-radius:4px;
  border:1px solid var(--line);background:var(--ink-800);color:var(--text);}
.stButton>button[kind="primary"]{background:var(--amber);color:#1A1203;border-color:var(--amber);}
.stButton>button:focus-visible{outline:2px solid var(--cyan);outline-offset:2px;}
/* queue row */
.q-row{display:grid;grid-template-columns:70px 1fr 44px;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--line);font-size:13px;}
.q-row .score{font-family:'IBM Plex Mono';font-size:18px;text-align:right;}
.footer{font-family:'IBM Plex Mono';font-size:11px;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;text-align:center;padding:16px 0;}
```
`.streamlit/config.toml`:
```toml
[theme]
base="dark"
primaryColor="#FFB547"
backgroundColor="#060B14"
secondaryBackgroundColor="#0B1422"
textColor="#E6EDF7"
font="sans serif"
[server]
maxUploadSize=5
```
UI helpers in `ui.py`: `chip_urgency(u)`, `chip_engine(e, date=None)`, `chip_sim()`, `stamp(status)`, `evidence_block(ev)`, `kpi(value,label,variant)`, `banner(kind,text)`, `top_bar(mode)`. Each returns an HTML string.

### 6.5 Map styling
Pins are `folium.CircleMarker`: radius by urgency (crit 11, high 9, med 7, low 6) and fill by urgency colour at opacity .85. Stroke encodes verification: verified = 3 px `#4ADE9A` solid; pending = 2 px `#FFB547` with `dash_array="4 3"`; under_review = 2 px `#3FD0E0` dashed; rejected = fill `#9AA4B2` at opacity .35 with no stroke. The **public** map uses `lat_pub/lon_pub`; the moderator map (Moderator page) uses exact coordinates. Popup HTML (max 260 px): `[SIMULATED] #id · stamp · urgency chip · summary_en · evidence badge label · "Open details →"`, with the link `?page=report&id=N`. Use `st_folium(m, height=620, returned_objects=["last_clicked"], key="cc_map")` to limit reruns.

### 6.6 Screens
**Global**: the sidebar holds the logo, mode radio (`Replay 2022` / `Live`), page nav, "Live AI calls left: n/3", and the footer "Not a flood predictor". The top bar shows the mode badge on every page.

1. **Command Center** (`1_command_center.py`, default page). Top bar → replay banner → 3 KPIs in `st.columns(3)`: Reports in view / **Verified by humans** / Critical pending. Then `st.columns([7,3])`: left is the map. Right holds the primary button `▶ Replay Sylhet 2022` (type primary; in live mode it reads "▶ Switch to Replay"), the date select_slider, layer checkboxes (Flood 2-day ☑, Flood 3-day ☐, True colour ☐, Shelters ☑), the legend, and the **Priority queue** card (top 5 rows: urgency chip · place · score, each linking to detail). Below the map is one line of pitch text in `--muted`.
2. **Submit Report** (`2_submit_report.py`) "Report a flood · বন্যার খবর দিন". Two columns [5,5]. Left: `st.text_area` (10–1000 chars; placeholder in BN+EN "কী হচ্ছে? কতজন? কী দরকার? / What is happening? How many people? What is needed?"), district selectbox (64 districts, BN+EN labels), `st.file_uploader(type=["png","jpg","jpeg"])`, consent checkbox (exact copy: "I consent to sharing this report and photo for flood response. I will not include names or phone numbers. Text (with personal data removed) may be processed by Google Gemini. / আমি সম্মতি দিচ্ছি…"), Submit (primary, disabled until consent and valid location). Right: a small map for click-to-pick (default centre = district centroid; the clicked point is shown with a cyan crosshair marker); "What leaves this device" card showing the redacted text live. After submit: a success card with the analysis, engine chip, duplicate hints, evidence badge and "View report →". Live mode stores `created_at=now`. Replay mode stores the replay date + current time and labels the report "USER-SUBMITTED DURING REPLAY (not historical)".
3. **Report Detail** (`3_report_detail.py?id=`). Header: `#id`, stamp, SIM chip, urgency chip, engine chip. Grid [6,4]. Left: Analysis card (category, needs as small chips, people affected, summary EN + BN, location hint, confidence bar) → Redacted text card (the public view never shows raw text) → Photo (if any, max 480 px) + photo-match warning → Links card (duplicates/corroborations). Right: **Evidence card**: badge row (dot + label + sentence), Satellite chip + "MODIS 2-day · {date}", River chip + ratio/pctl + Plotly sparkline (date−30…date+5, band = clim p10–p90, height 140), nearest DEMO shelter, footer "Evidence is context, never proof. A human moderator decides." → mini map of the blurred location.
4. **Moderator** (`4_moderator.py`). PIN gate: `st.text_input(type="password")`, compared with `hmac.compare_digest`. After 5 failures, lock for 60 s (session state). Once unlocked: filter chips (status, urgency, district) → table (`st.dataframe` with columns score, #, SIM, urgency, category, place, badge, links, age, status) sorted by priority → select a row → action panel: exact coords + raw text (labelled "moderator-only"), buttons **Mark under review / Verify / Reject**, a required note for Verify/Reject (5–200 chars, redacted before storing), audit trail list (ts, actor, from→to, note). A small grey line "AI suggestion: {category}/{urgency} — suggestion only" makes the AI/human separation visible.
5. **Analytics** (`5_analytics.py`). Row of 4 small KPIs. Then 2×2 Plotly charts using the palette, `paper_bgcolor/plot_bgcolor = #0B1422`, font IBM Plex Sans, gridcolor `#22324F`: (a) reports per day stacked by urgency (bar); (b) category share (horizontal bar, not pie); (c) status funnel pending → review → verified/rejected; (d) GloFAS discharge at the Sunamganj anchor, June 2022 vs climatological median band, with report counts as markers on a secondary axis. Caption under (d): "Correlation shown for context; reports are simulated." Engine mix line: "Analyses: 14 Gemini (pre-computed), 2 Gemini (live), 2 rule-based."
6. **Situation Report** (`6_situation_report.py`). Controls: date range, district multiselect, "Only verified" toggle (default ON). Button "Generate SitRep". The output is markdown in a card with sections **Overview · Hotspots (top 5 by priority) · Needs summary · Verified incidents · Unverified but critical (clearly marked) · Evidence context · Data caveats**. Gemini receives **aggregates only** (counts, district names, summaries of verified reports) with the prompt: "Write a concise situation report (≤250 words) for humanitarian coordinators from this JSON. Keep counts exactly as given. Mark simulated data as SIMULATED. Do not predict, do not give medical advice." Template fallback: f-string markdown built from `aggregate()`. Downloads: `.md`, and A7 `.csv`/`.geojson`, both with a `simulated` column and blurred coordinates.
7. **About & Limits** (`7_about_limits.py`). Cards: **What it is** (3 lines) · **What it is NOT** (not a flood predictor or warning system; not an official channel, so in an emergency call 999 in Bangladesh; AI does not verify; satellite evidence is not proof) · **Data** (real: NASA GIBS MODIS MCDWD flood + Terra true colour; GloFAS v4 via Open-Meteo, modelled discharge. Simulated: all replay reports, shelters) · **Privacy** (no accounts, no contact fields, redaction regexes summarised, 500 m public blur, EXIF stripped, Gemini free tier may use submitted text to improve products and may be read by human reviewers, so only redacted text is sent; live AI disabled for EEA/UK/CH users is not enforceable here, so README advises deployers there to use the rules tier or a paid key) · **AI disclosure** (Gemini model and engine tiers; Claude Code used to build; eval accuracy table if A6) · **Credits**.

---

## 7. Test plan (pytest, no network)

`tests/conftest.py`: an in-memory DB fixture; `monkeypatch.setattr(floodguard.http, "http_get", fake)` driven by fixtures in `tests/fixtures/` (`glofas_sylhet.json` synthetic series with a June spike, `gibs_flood_tile.png` 256×256 generated in the fixture with red/cyan/grey/transparent patches, `gemini_ok.json`, `gemini_bad.json`).

| File | Tests |
|---|---|
| test_redact.py | BD phone forms `01712345678`, `+880 1712-345678`, `০১৭১২৩৪৫৬৭৮` → `[PHONE]`; email; "my name is Rahim Uddin" → `[NAME]`; "আমার নাম করিম" → `[NAME]`; NID 10/13/17 digits; "30 people" untouched |
| test_rules.py | each of the 18 replay texts → expected category/urgency (≥ 15/18 must pass; record the misses); "পানি" alone ≠ food_water; families ×5; language detect bn/en |
| test_gemini.py | valid payload parses; bad enum → ValueError; extra `"status":"verified"` key ignored; timeout → GeminiUnavailable → rules engine used; caps: session cap 3 then rules with reason |
| test_dedupe.py | #3/#4 → duplicate; same category 2.5 km/30 h → corroborates; 4 km → none; jaccard BN tokenisation drops `।` |
| test_imaging.py | rejects .gif renamed .jpg (Pillow verify), >5 MB, 0-byte, decompression bomb (>40 MP); output has no EXIF; aHash of resized/recompressed image within 5 bits |
| test_status.py | `set_status(..., actor=Actor.AI, new=VERIFIED)` raises PermissionError; same for SYSTEM; HUMAN works and writes audit row with from/to |
| test_evidence.py | all 8 rows of §5.4 table; pixel classifier on fixture tile; anomaly: spike → HIGH with ratio>1.5; missing date → NA |
| test_priority.py | critical + no_signal ≥ critical + unavailable; max = 100; verified → 0 |
| test_db.py | insert → list → analysis roundtrip; seed_if_empty idempotent (18 rows after 2 calls); every seeded row is_simulated=1 |
| test_sitrep.py | template contains "SIMULATED" when any simulated rows; Gemini down → template |

**E2E happy path (manual, record results in README checklist):**
1. Fresh start → Command Center shows 18 reports, KPIs, flood layer visible at 2022-06-20.
2. ▶ Replay steps through 06-14…06-25 and the pin count grows.
3. Submit a Bangla text with a phone number → the preview shows `[PHONE]` → analysis with an engine chip → it appears on the map (blurred).
4. Submit a duplicate of #3 → "Possible duplicate of #3".
5. Report detail shows the evidence card with a sparkline.
6. Moderator wrong PIN ×5 → lock; correct PIN → verify with note → stamp changes → audit row.
7. Analytics charts render; SitRep generates and downloads.
8. Kill the network (or set the env `FG_OFFLINE=1`, which makes `http_*` return errors): app still works in replay, warn banners appear, engine chips say Rule-based / pre-computed.

---

## 8. Build order (≈30 h). Each milestone ends with `git commit`

| M | Hours (cum.) | Deliverable | Definition of done |
|---|---|---|---|
| M1 | 0–4 | Skeleton: config, db schema, seed loader, rules analyser, redaction, CSS, Command Center map with seeded pins | `streamlit run app.py` shows 18 SIMULATED pins coloured by urgency; tests for redact/rules pass |
| M2 | 4–11 | Submit → analyze (rules + Gemini live/cache) → store → map; Moderator PIN + status + audit; Analytics 2 charts; GIBS flood tile layer + date slider | **GO/NO-GO at hour 12**: the full loop report → analysis → map → moderator verify → dashboard works locally, and the GIBS layer renders for 2022-06-20. If not, the owner pivots to the backup project. |
| M3 | 11–16 | River anomaly + GIBS pixel sampling + evidence badge + report detail page; precompute scripts; caches committed | Evidence card correct for ≥ 3 replay reports; offline mode works from cache |
| M4 | 16–20 | Dedupe + aHash + priority queue + nearest shelter + replay play/step | Tests §7 dedupe/priority/imaging pass; queue order sensible |
| M5 | 20–23 | SitRep (Gemini + template), About & Limits, remaining analytics, exports (A7) | All 7 pages render with no errors in replay and live |
| M6 | 23–26 | Deploy to Streamlit Community Cloud, secrets, cold-start check, eval set + run_eval (A6) | Public URL works in incognito; eval_results.md written |
| M7 | 26–30 | README, CREDITS, docs, screenshots, video recording, Devpost text | All §9 deliverables present; video ≤ 6:00 uploaded |
Buffer: S4 IMERG only if M7 is finished before hour 28.

---

## 9. Deployment and deliverables

### 9.1 Streamlit Community Cloud
- Python 3.11. `requirements.txt`:
```
streamlit>=1.38,<2
folium>=0.17,<1
streamlit-folium>=0.22,<1
plotly>=5.22,<6
pandas>=2.1,<3
Pillow>=10.3,<12
requests>=2.31,<3
numpy>=1.26,<3
pytest>=8   # dev only (keep; harmless)
```
- Secrets are set in the Cloud UI (`GEMINI_API_KEY`, `MODERATOR_PIN`, `GEMINI_MODEL`).
- **The disk is ephemeral**: the DB lives at `/tmp/floodguard.db` and `seed_if_empty` runs on every cold start. Live submissions can vanish when the app sleeps or redeploys, and the About page says so: "Demo deployment: submissions are not permanent."
- Memory (~1 GB limit): no heavy libraries (no geopandas/torch), load caches once with `st.cache_resource`, cap the photo BLOB at 1600 px on the long edge and JPEG q=85.
- Cold start can take 30–60 s. Open the app 5 minutes before Demo Day and recording.
- Recorded-demo fallback: a pre-recorded 6-min video, plus a 90-s silent screen capture of the replay loop, both kept on the laptop and on YouTube (unlisted). If the live app fails at Demo Day, play the capture and narrate.
- Local Windows run (4 GB RAM): `py -3.11 -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && streamlit run app.py`.

### 9.2 README outline
1. Title + pitch line + 1 hero screenshot + live demo link + video link
2. Problem (3 bullets, sources: 7.2 M affected, 94% of Sunamganj submerged; see §10)
3. What it does (6 bullets max) · 4. How it works (diagram from §3.2) · 5. Run locally · 6. Configuration/secrets · 7. Data sources & honesty (real vs simulated) · 8. Privacy & safety · 9. Evaluation (A6 table) · 10. Limitations · 11. **AI disclosure** · 12. Credits · License
**AI disclosure text (paste, then owner edits the specifics):**
> **AI tools used.** *In the product:* Google Gemini (free tier, model set by `GEMINI_MODEL`) structures redacted report text into JSON and drafts situation reports. Each output in the UI is labelled with its engine (live, pre-computed, or rule-based fallback). Gemini never verifies reports. *In building it:* I used Anthropic's Claude (Claude Code) to plan the architecture and write this specification, and to generate much of the code. I directed the scope and product decisions, verified the data sources (NASA GIBS layers, Open-Meteo GloFAS), ran and fixed the test suite, tested the app end-to-end on my own machine, wrote the Bangla test reports' checks, and changed [owner lists: e.g. redaction regexes, thresholds, UI copy] after testing. All simulated data is labelled.

### 9.3 Other repo files
- `docs/architecture.md`: §3.2 diagram, module table, tier diagram, evidence pipeline.
- `docs/threat_model.md` outline: Assets (reports, photos, moderator PIN, API key) · Actors (citizen, moderator, spammer, misinformer) · Threats and mitigations (PII leakage → redaction + no contact fields + blur; fake or re-shared photos → aHash + human verification; prompt injection in report text → JSON schema + enum validation + no tool use + AI can't set status; spam floods → per-session submit limit of 5 per 10 min; PIN brute force → lockout; key leakage → secrets only; misleading evidence → "context not proof" wording) · Residual risks.
- `CREDITS.md`: "Imagery: NASA Global Imagery Browse Services (GIBS), part of NASA's ESDIS; MODIS/Aqua+Terra Global Flood Product (MCDWD) from LANCE." · "River discharge: GloFAS v4 (Copernicus Emergency Management Service), accessed via Open-Meteo Flood API (open-meteo.com), CC BY 4.0 [verify license page]." · "Base map: © OpenStreetMap contributors © CARTO." · "Fonts: Google Fonts (OFL)." · "Event facts: UN RCO Bangladesh situation update 22 Jun 2022; IFRC MDRBD028 final report (ReliefWeb)."
- Devpost description outline: **Inspiration** (Sylhet 2022) · **Problem** · **What it does** (pitch + 5 bullets) · **How we built it** (stack, 3-tier AI, GIBS, GloFAS) · **Use of AI** (tiers, schema, redaction, eval numbers, why AI never verifies) · **Challenges** (free-tier limits, cloud cover, river-cell snapping, Bangla keywords) · **What I learned** · **Accomplishments** · **What's next** (SMS/IVR intake with partners, Sentinel-1 SAR layer, BWDB gauge data, Bangla model fine-tuning, NGO pilot) · **Built with** tags.

### 9.4 Screenshot shot list (1920×1080, `docs/screenshots/`)
1. `01_command_center.png`: "Command Center — June 20 2022 replay: real MODIS flood pixels + simulated community reports."
2. `02_submit_bn.png`: "Report in Bangla; personal data removed before AI sees it."
3. `03_analysis_card.png`: "Structured incident, with the engine that produced it."
4. `04_evidence_card.png`: "Satellite + river context — never proof."
5. `05_duplicate.png`: "Duplicate and re-shared photo detection."
6. `06_moderator.png`: "Humans verify. Every action audited."
7. `07_analytics.png`: "Reports vs GloFAS river discharge, June 2022."
8. `08_sitrep.png`: "One-click situation report for coordinators."

### 9.5 Thumbnails
- YouTube 1280×720: left 60% is a dark-ink crop of the map with red flood pixels and pins; right side has "FLOODGUARD AI" in Chakra Petch 96 px, "Satellites see the water. People see the damage." in Plex Sans 34 px, and an amber chip "SYLHET 2022 REPLAY".
- Devpost 3:2 (1500×1000): centred logo mark (a hexagon outline with a cyan water line through it), title, three status stamps in a row: PENDING (amber dashed), VERIFIED (green), SUPPORTS (cyan dot). No photos of people, no alcohol imagery.

---

## 10. Risks, verified facts, open questions

### 10.1 Risk register
| Risk | L | I | Mitigation |
|---|---|---|---|
| Gemini free tier rate-limited or quota exhausted during judging | H | M | Pre-computed cache for all seeded data; caps; rules tier; engine chip makes the tier honest |
| GIBS tile matrix or colours wrong | M | H | `check_sources.py` on day 1; legend from user guide; optional offline tiles |
| GloFAS nearest cell isn't the river | H | M | 9-point snapping by max mean discharge; NO_CELL state |
| Satellite shows nothing (cloud, monsoon) | H | M | 2/3-day composites; INCONCLUSIVE badge; never down-rank critical |
| st_folium rerun loops / slow map | M | M | `returned_objects` limit, fixed `key`, ≤ 200 markers |
| Ephemeral DB loses live demo data | H | L | Seed on start; say so |
| Judges read simulated as real | L | H | SIM chip + banner on every page + exports column |
| Time overrun | M | H | M2 go/no-go; stretch items last |
| EEA/UK user hits live Gemini | L | M | README note; deployers can unset the key → rules only |

### 10.2 Verified data facts (checked 2026-11-20)
- GIBS WMTS REST pattern (EPSG:3857) `https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{Layer}/default/{Time}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.{ext}`, with time as YYYY-MM-DD and tile matrix sets named `GoogleMapsCompatible_LevelN`. Source: https://nasa-gibs.github.io/gibs-api-docs/access-basics/
- Layer ID `MODIS_Combined_Flood_2-Day` exists in the NASA Worldview layer config (https://raw.githubusercontent.com/nasa-gibs/worldview/main/config/default/common/config/wv.json/layers/modis/combined/MODIS_Combined_Flood_2-Day.json). GIBS metadata calls it "Flood (2-Day Window)", Terra+Aqua MODIS, daily, ongoing, products MCDWD_L3_NRT / MCDWD_L3_F2_NRT v6.1 (https://gibs.earthdata.nasa.gov/layer-metadata/v1.0/MODIS_Combined_Flood_2-Day.json).
- MODIS NRT flood imagery is in Worldview/GIBS **from 1 Jan 2021**, so June 2022 is covered. Only 2-day and 3-day composites are in Worldview (https://www.earthdata.nasa.gov/news/blog/new-flood-imagery-visualizations-soil-moisture ; MCDWD User Guide Rev D https://www.earthdata.nasa.gov/s3fs-public/2024-04/MCDWD_UserGuide_RevD.pdf).
- MCDWD pixel classes: 0 no water, 1 surface water, 2 recurring flood (unpopulated), 3 flood, 255 insufficient data. Nominal ~250 m. Worldview shows surface water as **cyan** and flood as **red**, with insufficient data grey/semi-transparent white. Known false positives: cloud shadow, terrain shadow. Flash floods, narrow roads and water under canopy/roofs are often missed (User Guide Rev D).
- `VIIRS_SNPP_CorrectedReflectance_TrueColor` metadata status is "not ongoing" (https://gibs.earthdata.nasa.gov/layer-metadata/v1.0/VIIRS_SNPP_CorrectedReflectance_TrueColor.json), so Terra MODIS true colour is used instead.
- Open-Meteo Flood API `https://flood-api.open-meteo.com/v1/flood`: params latitude, longitude, daily (`river_discharge`, plus mean/median/max/min/p25/p75 for **forecasts only**), start_date/end_date, past_days, forecast_days 0–210, ensemble, cell_selection. GloFAS v4 Seamless default, 0.05° (~5 km), data from 1984-01-01. The docs warn the nearest river may not be selected and suggest varying coordinates by about 0.1°. Commercial use needs an API key (https://open-meteo.com/en/docs/flood-api).
- 2022 event: on 16 Jun 2022 Cherrapunji recorded its third-highest rainfall in 122 years, which triggered flash floods in NE Bangladesh. About 94% of Sunamganj and over 84% of Sylhet were submerged. Over 7.2 M people were affected and about 481,827 evacuated to shelters (IFRC final report MDRBD028, https://reliefweb.int/report/bangladesh/bangladesh-floods-final-report-mdrbd028).
- UN RCO update (22 Jun 2022): about 7.2 M affected across 9 NE districts (Sylhet, Sunamganj, Moulvibazar, Habiganj, Kishoreganj, Netrakona, Brahmanbaria, Mymensingh, Sherpur); hardest hit were Sylhet, Sunamganj, Moulvibazar, Habiganj, Netrakona; about 472,856 people in about 1,605 shelters (https://bangladesh.un.org/bn/node/187390).
- Coordinates (given in the brief, consistent with the upazila list): Sylhet city 24.8949, 91.8687; Sunamganj 25.0658, 91.4073.

**[UNVERIFIED]. The owner checks these with `scripts/check_sources.py` on day 1:**
- Tile matrix set for the flood and Terra true-colour layers (expected `GoogleMapsCompatible_Level9`).
- Exact RGBA colours in GIBS flood PNG tiles (expected red/cyan/grey per the user guide).
- `MODIS_Combined_Flood_3-Day` ID (by analogy with 2-Day) and any IMERG layer ID (S4).
- The exact peak day of the 2022 flood. Sources confirm the 16 Jun rainfall trigger and the 17–22 Jun impact reporting. Replay centres on 06-20, which is defensible either way.
- Upazila coordinates in §5.7/§5.8 are approximate (±3 km) and from memory; check 2–3 of them on OpenStreetMap.
- The current default free-tier Flash model name, and the Open-Meteo data licence wording.

### 10.3 Open questions for the owner (defaults apply if no answer)
1. Repo account: `shahariar-ai` or `shahriarsharif406`? (Default: `shahariar-ai/floodguard-ai`.)
2. Is a Gemini API key from AI Studio ready for `precompute_gemini.py` today? (Default: yes. Without it, ship rules-only and label it.)
3. Should the brand line under the logo read "by Anvia Labs"? (Default: no brand line, to keep judging neutral.)
4. Moderator PIN for the public deployment: share it with judges on Devpost? (Default: yes. Put a judge PIN in the Devpost "Try it out" notes, not in the repo.)
5. Narrate the video yourself in English with Bangla snippets, or use TTS? (Default: own voice. Authenticity helps the "Learning" score.)


---
**Implementation notes (post-review):** §5.4 row `NA/NA` and `NA/NO_CELL` now return UNAVAILABLE (more honest than "river flow normal"); a failed river fetch is `unavailable`, never `no_river_cell`; GIBS HTTP 404 is `unavailable`, never "cloud". Evidence calls use blurred (~500 m) coordinates. Gemini calls disable thinking (`thinkingBudget: 0`) and retry once without it on HTTP 400. Map popups have no deep link (iframe sandbox); reports open from the "Open report" selector.
