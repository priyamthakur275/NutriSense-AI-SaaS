"""Response schema for the combined vision + nutrition pipeline endpoint —
kept separate from ai_vision.py/ai_nutrition.py since this is a composed
API-facing shape, not a raw provider-facing one."""

from uuid import UUID

from pydantic import BaseModel

from app.schemas.ai_nutrition import NutritionEstimationResponse
from app.schemas.ai_vision import ImageAnalysisResponse


class MealAnalysisResponse(BaseModel):
    vision: ImageAnalysisResponse
    nutrition: NutritionEstimationResponse | None = None
    nutrition_record_id: UUID | None = None
