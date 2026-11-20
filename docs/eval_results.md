# Evaluation (30 bilingual reports: 18 simulated replay + 12 synthetic)

The 18 replay items were used while tuning the rule lexicon, so their rule-based score is optimistic. The 12 synthetic items were written afterwards and not used for tuning (held-out). Misses are listed, not hidden.

| Tier | n | category acc. | urgency acc. |
|---|---|---|---|
| Rule-based | 30 | 77% | 83% |
| Gemini (not run) | 0 | n/a | n/a |

Rule-based, tuned set (18 replay): category 89%, urgency 94%. Rule-based, held-out (12 synthetic): category 58%, urgency 67%.

| id | expected | rules | gemini |
|---|---|---|---|
| R1 | water_level/medium | water_level/medium | — |
| R2 | food_water/high | food_water/high | — |
| R3 | rescue_needed/critical | rescue_needed/critical | — |
| R4 | rescue_needed/critical | rescue_needed/critical | — |
| R5 | infrastructure/medium | infrastructure/medium | — |
| R6 | shelter/high | food_water/high ✗ | — |
| R7 | power_telecom/high | power_telecom/high | — |
| R8 | rescue_needed/critical | rescue_needed/critical | — |
| R9 | livestock_crops/medium | livestock_crops/medium | — |
| R10 | medical/critical | medical/critical | — |
| R11 | shelter/high | shelter/high | — |
| R12 | food_water/high | food_water/high | — |
| R13 | medical/high | medical/high | — |
| R14 | medical/critical | medical/critical | — |
| R15 | infrastructure/medium | infrastructure/medium | — |
| R16 | water_level/low | water_level/low | — |
| R17 | food_water/high | food_water/high | — |
| R18 | shelter/medium | food_water/high ✗ | — |
| E1 | rescue_needed/critical | rescue_needed/critical | — |
| E2 | medical/high | medical/high | — |
| E3 | shelter/high | other/low ✗ | — |
| E4 | infrastructure/medium | infrastructure/medium | — |
| E5 | power_telecom/medium | power_telecom/medium | — |
| E6 | water_level/medium | water_level/medium | — |
| E7 | livestock_crops/medium | rescue_needed/critical ✗ | — |
| E8 | rescue_needed/critical | rescue_needed/critical | — |
| E9 | water_level/low | other/low ✗ | — |
| E10 | food_water/high | food_water/high | — |
| E11 | water_level/medium | other/low ✗ | — |
| E12 | medical/critical | other/low ✗ | — |

Caveats: small set, author-labelled, urgency labels are judgement calls; this is a sanity check, not a benchmark.