from __future__ import annotations
from .gibs import sample_flood
from .models import Badge, RiverClass, SatClass
from .river import anomaly, series_for

FOOTER = "Evidence is context, never proof. A human moderator decides."
LABEL = {"supports": "SUPPORTS", "no_signal": "NO SIGNAL", "inconclusive": "INCONCLUSIVE · CLOUD",
         "unavailable": "UNAVAILABLE"}


def decide_badge(sat: dict, river: dict) -> tuple[Badge, str]:
    s, r = sat["class"], river["class"]
    high = r == RiverClass.HIGH
    if s == SatClass.FLOOD:
        t = "Satellite imagery shows unusual water within ~1 km of this report."
        if high:
            t += " River flow nearby was also well above normal."
        return Badge.SUPPORTS, t
    if s == SatClass.CLEAR:
        if high:
            return Badge.SUPPORTS, ("River flow nearby was well above normal; satellite saw no flood pixels "
                                    "(it can miss small or under-canopy flooding).")
        return Badge.NO_SIGNAL, ("No flood signal from satellite or river data. This does NOT mean the report is "
                                 "false — flash and street flooding are often too small to see.")
    if s == SatClass.CLOUD:
        if high:
            return Badge.INCONCLUSIVE, "Clouds blocked the satellite; river flow nearby was well above normal."
        return Badge.INCONCLUSIVE, "Clouds blocked the satellite view for this date."
    if high:
        return Badge.SUPPORTS, "River flow nearby was well above normal (satellite data unavailable)."
    if r == RiverClass.NORMAL:
        return Badge.INCONCLUSIVE, "Satellite unavailable; river flow normal."
    return Badge.UNAVAILABLE, "Evidence services unavailable — judge on report content."


def build_evidence(report: dict, live: bool = True, cache_key: str | None = None) -> dict:
    date = report["created_at"][:10]
    sat = sample_flood(report["lat"], report["lon"], date, cache_key=cache_key, live=live)
    ser = series_for(report["lat"], report["lon"], date, live=live)
    riv = anomaly(ser, date)
    badge, sentence = decide_badge(sat, riv)
    src = "+".join(sorted({sat.get("source", "none"), "cache" if (ser and ser.get("anchor")) else
                           ("live" if ser else "none")}))
    return {"sat_class": sat["class"].value, "flood_frac": sat.get("flood_frac"), "nodata_frac": sat.get("nodata_frac"),
            "sat_date": date, "river_class": riv["class"].value, "q": riv["q"], "clim_median": riv["clim_median"],
            "ratio": riv["ratio"], "pctl": riv["pctl"], "badge": badge.value, "sentence": sentence, "source": src}
