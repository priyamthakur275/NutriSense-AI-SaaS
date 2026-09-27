"""Reports & analytics service. Every number in every response here is
computed deterministically via SQL aggregation — the LLM is only ever
asked (optionally, and only where explicitly requested) to phrase an
already-computed set of numbers as a short narrative, never to produce or
influence the figures themselves. This matters for a nutrition-compliance
product: a hallucinated statistic in a compliance report would be a real
liability, so the boundary between "computed fact" and "AI-generated text"
is enforced structurally, not just by prompt instructions.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents.exceptions import AIProviderError
from app.agents.prompts.report_prompts import (
    REPORT_NARRATIVE_SYSTEM_INSTRUCTION,
    build_report_narrative_prompt,
)
from app.agents.providers.base import LLMProvider
from app.agents.providers.factory import call_with_failover
from app.models.attendance import Attendance
from app.models.compliance_report import ComplianceReport
from app.models.ai_recommendation import AIRecommendation
from app.models.enums import AIRecommendationStatus, NotificationType
from app.models.meal import Meal
from app.models.notification import Notification
from app.models.nutrition_record import NutritionRecord
from app.models.staff import Staff
from app.models.student import Student
from app.models.user import User
from app.schemas.ai_reports import (
    ChartResponse,
    ChartSeries,
    DeficiencyAlert,
    InstitutionDashboardData,
    NutritionReportSummary,
    StudentInsights,
)

# Illustrative daily-value reference minimums (broadly aligned with common
# ICMR-NIN / WHO adult guidance) — NOT a certified per-individual medical
# threshold. Used only to flag "average intake looks low relative to a
# general benchmark", which is exactly how it's labeled in every response.
NUTRIENT_REFERENCE_MINIMUMS: dict[str, tuple[float, str]] = {
    "protein_g": (50.0, "g"),
    "fiber_g": (25.0, "g"),
    "iron_mg": (8.0, "mg"),
    "calcium_mg": (1000.0, "mg"),
    "vitamin_c_mg": (65.0, "mg"),
}


def _severity_for_ratio(ratio: float) -> str:
    if ratio < 0.5:
        return "severe"
    if ratio < 0.75:
        return "moderate"
    return "mild"


def detect_deficiencies(averages: dict[str, float | None]) -> list[DeficiencyAlert]:
    alerts = []
    for nutrient, (minimum, unit) in NUTRIENT_REFERENCE_MINIMUMS.items():
        current = averages.get(nutrient)
        if current is None or current >= minimum:
            continue
        alerts.append(
            DeficiencyAlert(
                nutrient=nutrient,
                current_average=round(current, 2),
                recommended_minimum=minimum,
                unit=unit,
                severity=_severity_for_ratio(current / minimum),
            )
        )
    return alerts


async def _try_generate_narrative(stats_description: str) -> str | None:
    """Best-effort narrative — a report is still fully useful with its
    numbers alone, so a provider failure here degrades to `None` rather
    than failing the whole report request (same philosophy as chat's
    graceful degradation, applied to a different subsystem)."""
    prompt = build_report_narrative_prompt(stats_description)

    async def _call(provider: LLMProvider):
        return await provider.generate_text(
            prompt, system_instruction=REPORT_NARRATIVE_SYSTEM_INSTRUCTION, temperature=0.3, max_output_tokens=200
        )

    try:
        response = await call_with_failover(_call)
        return response.content.strip()
    except AIProviderError:
        return None


def _period_bounds(period: str) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    if period == "daily":
        start = now - timedelta(days=1)
    elif period == "weekly":
        start = now - timedelta(days=7)
    elif period == "monthly":
        start = now - timedelta(days=30)
    else:
        raise ValueError(f"Unknown period '{period}'")
    return start, now


async def get_nutrition_summary(
    db: Session, institution_id: UUID, period: str, *, include_narrative: bool = True
) -> NutritionReportSummary:
    start, end = _period_bounds(period)

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
            func.avg(NutritionRecord.compliance_score),
            func.count(NutritionRecord.id),
        )
        .join(Meal, Meal.id == NutritionRecord.meal_id)
        .filter(Meal.institution_id == institution_id, Meal.served_at.between(start, end))
        .first()
    )
    calories, protein, carbs, fat, fiber, iron, calcium, vitamin_c, compliance, meal_count = row

    averages = {
        "protein_g": protein,
        "fiber_g": fiber,
        "iron_mg": iron,
        "calcium_mg": calcium,
        "vitamin_c_mg": vitamin_c,
    }
    alerts = detect_deficiencies(averages)

    narrative = None
    if include_narrative and meal_count:
        stats_description = (
            f"Period: {period}, {meal_count} meals analyzed. "
            f"Averages — calories: {calories}, protein: {protein}g, carbs: {carbs}g, fat: {fat}g, "
            f"compliance score: {compliance}. "
            f"Deficiency flags: {[a.nutrient for a in alerts] or 'none'}."
        )
        narrative = await _try_generate_narrative(stats_description)

    return NutritionReportSummary(
        period=period,
        period_start=start,
        period_end=end,
        institution_id=institution_id,
        meals_analyzed=meal_count or 0,
        average_calories=round(calories, 1) if calories else None,
        average_protein=round(protein, 1) if protein else None,
        average_carbs=round(carbs, 1) if carbs else None,
        average_fat=round(fat, 1) if fat else None,
        average_compliance_score=round(compliance, 1) if compliance else None,
        deficiency_alerts=alerts,
        narrative_summary=narrative,
    )


def get_nutrition_trend(db: Session, institution_id: UUID, days: int = 14) -> ChartResponse:
    """Daily-bucketed averages over the trailing `days` window — the raw
    data behind a line chart of calories/protein/carbs/fat over time."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    day_expr = func.date(Meal.served_at)
    rows = (
        db.query(
            day_expr.label("day"),
            func.avg(NutritionRecord.calories_kcal),
            func.avg(NutritionRecord.protein_g),
            func.avg(NutritionRecord.carbs_g),
            func.avg(NutritionRecord.fat_g),
        )
        .join(Meal, Meal.id == NutritionRecord.meal_id)
        .filter(Meal.institution_id == institution_id, Meal.served_at >= since)
        .group_by(day_expr)
        .order_by(day_expr)
        .all()
    )

    labels = [str(r[0]) for r in rows]
    return ChartResponse(
        labels=labels,
        series=[
            ChartSeries(label="Calories (kcal)", data=[round(r[1] or 0, 1) for r in rows]),
            ChartSeries(label="Protein (g)", data=[round(r[2] or 0, 1) for r in rows]),
            ChartSeries(label="Carbs (g)", data=[round(r[3] or 0, 1) for r in rows]),
            ChartSeries(label="Fat (g)", data=[round(r[4] or 0, 1) for r in rows]),
        ],
    )


