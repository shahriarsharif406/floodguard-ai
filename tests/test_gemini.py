import pytest
from floodguard import gemini
from floodguard.config import Settings

GOOD = {"category": "rescue_needed", "urgency": "critical", "needs": ["boat_rescue", "boat_rescue", "bogus"],
        "people_affected": 4, "summary_en": "Four people trapped on a roof need a boat.", "summary_bn": None,
        "location_hint": "Sunamganj", "language": "bn", "confidence": 1.4, "status": "verified", "verified": True}


def S(**kw):
    base = dict(gemini_api_key="k", gemini_model="m", live_ai_session_cap=3, live_ai_daily_cap=150,
                gemini_timeout_s=1, moderator_pin="x", db_path=":memory:", app_mode_default="replay")
    base.update(kw)
    return Settings(**base)


def test_valid_payload_and_ignored_status():
    p = gemini.validate_payload(GOOD)
    assert p["needs"] == ["boat_rescue"] and p["confidence"] == 1.0 and "status" not in p and "verified" not in p


def test_bad_enum_raises():
    with pytest.raises(ValueError):
        gemini.validate_payload({**GOOD, "category": "nope"})


def test_prompt_has_no_coordinates():
    user = gemini.build_prompt("water here", "Sunamganj")["contents"][0]["parts"][0]["text"]
    assert user == 'District (approximate, user-selected): Sunamganj\nReport text (redacted):\n"""water here"""'


def test_caps(conn):
    ok, why = gemini.caps_allow(3, conn, S())
    assert not ok and "session cap" in why
    assert not gemini.caps_allow(0, conn, S(gemini_api_key=None))[0]
    assert gemini.caps_allow(0, conn, S())[0]


def test_offline_falls_back_to_rules(conn):
    from floodguard.analysis import analyze
    a, note, used = analyze("zzz unknown text here", None, allow_live=True, conn=conn, settings=S())
    assert a.engine.value == "rules" and not used
