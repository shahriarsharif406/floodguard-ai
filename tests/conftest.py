import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["FG_OFFLINE"] = "1"      # no network in tests
import pytest
from floodguard import db


@pytest.fixture()
def conn():
    c = db.connect(":memory:")
    db.init_db(c)
    return c


@pytest.fixture()
def seeded(conn):
    db.seed_if_empty(conn)
    return conn
