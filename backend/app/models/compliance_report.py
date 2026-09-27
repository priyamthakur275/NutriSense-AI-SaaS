from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Table, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import ComplianceReportStatus

if TYPE_CHECKING:
    from app.models.ai_recommendation import AIRecommendation
    from app.models.department import Department
    from app.models.institution import Institution
    from app.models.meal import Meal

# Plain many-to-many association table: a report covers many meals, and (in
# principle) a meal could be referenced by more than one report. No extra
# attributes are needed on the association itself, so a bare `Table` is used
# rather than an association-object class (contrast with `Attendance`, which
# does need extra columns and is therefore a full model).
compliance_report_meals = Table(
    "compliance_report_meals",
    Base.metadata,
    Column(
        "report_id",
        Uuid(as_uuid=True),
        ForeignKey("compliance_reports.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "meal_id",
        Uuid(as_uuid=True),
        ForeignKey("meals.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ComplianceReport(Base, UUIDMixin, TimestampMixin):
    """A periodic (e.g. weekly) institutional nutrition-compliance report,
    aggregating the meals served in that window. Not soft-deletable — once
    finalized, a report is a historical record; corrections are made by
    generating a new report, not editing or hiding an old one.
    """

    __tablename__ = "compliance_reports"

    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[ComplianceReportStatus] = mapped_column(
        Enum(ComplianceReportStatus, name="compliance_report_status"),
        nullable=False,
        default=ComplianceReportStatus.DRAFT,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Relationships ---
    institution: Mapped["Institution"] = relationship(back_populates="compliance_reports")
    department: Mapped["Department | None"] = relationship()
    meals: Mapped[list["Meal"]] = relationship(
        secondary=compliance_report_meals, back_populates="compliance_reports"
    )
    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        back_populates="based_on_report"
    )

    def __repr__(self) -> str:
        return f"<ComplianceReport id={self.id} institution_id={self.institution_id} status={self.status.value}>"
