from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.meal import Meal


class NutritionRecord(Base, UUIDMixin, TimestampMixin):
    """The aggregated nutrition profile computed for exactly one Meal —
    one-to-one via the unique `meal_id`. Macro fields are always populated
    once analysis completes; micronutrients are nullable since not every
    detected food item has full micronutrient data available."""

    __tablename__ = "nutrition_records"

    meal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("meals.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # --- Macronutrients (always computed once analysis finishes) ---
    calories_kcal: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fiber_g: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Micronutrients (nullable — not always resolvable per food item) ---
    iron_mg: Mapped[float | None] = mapped_column(Float, nullable=True)
    calcium_mg: Mapped[float | None] = mapped_column(Float, nullable=True)
    vitamin_c_mg: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Compliance outcome (populated by the compliance engine, not here) ---
    compliance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_compliant: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    computed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    meal: Mapped["Meal"] = relationship(back_populates="nutrition_record")

    def __repr__(self) -> str:
        return f"<NutritionRecord meal_id={self.meal_id} calories={self.calories_kcal}>"
