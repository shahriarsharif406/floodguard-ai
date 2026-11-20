"""Rainfall context from the Open-Meteo Historical Weather API (free, no key). Context only, never a flood claim."""
from __future__ import annotations
from .http import http_get

API = "https://archive-api.open-meteo.com/v1/archive"
_memo: dict = {}


def daily_precip(lat: float, lon: float, start: str, end: str) -> dict:
    """{'time': [...], 'mm': [...]} or {'time': [], 'mm': [], 'error': str}. Memoised per rounded cell."""
    key = (round(lat, 1), round(lon, 1), start, end)
    if key in _memo:
        return _memo[key]
    status, data, err = http_get(API, params={"latitude": lat, "longitude": lon, "daily": "precipitation_sum",
                                              "start_date": start, "end_date": end, "timezone": "Asia/Dhaka"},
                                 timeout=15)
    if status != 200 or not data or "daily" not in data:
        return {"time": [], "mm": [], "error": err or "no data"}   # not memoised: retry next time
    d = data["daily"]
    out = {"time": d.get("time", []), "mm": [v or 0.0 for v in d.get("precipitation_sum", [])]}
    _memo[key] = out
    return out


def rain_sentence(series: dict, date: str, days: int = 3) -> str | None:
    t, mm = series.get("time") or [], series.get("mm") or []
    if date not in t:
        return None
    i = t.index(date)
    window = mm[max(0, i - days + 1): i + 1]
    return f"Rain at this location: {sum(window):.0f} mm over the last {len(window)} days (Open-Meteo reanalysis; context only)."
