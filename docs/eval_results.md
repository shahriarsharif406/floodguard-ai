# Evaluation (66 bilingual reports: 18 simulated replay + 12 synthetic + 36 fresh held-out)

The 18 replay items were used while tuning the rule lexicon, so their rule-based score is optimistic. The 12 synthetic items were written afterwards and not used for tuning (held-out). The H-items were written later in a separate batch and the rules were NOT tuned on them. Misses are listed, not hidden.

| Tier | n | category acc. | urgency acc. |
|---|---|---|---|
| Rule-based | 66 | 73% | 76% |
| Gemini (not run) | 0 | n/a | n/a |

Rule-based, tuned set (18 replay): category 89%, urgency 94%. Rule-based, fresh held-out (36 items H1+): category 69%, urgency 69%. Critical reports (all sets, n=14): 1 not rated critical by rules, 1 of them rated only medium/low. This is why every report, whatever its AI rating, goes to a human moderator. Rule-based, held-out (12 synthetic): category 58%, urgency 67%.

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
| H1 | rescue_needed/critical | rescue_needed/critical | — |
| H2 | rescue_needed/critical | rescue_needed/critical | — |
| H3 | rescue_needed/critical | rescue_needed/critical | — |
| H4 | medical/critical | medical/critical | — |
| H5 | medical/critical | medical/critical | — |
| H6 | medical/high | medical/high | — |
| H7 | medical/high | medical/high | — |
| H8 | food_water/high | medical/high ✗ | — |
| H9 | food_water/high | food_water/high | — |
| H10 | food_water/high | other/low ✗ | — |
| H11 | food_water/medium | other/low ✗ | — |
| H12 | shelter/high | shelter/medium ✗ | — |
| H13 | shelter/high | shelter/high | — |
| H14 | shelter/medium | other/low ✗ | — |
| H15 | shelter/high | other/low ✗ | — |
| H16 | infrastructure/medium | infrastructure/medium | — |
| H17 | infrastructure/medium | infrastructure/medium | — |
| H18 | infrastructure/medium | infrastructure/medium | — |
| H19 | infrastructure/medium | infrastructure/medium | — |
| H20 | power_telecom/medium | power_telecom/medium | — |
| H21 | power_telecom/medium | power_telecom/medium | — |
| H22 | power_telecom/high | other/low ✗ | — |
| H23 | water_level/medium | other/low ✗ | — |
| H24 | water_level/medium | water_level/medium | — |
| H25 | water_level/low | other/low ✗ | — |
| H26 | water_level/low | infrastructure/medium ✗ | — |
| H27 | livestock_crops/medium | livestock_crops/medium | — |
| H28 | livestock_crops/medium | livestock_crops/medium | — |
| H29 | livestock_crops/low | livestock_crops/medium ✗ | — |
| H30 | other/low | other/low | — |
| H31 | other/low | other/low | — |
| H32 | rescue_needed/critical | rescue_needed/critical | — |
| H33 | rescue_needed/high | rescue_needed/critical ✗ | — |
| H34 | food_water/high | medical/high ✗ | — |
| H35 | medical/medium | medical/medium | — |
| H36 | infrastructure/medium | other/low ✗ | — |

Caveats: small set, author-labelled, urgency labels are judgement calls; this is a sanity check, not a benchmark.