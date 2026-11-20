"""Run on a machine with internet:  python scripts/check_sources.py
Probes NASA GIBS (tile matrix sets, flood layer IDs, pixel colours) and Open-Meteo; prints what to put in gibs.LAYERS."""
import io, sys
from collections import Counter
from pathlib import Path
import requests
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from floodguard.gibs import BASE, lonlat_to_pixel

DATE, LAT, LON = "2022-06-20", 24.8949, 91.8687
for layer, ext in [("MODIS_Combined_Flood_2-Day", "png"), ("MODIS_Combined_Flood_3-Day", "png"),
                   ("MODIS_Terra_CorrectedReflectance_TrueColor", "jpg")]:
    for lvl in (9, 8, 7, 6):
        z = lvl
        x, y, px, py = lonlat_to_pixel(LAT, LON, z)
        url = f"{BASE}/{layer}/default/{DATE}/GoogleMapsCompatible_Level{lvl}/{z}/{y}/{x}.{ext}"
        r = requests.get(url, timeout=20)
        ok = r.status_code == 200 and r.headers.get("content-type", "").startswith("image")
        print(f"{layer:45s} Level{lvl} z={z} -> {r.status_code} {'IMAGE' if ok else ''}")
        if ok:
            if ext == "png":
                im = Image.open(io.BytesIO(r.content)).convert("RGBA")
                print("   top RGBA values:", Counter(im.getdata()).most_common(6))
            break
r = requests.get("https://flood-api.open-meteo.com/v1/flood", params={"latitude": 24.89, "longitude": 91.87,
                 "daily": "river_discharge", "start_date": "2022-06-15", "end_date": "2022-06-21"}, timeout=20)
print("Open-Meteo:", r.status_code, r.json().get("daily", {}).get("river_discharge"))
