from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MealStatus, MealType


class MealBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    meal_type: MealType
    served_at: datetime
    description: str | None = Field(default=None, max_length=500)


class MealCreate(MealBase):
    institution_id: UUID
    department_id: UUID | None = None


class MealUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    meal_type: MealType | None = None
    status: MealStatus | None = None
    served_at: datetime | None = None
    description: str | None = Field(default=None, max_length=500)
    department_id: UUID | None = None


class MealRead(MealBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    institution_id: UUID
    department_id: UUID | None
    created_by_id: str | None
    status: MealStatus
    created_at: datetime
    updated_at: datetime
