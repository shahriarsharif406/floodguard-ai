# FloodGuard AI: mid-way review (Opus, 2026-11-20)

Scope: `app.py`, `floodguard/*.py`, `pages/*.py`, `tests/`, plus a quick look at `scripts/precompute_*.py`.
How I checked: `python3 -m pytest -q` passed (33 tests). I ran AppTest smoke checks with `FG_OFFLINE=1` and a fresh DB: all 7 pages render, then I tried mode switching, date stepping, submits at different replay dates, moderator unlock and SitRep generation. I also read the seeded DB rows.
Not verifiable here (no network): GIBS tile matrix and colours, the live Gemini call, Open-Meteo, and whether the CARTO basemap needs a key (see M1).

Severity: **BLOCKER** = crashes or breaks the hero demo · **MAJOR** = misleads judges or visibly fails a storyboard beat · **MINOR** = polish or hardening.

---

## BLOCKERS

### B1. "▶ Switch to Replay" crashes the app (confirmed in AppTest)
`pages/1_command_center.py:31-32` sets `st.session_state["mode_label"]` after `app.py:26` has already created the sidebar radio with that key. The result is `StreamlitWidgetAlreadyInstantiatedError`, which appears every time someone presses the primary CTA in Live mode.
**Fix:** use a callback, which runs before widgets are built:
```python
def _to_replay(): st.session_state["mode_label"] = "Replay 2022"
st.button("▶ Switch to Replay", type="primary", width="stretch", on_click=_to_replay)
```

### B2. Hero evidence is empty: every replay report shows UNAVAILABLE and "Rule-based fallback"
`data/` has no `glofas_cache.json`, `gibs_samples.json` or `gemini_cache.json`. In the seeded DB, all 18 rows have `badge=unavailable`, `sat_class=unavailable`, `river_class=no_river_cell` and `engine=rules`. So none of the storyboard beats work offline: the "FLOOD SEEN / ABOVE NORMAL 2.4×" evidence card (2:45), the sparkline, Analytics chart (d), and the "Gemini (pre-computed)" chips. The scripts now exist, so the owner has to run them on a networked machine **before** M3 can be called done:
`python scripts/check_sources.py` → `python scripts/precompute_evidence.py` → `python scripts/precompute_gemini.py` (after the M2 fix below) → commit the three JSON files → delete `floodguard.db` so the DB re-seeds.
Also, `replay.py:48-49` builds the GIBS cache key from the **DB rowid**, but `precompute_evidence.py:37` uses the **JSON id**. They only match on a fresh DB that has no earlier rows. **Fix:** in `replay.py`, use `cache_key=f"{r['id']}|{r['created_at'][:10]}"`.

---

## MAJOR

### M1. CARTO dark basemap may need an API key now [UNVERIFIED, check on day 1]
The installed `xyzservices 2026.9.1` warns, on every `folium.TileLayer("CartoDB dark_matter")`, that "CartoDB tiles now require an API key", and strips the key placeholder. If this is true, all four maps get a black base, and that hurts every screenshot. Open the app online and look. If tiles fail, pass an explicit URL template with attribution (still CARTO if it works without a key), or fall back to `"Esri.WorldDarkGrayBase"` / OSM with a CSS darken. Spots: `ui.py:122`, `2_submit_report.py:37`, `3_report_detail.py:103`. Pin `xyzservices` in requirements once a working choice is found.

### M2. Live Gemini will probably return empty or truncated output (gemini-2.5-flash "thinking")
On 2.5 models, thinking tokens count against `maxOutputTokens`. With `512` (`gemini.py:33`) and `700` (`sitrep.py:72`), a response can end with `finishReason=MAX_TOKENS` and no `parts[0].text`. Analysis then falls to "invalid response → rules", the SitRep is cut short, and `precompute_gemini.py` fails on most items.
**Fix:** add `"thinkingConfig": {"thinkingBudget": 0}` to both `generationConfig` blocks and raise the limits to ~1024. Then verify with one real call in `check_sources.py`.

### M3. Map popup "Open details →" link is dead
`ui.py:144` uses `<a href='/report?id=N' target='_top'>`, but the streamlit-folium iframe sandbox has `allow-popups` and no `allow-top-navigation` (checked in the Streamlit 1.67 static bundle). The browser blocks the click.
**Fix (minimal):** `target='_blank'` (a new tab means a new session, so state resets). **Better:** `st_folium(..., returned_objects=["last_object_clicked_tooltip"])`, parse `#id` from the tooltip, then call `state.goto_detail(id)`.

### M4. `goto_detail` loses the `?id=`
`state.py:54-55`: `st.switch_page()` clears query params unless they are passed explicitly (Streamlit ≥1.4x). The page still works through `session_state["detail_id"]`, but the URL cannot be shared and a reload falls back to the last-viewed id.
**Fix:** `st.switch_page("pages/3_report_detail.py", query_params={"id": str(report_id)})` and drop the line before it. Also guard `int(qid)` at `3_report_detail.py:17` (`?id=abc` crashes).

