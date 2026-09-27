"""Async retry-with-backoff, purpose-built for LLM provider calls rather
than a generic decorator library — it knows about the specific AI
exception types (app.agents.exceptions) so it can decide per-error-type
whether retrying even makes sense (a timeout is worth retrying; a
validation error on our own output never will be, retrying just repeats
the same mistake).
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.agents.exceptions import (
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)
from app.core.logging import get_logger

logger = get_logger("app.agents.retry")

T = TypeVar("T")

# Only these are considered transient/worth retrying. Anything else (bad
# API key, malformed request, our own validation errors) fails immediately
# — retrying a 401 five times just wastes five timeouts' worth of latency
# before failing anyway.
_RETRYABLE_EXCEPTIONS = (AIProviderTimeoutError, AIProviderRateLimitError, AIProviderUnavailableError)


async def with_retry(
    fn: Callable[[], Awaitable[T]],
    *,
    max_retries: int,
    base_delay_seconds: float = 0.5,
    provider_name: str = "unknown",
) -> T:
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return await fn()
        except _RETRYABLE_EXCEPTIONS as exc:
            last_exception = exc
            if attempt >= max_retries:
                break

            delay = base_delay_seconds * (2**attempt)
            if isinstance(exc, AIProviderRateLimitError) and exc.retry_after_seconds:
                delay = max(delay, exc.retry_after_seconds)

            logger.warning(
                "%s call failed (attempt %d/%d), retrying in %.1fs: %s",
                provider_name,
                attempt + 1,
                max_retries + 1,
                delay,
                exc,
            )
            await asyncio.sleep(delay)

    assert last_exception is not None
    raise last_exception
