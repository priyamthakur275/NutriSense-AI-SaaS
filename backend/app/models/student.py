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
    from app.models.parent_student_link import ParentStudentLink
    from app.models.user import User


class Student(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Student profile — a one-to-one extension of `User` for the
    `UserRole.STUDENT` role, holding institution-specific enrollment data
    that doesn't belong on the auth identity itself.

    Note: `user_id` is `String(36)` (not the native `Uuid` type used by this
    model's own primary key) because it must exactly match the type of the
    existing, already-migrated `users.id` column for the foreign key to be
    valid.
    """

    __tablename__ = "students"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    enrollment_number: Mapped[str] = mapped_column(String(50), nullable=False)
    grade_or_year: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="student_profile")
    institution: Mapped["Institution"] = relationship(back_populates="students")
    department: Mapped["Department | None"] = relationship(back_populates="students")
    parent_links: Mapped[list["ParentStudentLink"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )

    # Note: attendance is tracked on `User` (not here) since both Student and
    # Staff already link 1:1 to User — avoids a duplicate/ambiguous FK path.
    # Access via `student.user.attendances`.

    def __repr__(self) -> str:
        return f"<Student id={self.id} enrollment_number={self.enrollment_number!r}>"
