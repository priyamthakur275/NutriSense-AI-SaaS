from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MealImageCreate(BaseModel):
    meal_id: UUID
    storage_path: str = Field(min_length=1, max_length=1000)
    captured_at: datetime


class MealImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    meal_id: UUID
    uploaded_by_id: str | None
    storage_path: str
    captured_at: datetime
    detection_metadata: dict[str, Any] | None
    created_at: datetime
