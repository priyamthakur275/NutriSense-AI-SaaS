from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.agents.reports import report_service
from app.api.deps import get_current_user
from app.api.rbac import Permission, has_permission, require_permission
from app.api.tenant_scope import verify_institution_scope
from app.core.exceptions import AuthorizationError, NotFoundError
from app.core.rate_limit import RateLimiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai_reports import (
    ChartResponse,
    InstitutionDashboardData,
    NutritionReportSummary,
    StudentInsights,
)

router = APIRouter(prefix="/ai/reports", tags=["AI Reports"])


@router.get(
    "/summary",
    response_model=NutritionReportSummary,
    dependencies=[
        Depends(require_permission(Permission.REPORTS_READ)),
        Depends(RateLimiter(times=15, seconds=60, scope="ai_reports_summary")),
    ],
)
async def get_nutrition_summary(
    institution_id: UUID = Depends(verify_institution_scope),
    period: Literal["daily", "weekly", "monthly"] = Query("daily"),
    include_narrative: bool = Query(True),
    db: Session = Depends(get_db),
) -> NutritionReportSummary:
    """Daily/weekly/monthly report — every figure here is computed
    deterministically via SQL; `narrative_summary` is the one optional
    AI-generated field (a plain-language description of the numbers above
    it, never a source of the numbers themselves)."""
    return await report_service.get_nutrition_summary(
        db, institution_id, period, include_narrative=include_narrative
    )


@router.get(
    "/nutrition-trend",
    response_model=ChartResponse,
    dependencies=[Depends(require_permission(Permission.REPORTS_READ))],
)
def get_nutrition_trend(
    institution_id: UUID = Depends(verify_institution_scope),
    days: int = Query(14, ge=1, le=90),
    db: Session = Depends(get_db),
) -> ChartResponse:
    return report_service.get_nutrition_trend(db, institution_id, days)


@router.get(
    "/attendance-nutrition",
    response_model=ChartResponse,
    dependencies=[Depends(require_permission(Permission.REPORTS_READ))],
)
def get_attendance_vs_nutrition(
    institution_id: UUID = Depends(verify_institution_scope),
    days: int = Query(14, ge=1, le=90),
    db: Session = Depends(get_db),
) -> ChartResponse:
    return report_service.get_attendance_vs_nutrition(db, institution_id, days)


@router.get(
    "/institution-dashboard",
    response_model=InstitutionDashboardData,
    dependencies=[Depends(require_permission(Permission.REPORTS_READ))],
)
def get_institution_dashboard(
    institution_id: UUID = Depends(verify_institution_scope), db: Session = Depends(get_db)
) -> InstitutionDashboardData:
    return report_service.get_institution_dashboard(db, institution_id)


@router.get(
    "/student-insights",
    response_model=StudentInsights,
    dependencies=[Depends(RateLimiter(times=15, seconds=60, scope="ai_reports_student_insights"))],
)
async def get_student_insights(
    user_id: str | None = Query(None, description="Omit to view your own insights"),
    include_narrative: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentInsights:
    """Defaults to the caller's own insights (any authenticated user may
    view their own data). Viewing another user's insights requires
    `reports:read` — a student cannot pull another student's nutrition
    history just by knowing their user ID."""
    if user_id is None or user_id == current_user.id:
        target = current_user
    else:
        if not has_permission(current_user.role, Permission.REPORTS_READ):
            raise AuthorizationError("You do not have permission to view another user's insights")
        target = db.query(User).filter(User.id == user_id).first()
        if target is None:
            raise NotFoundError(f"User '{user_id}' not found")

    return await report_service.get_student_insights(db, target, include_narrative=include_narrative)