def get_attendance_vs_nutrition(db: Session, institution_id: UUID, days: int = 14) -> ChartResponse:
    """Correlates daily attendance count against average compliance score —
    the data behind a dual-axis chart showing whether low attendance days
    also tend to be low-compliance days (or vice versa)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    day_expr = func.date(Attendance.attended_at)
    attendance_rows = (
        db.query(day_expr.label("day"), func.count(Attendance.id))
        .join(Meal, Meal.id == Attendance.meal_id)
        .filter(Meal.institution_id == institution_id, Attendance.attended_at >= since)
        .group_by(day_expr)
        .order_by(day_expr)
        .all()
    )
    attendance_by_day = {str(r[0]): r[1] for r in attendance_rows}

    meal_day_expr = func.date(Meal.served_at)
    compliance_rows = (
        db.query(meal_day_expr.label("day"), func.avg(NutritionRecord.compliance_score))
        .join(Meal, Meal.id == NutritionRecord.meal_id)
        .filter(Meal.institution_id == institution_id, Meal.served_at >= since)
        .group_by(meal_day_expr)
        .order_by(meal_day_expr)
        .all()
    )
    compliance_by_day = {str(r[0]): r[1] for r in compliance_rows}

    all_days = sorted(set(attendance_by_day) | set(compliance_by_day))
    return ChartResponse(
        labels=all_days,
        series=[
            ChartSeries(label="Attendance count", data=[float(attendance_by_day.get(d, 0)) for d in all_days]),
            ChartSeries(
                label="Avg compliance score",
                data=[round(compliance_by_day.get(d) or 0, 1) for d in all_days],
            ),
        ],
    )


def get_institution_dashboard(db: Session, institution_id: UUID) -> InstitutionDashboardData:
    since = datetime.now(timezone.utc) - timedelta(days=30)

    total_meals = (
        db.query(func.count(Meal.id))
        .filter(Meal.institution_id == institution_id, Meal.served_at >= since, Meal.deleted_at.is_(None))
        .scalar()
    )
    total_students = (
        db.query(func.count(Student.id))
        .filter(Student.institution_id == institution_id, Student.deleted_at.is_(None))
        .scalar()
    )
    total_staff = (
        db.query(func.count(Staff.id))
        .filter(Staff.institution_id == institution_id, Staff.deleted_at.is_(None))
        .scalar()
    )
    avg_compliance = (
        db.query(func.avg(NutritionRecord.compliance_score))
        .join(Meal, Meal.id == NutritionRecord.meal_id)
        .filter(Meal.institution_id == institution_id, Meal.served_at >= since)
        .scalar()
    )
    pending_recommendations = (
        db.query(func.count(AIRecommendation.id))
        .filter(
            AIRecommendation.institution_id == institution_id,
            AIRecommendation.status == AIRecommendationStatus.PENDING,
        )
        .scalar()
    )
    unread_alerts = (
        db.query(func.count(Notification.id))
        .join(Student, Student.user_id == Notification.user_id)
        .filter(
            Student.institution_id == institution_id,
            Notification.type == NotificationType.ALERT,
            Notification.is_read.is_(False),
        )
        .scalar()
    )

    return InstitutionDashboardData(
        institution_id=institution_id,
        total_meals_last_30_days=total_meals or 0,
        total_students=total_students or 0,
        total_staff=total_staff or 0,
        average_compliance_score=round(avg_compliance, 1) if avg_compliance else None,
        pending_recommendations=pending_recommendations or 0,
        unread_alert_notifications=unread_alerts or 0,
        compliance_trend=get_nutrition_trend(db, institution_id, days=14),
    )


async def get_student_insights(db: Session, user: User, *, include_narrative: bool = True) -> StudentInsights:
    since = datetime.now(timezone.utc) - timedelta(days=30)

    student = db.query(Student).filter(Student.user_id == user.id).first()
    institution_id = student.institution_id if student else None

    day_expr = func.date(Meal.served_at)
    query = (
        db.query(
            day_expr.label("day"),
            func.avg(NutritionRecord.calories_kcal),
            func.avg(NutritionRecord.protein_g),
        )
        .join(Meal, Meal.id == NutritionRecord.meal_id)
        .join(Attendance, Attendance.meal_id == Meal.id)
        .filter(Attendance.user_id == user.id, Meal.served_at >= since)
        .group_by(day_expr)
        .order_by(day_expr)
    )
    rows = query.all()
    trend = ChartResponse(
        labels=[str(r[0]) for r in rows],
        series=[
            ChartSeries(label="Calories (kcal)", data=[round(r[1] or 0, 1) for r in rows]),
            ChartSeries(label="Protein (g)", data=[round(r[2] or 0, 1) for r in rows]),
        ],
    )

    avg_row = (
        db.query(
            func.avg(NutritionRecord.protein_g),
            func.avg(NutritionRecord.fiber_g),
            func.avg(NutritionRecord.iron_mg),
            func.avg(NutritionRecord.calcium_mg),
            func.avg(NutritionRecord.vitamin_c_mg),
        )
        .join(Meal, Meal.id == NutritionRecord.meal_id)
        .join(Attendance, Attendance.meal_id == Meal.id)
        .filter(Attendance.user_id == user.id, Meal.served_at >= since)
        .first()
    )
    averages = {
        "protein_g": avg_row[0],
        "fiber_g": avg_row[1],
        "iron_mg": avg_row[2],
        "calcium_mg": avg_row[3],
        "vitamin_c_mg": avg_row[4],
    }
    alerts = detect_deficiencies(averages)

    attended_count = (
        db.query(func.count(Attendance.id))
        .filter(Attendance.user_id == user.id, Attendance.attended_at >= since)
        .scalar()
    ) or 0
    total_meals_in_window = (
        db.query(func.count(Meal.id))
        .filter(
            Meal.institution_id == institution_id if institution_id else False,
            Meal.served_at >= since,
        )
        .scalar()
    ) or 0
    attendance_rate = round(attended_count / total_meals_in_window * 100, 1) if total_meals_in_window else 0.0

    narrative = None
    if include_narrative and rows:
        stats_description = (
            f"Student attendance rate: {attendance_rate}%. "
            f"Deficiency flags: {[a.nutrient for a in alerts] or 'none'}."
        )
        narrative = await _try_generate_narrative(stats_description)

    return StudentInsights(
        user_id=user.id,
        nutrition_trend=trend,
        attendance_rate_last_30_days=attendance_rate,
        deficiency_alerts=alerts,
        narrative_summary=narrative,
    )
