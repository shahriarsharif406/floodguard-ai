from __future__ import annotations
from .models import Badge, Status, Urgency

U = {"critical": 1.00, "high": 0.75, "medium": 0.45, "low": 0.20}
E = {"supports": 1.20, "inconclusive": 1.00, "unavailable": 1.00, "no_signal": 0.85}


def breakdown(urgency, n_corroborations: int, badge) -> tuple[float, float, float]:
    u = urgency.value if hasattr(urgency, "value") else str(urgency)
    b = badge.value if hasattr(badge, "value") else str(badge)
    c = 1 + 0.15 * min(max(n_corroborations, 0), 4)
    e = E.get(b, 1.0)
    if u == "critical":
        e = max(e, 1.0)   # satellites miss roof-level/flash floods; never down-rank life risk
    return U[u], c, e


def priority(urgency, n_corroborations: int, badge, status) -> int:
    s = status.value if hasattr(status, "value") else str(status)
    if s in ("verified", "rejected"):
        return 0
    u, c, e = breakdown(urgency, n_corroborations, badge)
    return round(100 * u * c * e / 1.92)
