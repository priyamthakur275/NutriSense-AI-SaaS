from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.kitchen.catalog import CATALOG, Diet
from app.models.enums import MealType


class ServiceDishIn(BaseModel):
    dish_key: str
    prepared_kg: float = Field(gt=0, le=2000)
    pot_leftover_kg: float = Field(default=0, ge=0)
    plate_waste_kg: float = Field(default=0, ge=0)

    @field_validator("dish_key")
    @classmethod
    def _known(cls, v: str) -> str:
        if v not in CATALOG:
            raise ValueError(f"Unknown dish '{v}'")
        return v

    @model_validator(mode="after")
    def _weights(self):
        if self.pot_leftover_kg + self.plate_waste_kg > self.prepared_kg:
            raise ValueError("Leftover plus plate waste cannot exceed what was prepared")
        return self


class ServiceIn(BaseModel):
    service_date: date
    meal_type: MealType
    plates_served: int = Field(gt=0, le=20000)
    notes: str | None = Field(default=None, max_length=300)
    dishes: list[ServiceDishIn] = Field(min_length=1, max_length=12)


class ServiceDishOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    dish_key: str
    prepared_kg: float
    pot_leftover_kg: float
    plate_waste_kg: float


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    service_date: date
    meal_type: MealType
    plates_served: int
    is_sample: bool
    notes: str | None
    dishes: list[ServiceDishOut]


class MenuPlanIn(BaseModel):
    preset: str = "hostel_lunch"
    budget_per_plate: float = Field(default=50, ge=5, le=500)
    diet: Diet = Diet.VEG
    days: int = Field(default=7, ge=1, le=7)
    include_bread: bool = True
    max_repeats: int = Field(default=2, ge=1, le=7)
    goal: str = Field(default="nutrition", pattern="^(nutrition|cost)$")
    exclude: list[str] = Field(default_factory=list, max_length=30)
