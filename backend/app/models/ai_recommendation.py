from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import AIRecommendationStatus, AIRecommendationType

if TYPE_CHECKING:
    from app.models.compliance_report import ComplianceReport
    from app.models.department import Department
    from app.models.institution import Institution
    from app.models.user import User


class AIRecommendation(Base, UUIDMixin, TimestampMixin):
    """A recommendation produced by an agent (e.g. the Suggestion or Planner
    agent), optionally grounded in a specific ComplianceReport. Reviewed and
    actioned by a human staff/admin user before it's considered applied."""

    __tablename__ = "ai_recommendations"

    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    based_on_report_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("compliance_reports.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    recommendation_type: Mapped[AIRecommendationType] = mapped_column(
        Enum(AIRecommendationType, name="ai_recommendation_type"), nullable=False
    )
    status: Mapped[AIRecommendationStatus] = mapped_column(
        Enum(AIRecommendationStatus, name="ai_recommendation_status"),
        nullable=False,
        default=AIRecommendationStatus.PENDING,
    )
    generated_by_agent: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    institution: Mapped["Institution"] = relationship(back_populates="ai_recommendations")
    department: Mapped["Department | None"] = relationship()
    based_on_report: Mapped["ComplianceReport | None"] = relationship(
        back_populates="ai_recommendations"
    )
    reviewed_by: Mapped["User | None"] = relationship(foreign_keys=[reviewed_by_id])

    def __repr__(self) -> str:
        return f"<AIRecommendation id={self.id} type={self.recommendation_type.value} status={self.status.value}>"
