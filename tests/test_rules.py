import json
from floodguard.rules import analyze_rules, detect_language
from floodguard.models import Category, Urgency

EXP = {1: ("water_level", "medium"), 2: ("food_water", "high"), 3: ("rescue_needed", "critical"),
       4: ("rescue_needed", "critical"), 5: ("infrastructure", "medium"), 6: ("shelter", "high"),
       7: ("power_telecom", "high"), 8: ("rescue_needed", "critical"), 9: ("livestock_crops", "medium"),
       10: ("medical", "critical"), 11: ("shelter", "high"), 12: ("food_water", "high"), 13: ("medical", "high"),
       14: ("medical", "critical"), 15: ("infrastructure", "medium"), 16: ("water_level", "low"),
       17: ("food_water", "high"), 18: ("shelter", "medium")}


def test_replay_texts_accuracy():
    rows = json.load(open("data/replay_sylhet2022.json", encoding="utf-8"))
    ok, misses = 0, []
    for r in rows:
        a = analyze_rules(r["text"], r["district"])
        if (a.category.value, a.urgency.value) == EXP[r["id"]]:
            ok += 1
        else:
            misses.append((r["id"], a.category.value, a.urgency.value))
    assert ok >= 15, misses


def test_bare_water_not_food():
    assert analyze_rules("পানি").category == Category.OTHER


def test_families_times_five():
    assert analyze_rules("6 families need rice").people_affected == 30


def test_language():
    assert detect_language("আমরা আটকা") == "bn" and detect_language("we are stuck") == "en"


def test_trapped_is_critical():
    assert analyze_rules("we are trapped on the roof").urgency == Urgency.CRITICAL
