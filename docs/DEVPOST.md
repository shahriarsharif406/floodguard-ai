# Devpost submission text (paste into the form)

**Project name:** FloodGuard AI
**Tagline (≤60 chars):** Satellites see the water; people see the damage.
**Track:** Community Impact

## Inspiration
In June 2022 floods in Sylhet and Sunamganj affected over 7 million people. Satellites could map the water, but responders still struggled to learn who needed rescue first. I'm a student from Bangladesh, and I wanted to connect what satellites see with what people on the ground report, without letting an AI decide what is true.

## Problem
Citizen flood reports arrive as messy Bangla/English text, duplicated, unverified, often with personal data. Satellite flood maps show water but not human need. Responders need one prioritised, trustworthy picture.

## What it does
- Bangla/English flood reports with optional photo and map location; no accounts or contact fields.
- AI structures each report (category, urgency, needs, people affected, summary) after personal data is removed.
- Flags duplicates, corroboration and re-shared photos.
- Sets each report against NASA MODIS flood imagery and GloFAS river discharge: "evidence is context, never proof".
- Human moderators verify or reject; AI can never verify; full audit trail.
- Priority map, analytics, one-click situation report, and a June 2022 Event Replay (real satellite/river data, simulated and labelled reports).

## How we built it
Python, Streamlit, SQLite, Folium, Plotly, Pillow. NASA GIBS WMTS tiles and pixel sampling; Open-Meteo GloFAS v4 for river discharge with a climatology anomaly. Gemini free tier via REST with a strict JSON schema.

## Use of AI
Three-tier design so free-tier limits never break the demo: pre-computed Gemini results → limited live Gemini (session and daily caps) → rule-based Bangla/English fallback. Every output is labelled with its engine. PII is redacted before anything leaves the app; only redacted text and a district name are sent. Gemini output is validated against an enum schema; the AI cannot set a report to Verified. Evaluation on 30 bilingual reports: see docs/eval_results.md. AI assistants used to build: Claude Code (Opus for specification/review, Sonnet for most code) — disclosed in the README.

## Challenges
Free-tier limits and privacy terms; cloud cover and 250 m pixels in satellite data; GloFAS grid cells that miss the river; Bangla keyword rules; no live flood in November, solved with a replay.

## What I learned
_(Write 3 things in your own words, e.g. about satellite data limits, designing AI with a human in the loop, privacy by design.)_

## Accomplishments
A working end-to-end tool that is honest about what it does not know; offline-capable replay; tests for the safety rules.

## What's next
SMS/IVR intake with partners, Sentinel-1 SAR layer, BWDB gauge data, Bangla model fine-tuning, an NGO pilot.

## Built with
python, streamlit, sqlite, folium, plotly, pillow, nasa-gibs, glofas, open-meteo, gemini-api, claude-code

## Links
GitHub: https://github.com/shahriarsharif406/floodguard-ai · Live demo: _(URL)_ · Video: _(URL)_
**Try it out notes:** Moderator desk: press "Open judge preview" (no PIN, replay data only). The app starts in Replay mode; community reports in it are SIMULATED.
