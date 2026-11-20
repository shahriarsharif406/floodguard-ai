"""GloFAS v4 river discharge via Open-Meteo Flood API, plus a simple climatology anomaly."""
from __future__ import annotations
import json
import statistics
from datetime import date as _date
from pathlib import Path
from .geo import haversine_m
from .http import http_get
from .models import RiverClass

API = "https://flood-api.open-meteo.com/v1/flood"
CACHE = Path(__file__).resolve().parent.parent / "data" / "glofas_cache.json"
_cache: dict | None = None
_live_memo: dict = {}


def fetch_series(lat: float, lon: float, start: str, end: str) -> dict:
    status, data, err = http_get(API, params={"latitude": lat, "longitude": lon, "daily": "river_discharge",
                                              "start_date": start, "end_date": end}, timeout=15)
    if status != 200 or not data or "daily" not in data:
        return {"time": [], "q": [], "lat": lat, "lon": lon, "error": err or "no data"}
    d = data["daily"]
    return {"time": d.get("time", []), "q": d.get("river_discharge", []), "lat": lat, "lon": lon}


def _load_cache() -> dict:
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
        except ValueError:
            _cache = {}
    return _cache


def cached_series(lat: float, lon: float, max_km: float = 25.0) -> dict | None:
    anchors = (_load_cache().get("anchors") or {})
    best, bd = None, 1e18
    for name, a in anchors.items():
        d = haversine_m(lat, lon, a["lat"], a["lon"]) / 1000
        if d < bd:
            best, bd = {**a, "anchor": name}, d
    return best if best and bd <= max_km else None


def series_for(lat: float, lon: float, date: str, live: bool = True) -> dict | None:
    s = cached_series(lat, lon)
    if s and date in s["time"]:
        return s
    if not live:
        return None
    key = (round(lat, 2), round(lon, 2), date[:4])
    if key in _live_memo:
        return _live_memo[key]
    y = int(date[:4])
    out = None
    for dy in (0, 0.1, -0.1):      # nudge toward the river cell (API may not pick the river)
        cand = fetch_series(lat + dy * 0.5, lon + dy * 0.5, f"{max(2003, y - 20)}-01-01", date)
        if cand["time"] and any(v is not None for v in cand["q"]):
            if out is None or statistics.fmean([v or 0 for v in cand["q"]]) > statistics.fmean([v or 0 for v in out["q"]]):
                out = cand
    _live_memo[key] = out
    return out


def _window(series: dict, date: str, half: int = 15) -> list[float]:
    d0 = _date.fromisoformat(date)
    j = d0.timetuple().tm_yday
    vals = []
    for t, q in zip(series["time"], series["q"]):
        if q is None:
            continue
        td = _date.fromisoformat(t)
        if td.year >= d0.year or td.year < 2003:
            continue
        dj = abs(td.timetuple().tm_yday - j)
        dj = min(dj, 365 - dj)
        if dj <= half:
            vals.append(float(q))
    return vals


def anomaly(series: dict | None, date: str) -> dict:
    na = {"class": RiverClass.NA, "q": None, "clim_median": None, "ratio": None, "pctl": None, "window": 0}
    if not series:
        return {**na, "class": RiverClass.NO_CELL}
    try:
        idx = series["time"].index(date)
    except ValueError:
        return na
    q = series["q"][idx]
    win = _window(series, date)
    if q is None or len(win) < 30:
        return na
    med = statistics.median(win)
    ratio = q / med if med > 0 else None
    pctl = 100.0 * sum(1 for v in win if v < q) / len(win)
    high = pctl >= 90 or (ratio is not None and ratio >= 1.5)
    return {"class": RiverClass.HIGH if high else RiverClass.NORMAL, "q": round(q, 1), "clim_median": round(med, 1),
            "ratio": round(ratio, 2) if ratio else None, "pctl": round(pctl, 1), "window": len(win)}


def sparkline_data(series: dict, date: str, before: int = 30, after: int = 5) -> dict | None:
    try:
        i = series["time"].index(date)
    except (ValueError, KeyError):
        return None
    lo, hi = max(0, i - before), min(len(series["time"]), i + after + 1)
    win = sorted(_window(series, date))
    p10 = win[int(len(win) * 0.10)] if win else None
    p90 = win[min(len(win) - 1, int(len(win) * 0.90))] if win else None
    return {"time": series["time"][lo:hi], "q": series["q"][lo:hi], "p10": p10, "p90": p90, "date": date}
