from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NutritionRecordBase(BaseModel):
    calories_kcal: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    fiber_g: float | None = Field(default=None, ge=0)
    iron_mg: float | None = Field(default=None, ge=0)
    calcium_mg: float | None = Field(default=None, ge=0)
    vitamin_c_mg: float | None = Field(default=None, ge=0)


class NutritionRecordCreate(NutritionRecordBase):
    meal_id: UUID


class NutritionRecordUpdate(BaseModel):
    calories_kcal: float | None = Field(default=None, ge=0)
    protein_g: float | None = Field(default=None, ge=0)
    carbs_g: float | None = Field(default=None, ge=0)
    fat_g: float | None = Field(default=None, ge=0)
    fiber_g: float | None = Field(default=None, ge=0)
    iron_mg: float | None = Field(default=None, ge=0)
    calcium_mg: float | None = Field(default=None, ge=0)
    vitamin_c_mg: float | None = Field(default=None, ge=0)
    compliance_score: float | None = Field(default=None, ge=0, le=100)
    is_compliant: bool | None = None


class NutritionRecordRead(NutritionRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    meal_id: UUID
    compliance_score: float | None
    is_compliant: bool | None
    computed_at: datetime | None
    created_at: datetime
    updated_at: datetime
