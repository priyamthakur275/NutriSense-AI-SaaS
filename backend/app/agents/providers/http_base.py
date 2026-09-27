"""Shared HTTP-call plumbing for provider implementations. Both Gemini and
OpenAI providers are thin HTTP clients over their respective REST APIs
(deliberately not using either vendor's heavyweight SDK, to keep the
dependency footprint small and behavior — timeouts, error translation —
identical across providers). This base class holds the one piece of logic
that would otherwise be duplicated: turning httpx-level failures into our
own AIProviderError hierarchy so callers never need to know which HTTP
library is underneath.
"""

import httpx

from app.agents.exceptions import (
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)
from app.core.config import settings


class BaseHTTPProvider:
    name: str = "base"

    async def _post_json(self, url: str, *, headers: dict, json_body: dict) -> dict:
        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT_SECONDS)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, headers=headers, json=json_body)
        except httpx.TimeoutException as exc:
            raise AIProviderTimeoutError(self.name) from exc
        except httpx.RequestError as exc:
            raise AIProviderUnavailableError(self.name, detail=str(exc)) from exc

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise AIProviderRateLimitError(
                self.name, retry_after_seconds=int(retry_after) if retry_after else None
            )
        if response.status_code >= 500:
            raise AIProviderUnavailableError(self.name, detail=f"HTTP {response.status_code}")
        if response.status_code >= 400:
            raise AIProviderUnavailableError(
                self.name, detail=f"HTTP {response.status_code}: {response.text[:300]}"
            )

        return response.json()
