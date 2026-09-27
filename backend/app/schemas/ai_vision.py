from pydantic import BaseModel, Field

# Food categories recognized by the vision pipeline — an explicit allow-list
# rather than a free-text field, so downstream nutrition estimation and
# analytics can group/filter reliably instead of fuzzy-matching whatever
# string the model felt like returning.
FOOD_CATEGORIES = (
    "fruit",
    "vegetable",
    "rice",
    "bread",
    "dairy",
    "meat",
    "snack",
    "dessert",
    "beverage",
    "mixed_meal",
    "packaged_food",
    "other",
)


class DetectedFoodItem(BaseModel):
    name: str = Field(description="Specific food name, e.g. 'steamed rice', 'grilled chicken breast'")
    category: str = Field(description=f"One of: {', '.join(FOOD_CATEGORIES)}")
    estimated_portion_grams: float = Field(gt=0, description="Estimated serving size in grams")
    confidence: float = Field(ge=0, le=1, description="Model's confidence in this detection, 0-1")


class FoodDetectionResult(BaseModel):
    """The raw structured output the vision LLM is asked to produce — kept
    separate from ImageAnalysisResponse (the API-facing schema) so the
    prompt contract and the public API contract can evolve independently."""

    items: list[DetectedFoodItem]
    overall_confidence: float = Field(ge=0, le=1)


class ImageAnalysisResponse(BaseModel):
    detected_items: list[DetectedFoodItem]
    overall_confidence: float
    provider_used: str
    original_width: int
    original_height: int
    processed_size_bytes: int
