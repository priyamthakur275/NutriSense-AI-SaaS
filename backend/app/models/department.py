from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.institution import Institution
    from app.models.meal import Meal
    from app.models.staff import Staff
    from app.models.student import Student


class Department(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """A sub-unit within an Institution (e.g. a hostel block, a school wing,
    a hospital ward). Optional — Students/Staff/Meals link to an Institution
    directly and a Department only when finer-grained grouping is used."""

    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("institution_id", "code", name="uq_department_institution_code"),
    )

    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # --- Relationships ---
    institution: Mapped["Institution"] = relationship(back_populates="departments")
    students: Mapped[list["Student"]] = relationship(back_populates="department")
    staff_members: Mapped[list["Staff"]] = relationship(back_populates="department")
    meals: Mapped[list["Meal"]] = relationship(back_populates="department")

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r} institution_id={self.institution_id}>"
