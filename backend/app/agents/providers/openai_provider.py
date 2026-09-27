"""OpenAI provider, calling the Chat Completions REST API directly (same
rationale as GeminiProvider: no SDK dependency, identical timeout/retry
behavior via BaseHTTPProvider). Images are sent as base64 data URLs per
the OpenAI vision message format.
"""

import base64

from app.agents.exceptions import AIProviderUnavailableError
from app.agents.providers.base import LLMResponse
from app.agents.providers.http_base import BaseHTTPProvider
from app.core.config import settings

_ENDPOINT = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(BaseHTTPProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    async def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float = 0.4,
        max_output_tokens: int = 1024,
    ) -> LLMResponse:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }
        data = await self._post_json(_ENDPOINT, headers=self._headers(), json_body=body)
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
        data_url = f"data:{mime_type};base64,{encoded_image}"

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        )

        body = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }
        data = await self._post_json(_ENDPOINT, headers=self._headers(), json_body=body)
        return self._parse_response(data)

    def _parse_response(self, data: dict) -> LLMResponse:
        try:
            choice = data["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise AIProviderUnavailableError(
                self.name, detail="Unexpected response shape from OpenAI"
            ) from exc

        usage = data.get("usage", {})
        return LLMResponse(
            content=content,
            provider=self.name,
            model=self._model,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            raw_metadata={"finish_reason": choice.get("finish_reason")},
        )


def build_openai_provider() -> OpenAIProvider:
    if not settings.OPENAI_API_KEY:
        raise AIProviderUnavailableError("openai", detail="OPENAI_API_KEY is not configured")
    return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)
