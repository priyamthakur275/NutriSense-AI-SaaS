"""Nutrition estimation engine: takes detected food items, gets a per-item
nutrient breakdown from an LLM, and computes aggregate totals
deterministically in Python (never trusting the model's own arithmetic —
LLMs are unreliable at summing numbers they just generated).

`persist_nutrition_record` bridges into the existing Phase 4D CRUD
infrastructure (NutritionRecordRepository) rather than reimplementing
persistence here — this engine estimates; the repository still owns
storage, exactly as it does for manually-entered records.
"""

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.agents.exceptions import AIOutputValidationError
from app.agents.prompts.nutrition_prompts import (
    NUTRITION_SYSTEM_INSTRUCTION,
    build_nutrition_estimation_prompt,
)
from app.agents.providers.base import LLMProvider
from app.agents.providers.factory import call_with_failover
from app.agents.utils.json_parsing import parse_structured_response
from app.core.exceptions import DuplicateResourceError
from app.models.nutrition_record import NutritionRecord
from app.repositories.nutrition_record import NutritionRecordRepository
from app.schemas.ai_nutrition import (
    FoodNutrientEstimate,
    NutrientBreakdown,
    NutritionEstimationResponse,
    NutritionEstimationResult,
)
from app.schemas.ai_vision import DetectedFoodItem


def _sum_totals(items: list[FoodNutrientEstimate]) -> NutrientBreakdown:
    if not items:
        return NutrientBreakdown(
            calories_kcal=0, protein_g=0, carbs_g=0, fat_g=0, fiber_g=0, sugar_g=0, sodium_mg=0
        )

    totals = {
        "calories_kcal": 0.0,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
        "fiber_g": 0.0,
        "sugar_g": 0.0,
        "sodium_mg": 0.0,
    }
    vitamins: dict[str, float] = {}
    minerals: dict[str, float] = {}

    for item in items:
        n = item.nutrients
        totals["calories_kcal"] += n.calories_kcal
        totals["protein_g"] += n.protein_g
        totals["carbs_g"] += n.carbs_g
        totals["fat_g"] += n.fat_g
        totals["fiber_g"] += n.fiber_g
        totals["sugar_g"] += n.sugar_g
        totals["sodium_mg"] += n.sodium_mg
        for key, value in n.vitamins.items():
            vitamins[key] = vitamins.get(key, 0.0) + value
        for key, value in n.minerals.items():
            minerals[key] = minerals.get(key, 0.0) + value

    return NutrientBreakdown(**totals, vitamins=vitamins, minerals=minerals)


async def estimate_nutrition(detected_items: list[DetectedFoodItem]) -> NutritionEstimationResponse:
    if not detected_items:
        raise AIOutputValidationError("Cannot estimate nutrition for an empty food item list")

    prompt = build_nutrition_estimation_prompt([item.model_dump() for item in detected_items])

    async def _call(provider: LLMProvider):
        return await provider.generate_text(
            prompt, system_instruction=NUTRITION_SYSTEM_INSTRUCTION, temperature=0.2
        )

    llm_response = await call_with_failover(_call)
    result = parse_structured_response(llm_response.content, NutritionEstimationResult)

    totals = _sum_totals(result.items)
    overall_confidence = (
        sum(item.confidence for item in result.items) / len(result.items) if result.items else 0.0
    )

    return NutritionEstimationResponse(
        items=result.items,
        totals=totals,
        overall_confidence=round(overall_confidence, 3),
        provider_used=llm_response.provider,
    )


def persist_nutrition_record(
    db: Session, meal_id: UUID, estimation: NutritionEstimationResponse
) -> NutritionRecord:
    """Writes the engine's output into the existing NutritionRecord table
    via the existing repository — one record per meal, same uniqueness
    constraint as manual entry (Phase 4D), surfaced as the same
    DuplicateResourceError rather than a raw IntegrityError leaking through."""
    repo = NutritionRecordRepository(db)
    totals = estimation.totals

    data = {
        "meal_id": meal_id,
        "calories_kcal": totals.calories_kcal,
        "protein_g": totals.protein_g,
        "carbs_g": totals.carbs_g,
        "fat_g": totals.fat_g,
        "fiber_g": totals.fiber_g,
        "iron_mg": totals.minerals.get("iron_mg"),
        "calcium_mg": totals.minerals.get("calcium_mg"),
        "vitamin_c_mg": totals.vitamins.get("vitamin_c_mg"),
    }
    try:
        record = repo.create(data)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateResourceError("This meal already has a nutrition record") from exc

    db.refresh(record)
    return record
