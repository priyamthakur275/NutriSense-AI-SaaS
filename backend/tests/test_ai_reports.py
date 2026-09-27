"""Reports & analytics: deterministic aggregation regression tests.

Every assertion here checks a number against known seeded data — these
tests exist specifically to guard against a hallucinated or miscalculated
statistic ever reaching a nutrition-compliance report.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.agents.reports import report_service
from app.models.attendance import Attendance
from app.models.enums import AttendanceMethod, MealStatus
from app.models.nutrition_record import NutritionRecord


def _seed_five_days_of_low_fiber_meals(db_session, institution, user, make_meal):
    for i in range(5):
        served = datetime.now(timezone.utc) - timedelta(days=i)
        meal = make_meal(institution, served_at=served, status=MealStatus.ANALYZED)
        db_session.add(
            NutritionRecord(
                meal_id=meal.id,
                calories_kcal=400 + i * 10,
                protein_g=20,
                carbs_g=60,
                fat_g=12,
                fiber_g=5.0,  # below the 25g reference minimum
                iron_mg=3.0,  # below the 8mg reference minimum
                calcium_mg=1200,  # above the 1000mg reference minimum
                compliance_score=70 + i * 5,
            )
        )
        db_session.add(Attendance(user_id=user.id, meal_id=meal.id, method=AttendanceMethod.MANUAL, attended_at=served))
    db_session.commit()


def test_deficiency_detection_flags_low_nutrients_only():
    alerts = report_service.detect_deficiencies(
        {"protein_g": 20, "fiber_g": 5.0, "iron_mg": 3.0, "calcium_mg": 1200, "vitamin_c_mg": None}
    )
    flagged = {a.nutrient for a in alerts}

    assert "fiber_g" in flagged
    assert "iron_mg" in flagged
    assert "calcium_mg" not in flagged  # above minimum — must not be flagged
    assert "vitamin_c_mg" not in flagged  # None (no data) — must not be flagged


@pytest.mark.asyncio
async def test_nutrition_summary_aggregates_correctly(db_session, make_institution, make_user, make_meal):
    institution = make_institution()
    user = make_user()
    _seed_five_days_of_low_fiber_meals(db_session, institution, user, make_meal)

    summary = await report_service.get_nutrition_summary(db_session, institution.id, "weekly", include_narrative=False)

    assert summary.meals_analyzed == 5
    assert summary.average_calories == pytest.approx(420.0)
    assert summary.average_compliance_score == pytest.approx(80.0)
    flagged = {a.nutrient for a in summary.deficiency_alerts}
    assert "fiber_g" in flagged and "iron_mg" in flagged


def test_nutrition_trend_produces_chart_ready_shape(db_session, make_institution, make_user, make_meal):
    institution = make_institution()
    user = make_user()
    _seed_five_days_of_low_fiber_meals(db_session, institution, user, make_meal)

    trend = report_service.get_nutrition_trend(db_session, institution.id, days=10)

    assert len(trend.labels) == 5
    assert {s.label for s in trend.series} == {"Calories (kcal)", "Protein (g)", "Carbs (g)", "Fat (g)"}
    for series in trend.series:
        assert len(series.data) == len(trend.labels)  # every series aligns with the label axis


def test_institution_dashboard_aggregates_across_models(db_session, make_institution, make_user, make_student, make_meal):
    institution = make_institution()
    user = make_user()
    make_student(user, institution)
    _seed_five_days_of_low_fiber_meals(db_session, institution, user, make_meal)

    dashboard = report_service.get_institution_dashboard(db_session, institution.id)

    assert dashboard.total_meals_last_30_days == 5
    assert dashboard.total_students == 1
    assert dashboard.average_compliance_score == pytest.approx(80.0)


@pytest.mark.asyncio
async def test_student_insights_computes_attendance_rate(db_session, make_institution, make_user, make_student, make_meal):
    institution = make_institution()
    user = make_user()
    make_student(user, institution)
    _seed_five_days_of_low_fiber_meals(db_session, institution, user, make_meal)

    insights = await report_service.get_student_insights(db_session, user, include_narrative=False)

    assert insights.attendance_rate_last_30_days == 100.0  # attended all 5 of 5 meals
    flagged = {a.nutrient for a in insights.deficiency_alerts}
    assert "fiber_g" in flagged
