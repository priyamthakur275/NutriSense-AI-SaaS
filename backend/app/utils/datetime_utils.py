"""Datetime helpers.

SQLite (used for local dev) does not truly store timezone-aware timestamps
the way Postgres does — `DateTime(timezone=True)` columns round-trip as
*naive* datetimes on SQLite, even though the same model works correctly
against Postgres. Comparing a naive value against `datetime.now(timezone.utc)`
raises `TypeError: can't compare offset-naive and offset-aware datetimes`.

`ensure_aware` normalizes either case so comparisons are safe regardless of
which backend loaded the value. Every model property that compares a
stored timestamp against "now" (token expiry, account lockout, etc.) should
go through this rather than comparing `self.some_datetime` directly.
"""

from datetime import datetime, timezone


def ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
