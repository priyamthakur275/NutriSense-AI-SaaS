from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import MealStatus, MealType

if TYPE_CHECKING:
    from app.models.attendance import Attendance
    from app.models.compliance_report import ComplianceReport
    from app.models.department import Department
    from app.models.institution import Institution
    from app.models.meal_image import MealImage
    from app.models.nutrition_record import NutritionRecord
    from app.models.user import User


class Meal(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """A single served meal event captured for analysis — one tray/batch at
    a specific place and time. The hub of the domain: images, the resulting
    nutrition profile, attendance, and compliance reporting all trace back
    to a Meal."""

    __tablename__ = "meals"
    __table_args__ = (
        Index("ix_meals_institution_served_at", "institution_id", "served_at"),
    )

    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType, name="meal_type"), nullable=False)
    status: Mapped[MealStatus] = mapped_column(
        Enum(MealStatus, name="meal_status"), nullable=False, default=MealStatus.PENDING
    )
    served_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # --- Relationships ---
    institution: Mapped["Institution"] = relationship(back_populates="meals")
    department: Mapped["Department | None"] = relationship(back_populates="meals")
    created_by: Mapped["User | None"] = relationship(foreign_keys=[created_by_id])

    images: Mapped[list["MealImage"]] = relationship(
        back_populates="meal", cascade="all, delete-orphan"
    )
    nutrition_record: Mapped["NutritionRecord | None"] = relationship(
        back_populates="meal", uselist=False, cascade="all, delete-orphan"
    )
    attendances: Mapped[list["Attendance"]] = relationship(
        back_populates="meal", cascade="all, delete-orphan"
    )
    compliance_reports: Mapped[list["ComplianceReport"]] = relationship(
        secondary="compliance_report_meals", back_populates="meals"
    )

    def __repr__(self) -> str:
        return f"<Meal id={self.id} name={self.name!r} type={self.meal_type.value} status={self.status.value}>"
