"""In-memory TTL cache for AI responses. Same honest caveat as
app.core.rate_limit's InMemoryRateLimiterBackend: this is correct for a
single-process deployment only. The `AICacheBackend` protocol is the swap
point for a Redis-backed implementation once running more than one worker
— every caller depends on `get_ai_cache()`, never on this module's dict
directly, so that swap touches one function, not every call site.

Used to avoid re-calling an LLM for an identical request (same prompt +
same image hash) within a short window — meaningfully cuts both latency
and provider cost for things like a user re-opening the same meal's
analysis, without needing a real distributed cache for this phase.
"""

import hashlib
import time
from typing import Protocol


class AICacheBackend(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str, ttl_seconds: int) -> None: ...


class InMemoryAICacheBackend:
    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}

    def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._store[key] = (value, time.monotonic() + ttl_seconds)


_backend: AICacheBackend = InMemoryAICacheBackend()


def get_ai_cache() -> AICacheBackend:
    return _backend


def make_cache_key(*parts: str) -> str:
    joined = "|".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
