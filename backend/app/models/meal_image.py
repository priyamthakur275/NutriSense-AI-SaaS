from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.meal import Meal
    from app.models.user import User

# JSONB on Postgres, plain JSON (TEXT-backed) on SQLite for local dev —
# `with_variant` keeps the model portable across both without a compile-time
# dependency on which backend is active.
JSONVariant = JSON().with_variant(JSONB(), "postgresql")


class MealImage(Base, UUIDMixin, TimestampMixin):
    """One captured image of a Meal (a tray may be photographed from
    multiple angles, or re-captured). Not soft-deletable — images are either
    present or removed outright by storage lifecycle policy, not "hidden"."""

    __tablename__ = "meal_images"

    meal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    uploaded_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    detection_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONVariant, nullable=True)

    # --- Relationships ---
    meal: Mapped["Meal"] = relationship(back_populates="images")
    uploaded_by: Mapped["User | None"] = relationship(foreign_keys=[uploaded_by_id])

    def __repr__(self) -> str:
        return f"<MealImage id={self.id} meal_id={self.meal_id}>"
