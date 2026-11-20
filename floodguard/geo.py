from __future__ import annotations
import json
import math
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def blur(lat: float, lon: float, cell_m: int = 500) -> tuple[float, float]:
    """Snap to the centre of a ~cell_m grid cell (public map never shows exact points)."""
    dlat = cell_m / 111_320.0
    dlon = cell_m / (111_320.0 * max(math.cos(math.radians(lat)), 0.1))
    return (round((math.floor(lat / dlat) + 0.5) * dlat, 5), round((math.floor(lon / dlon) + 0.5) * dlon, 5))


@lru_cache(maxsize=1)
def districts() -> list[dict]:
    return json.loads((DATA / "districts_bd.json").read_text(encoding="utf-8"))


def district_centroid(name_en: str) -> tuple[float, float]:
    for d in districts():
        if d["name_en"].lower() == (name_en or "").lower():
            return d["lat"], d["lon"]
    return 23.8, 90.4


def nearest_shelter(lat: float, lon: float, shelters: list[dict]) -> tuple[dict, float]:
    best = min(shelters, key=lambda s: haversine_m(lat, lon, s["lat"], s["lon"]))
    return best, haversine_m(lat, lon, best["lat"], best["lon"]) / 1000.0
