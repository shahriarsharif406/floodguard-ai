"""PII redaction applied before any text leaves the app."""
from __future__ import annotations
import re

_BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL = re.compile(r"https?://\S+|www\.\S+")
BD_PHONE = re.compile(r"(?<!\d)(?:\+?88[\s-]?)?0?1[3-9]\d{2}[\s-]?\d{3}[\s-]?\d{3}(?!\d)")
INTL_PHONE = re.compile(r"(?<!\d)\+\d[\d\s-]{8,14}\d(?!\d)")
LONG_ID = re.compile(r"(?<!\d)(?:\d{17}|\d{13}|\d{10})(?!\d)")
NAME_EN = re.compile(r"(?i:\b(my name is|i am|this is|name:))\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})")
HONORIFIC_EN = re.compile(r"\b(?:Mr|Mrs|Ms|Md|Mohammad|Dr)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?")
NAME_BN = re.compile(r"(আমার নাম|নাম[:：]?)\s*([ঀ-৿]+(?:\s+[ঀ-৿]+){0,2})")
HONORIFIC_BN = re.compile(r"(?:জনাব|মোঃ|মো\.|মোছাঃ|বেগম)\s*[ঀ-৿]+(?:\s+[ঀ-৿]+)?")


def normalize_digits(text: str) -> str:
    return text.translate(_BN_DIGITS)


def redact(text: str) -> tuple[str, dict[str, int]]:
    t = normalize_digits(text or "")
    counts = {"phone": 0, "email": 0, "name": 0, "id": 0, "url": 0}

    def sub(pattern, repl, key):
        nonlocal t
        t, n = pattern.subn(repl, t)
        counts[key] += n

    sub(EMAIL, "[EMAIL]", "email")
    sub(URL, "[URL]", "url")
    sub(BD_PHONE, "[PHONE]", "phone")
    sub(INTL_PHONE, "[PHONE]", "phone")
    sub(LONG_ID, "[ID]", "id")
    sub(NAME_EN, r"\1 [NAME]", "name")
    sub(HONORIFIC_EN, "[NAME]", "name")
    sub(NAME_BN, r"\1 [NAME]", "name")
    sub(HONORIFIC_BN, "[NAME]", "name")
    return t, counts
