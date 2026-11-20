"""Run LOCALLY (internet needed):  python scripts/precompute_evidence.py
Writes data/glofas_cache.json (river discharge per anchor, 2003-01-01..2022-07-15) and data/gibs_samples.json
(satellite pixel class per replay report/date). Commit both so the replay works offline."""
import json, statistics, sys, time
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from floodguard.gibs import sample_flood
from floodguard.river import fetch_series

D = Path(__file__).resolve().parent.parent / "data"
ANCHORS = {"sylhet_surma": (24.89, 91.87), "sunamganj_surma": (25.07, 91.40), "companiganj_piyain": (25.05, 91.78),
           "kanaighat_surma": (25.00, 92.26), "sheola_kushiyara": (24.86, 92.18), "derai_kalni": (24.79, 91.35)}
out = {"anchors": {}, "meta": {"fetched_on": date.today().isoformat(), "source": "Open-Meteo Flood API, GloFAS v4"}}
for name, (lat, lon) in ANCHORS.items():
    best = None
    for dlat in (-0.05, 0, 0.05):
        for dlon in (-0.05, 0, 0.05):
            s = fetch_series(lat + dlat, lon + dlon, "2003-01-01", "2022-07-15")
            time.sleep(0.5)
            if s["time"] and any(v is not None for v in s["q"]):
                m = statistics.fmean([v or 0 for v in s["q"]])
                if best is None or m > best[0]:
                    best = (m, s)
    if best:
        out["anchors"][name] = {"lat": lat, "lon": lon, "time": best[1]["time"], "q": best[1]["q"],
                                "snapped_to": [best[1]["lat"], best[1]["lon"]]}
        print("ok", name, "mean", round(best[0], 1))
    else:
        print("NO DATA", name)
(D / "glofas_cache.json").write_text(json.dumps(out), encoding="utf-8")
samples = {}
for r in json.loads((D / "replay_sylhet2022.json").read_text(encoding="utf-8")):
    d = r["created_at"][:10]
    smp = sample_flood(r["lat"], r["lon"], d)
    if smp["source"] != "none":
        samples[f"{r['id']}|{d}"] = {k: (v.value if hasattr(v, "value") else v) for k, v in smp.items()}
    print(r["id"], d, smp["class"].value)
(D / "gibs_samples.json").write_text(json.dumps(samples, indent=1), encoding="utf-8")
print("written glofas_cache.json and gibs_samples.json")
