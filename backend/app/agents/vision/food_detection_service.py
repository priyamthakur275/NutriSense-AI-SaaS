"""Food detection service: orchestrates preprocessing + the vision LLM call
+ response validation into one function the API layer calls. This is
where AI-response caching lives for this pipeline — identical image bytes
within the TTL window skip the provider call entirely.
"""

from app.agents.providers.base import LLMProvider
from app.agents.providers.factory import call_with_failover
from app.agents.prompts.vision_prompts import (
    FOOD_DETECTION_SYSTEM_INSTRUCTION,
    build_food_detection_prompt,
)
from app.agents.utils.cache import get_ai_cache, make_cache_key
from app.agents.utils.json_parsing import parse_structured_response
from app.agents.vision.image_processing import ProcessedImage, preprocess_image
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.ai_vision import FoodDetectionResult, ImageAnalysisResponse

logger = get_logger("app.agents.vision")


async def analyze_food_image(raw_image_bytes: bytes) -> ImageAnalysisResponse:
    processed = preprocess_image(raw_image_bytes)

    cache = get_ai_cache()
    cache_key = make_cache_key("vision:v1", processed.content.hex())
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Vision analysis cache hit")
        result = parse_structured_response(cached, FoodDetectionResult)
        return _to_response(result, processed, provider_used="cache")

    prompt = build_food_detection_prompt()

    async def _call(provider: LLMProvider):
        return await provider.generate_from_image(
            prompt,
            processed.content,
            mime_type=processed.mime_type,
            system_instruction=FOOD_DETECTION_SYSTEM_INSTRUCTION,
            temperature=0.1,  # low temperature: this is a detection task, not creative writing
        )

    llm_response = await call_with_failover(_call)
    result = parse_structured_response(llm_response.content, FoodDetectionResult)

    cache.set(cache_key, llm_response.content, settings.AI_CACHE_TTL_SECONDS)

    return _to_response(result, processed, provider_used=llm_response.provider)


def _to_response(
    result: FoodDetectionResult, processed: ProcessedImage, *, provider_used: str
) -> ImageAnalysisResponse:
    return ImageAnalysisResponse(
        detected_items=result.items,
        overall_confidence=result.overall_confidence,
        provider_used=provider_used,
        original_width=processed.original_width,
        original_height=processed.original_height,
        processed_size_bytes=processed.processed_size_bytes,
    )
