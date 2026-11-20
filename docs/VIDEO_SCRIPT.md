# FloodGuard AI — 6-minute demo video (hard cap 5:55)

Record at 1920×1080, browser zoom 90%, open the live app 5 minutes before (cold start). Narrate in your own voice (English, a few Bangla phrases). Keep the SIMULATED tag visible in every frame that shows reports.

| Time | On screen | Narration (read naturally, don't memorise) |
|---|---|---|
| 0:00–0:35 | Command Center, flood layer on, date 2022-06-20, slow zoom on red pixels | "June 2022. Seven point two million people affected by floods in north-east Bangladesh. Satellites could see the water. They couldn't see who was on a roof. I'm Shahariar, a student from Bangladesh, and this is FloodGuard AI." |
| 0:35–1:05 | Top bar + 3 KPI cards + priority queue + pitch line | "Satellites see the water; people see the damage. FloodGuard connects both, with a human in the loop. It is not a flood predictor. This view replays the real June 2022 flood: satellite and river data are real, community reports are simulated and labelled." |
| 1:05–2:05 | Submit page: paste Bangla text with a phone number → "What leaves this device" preview shows [PHONE] → Submit → analysis card with engine chip | "A citizen writes in Bangla — আমরা চার জন ছাদে আটকা। Before any AI sees it, personal data is removed. You can see exactly what leaves the device. Gemini turns the text into structured data: category, urgency, needs. And every result shows which engine made it: live Gemini, pre-computed Gemini, or a rule-based fallback, so the demo never breaks on free-tier limits." |
| 2:05–2:45 | Submit a near-duplicate → "Possible duplicate"; open #16 → "Same photo as #7" | "A second, almost identical report is flagged as a possible duplicate. A photo that was re-shared from an older event is caught by an image hash. These are suggestions for the moderator, never decisions." |
| 2:45–3:35 | Report detail: evidence card, satellite chip, river chip, sparkline | "Each report is set against NASA MODIS flood imagery and GloFAS river discharge for that place and date. Here the river was two times above its typical June level. The badge says SUPPORTS — and the footer says it plainly: evidence is context, never proof. 'No signal' never means the report is false." |
| 3:35–4:20 | Moderator: wrong PIN, correct PIN, queue by priority, Verify with note, audit trail | "Only a human moderator can verify or reject. The AI can suggest, but the code refuses: it raises a permission error if anything but a human tries. Every action is in the audit trail." |
| 4:20–4:50 | Command Center ▶ Replay stepping 06-14 → 06-25; Analytics page | "Press play and the flood unfolds day by day, reports appear, and the analytics respond." |
| 4:50–5:15 | Situation Report → generate → download | "One click gives coordinators a short situation report from aggregate counts only. Simulated data is marked as such." |
| 5:15–5:45 | About & Limits page; eval_results.md | "I'm explicit about limits: not a predictor, simulated reports, satellite pixels are 250 metres and miss flash floods. My rule-based fallback scores [X]% on held-out reports — a sanity check, not a benchmark." |
| 5:45–6:00 | Title card | "I learned [3 things you actually learned]. I built this with Claude Code and Gemini, and I'm next planning an NGO pilot. FloodGuard AI: satellites see the water, people see the damage." |

## Checklist before recording
- [ ] App URL opens in incognito; replay mode shows 18 reports
- [ ] Judge PIN known; Gemini key set (so "Gemini (live)" shows) — or say the engine honestly
- [ ] Replace [X] and the three learnings with your real ones
- [ ] Upload to YouTube (public or unlisted), ≤ 6:00, add thumbnail from `docs/thumbnails/`
