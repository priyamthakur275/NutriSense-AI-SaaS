from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import UUIDMixin
from app.db.session import Base
from app.models.enums import AttendanceMethod

if TYPE_CHECKING:
    from app.models.meal import Meal
    from app.models.user import User


class Attendance(Base, UUIDMixin):
    """Links a User (Student or Staff — both extend User 1:1) to a Meal they
    were confirmed present for. The association-object pattern is used
    (rather than a bare M2M secondary table) because attendance carries its
    own attributes (method, timestamp).

    Not soft-deletable and has no `updated_at`: an attendance record is an
    immutable fact about a point in time, not a mutable entity.
    """

    __tablename__ = "attendances"
    __table_args__ = (
        UniqueConstraint("user_id", "meal_id", name="uq_attendance_user_meal"),
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    meal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    method: Mapped[AttendanceMethod] = mapped_column(
        Enum(AttendanceMethod, name="attendance_method"), nullable=False
    )
    attended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="attendances")
    meal: Mapped["Meal"] = relationship(back_populates="attendances")

    def __repr__(self) -> str:
        return f"<Attendance user_id={self.user_id} meal_id={self.meal_id} method={self.method.value}>"
