"""Chart-ready response schemas for the reporting/analytics layer.

`ChartResponse` follows the shape most charting libraries (Chart.js,
Recharts) expect directly: `labels` for the x-axis, `series` as one or
more named datasets — the frontend can bind this with no reshaping.

Nutrient reference thresholds used for deficiency detection are
illustrative, general-population daily-value approximations (broadly
aligned with common ICMR-NIN / WHO guidance), not a certified per-individual
medical determination — stated plainly in the deficiency-detection module
itself rather than implied here.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChartSeries(BaseModel):
    label: str
    data: list[float]


class ChartResponse(BaseModel):
    labels: list[str]
    series: list[ChartSeries]


class DeficiencyAlert(BaseModel):
    nutrient: str
    current_average: float
    recommended_minimum: float
    unit: str
    severity: str  # "mild" | "moderate" | "severe"


class NutritionReportSummary(BaseModel):
    period: str  # "daily" | "weekly" | "monthly"
    period_start: datetime
    period_end: datetime
    institution_id: UUID
    meals_analyzed: int
    average_calories: float | None
    average_protein: float | None
    average_carbs: float | None
    average_fat: float | None
    average_compliance_score: float | None
    deficiency_alerts: list[DeficiencyAlert]
    narrative_summary: str | None = None


class InstitutionDashboardData(BaseModel):
    institution_id: UUID
    total_meals_last_30_days: int
    total_students: int
    total_staff: int
    average_compliance_score: float | None
    pending_recommendations: int
    unread_alert_notifications: int
    compliance_trend: ChartResponse


class StudentInsights(BaseModel):
    user_id: str
    nutrition_trend: ChartResponse
    attendance_rate_last_30_days: float
    deficiency_alerts: list[DeficiencyAlert]
    narrative_summary: str | None = None
