from floodguard import db
from floodguard.dedupe import find_matches, tokens


def test_bn_tokenisation_drops_danda():
    assert "।" not in "".join(tokens("উদ্ধার করুন। নৌকা দরকার।"))


def test_replay_duplicate_3_4(seeded):
    kinds = {(l["other_id"], l["kind"]) for l in db.get_links(seeded, 4)}
    assert (3, "duplicate") in kinds


def test_corroborates_and_far():
    a = {"id": 1, "created_at": "2022-06-16T10:00", "lat": 25.0, "lon": 91.4, "redacted_text": "flood road cut", "category": "infrastructure", "photo_ahash": None}
    b = {"id": 2, "created_at": "2022-06-17T16:00", "lat": 25.0225, "lon": 91.4, "redacted_text": "bridge broken", "category": "infrastructure", "photo_ahash": None}
    assert [m["kind"] for m in find_matches(a, [a, b])] == ["corroborates"]
    b["lat"] = 25.04
    assert find_matches(a, [a, b]) == []


def test_same_photo_seed(seeded):
    assert any(l["kind"] == "same_photo" for l in db.get_links(seeded, 16))