### M5. Duplicate and corroboration beats fail at the default replay date (confirmed)
Submitting a copy of #3 at the landing date 2022-06-20 gives **no matches**, because the time gap is over 72 h (`dedupe.py:44`). At 06-16 it works. There are also **zero `corroborates` links** among the 18 seeds, so "Corroborated by N nearby reports" never appears unless the presenter creates one. Storyboard 2:05 ("Corroborates #7", which is 06-17 10:00) only works with the date set to 06-17 or 06-18.
**Fix:** (a) put "set date to 06-16/06-17 before the duplicate demo" in the recording script, or (b) when `mode=="replay"`, default the Submit page's `replay_date` to the date of the report being imitated. Optionally move one seed (e.g. #12 Jagannathpur → near #2) so the map shows a corroboration out of the box.
Related: with no map click, the location is the district centroid. A verbatim copy of #3 then landed 1007 m away, which counts as `corroborates`, not `duplicate`. Consider treating `location_source=="district"` + same district + jaccard ≥ 0.6 as a duplicate.

### M6. SitRep "Only verified" toggle does nothing for the report; hotspots are unverified but not labelled
`6_situation_report.py:17`: `agg_src if not only_ver else agg_src` (both branches are the same). Priority is 0 for verified rows, so "Hotspots (top 5 by priority)" (`sitrep.py:15-16, 35-37`) **only lists unverified reports** under a neutral heading. A coordinator can read them as confirmed.
**Fix:** when `only_ver`, aggregate counts, needs and verified incidents from verified rows, and keep `critical_unverified` as a separately labelled list. Rename the heading to "Hotspots — awaiting human verification" (or rank hotspots by raw score with a status stamp). Also: the Gemini path relies on the prompt alone to write "SIMULATED". Prepend a fixed line in code when `agg["simulated"]`.

### M7. Analytics chart (d) is the screenshot-07 hero, and without the cache it shows a developer instruction
`5_analytics.py:61` prints "Run scripts/precompute_evidence.py…" inside a judge-facing chart. It also lacks the climatological median band from spec §6.6(d).
**Fix:** after B2, add a median/p10–p90 band (reuse `river._window`) and replace the annotation with "River data not cached".

### M8. Moderator PIN default and lockout
`config.py:37` falls back to `2468`, which is in the public spec and repo. If `MODERATOR_PIN` is missing on Cloud, anyone can verify or reject.
**Fix:** when `on_cloud` and the PIN is unset, disable the desk with a banner. The lockout (`4_moderator.py:28-31`) lives in session state, so a page reload bypasses it. That is acceptable for a demo, but say so in the threat model.

### M9. Live evidence wording claims cloud with no evidence
`gibs.py:98-99` maps HTTP 404 (tile not produced yet, which is common for "today" in Live mode) to `SatClass.CLOUD`. The card then says "Clouds blocked the satellite view". That is a factual claim, so it violates the honesty rule.
**Fix:** return `SatClass.NA` on 404. Default the Live date to **yesterday** (`state.py:43` → `ds[-2]`), because the NRT composite lags.
Related: `river.anomaly` returns `NO_CELL` whenever `series is None` (`river.py:85-86`), including when Open-Meteo is down in live mode. With satellite CLEAR, the card then says "No flood signal from satellite **or river data**". **Fix:** have `series_for` return a sentinel (`{"error":...}`) on fetch failure → `RiverClass.NA`.

---

## MINOR

