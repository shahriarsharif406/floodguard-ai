from __future__ import annotations
import re
from datetime import datetime, timezone
from .geo import districts
from .lexicon import (CATEGORY_NEEDS, CATEGORY_ORDER, CRITICAL_WORDS, HIGH_WORDS, KEYWORDS, LARGE_GROUP, LOW_MARKERS,
                      VULNERABLE_WORDS)
from .models import CATEGORY_LABEL, Analysis, Category, Engine, Urgency
from .redact import normalize_digits

_BN_RANGE = re.compile(r"[ঀ-৿]")
_PEOPLE = re.compile(r"(\d{1,5})\s*(people|persons|families|family|জন|পরিবার|লোক|মানুষ)", re.I)
_UPAZILAS = [("Companiganj", "কোম্পানীগঞ্জ"), ("Chhatak", "ছাতক"), ("Gowainghat", "গোয়াইনঘাট"), ("Kanaighat", "কানাইঘাট"),
             ("Dowarabazar", "দোয়ারাবাজার"), ("Tahirpur", "তাহিরপুর"), ("Zakiganj", "জকিগঞ্জ"),
             ("Jagannathpur", "জগন্নাথপুর"), ("Bishwanath", "বিশ্বনাথ"), ("Derai", "দিরাই"), ("Kulaura", "কুলাউড়া"),
             ("Kalmakanda", "কলমাকান্দা"), ("Bishwambharpur", "বিশ্বম্ভরপুর"), ("Upashahar", "উপশহর"),
             ("Zindabazar", "জিন্দাবাজার")]


def detect_language(text: str) -> str:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return "en"
    bn = sum(1 for ch in letters if _BN_RANGE.match(ch))
    return "bn" if bn / len(letters) >= 0.30 else "en"


def _hits(text: str, words: dict[str, list[str]]) -> int:
    n = 0
    for w in words["bn"]:
        if w in text:
            n += 1
    for w in words["en"]:
        if " " in w or "'" in w:
            if w in text:
                n += 1
        elif re.search(rf"\b{re.escape(w)}\b", text):
            n += 1
    return n


def _contains(text: str, words: list[str]) -> bool:
    for w in words:
        if re.search(r"[ঀ-৿]", w) or " " in w:
            if w in text:
                return True
        elif re.search(rf"\b{re.escape(w)}\b", text):
            return True
    return False


def _location_hint(text: str, district: str | None) -> str | None:
    low = text.lower()
    for en, bn in _UPAZILAS:
        if en.lower() in low or bn in text:
            return en
    for d in districts():
        if d["name_en"].lower() in low or d["name_bn"] in text:
            return d["name_en"]
    return None


def analyze_rules(text: str, district: str | None = None) -> Analysis:
    raw = normalize_digits(text or "")
    t = raw.lower()
    scores = {c: _hits(t, KEYWORDS[c]) for c in CATEGORY_ORDER}
    best = max(CATEGORY_ORDER, key=lambda c: (scores[c], -CATEGORY_ORDER.index(c)))
    category = best if scores[best] > 0 else "other"
    total_hits = sum(scores.values())

    people = None
    for m in _PEOPLE.finditer(raw):
        n = int(m.group(1))
        if m.group(2).lower() in ("families", "family", "পরিবার"):
            n *= 5
        people = max(people or 0, n)

    critical = category == "rescue_needed" or _contains(t, CRITICAL_WORDS)
    vulnerable = _contains(t, VULNERABLE_WORDS) and any(scores[c] > 0 for c in ("medical", "food_water", "shelter"))
    if critical:
        urgency = Urgency.CRITICAL
    elif vulnerable or _contains(t, HIGH_WORDS) or (
            people and people >= LARGE_GROUP and category in ("food_water", "shelter", "medical")):
        urgency = Urgency.HIGH
    elif category in ("infrastructure", "power_telecom", "shelter", "food_water", "livestock_crops", "medical") \
            or scores["water_level"] >= 1:
        urgency = Urgency.MEDIUM
    else:
        urgency = Urgency.LOW
    if urgency in (Urgency.MEDIUM, Urgency.LOW) and _contains(t, LOW_MARKERS):
        urgency = Urgency.LOW

    needs: list[str] = []
    for c in CATEGORY_ORDER:
        if scores[c] > 0:
            for n in CATEGORY_NEEDS[c]:
                if n not in needs and n != "information":
                    needs.append(n)
    if not needs:
        needs = ["information"]
    needs = needs[:6]

    hint = _location_hint(raw, district)
    label = CATEGORY_LABEL[category]
    s = f"{urgency.value.capitalize()} {label.lower()} report"
    if hint:
        s += f" near {hint}"
    if people:
        s += f": ~{people} people affected"
    s += "."
    lang = detect_language(raw)
    return Analysis(
        category=Category(category), urgency=urgency, needs=needs, people_affected=people, summary_en=s,
        summary_bn=None, location_hint=hint, language=lang, confidence=round(min(0.9, 0.3 + 0.15 * total_hits), 2),
        engine=Engine.RULES, model=None, created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
