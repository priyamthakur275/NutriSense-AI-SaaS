"""Provider-agnostic LLM interface. Every concrete provider (Gemini, OpenAI,
and anything added later — Claude, a local model) implements this same
`LLMProvider` Protocol, so nothing in the vision/nutrition/recommendation/
chat services ever imports a provider-specific SDK type or branches on
"which provider is this". Business logic depends only on this module.

Two capabilities are modeled because they genuinely differ in what a
provider needs to accept, not because of arbitrary API taste:
  - `generate_text`     — plain prompt -> text/JSON-string completion.
  - `generate_from_image` — prompt + image bytes -> completion, for the
    vision (food detection) pipeline. Not every provider/model combination
    supports this, so it's a separate method rather than an optional
    parameter on `generate_text` — a provider that can't do vision should
    be a clear `NotImplementedError`, not a silently-ignored image.
"""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class LLMResponse:
    """Normalized response shape every provider adapts its raw SDK response
    into, so callers never touch a provider-specific response object."""

    content: str
    provider: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    raw_metadata: dict = field(default_factory=dict)


@runtime_checkable
class LLMProvider(Protocol):
    """Every provider must expose its own name for logging/error messages
    and metrics labels — never inferred from the class name via reflection,
    which would silently break if a class were ever renamed."""

    name: str

    async def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float = 0.4,
        max_output_tokens: int = 1024,
    ) -> LLMResponse: ...

    async def generate_from_image(
        self,
        prompt: str,
        image_bytes: bytes,
        *,
        mime_type: str = "image/jpeg",
        system_instruction: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> LLMResponse: ...
