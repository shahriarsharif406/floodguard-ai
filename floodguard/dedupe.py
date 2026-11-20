from __future__ import annotations
import re
from datetime import datetime
from .geo import haversine_m
from .imaging import hamming
from .lexicon import STOPWORDS_BN, STOPWORDS_EN, SYNONYMS

_PUNCT = re.compile(r"[^\wঀ-৿]+", re.UNICODE)


def tokens(text: str) -> set[str]:
    t = (text or "").lower().replace("।", " ")
    out = set()
    for w in _PUNCT.split(t):
        if len(w) >= 2 and w not in STOPWORDS_EN and w not in STOPWORDS_BN:
            out.add(SYNONYMS.get(w, w))
    return out


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)


def find_matches(report: dict, candidates: list[dict]) -> list[dict]:
    """report/candidates carry: id, created_at, lat, lon, redacted_text, category, photo_ahash."""
    out: list[dict] = []
    t0 = tokens(report["redacted_text"])
    for c in candidates:
        if c["id"] == report.get("id"):
            continue
        hours = abs((_dt(report["created_at"]) - _dt(c["created_at"])).total_seconds()) / 3600
        dist = haversine_m(report["lat"], report["lon"], c["lat"], c["lon"])
        score = jaccard(t0, tokens(c["redacted_text"]))
        base = {"other_id": c["id"], "score": round(score, 3), "distance_m": round(dist), "hours": round(hours, 1)}
        # a re-shared photo is suspicious at ANY time gap (old images recirculate), so it is checked first
        if report.get("photo_ahash") and c.get("photo_ahash") and hamming(report["photo_ahash"], c["photo_ahash"]) <= 5:
            out.append({**base, "kind": "same_photo"})
        if hours > 72:
            continue
        if dist <= 1000 and hours <= 24 and score >= 0.45:
            out.append({**base, "kind": "duplicate"})
        elif dist <= 3000 and hours <= 48 and report.get("category") and report.get("category") == c.get("category"):
            out.append({**base, "kind": "corroborates"})
    return out
