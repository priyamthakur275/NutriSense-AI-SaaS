from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AIRecommendationStatus, AIRecommendationType


class AIRecommendationCreate(BaseModel):
    institution_id: UUID
    department_id: UUID | None = None
    based_on_report_id: UUID | None = None
    recommendation_type: AIRecommendationType
    generated_by_agent: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class AIRecommendationUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)
    recommendation_type: AIRecommendationType | None = None


class AIRecommendationReview(BaseModel):
    status: AIRecommendationStatus


class AIRecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    institution_id: UUID
    department_id: UUID | None
    based_on_report_id: UUID | None
    recommendation_type: AIRecommendationType
    status: AIRecommendationStatus
    generated_by_agent: str
    content: str
    reviewed_by_id: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
