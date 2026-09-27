"""ComplianceReport has one piece of real logic beyond plain field
assignment: `meal_ids` in the request body must be resolved into actual
Meal objects to populate the many-to-many `meals` relationship — a bare
`repo.create(payload.model_dump())` can't do that (SQLAlchemy relationships
aren't set via raw UUID lists), so it lives here rather than in the
repository or endpoint.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.models.compliance_report import ComplianceReport
from app.models.enums import ComplianceReportStatus
from app.models.meal import Meal
from app.repositories.compliance_report import ComplianceReportRepository
from app.schemas.compliance_report import ComplianceReportCreate, ComplianceReportUpdate


def _resolve_meals(db: Session, meal_ids: list[UUID]) -> list[Meal]:
    if not meal_ids:
        return []
    meals = db.query(Meal).filter(Meal.id.in_(meal_ids), Meal.deleted_at.is_(None)).all()
    found_ids = {m.id for m in meals}
    missing = set(meal_ids) - found_ids
    if missing:
        raise ValidationAppError(f"Meal(s) not found: {', '.join(str(m) for m in missing)}")
    return meals


def create_report(db: Session, payload: ComplianceReportCreate) -> ComplianceReport:
    repo = ComplianceReportRepository(db)
    data = payload.model_dump(exclude={"meal_ids"})
    data["generated_at"] = datetime.now(timezone.utc)
    data["status"] = ComplianceReportStatus.DRAFT
    report = repo.create(data)
    report.meals = _resolve_meals(db, payload.meal_ids)
    db.commit()
    db.refresh(report)
    return report


def update_report(db: Session, report: ComplianceReport, payload: ComplianceReportUpdate) -> ComplianceReport:
    data = payload.model_dump(exclude={"meal_ids"}, exclude_unset=True)
    for field, value in data.items():
        setattr(report, field, value)

    if payload.meal_ids is not None:
        report.meals = _resolve_meals(db, payload.meal_ids)

    db.commit()
    db.refresh(report)
    return report
