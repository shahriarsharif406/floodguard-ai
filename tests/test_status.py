import pytest
from floodguard import db
from floodguard.models import Actor, Status


def test_ai_and_system_cannot_verify(seeded):
    for actor in (Actor.AI, Actor.SYSTEM):
        for st in (Status.VERIFIED, Status.REJECTED):
            with pytest.raises(PermissionError):
                db.set_status(seeded, 6, st, actor, "x", "t")


def test_human_verifies_with_audit(seeded):
    db.set_status(seeded, 6, Status.VERIFIED, Actor.HUMAN, "checked with field team", "moderator")
    assert db.get_report(seeded, 6)["status"] == "verified"
    last = db.get_audit(seeded, 6)[-1]
    assert (last["from_status"], last["to_status"], last["actor"]) == ("pending", "verified", "human_moderator")


def test_audit_note_redacted(seeded):
    db.set_status(seeded, 6, Status.REVIEW, Actor.HUMAN, "called 01712345678", "moderator")
    assert "01712345678" not in db.get_audit(seeded, 6)[-1]["note"]
