from floodguard.redact import redact


def test_bd_phone_forms():
    for t in ["01712345678", "+880 1712-345678", "০১৭১২৩৪৫৬৭৮", "8801712345678"]:
        out, c = redact(f"call {t} now")
        assert "[PHONE]" in out and c["phone"] >= 1, t


def test_email_name_id():
    out, c = redact("mail a.b@x.com, my name is Rahim Uddin, NID 1234567890")
    assert "[EMAIL]" in out and "[NAME]" in out and "[ID]" in out
    out, _ = redact("আমার নাম করিম আহমেদ")
    assert "[NAME]" in out and "করিম" not in out


def test_counts_untouched():
    out, c = redact("30 people and 6 families need food")
    assert out == "30 people and 6 families need food" and sum(c.values()) == 0


def test_spaced_phone_formats():
    for t in ["017 1234 5678", "+880 1712-345678", "01712 345678"]:
        out, _ = redact(f"call {t} please")
        assert "[PHONE]" in out and "1234" not in out and "345678" not in out, out


def test_sunamganj_not_mangled():
    from floodguard.redact import redact
    out, c = redact("সুনামগঞ্জ সদরে পানি ঢুকে গেছে")
    assert "সুনামগঞ্জ" in out and c["name"] == 0
    out, c = redact("আমার নাম করিম, সিলেট")
    assert "[NAME]" in out and "করিম" not in out
