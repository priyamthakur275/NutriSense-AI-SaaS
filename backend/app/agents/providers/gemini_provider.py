"""Google Gemini provider, calling the generativelanguage REST API directly
(no google-generativeai SDK dependency) so timeout/retry/error-translation
behavior is identical to every other provider via BaseHTTPProvider.
"""

import base64

from app.agents.exceptions import AIProviderUnavailableError
from app.agents.providers.base import LLMResponse
from app.agents.providers.http_base import BaseHTTPProvider
from app.core.config import settings

_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(BaseHTTPProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def _endpoint(self) -> str:
        return f"{_BASE_URL}/{self._model}:generateContent?key={self._api_key}"

    async def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float = 0.4,
        max_output_tokens: int = 1024,
    ) -> LLMResponse:
        body: dict = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_output_tokens},
        }
        if system_instruction:
            body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        data = await self._post_json(self._endpoint(), headers={}, json_body=body)
        return self._parse_response(data)

    async def generate_from_image(
        self,
        prompt: str,
        image_bytes: bytes,
        *,
        mime_type: str = "image/jpeg",
        system_instruction: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> LLMResponse:
        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        body: dict = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime_type, "data": encoded_image}},
                    ],
                }
            ],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_output_tokens},
        }
        if system_instruction:
            body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        data = await self._post_json(self._endpoint(), headers={}, json_body=body)
        return self._parse_response(data)

    def _parse_response(self, data: dict) -> LLMResponse:
        try:
            candidates = data["candidates"]
            parts = candidates[0]["content"]["parts"]
            content = "".join(part.get("text", "") for part in parts)
        except (KeyError, IndexError) as exc:
            raise AIProviderUnavailableError(
                self.name, detail="Unexpected response shape from Gemini"
            ) from exc

        usage = data.get("usageMetadata", {})
        return LLMResponse(
            content=content,
            provider=self.name,
            model=self._model,
            input_tokens=usage.get("promptTokenCount"),
            output_tokens=usage.get("candidatesTokenCount"),
            raw_metadata={"finish_reason": candidates[0].get("finishReason")},
        )


def build_gemini_provider() -> GeminiProvider:
    if not settings.GEMINI_API_KEY:
        raise AIProviderUnavailableError("gemini", detail="GEMINI_API_KEY is not configured")
    return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
