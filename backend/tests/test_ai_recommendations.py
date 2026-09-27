"""Nutrition profile and recommendation engine tests."""

import json
from datetime import datetime, timedelta, timezone

import pytest

from app.agents.providers import factory
from app.agents.providers.base import LLMResponse
from app.agents.recommendations.recommendation_engine import generate_recommendations
from app.core.config import settings
from app.models.attendance import Attendance
from app.models.enums import AttendanceMethod, MealStatus
from app.models.nutrition_record import NutritionRecord
from app.services.nutrition_profile_service import get_or_create_profile


class _StubRecommendationProvider:
    name = "stub-rec"

    async def generate_text(self, prompt, **kwargs):
        payload = {
            "suggestions": [
                {"recommendation_type": "menu_change", "content": "Add more whole grains."},
                {"recommendation_type": "general", "content": "Fiber intake is below target."},
            ]
        }
        return LLMResponse(content=json.dumps(payload), provider="stub-rec", model="stub")

    async def generate_from_image(self, *a, **kw):
        raise NotImplementedError


@pytest.fixture(autouse=True)
def _use_stub_recommendation_provider():
    factory._BUILDERS["stub-rec"] = lambda: _StubRecommendationProvider()
    settings.AI_PROVIDER = "stub-rec"
    settings.AI_FALLBACK_PROVIDERS = []


def test_nutrition_profile_lazy_creates_and_computes_bmi(db_session, make_user):
    user = make_user()
    profile = get_or_create_profile(db_session, user)
    assert profile.user_id == user.id
    assert profile.bmi is None  # no height/weight yet

    profile.height_cm = 165
    profile.weight_kg = 58
    db_session.commit()
    assert profile.bmi == pytest.approx(21.3, abs=0.1)


def test_get_or_create_profile_does_not_duplicate(db_session, make_user):
    user = make_user()
    first = get_or_create_profile(db_session, user)
    second = get_or_create_profile(db_session, user)
    assert first.id == second.id


@pytest.mark.asyncio
async def test_recommendation_engine_gathers_context_and_persists(
    db_session, make_institution, make_user, make_student, make_meal
):
    institution = make_institution()
    user = make_user()
    make_student(user, institution)

    for i in range(3):
        served = datetime.now(timezone.utc) - timedelta(days=i)
        meal = make_meal(institution, served_at=served, status=MealStatus.ANALYZED)
        db_session.add(
            NutritionRecord(meal_id=meal.id, calories_kcal=450, protein_g=15, carbs_g=70, fat_g=10, fiber_g=1.5)
        )
        db_session.add(
            Attendance(user_id=user.id, meal_id=meal.id, method=AttendanceMethod.MANUAL, attended_at=served)
        )
    db_session.commit()

    response = await generate_recommendations(db_session, user, institution_id=institution.id)

    assert len(response.generated) == 2
    assert all(r.status.value == "pending" for r in response.generated)
    assert "kcal" in response.context_summary
