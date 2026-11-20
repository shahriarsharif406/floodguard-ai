from floodguard.priority import priority


def test_critical_not_downranked():
    assert priority("critical", 0, "no_signal", "pending") >= priority("critical", 0, "unavailable", "pending")


def test_max_and_done():
    assert priority("critical", 4, "supports", "pending") == 100
    assert priority("critical", 4, "supports", "verified") == 0
