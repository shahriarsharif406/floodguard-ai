# Threat model
**Assets:** reports, photos, moderator PIN, Gemini API key. **Actors:** citizen, moderator, spammer, misinformer.

| Threat | Mitigation |
|---|---|
| PII leakage (phones, names, IDs) | no contact fields; regex redaction before AI/logs; ~500 m public blur; EXIF stripped |
| Fake or re-shared photos | aHash duplicate-photo flag; human verification required |
| Prompt injection in report text | strict JSON schema + enum validation; no tools; any `status`/`verified` key ignored; AI cannot set status (`PermissionError`) |
| Spam flood | 5 submissions per 10 min per session; caps on live AI calls |
| PIN brute force | constant-time compare; 5 failures → 60 s lockout |
| Key leakage | key only in Streamlit secrets/env; `.gitignore` covers secrets |
| Misleading satellite evidence | wording "context, never proof"; NO SIGNAL never implies false; critical reports never down-ranked |
| Free-tier data use by Google | only redacted text + district sent; no photos/coordinates; documented in About page |
**Residual risks:** regex redaction can miss unusual names/numbers; session-based limits are bypassable; demo PIN is shared with judges; simulated data could be mistaken for real if tags are cropped from screenshots.
