"""Shared 'ask an LLM for structured JSON, then validate it' logic. Every
AI subsystem that expects structured output (vision detection, nutrition
estimation, recommendations) goes through this exact function rather than
each reimplementing markdown-fence-stripping and error handling slightly
differently.
"""

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.agents.exceptions import AIOutputValidationError

T = TypeVar("T", bound=BaseModel)

# LLMs very commonly wrap JSON output in a markdown code fence even when
# explicitly told not to — stripping it here means every prompt template
# doesn't need defensive "do not include backticks" boilerplate to work
# reliably, and this still works on the (correct) responses that already
# omit the fence.
_CODE_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def parse_structured_response(content: str, schema: type[T]) -> T:
    cleaned = _CODE_FENCE_PATTERN.sub("", content.strip()).strip()

    try:
        raw = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AIOutputValidationError(
            f"AI response was not valid JSON: {exc}. Raw content: {cleaned[:300]}"
        ) from exc

    try:
        return schema.model_validate(raw)
    except ValidationError as exc:
        raise AIOutputValidationError(
            f"AI response did not match the expected structure: {exc}"
        ) from exc
