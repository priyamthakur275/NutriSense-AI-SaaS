from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import ParentRelationship

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class ParentStudentLink(Base, UUIDMixin, TimestampMixin):
    """Links a Parent-role User to a Student they have guardianship over.

    This is the model that closes a gap explicitly flagged in Phase 5/6's
    tenant-isolation work: PARENT accounts previously had no institution
    linkage anywhere in the schema, so `resolve_institution_scope` /
    `verify_object_institution_access` (app.api.tenant_scope) could not
    grant them access to anything. A Parent's institutional access is
    derived transitively through this link -> the Student -> the
    Student's institution, rather than the Parent having their own
    Staff/Student-style profile (a parent isn't institutionally affiliated
    themselves; their access is entirely in service of their child's
    record).

    Many-to-many by design: a student can have more than one parent/
    guardian linked, and — less commonly but validly — a parent can have
    more than one child at the same or different institutions.
    """

    __tablename__ = "parent_student_links"
    __table_args__ = (
        UniqueConstraint("parent_user_id", "student_id", name="uq_parent_student_link"),
    )

    parent_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relationship_type: Mapped[ParentRelationship] = mapped_column(
        Enum(ParentRelationship, name="parent_relationship"), nullable=False, default=ParentRelationship.GUARDIAN
    )
    is_primary_contact: Mapped[bool] = mapped_column(default=False, nullable=False)

    # --- Relationships ---
    parent: Mapped["User"] = relationship(foreign_keys=[parent_user_id])
    student: Mapped["Student"] = relationship(back_populates="parent_links")

    def __repr__(self) -> str:
        return f"<ParentStudentLink parent={self.parent_user_id} student={self.student_id}>"
