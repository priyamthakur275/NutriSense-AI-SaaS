"""AI-specific exceptions. Kept separate from app.core.exceptions (which
covers auth/authorization/generic API errors) so the AI module stays
self-contained and could, in principle, be extracted into its own package
later without dragging the rest of the app's exception hierarchy with it.

All inherit from app.core.exceptions.AppError so they still get translated
into consistent JSON responses by the handler already registered in
main.py — no new exception handler needed.
"""

from fastapi import status

from app.core.exceptions import AppError


class AIProviderError(AppError):
    """Base class for anything that goes wrong talking to an LLM provider."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "ai_provider_error"


class AIProviderTimeoutError(AIProviderError):
    error_code = "ai_provider_timeout"

    def __init__(self, provider: str) -> None:
        super().__init__(f"The {provider} provider did not respond in time")


class AIProviderRateLimitError(AIProviderError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "ai_provider_rate_limited"

    def __init__(self, provider: str, retry_after_seconds: int | None = None) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"The {provider} provider is rate-limiting requests")


class AIProviderUnavailableError(AIProviderError):
    error_code = "ai_provider_unavailable"

    def __init__(self, provider: str, detail: str | None = None) -> None:
        message = f"The {provider} provider is currently unavailable"
        if detail:
            message += f": {detail}"
        super().__init__(message)


class AllProvidersFailedError(AIProviderError):
    error_code = "ai_all_providers_failed"

    def __init__(self, attempted: list[str]) -> None:
        super().__init__(
            f"All configured AI providers failed: {', '.join(attempted)}"
        )


class AIOutputValidationError(AppError):
    """Raised when a provider responds successfully but the content doesn't
    conform to the structured shape we asked for (e.g. the model returned
    prose instead of the requested JSON) — a distinct failure mode from a
    provider being down, and one that should never be silently coerced."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "ai_output_validation_failed"


class UnsupportedProviderError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "ai_unsupported_provider"
