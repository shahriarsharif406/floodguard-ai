"""Evaluate the analysers on data/eval_set.json → docs/eval_results.md (honest accuracy, no cherry-picking).
Rule-based tier always; Gemini (pre-computed) tier for every item present in data/gemini_cache.json."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from floodguard.analysis import cache_key, load_precomputed
from floodguard.redact import redact
from floodguard.rules import analyze_rules

items = json.loads((ROOT / "data" / "eval_set.json").read_text(encoding="utf-8"))
pre = load_precomputed(); model = (pre.get("meta") or {}).get("model", "")
rows, rc = [], {"n": 0, "cat": 0, "urg": 0}; gc = {"n": 0, "cat": 0, "urg": 0}
split = {"replay": [0, 0, 0], "synthetic": [0, 0, 0], "heldout2": [0, 0, 0]}
crit = {"n": 0, "missed": 0, "under": 0}
for it in items:
    red, _ = redact(it["text"])
    r = analyze_rules(red)
    rc["n"] += 1; rc["cat"] += r.category.value == it["category"]; rc["urg"] += r.urgency.value == it["urgency"]
    sp = split[it["source"]]; sp[0] += 1; sp[1] += r.category.value == it["category"]; sp[2] += r.urgency.value == it["urgency"]
    if it["urgency"] == "critical":
        crit["n"] += 1; crit["missed"] += r.urgency.value != "critical"
        crit["under"] += r.urgency.value in ("medium", "low")
    g = (pre.get("items") or {}).get(cache_key(red, model)) if model else None
    if g:
        gc["n"] += 1; gc["cat"] += g["category"] == it["category"]; gc["urg"] += g["urgency"] == it["urgency"]
    rows.append((it["id"], it["category"], it["urgency"], r.category.value, r.urgency.value,
                 f'{g["category"]}/{g["urgency"]}' if g else "—"))
pct = lambda a, n: f"{100*a/n:.0f}%" if n else "n/a"
md = [f"# Evaluation ({rc['n']} bilingual reports: 18 simulated replay + 12 synthetic + {split['heldout2'][0]} fresh held-out)", "",
      "The 18 replay items were used while tuning the rule lexicon, so their rule-based score is optimistic. The 12 synthetic items were written afterwards and not used for tuning (held-out). The H-items were written later in a separate batch and the rules were NOT tuned on them. Misses are listed, not hidden.", "",
      "| Tier | n | category acc. | urgency acc. |", "|---|---|---|---|",
      f"| Rule-based | {rc['n']} | {pct(rc['cat'], rc['n'])} | {pct(rc['urg'], rc['n'])} |",
      f"| Gemini ({model or 'not run'}) | {gc['n']} | {pct(gc['cat'], gc['n'])} | {pct(gc['urg'], gc['n'])} |", "",
      f"Rule-based, tuned set (18 replay): category {pct(split['replay'][1], split['replay'][0])}, urgency {pct(split['replay'][2], split['replay'][0])}. Rule-based, fresh held-out ({split['heldout2'][0]} items H1+): category {pct(split['heldout2'][1], split['heldout2'][0])}, urgency {pct(split['heldout2'][2], split['heldout2'][0])}. Critical reports (all sets, n={crit['n']}): {crit['missed']} not rated critical by rules, {crit['under']} of them rated only medium/low. This is why every report, whatever its AI rating, goes to a human moderator. Rule-based, held-out (12 synthetic): category {pct(split['synthetic'][1], split['synthetic'][0])}, urgency {pct(split['synthetic'][2], split['synthetic'][0])}.", "",
      "| id | expected | rules | gemini |", "|---|---|---|---|"]
for i, ec, eu, rcat, rurg, g in rows:
    flag = "" if (ec, eu) == (rcat, rurg) else " ✗"
    md.append(f"| {i} | {ec}/{eu} | {rcat}/{rurg}{flag} | {g} |")
md += ["", "**Untuned first run on the 36 H-items: category 56%, urgency 56%, and 4 of 14 critical reports were rated only medium/low.** I then extended the lexicon (romanised Bangla, 'capsized', chest pain, insulin, etc.), so the H-item numbers above are no longer truly held-out and are optimistic. The honest generalisation estimate is the first run. A fresh batch is still needed.", "", "Caveats: small set, author-labelled, urgency labels are judgement calls; this is a sanity check, not a benchmark."]
(ROOT / "docs" / "eval_results.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md[:9]))
