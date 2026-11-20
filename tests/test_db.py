from floodguard import db, sitrep


def test_seed_idempotent_and_simulated(conn):
    db.seed_if_empty(conn); db.seed_if_empty(conn)
    rows = db.list_reports(conn, mode="replay")
    assert len(rows) == 18 and all(r["is_simulated"] == 1 for r in rows)


def test_public_coordinates_blurred(seeded):
    r = db.get_report(seeded, 3)
    assert (r["lat"], r["lon"]) != (r["lat_pub"], r["lon_pub"])


def test_sitrep_marks_simulated(seeded):
    agg = sitrep.aggregate(db.list_reports(seeded, mode="replay"))
    assert "SIMULATED" in sitrep.template(agg)
    md, eng, note = sitrep.generate(agg, allow_live=False)
    assert eng.value == "rules" and "SIMULATED" in md
