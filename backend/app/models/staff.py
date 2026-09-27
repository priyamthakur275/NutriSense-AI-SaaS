from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.institution import Institution
    from app.models.user import User


class Staff(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Staff profile — a one-to-one extension of `User` for institutional
    staff (canteen managers, nutritionists, wardens). Same `user_id` typing
    rationale as `Student`: must match `users.id` (String(36)) exactly.
    """

    __tablename__ = "staff"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="staff_profile")
    institution: Mapped["Institution"] = relationship(back_populates="staff_members")
    department: Mapped["Department | None"] = relationship(back_populates="staff_members")

    # Note: attendance is tracked on `User` — see Student's equivalent note.

    def __repr__(self) -> str:
        return f"<Staff id={self.id} employee_id={self.employee_id!r}>"
