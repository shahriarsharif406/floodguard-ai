# Architecture
```
 user ─► Submit form ─► validate ─► imaging (verify, strip EXIF, aHash)
                         │
                   redact.redact(text) ─► redacted_text
                         │
        analysis.analyze(redacted_text, district)
          ├─1 cache hit?  data/gemini_cache.json / ai_cache  ─► engine = gemini_precomputed | gemini_live
          ├─2 caps ok & key?  gemini.call_gemini()  (strict JSON schema, 8 s timeout) ─► engine = gemini_live
          └─3 rules.analyze_rules()  (EN + BN lexicon) ─────────────────────────────► engine = rules
                         │
                   db.insert_report + insert_analysis (status = pending)
                         │
     dedupe.find_matches ─► links (duplicate | corroborates | same_photo)   [suggestions only]
     evidence.build_evidence ─► gibs.sample_flood + river.anomaly ─► badge  [context, never proof]
     priority.priority(urgency × corroboration × evidence) ─► reports.priority
                         │
   Command Center map ◄──┼──► Moderator desk (PIN) ─► set_status() ─► audit_log  (AI cannot verify)
                         └──► Analytics · Situation Report (aggregates only)
```
| Module | Role |
|---|---|
| `redact.py` | PII removal before any AI call |
| `analysis.py`, `gemini.py`, `rules.py` | 3-tier analysis, schema validation, caps |
| `dedupe.py`, `imaging.py` | duplicate/corroboration, photo hash |
| `gibs.py`, `river.py`, `evidence.py` | NASA GIBS pixel sampling, GloFAS anomaly, badge table |
| `priority.py`, `sitrep.py` | queue ordering, situation report |
| `replay.py` | June 2022 Event Replay seeding (SIMULATED reports) |
| `db.py` | SQLite schema, CRUD, audit trail; `set_status` raises `PermissionError` unless the actor is a human |
