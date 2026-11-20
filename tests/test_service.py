from floodguard import db
from floodguard.service import submit_report


def test_submit_redacts_and_stores(seeded):
    res = submit_report(seeded, text="Water rising, call 01712345678 we are 5 people", district="Sunamganj",
                        lat=25.07, lon=91.41, location_source="district", photo=None, mode="replay",
                        replay_date="2022-06-20", allow_live=False, live_evidence=False)
    r = db.get_report(seeded, res["id"])
    assert "01712345678" not in r["redacted_text"] and "[PHONE]" in r["redacted_text"]
    assert r["is_simulated"] == 0 and r["user_during_replay"] == 1 and r["status"] == "pending"
