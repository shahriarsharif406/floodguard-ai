"""NASA GIBS WMTS helpers: tile URLs for Folium and pixel sampling for evidence."""
from __future__ import annotations
import io
import json
import math
from pathlib import Path
from PIL import Image
from .http import http_get
from .models import SatClass

LAYERS: dict[str, dict] = {
    "flood2": {"id": "MODIS_Combined_Flood_2-Day", "ext": "png", "matrix": "GoogleMapsCompatible_Level9",
               "max_native": 9, "label": "MODIS Flood (2-day composite, ~250 m)", "opacity": 0.75},
    "flood3": {"id": "MODIS_Combined_Flood_3-Day", "ext": "png", "matrix": "GoogleMapsCompatible_Level9",
               "max_native": 9, "label": "MODIS Flood (3-day, fewer false positives)", "opacity": 0.75},
    "truecolor": {"id": "MODIS_Terra_CorrectedReflectance_TrueColor", "ext": "jpg",
                  "matrix": "GoogleMapsCompatible_Level9", "max_native": 9, "label": "MODIS Terra true colour",
                  "opacity": 1.0},
    "imerg": {"id": "IMERG_Precipitation_Rate", "ext": "png", "matrix": "GoogleMapsCompatible_Level6",
              "max_native": 6, "label": "NASA IMERG rainfall rate (~10 km)", "opacity": 0.55},
}
BASE = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best"
SAMPLES = Path(__file__).resolve().parent.parent / "data" / "gibs_samples.json"
_samples_cache: dict | None = None


def tile_url(layer_key: str, date: str) -> str:
    L = LAYERS[layer_key]
    return f"{BASE}/{L['id']}/default/{date}/{L['matrix']}/{{z}}/{{y}}/{{x}}.{L['ext']}"


def _real_url(layer_key: str, date: str, z: int, y: int, x: int) -> str:
    return tile_url(layer_key, date).format(z=z, y=y, x=x)


def lonlat_to_pixel(lat: float, lon: float, z: int) -> tuple[int, int, int, int]:
    n = 2 ** z
    fx = (lon + 180.0) / 360.0 * n
    fy = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return int(fx), int(fy), int((fx - int(fx)) * 256), int((fy - int(fy)) * 256)


def classify_pixel(r: int, g: int, b: int, a: int) -> str:
    if a < 20:
        return "none"
    if r >= 150 and g < 110 and b < 110:
        return "flood"
    if g >= 150 and b >= 150 and r < 120:
        return "water"
    return "nodata"


def classify_tile(png: bytes, px: int, py: int, half: int = 3) -> dict:
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    counts = {"flood": 0, "water": 0, "nodata": 0, "none": 0}
    total = 0
    for yy in range(max(0, py - half), min(im.height, py + half + 1)):
        for xx in range(max(0, px - half), min(im.width, px + half + 1)):
            counts[classify_pixel(*im.getpixel((xx, yy)))] += 1
            total += 1
    total = max(total, 1)
    ff, wf, nf = counts["flood"] / total, counts["water"] / total, counts["nodata"] / total
    if ff >= 0.04:
        cls = SatClass.FLOOD
    elif nf >= 0.5:
        cls = SatClass.CLOUD
    else:
        cls = SatClass.CLEAR
    return {"class": cls, "flood_frac": round(ff, 3), "water_frac": round(wf, 3), "nodata_frac": round(nf, 3)}


def _cached_sample(key: str) -> dict | None:
    global _samples_cache
    if _samples_cache is None:
        try:
            _samples_cache = json.loads(SAMPLES.read_text(encoding="utf-8")) if SAMPLES.exists() else {}
        except ValueError:
            _samples_cache = {}
    v = _samples_cache.get(key)
    if v:
        return {**v, "class": SatClass(v["class"]), "source": "cache"}
    return None


def sample_flood(lat: float, lon: float, date: str, cache_key: str | None = None, live: bool = True) -> dict:
    if cache_key:
        hit = _cached_sample(cache_key)
        if hit:
            return hit
    if not live:
        return {"class": SatClass.NA, "flood_frac": None, "water_frac": None, "nodata_frac": None, "source": "none"}
    z = LAYERS["flood2"]["max_native"]
    x, y, px, py = lonlat_to_pixel(lat, lon, z)
    status, data, err = http_get(_real_url("flood2", date, z, y, x), timeout=10, as_bytes=True)
    if status == 200 and data:
        try:
            return {**classify_tile(data, px, py), "source": "live"}
        except Exception:  # noqa: BLE001
            pass
    return {"class": SatClass.NA, "flood_frac": None, "water_frac": None, "nodata_frac": None, "source": "none"}
