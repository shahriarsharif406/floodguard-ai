import io
from PIL import Image
from floodguard import evidence, gibs, river
from floodguard.models import Badge, RiverClass, SatClass

S = lambda c: {"class": c}
R = lambda c: {"class": c}
TABLE = [
    (SatClass.FLOOD, RiverClass.NORMAL, Badge.SUPPORTS), (SatClass.FLOOD, RiverClass.HIGH, Badge.SUPPORTS),
    (SatClass.CLEAR, RiverClass.HIGH, Badge.SUPPORTS), (SatClass.CLEAR, RiverClass.NORMAL, Badge.NO_SIGNAL),
    (SatClass.CLEAR, RiverClass.NO_CELL, Badge.NO_SIGNAL), (SatClass.CLOUD, RiverClass.HIGH, Badge.INCONCLUSIVE),
    (SatClass.CLOUD, RiverClass.NORMAL, Badge.INCONCLUSIVE), (SatClass.NA, RiverClass.HIGH, Badge.SUPPORTS),
    (SatClass.NA, RiverClass.NORMAL, Badge.INCONCLUSIVE), (SatClass.NA, RiverClass.NA, Badge.UNAVAILABLE),
    (SatClass.NA, RiverClass.NO_CELL, Badge.UNAVAILABLE)]


def test_badge_table():
    for s, r, exp in TABLE:
        assert evidence.decide_badge(S(s), R(r))[0] == exp, (s, r)


def test_no_signal_sentence_is_honest():
    assert "does NOT mean the report is false" in evidence.decide_badge(S(SatClass.CLEAR), R(RiverClass.NORMAL))[1]


def _tile(color):
    b = io.BytesIO(); Image.new("RGBA", (256, 256), color).save(b, "PNG"); return b.getvalue()


def test_pixel_classifier():
    assert gibs.classify_tile(_tile((255, 40, 40, 255)), 128, 128)["class"] == SatClass.FLOOD
    assert gibs.classify_tile(_tile((0, 0, 0, 0)), 128, 128)["class"] == SatClass.CLEAR
    assert gibs.classify_tile(_tile((200, 200, 200, 200)), 128, 128)["class"] == SatClass.CLOUD


def _series(spike):
    from datetime import date, timedelta
    d, t, q = date(2003, 1, 1), [], []
    while d <= date(2022, 7, 15):
        t.append(d.isoformat()); q.append(100.0 + (d.timetuple().tm_yday % 7)); d += timedelta(days=1)
    i = t.index("2022-06-20"); q[i] = 300.0 if spike else 100.0
    return {"time": t, "q": q, "lat": 25, "lon": 91}


def test_anomaly():
    hi = river.anomaly(_series(True), "2022-06-20")
    assert hi["class"] == RiverClass.HIGH and hi["ratio"] > 1.5
    assert river.anomaly(_series(False), "2022-06-20")["class"] == RiverClass.NORMAL
    assert river.anomaly(_series(True), "2030-01-01")["class"] == RiverClass.NA
