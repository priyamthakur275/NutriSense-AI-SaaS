"""Provider selection and failover.

`get_provider(name)` is the one place that maps a provider name string to
a concrete class — adding Claude or a local model later means adding one
entry to `_BUILDERS` here; nothing else in the AI module changes.

`call_with_failover` is what business logic (vision/nutrition/recommendation/
chat services) should actually call, rather than talking to a single
provider directly: it tries the primary provider first, then each
configured fallback in order, only raising `AllProvidersFailedError` if
every one of them fails. Each individual attempt still goes through
`with_retry` for transient failures before being counted as a failure at
all.
"""

from collections.abc import Awaitable, Callable

from app.agents.exceptions import AIProviderError, AllProvidersFailedError, UnsupportedProviderError
from app.agents.providers.base import LLMProvider, LLMResponse
from app.agents.providers.gemini_provider import build_gemini_provider
from app.agents.providers.openai_provider import build_openai_provider
from app.agents.utils.retry import with_retry
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.agents.providers")

_BUILDERS: dict[str, Callable[[], LLMProvider]] = {
    "gemini": build_gemini_provider,
    "openai": build_openai_provider,
}


def get_provider(name: str) -> LLMProvider:
    builder = _BUILDERS.get(name)
    if builder is None:
        raise UnsupportedProviderError(
            f"Unknown AI provider '{name}'. Supported: {', '.join(_BUILDERS.keys())}"
        )
    return builder()


async def call_with_failover(
    call: Callable[[LLMProvider], Awaitable[LLMResponse]],
) -> LLMResponse:
    """Runs `call` against the primary provider, falling back through
    `settings.AI_FALLBACK_PROVIDERS` in order on failure. `call` is a
    closure so the caller can invoke either `generate_text` or
    `generate_from_image` with whatever arguments it needs, without this
    function needing to know which one.
    """
    provider_order = [settings.AI_PROVIDER, *settings.AI_FALLBACK_PROVIDERS]
    attempted: list[str] = []
    last_error: Exception | None = None

    for provider_name in provider_order:
        if provider_name in attempted:
            continue
        attempted.append(provider_name)

        try:
            provider = get_provider(provider_name)
        except AIProviderError as exc:
            logger.warning("Provider '%s' unavailable at build time: %s", provider_name, exc)
            last_error = exc
            continue

        try:
            return await with_retry(
                lambda p=provider: call(p),
                max_retries=settings.AI_MAX_RETRIES,
                provider_name=provider_name,
            )
        except AIProviderError as exc:
            logger.warning("Provider '%s' failed, trying next fallback: %s", provider_name, exc)
            last_error = exc
            continue

    logger.error("All AI providers failed: %s", attempted)
    raise AllProvidersFailedError(attempted) from last_error
