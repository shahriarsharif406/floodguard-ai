"""Run LOCALLY with your own key:  set GEMINI_API_KEY=...   then   python scripts/precompute_gemini.py
Calls Gemini once per replay/eval text (redacted first), writes data/gemini_cache.json, commit that file.
Resumable: existing entries are kept. Sleeps between calls to respect free-tier limits."""
import json, os, sys, time
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from floodguard.analysis import CACHE_FILE, cache_key
from floodguard.config import get_settings
from floodguard.gemini import GeminiUnavailable, call_gemini
from floodguard.redact import redact

D = Path(__file__).resolve().parent.parent / "data"
s = get_settings()
if not s.gemini_api_key:
    sys.exit("Set GEMINI_API_KEY first (Google AI Studio key).")
cache = json.loads(CACHE_FILE.read_text(encoding="utf-8")) if CACHE_FILE.exists() else {"items": {}}
cache["meta"] = {"model": s.gemini_model, "generated_on": date.today().isoformat()}
texts = [r["text"] for r in json.loads((D / "replay_sylhet2022.json").read_text(encoding="utf-8"))]
texts += [e["text"] for e in json.loads((D / "eval_set.json").read_text(encoding="utf-8")) if e["source"] != "replay"]
ok = fail = 0
for t in texts:
    red, _ = redact(t)
    key = cache_key(red, s.gemini_model)
    if key in cache["items"]:
        continue
    try:
        a = call_gemini(red, None, s)
    except GeminiUnavailable as e:
        fail += 1; print("fail:", e); time.sleep(10); continue
    cache["items"][key] = {"category": a.category.value, "urgency": a.urgency.value, "needs": a.needs,
                           "people_affected": a.people_affected, "summary_en": a.summary_en, "summary_bn": a.summary_bn,
                           "location_hint": a.location_hint, "language": a.language, "confidence": a.confidence}
    ok += 1; print("ok", ok, a.category.value, a.urgency.value)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    time.sleep(6)
print(f"done: {ok} new, {fail} failed, {len(cache['items'])} cached → {CACHE_FILE}")
