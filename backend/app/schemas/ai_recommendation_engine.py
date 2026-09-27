"""Request/response schemas for the recommendation *generation* pipeline —
distinct from app.schemas.ai_recommendation (the Phase 4D CRUD schema for
already-persisted AIRecommendation rows). This module is about producing
new ones; that module is about managing existing ones."""

from pydantic import BaseModel, Field

from app.models.enums import AIRecommendationType
from app.schemas.ai_recommendation import AIRecommendationRead


class RecommendationSuggestion(BaseModel):
    """Raw LLM-facing shape — one suggestion, typed against the same
    AIRecommendationType enum the persisted model already uses, so there's
    no separate mapping table between "what the LLM calls it" and "what
    the database calls it"."""

    recommendation_type: AIRecommendationType
    content: str = Field(min_length=1)


class RecommendationGenerationResult(BaseModel):
    suggestions: list[RecommendationSuggestion]


class RecommendationGenerationResponse(BaseModel):
    generated: list[AIRecommendationRead]
    provider_used: str
    context_summary: str
