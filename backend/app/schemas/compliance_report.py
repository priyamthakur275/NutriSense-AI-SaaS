from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ComplianceReportStatus


class ComplianceReportBase(BaseModel):
    period_start: datetime
    period_end: datetime
    overall_score: float | None = Field(default=None, ge=0, le=100)
    summary: str | None = None


class ComplianceReportCreate(ComplianceReportBase):
    institution_id: UUID
    department_id: UUID | None = None
    meal_ids: list[UUID] = Field(default_factory=list, description="Meals covered by this report")


class ComplianceReportUpdate(BaseModel):
    period_start: datetime | None = None
    period_end: datetime | None = None
    overall_score: float | None = Field(default=None, ge=0, le=100)
    status: ComplianceReportStatus | None = None
    summary: str | None = None
    meal_ids: list[UUID] | None = Field(default=None, description="Replaces the full set of covered meals")


class ComplianceReportRead(ComplianceReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    institution_id: UUID
    department_id: UUID | None
    status: ComplianceReportStatus
    generated_at: datetime
    meal_ids: list[UUID]
    created_at: datetime

    @classmethod
    def from_model(cls, report) -> "ComplianceReportRead":
        return cls(
            id=report.id,
            institution_id=report.institution_id,
            department_id=report.department_id,
            period_start=report.period_start,
            period_end=report.period_end,
            overall_score=report.overall_score,
            status=report.status,
            summary=report.summary,
            generated_at=report.generated_at,
            meal_ids=[m.id for m in report.meals],
            created_at=report.created_at,
        )