1. **Time zones mixed** (`service.py:22-25`): replay user reports get `replay_date` + **UTC** HH:MM, while seeds are **BST**, so `hours` in dedupe is off by 6 h. Use `datetime.now(ZoneInfo("Asia/Dhaka"))` for replay. Note in the code that replay `created_at` is BST-naive, live is UTC (spec §3.4 says "UTC"). The `until` filter (`state.py:49`) is fine for both formats.
2. **Exact coordinates sent to Open-Meteo/NASA** (`service.py:40`, `3_report_detail.py:85`): evidence fetches use exact lat/lon. The GloFAS cell is about 5 km, so use `lat_pub/lon_pub` for all third-party calls. It costs nothing and keeps the privacy claim clean.
3. **Detail page does slow network calls on public view** (`3_report_detail.py:22-30`): a report still `unavailable` triggers `refresh_evidence` (up to ~55 s: 3 Open-Meteo calls at 15 s + GIBS at 10 s) once per session per report, and writes an `evidence_refreshed` audit row each time. Skip it for `mode=="replay"` once caches exist, and lower the timeouts to about 6 s.
4. **Moderator note persists across reports and actions** (`4_moderator.py:67`): after Verify on #6, the same note is pre-filled for #8. Give the text_area `key=f"note_{pick}"`. In addition, `disabled=not ok_note` (lines 72-75) means typing a note and then clicking Verify needs **two clicks** (blur reruns first), which is awkward on camera. Keep the button enabled and validate on click with `st.warning`.
5. **Seeded decisions look like real human actions**: the audit list shows `human_moderator` (`4_moderator.py:80`) for rows whose `actor_label='seed'`. Display `actor_label` and add "(simulated)" when it equals `seed`.
6. **Live default mode breaks the radio** (`state.py:21`): `"Live"` is not an option (`"Live (today)"`). Use the exact label.
7. **Redaction gap**: the `017 1234 5678` (3-4-4) phone form is not caught. Add `(?<!\d)0?1[3-9]\d[\s-]?\d{4}[\s-]?\d{4}(?!\d)` to `BD_PHONE` handling, plus a test.
8. **Precomputed cache trusted blindly** (`analysis.py:37`): run `validate_payload(item)` before `payload_to_analysis`, so a bad cache entry cannot crash `seed`. Also, `ai_cache` hits are labelled "Gemini (live)" (`analysis.py:41`). Use the note "cached live result" in the chip tooltip.
9. **SitRep card wrapper is broken** (`6_situation_report.py:29-31`): separate `st.markdown('<div class="fg-card">')` / `('</div>')` calls do not wrap the markdown, so an empty card box renders. Use `with st.container(border=True): st.markdown(md)`. Spec controls also call for a date range.
10. **SitRep sends unverified summaries to Gemini**: spec §6.6 says "summaries of verified reports" only. `aggregate()` also sends hotspot and critical-unverified summaries. They are AI or rules output from redacted text, so the risk is low, but either align the code or update the spec sentence.
11. **Submit page copy**: "What leaves this device (to AI)" is inaccurate, because raw text does reach the server and DB for moderators. Rename it to "What is sent to the AI". Also show "USER-SUBMITTED DURING REPLAY (not historical)" on the success card, not only on the detail page.
12. **Pick-map click survives a district change** (`2_submit_report.py:33-47`): the `st_folium` value persists, so the old click re-applies under the new district. Use a district-specific key: `key=f"pick_map_{district}"`.
13. **Replay play loop**: every 1.2 s frame rebuilds the folium iframe (flicker, tiles reload, pan/zoom lost). Fine for the step buttons. For recording, try 2.0 s frames or use ◀/▶. `playing` stays True when navigating away and resumes later. Reset it in other pages or on page entry.
14. **Spec deviation, evidence table**: `evidence.py:31-33` returns UNAVAILABLE for satellite NA + river NO_CELL, while §5.4 says INCONCLUSIVE "river flow normal". The code is **more honest** (no river cell ≠ normal flow). Keep it and update SPEC §5.4.
15. **Public error details**: add `[client] showErrorDetails = "none"` to `config.toml` for the Cloud deployment.
16. **Tests missing vs §7**: `test_sitrep.py` (Gemini down → template; "Only verified" honoured), Gemini timeout/429 via `http_post` monkeypatch, an AppTest smoke test (would have caught B1), and `tests/fixtures/`. A 20-line `tests/test_app_smoke.py` that runs every page plus the Live→Replay CTA under `FG_OFFLINE=1` is the best value per line.
17. **UI polish for screenshots (§6)**: moderator table → `st.column_config.ProgressColumn` for score and a status column; no district filter and no "age" column (spec). The priority queue rows have no per-row link (a selectbox is used instead). The rules-engine summaries are mechanical ("Critical rescue needed report.") and have no `summary_bn`, so the cards look thin until the Gemini cache lands (B2/M2). The `.q-row` CSS diverges from the spec grid, which is acceptable.

---

## Safety and trust checklist (spec §0, §4)

| Rule | Status |
|---|---|
| AI can never set Verified/Rejected | **OK**: `db.set_status` raises for non-HUMAN; Gemini `status` keys are ignored; tested. |
| Redaction before anything leaves | **OK** for analysis, `ai_cache` key/payload, `location_hint` (re-redacted), and audit notes (`db.audit` redacts). SitRep sends derived summaries only (MINOR 10). |
| Only redacted text + district to Gemini | **OK** (`build_prompt`; tested no coordinates). |
| No raw_text / PII in logs | **OK**: no `logging` or `print` anywhere; the generic `except` in Submit hides details. |
| EXIF stripped | **OK**: full re-encode to JPEG after `exif_transpose`; tested. |
| Public views: no exact coordinates or raw text | **OK** on map, popups, detail, mini map, shelter distance, analytics and exports (all `lat_pub`). Raw text appears only on the Moderator desk. Third-party fetches use exact coordinates (MINOR 2). |
| Moderator PIN | `hmac.compare_digest` OK; default PIN and session-only lockout (M8). |
| SIMULATED/DEMO tags | Top bar + banner on every page, popups, detail, moderator table, exports column, template SitRep. Gaps: Gemini SitRep (M6) and seeded audit rows (MINOR 5). |
| No predict/confirm/proof claims | **OK**: footer and evidence wording match §5.4. One wrong factual claim: "clouds blocked" on HTTP 404 (M9). |

## Suggested fix order (about 2–3 h before M3 sign-off)
B1 → M2 → B2 (run scripts, fix cache key) → M3/M4 → M6 → M9 → M5 (demo script) → M1 (check online) → M7 → MINOR 4, 5, 6, 9, 11 → smoke test (MINOR 16).
