from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    RESCUE = "rescue_needed"; MEDICAL = "medical"; FOOD_WATER = "food_water"; SHELTER = "shelter"
    INFRA = "infrastructure"; POWER_TELECOM = "power_telecom"; WATER_LEVEL = "water_level"
    LIVELIHOOD = "livestock_crops"; OTHER = "other"


class Urgency(str, Enum):
    CRITICAL = "critical"; HIGH = "high"; MEDIUM = "medium"; LOW = "low"


class Status(str, Enum):
    PENDING = "pending"; REVIEW = "under_review"; VERIFIED = "verified"; REJECTED = "rejected"


class Engine(str, Enum):
    LIVE = "gemini_live"; PRE = "gemini_precomputed"; RULES = "rules"


class Badge(str, Enum):
    SUPPORTS = "supports"; NO_SIGNAL = "no_signal"; INCONCLUSIVE = "inconclusive"; UNAVAILABLE = "unavailable"


class SatClass(str, Enum):
    FLOOD = "flood_seen"; CLEAR = "clear_no_flood"; CLOUD = "clouded"; NA = "unavailable"


class RiverClass(str, Enum):
    HIGH = "above_normal"; NORMAL = "normal"; NO_CELL = "no_river_cell"; NA = "unavailable"


class Actor(str, Enum):
    HUMAN = "human_moderator"; SYSTEM = "system"; AI = "ai"


NEEDS = ["boat_rescue", "drinking_water", "food", "dry_shelter", "medical_help", "baby_supplies", "power",
         "phone_network", "road_access", "animal_shelter", "sanitation", "information"]

CATEGORY_LABEL = {
    "rescue_needed": "Rescue needed", "medical": "Medical", "food_water": "Food & water", "shelter": "Shelter",
    "infrastructure": "Infrastructure", "power_telecom": "Power / telecom", "water_level": "Water level",
    "livestock_crops": "Livestock & crops", "other": "Other",
}


@dataclass
class Analysis:
    category: Category
    urgency: Urgency
    needs: list[str]
    people_affected: int | None
    summary_en: str
    summary_bn: str | None
    location_hint: str | None
    language: str
    confidence: float
    engine: Engine
    model: str | None = None
    created_at: str = ""
    note: str = ""          # why a fallback tier was used (not stored in DB)


ANALYSIS_JSON_SCHEMA: dict = {
    "type": "object",
    "required": ["category", "urgency", "needs", "people_affected", "summary_en", "language", "confidence"],
    "properties": {
        "category": {"type": "string", "enum": [c.value for c in Category]},
        "urgency": {"type": "string", "enum": [u.value for u in Urgency]},
        "needs": {"type": "array", "maxItems": 6, "items": {"type": "string", "enum": NEEDS}},
        "people_affected": {"type": "integer", "nullable": True},
        "summary_en": {"type": "string"},
        "summary_bn": {"type": "string", "nullable": True},
        "location_hint": {"type": "string", "nullable": True},
        "language": {"type": "string", "enum": ["bn", "en", "mixed"]},
        "confidence": {"type": "number"},
    },
}
