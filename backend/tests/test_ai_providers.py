"""Provider abstraction, failover, and error-handling regression tests."""

import pytest

from app.agents.exceptions import (
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AllProvidersFailedError,
    UnsupportedProviderError,
)
from app.agents.providers import factory
from app.agents.providers.base import LLMResponse
from app.core.config import settings


def test_unsupported_provider_name_raises():
    with pytest.raises(UnsupportedProviderError):
        factory.get_provider("nonexistent-provider")


def test_missing_api_key_raises_clear_error():
    # No GEMINI_API_KEY is configured in the test environment.
    with pytest.raises(AIProviderUnavailableError):
        factory.get_provider("gemini")


@pytest.mark.asyncio
async def test_failover_tries_fallback_after_primary_fails():
    call_log = []

    class FlakyProvider:
        name = "flaky"

        async def generate_text(self, prompt, **kwargs):
            call_log.append("flaky")
            raise AIProviderTimeoutError("flaky")

        async def generate_from_image(self, *a, **kw):
            raise NotImplementedError

    class ReliableProvider:
        name = "reliable"

        async def generate_text(self, prompt, **kwargs):
            call_log.append("reliable")
            return LLMResponse(content="ok", provider="reliable", model="test")

        async def generate_from_image(self, *a, **kw):
            raise NotImplementedError

    factory._BUILDERS["flaky"] = lambda: FlakyProvider()
    factory._BUILDERS["reliable"] = lambda: ReliableProvider()
    settings.AI_PROVIDER = "flaky"
    settings.AI_FALLBACK_PROVIDERS = ["reliable"]
    settings.AI_MAX_RETRIES = 0

    result = await factory.call_with_failover(lambda p: p.generate_text("test"))

    assert result.content == "ok"
    assert call_log == ["flaky", "reliable"]


@pytest.mark.asyncio
async def test_all_providers_failing_raises_aggregate_error():
    class AlwaysFails:
        name = "always-fails"

        async def generate_text(self, prompt, **kwargs):
            raise AIProviderTimeoutError("always-fails")

        async def generate_from_image(self, *a, **kw):
            raise NotImplementedError

    factory._BUILDERS["always-fails"] = lambda: AlwaysFails()
    settings.AI_PROVIDER = "always-fails"
    settings.AI_FALLBACK_PROVIDERS = []
    settings.AI_MAX_RETRIES = 0

    with pytest.raises(AllProvidersFailedError):
        await factory.call_with_failover(lambda p: p.generate_text("test"))


@pytest.mark.asyncio
async def test_retry_eventually_succeeds_within_max_retries():
    attempts = {"n": 0}

    class EventuallyWorks:
        name = "eventually"

        async def generate_text(self, prompt, **kwargs):
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise AIProviderTimeoutError("eventually")
            return LLMResponse(content="succeeded on retry", provider="eventually", model="test")

        async def generate_from_image(self, *a, **kw):
            raise NotImplementedError

    factory._BUILDERS["eventually"] = lambda: EventuallyWorks()
    settings.AI_PROVIDER = "eventually"
    settings.AI_FALLBACK_PROVIDERS = []
    settings.AI_MAX_RETRIES = 3

    result = await factory.call_with_failover(lambda p: p.generate_text("test"))

    assert result.content == "succeeded on retry"
    assert attempts["n"] == 3
