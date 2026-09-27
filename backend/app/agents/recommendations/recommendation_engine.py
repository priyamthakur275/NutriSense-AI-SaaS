"""Personalized recommendation engine: gathers a user's health profile and
recent nutrition intake, asks an LLM for tailored suggestions, and persists
each one as an AIRecommendation row via the existing Phase 4D repository —
this engine is a producer of AIRecommendation rows, not a parallel storage
mechanism for them.

Known gap, stated honestly rather than fabricated: "Institution Policies"
is listed in the product requirements as a recommendation input, but no
such data is modeled anywhere in the schema yet (no InstitutionPolicy
table). This engine does not invent placeholder policy data — it simply
omits that input until a real policy model exists.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents.prompts.recommendation_prompts import (
    RECOMMENDATION_SYSTEM_INSTRUCTION,
    build_recommendation_prompt,
)
from app.agents.providers.base import LLMProvider
from app.agents.providers.factory import call_with_failover
from app.agents.utils.json_parsing import parse_structured_response
from app.models.attendance import Attendance
from app.models.enums import AIRecommendationStatus
from app.models.meal import Meal
from app.models.nutrition_record import NutritionRecord
from app.models.user import User
from app.repositories.ai_recommendation import AIRecommendationRepository
from app.schemas.ai_recommendation import AIRecommendationRead
from app.schemas.ai_recommendation_engine import (
    RecommendationGenerationResponse,
    RecommendationGenerationResult,
)
from app.services.nutrition_profile_service import get_or_create_profile

RECENT_DAYS_WINDOW = 7


def _build_profile_summary(profile) -> str:
    parts = []
    if profile.age:
        parts.append(f"Age: {profile.age}")
    if profile.gender:
        parts.append(f"Gender: {profile.gender.value}")
    if profile.bmi:
        parts.append(f"BMI: {profile.bmi}")
    if profile.activity_level:
        parts.append(f"Activity level: {profile.activity_level.value}")
    if profile.diet_preference:
        parts.append(f"Diet preference: {profile.diet_preference.value}")
    if profile.fitness_goal:
        parts.append(f"Fitness goal: {profile.fitness_goal.value}")
    if profile.medical_conditions:
        parts.append(f"Medical conditions: {', '.join(profile.medical_conditions)}")
    if profile.food_allergies:
        parts.append(f"Food allergies: {', '.join(profile.food_allergies)}")

    return "\n".join(parts) if parts else "No profile details provided yet."


def _gather_recent_nutrition_summary(db: Session, user: User) -> str:
    since = datetime.now(timezone.utc) - timedelta(days=RECENT_DAYS_WINDOW)

    row = (
        db.query(
            func.avg(NutritionRecord.calories_kcal),
            func.avg(NutritionRecord.protein_g),
            func.avg(NutritionRecord.carbs_g),
            func.avg(NutritionRecord.fat_g),
            func.avg(NutritionRecord.fiber_g),
            func.avg(NutritionRecord.iron_mg),
            func.avg(NutritionRecord.calcium_mg),
            func.avg(NutritionRecord.vitamin_c_mg),
            func.count(NutritionRecord.id),
        )
        .join(Meal, Meal.id == NutritionRecord.meal_id)
        .join(Attendance, Attendance.meal_id == Meal.id)
        .filter(Attendance.user_id == user.id, Attendance.attended_at >= since)
        .first()
    )

    calories, protein, carbs, fat, fiber, iron, calcium, vitamin_c, meal_count = row

    if not meal_count:
        return "No attended, nutrition-analyzed meals in the last 7 days."

    def fmt(value: float | None, unit: str) -> str:
        return f"{value:.1f}{unit}" if value is not None else "unknown"

    return (
        f"Based on {meal_count} analyzed meal(s) in the last {RECENT_DAYS_WINDOW} days — "
        f"average per meal: {fmt(calories, ' kcal')}, protein {fmt(protein, 'g')}, "
        f"carbs {fmt(carbs, 'g')}, fat {fmt(fat, 'g')}, fiber {fmt(fiber, 'g')}, "
        f"iron {fmt(iron, 'mg')}, calcium {fmt(calcium, 'mg')}, vitamin C {fmt(vitamin_c, 'mg')}."
    )


async def generate_recommendations(
    db: Session, user: User, *, institution_id: UUID
) -> RecommendationGenerationResponse:
    profile = get_or_create_profile(db, user)
    profile_summary = _build_profile_summary(profile)
    nutrition_summary = _gather_recent_nutrition_summary(db, user)

    prompt = build_recommendation_prompt(
        profile_summary=profile_summary, nutrition_summary=nutrition_summary
    )

    async def _call(provider: LLMProvider):
        return await provider.generate_text(
            prompt, system_instruction=RECOMMENDATION_SYSTEM_INSTRUCTION, temperature=0.5
        )

    llm_response = await call_with_failover(_call)
    result = parse_structured_response(llm_response.content, RecommendationGenerationResult)

    repo = AIRecommendationRepository(db)
    persisted = []
    for suggestion in result.suggestions:
        row = repo.create(
            {
                "institution_id": institution_id,
                "recommendation_type": suggestion.recommendation_type,
                "status": AIRecommendationStatus.PENDING,
                "generated_by_agent": f"recommendation_engine:{llm_response.provider}",
                "content": suggestion.content,
            }
        )
        persisted.append(row)
    db.commit()
    for row in persisted:
        db.refresh(row)

    return RecommendationGenerationResponse(
        generated=[AIRecommendationRead.model_validate(r) for r in persisted],
        provider_used=llm_response.provider,
        context_summary=f"{profile_summary} | {nutrition_summary}",
    )
