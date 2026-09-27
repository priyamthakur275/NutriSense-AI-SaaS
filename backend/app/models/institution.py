from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import InstitutionType

if TYPE_CHECKING:
    from app.models.ai_recommendation import AIRecommendation
    from app.models.compliance_report import ComplianceReport
    from app.models.department import Department
    from app.models.institution_settings import InstitutionSettings
    from app.models.meal import Meal
    from app.models.staff import Staff
    from app.models.student import Student


class Institution(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """A tenant organization (school, hospital, hostel, canteen operator, etc.)
    that NutriSense AI serves. The root of the multi-tenancy hierarchy —
    Departments, Students, Staff, and Meals all trace back to one."""

    __tablename__ = "institutions"
    __table_args__ = (Index("ix_institutions_type_active", "type", "deleted_at"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[InstitutionType] = mapped_column(
        Enum(InstitutionType, name="institution_type"), nullable=False
    )
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str] = mapped_column(String(120), nullable=False, default="India")
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # --- Relationships (one-to-many) ---
    departments: Mapped[list["Department"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    students: Mapped[list["Student"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    staff_members: Mapped[list["Staff"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    meals: Mapped[list["Meal"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    compliance_reports: Mapped[list["ComplianceReport"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    settings: Mapped["InstitutionSettings | None"] = relationship(
        back_populates="institution", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Institution id={self.id} name={self.name!r} type={self.type.value}>"
