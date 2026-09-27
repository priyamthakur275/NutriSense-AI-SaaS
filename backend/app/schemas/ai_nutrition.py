from pydantic import BaseModel, Field


class NutrientBreakdown(BaseModel):
    """Full nutrient panel per the mission's requirements. Vitamins/minerals
    are a flexible dict (name -> mg or IU as a plain float) rather than one
    fixed field per nutrient — the specific set worth reporting varies by
    food, and a fixed schema would force either omitting real data or
    padding every response with irrelevant zeros."""

    calories_kcal: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    fiber_g: float = Field(ge=0)
    sugar_g: float = Field(ge=0)
    sodium_mg: float = Field(ge=0)
    vitamins: dict[str, float] = Field(default_factory=dict, description="e.g. {'vitamin_c_mg': 12.0}")
    minerals: dict[str, float] = Field(default_factory=dict, description="e.g. {'iron_mg': 2.1, 'calcium_mg': 80.0}")


class FoodNutrientEstimate(BaseModel):
    food_name: str
    portion_grams: float = Field(gt=0)
    nutrients: NutrientBreakdown
    confidence: float = Field(ge=0, le=1)


class NutritionEstimationResult(BaseModel):
    """Raw LLM-facing schema (per-item breakdown only) — totals are
    computed deterministically from this in Python, not trusted from the
    model's own arithmetic."""

    items: list[FoodNutrientEstimate]


class NutritionEstimationResponse(BaseModel):
    items: list[FoodNutrientEstimate]
    totals: NutrientBreakdown
    overall_confidence: float
    provider_used: str
