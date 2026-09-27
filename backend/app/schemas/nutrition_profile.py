from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ActivityLevel, DietPreference, FitnessGoal, Gender


class NutritionProfileUpdate(BaseModel):
    age: int | None = Field(default=None, ge=1, le=120)
    gender: Gender | None = None
    height_cm: float | None = Field(default=None, gt=0, le=300)
    weight_kg: float | None = Field(default=None, gt=0, le=500)
    activity_level: ActivityLevel | None = None
    medical_conditions: list[str] | None = None
    food_allergies: list[str] | None = None
    diet_preference: DietPreference | None = None
    fitness_goal: FitnessGoal | None = None


class NutritionProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    age: int | None
    gender: Gender | None
    height_cm: float | None
    weight_kg: float | None
    bmi: float | None
    activity_level: ActivityLevel | None
    medical_conditions: list[str]
    food_allergies: list[str]
    diet_preference: DietPreference | None
    fitness_goal: FitnessGoal | None
