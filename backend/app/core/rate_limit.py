"""Rate-limiting hooks.

This is an in-memory, single-process limiter — correct for local dev and a
single-instance deployment, but NOT correct once the API runs behind more
than one worker/replica (each process would track its own counters). The
`RateLimiterBackend` protocol below is the seam for swapping in a
Redis-backed implementation (e.g. a sliding-window counter via `INCR` +
`EXPIRE`) in a real production rollout without touching call sites — every
endpoint depends on `RateLimiter(...)`, not on this module's internals.
"""

import time
from collections import defaultdict
from typing import Protocol

from fastapi import Request

from app.core.exceptions import RateLimitExceededError


class RateLimiterBackend(Protocol):
    def hit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        """Record one hit for `key`. Returns (allowed, retry_after_seconds)."""
        ...


class InMemoryRateLimiterBackend:
    """Fixed-window counter per key, held in process memory."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)

    def hit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = time.monotonic()
        window_start = now - window_seconds

        timestamps = self._hits[key]
        # Drop anything outside the current window.
        timestamps[:] = [t for t in timestamps if t > window_start]

        if len(timestamps) >= limit:
            retry_after = int(window_seconds - (now - timestamps[0])) + 1
            return False, max(retry_after, 1)

        timestamps.append(now)
        return True, 0


_backend: RateLimiterBackend = InMemoryRateLimiterBackend()


def get_rate_limiter_backend() -> RateLimiterBackend:
    return _backend


class RateLimiter:
    """FastAPI dependency: `Depends(RateLimiter(times=5, seconds=60))`.

    Keys on client IP + the given `scope` name, so `/auth/login` and
    `/auth/register` maintain independent counters even for the same caller.
    """

    def __init__(self, *, times: int, seconds: int, scope: str) -> None:
        self.times = times
        self.seconds = seconds
        self.scope = scope

    def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{self.scope}:{client_ip}"

        allowed, retry_after = _backend.hit(key, self.times, self.seconds)
        if not allowed:
            raise RateLimitExceededError(retry_after_seconds=retry_after)
