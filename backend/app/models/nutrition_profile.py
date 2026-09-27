from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import ActivityLevel, DietPreference, FitnessGoal, Gender

if TYPE_CHECKING:
    from app.models.user import User

JSONVariant = JSON().with_variant(JSONB(), "postgresql")


class NutritionProfile(Base, UUIDMixin, TimestampMixin):
    """Per-user health/fitness profile driving the recommendation engine —
    one-to-one with User, kept in its own table for the same reason as
    UserSettings: this is optional, lazily-created data that shouldn't
    churn the auth-critical users table, and a user may never fill it in.

    `medical_conditions` and `food_allergies` are free-form string lists
    (JSON) rather than a fixed enum set — the space of real-world
    conditions/allergies is too open-ended to enumerate, and what matters
    to the recommendation engine is the text itself being passed to the
    LLM, not a closed taxonomy.

    BMI is deliberately NOT stored as a column — it's fully derived from
    height/weight and would go stale the moment either changes; it's
    exposed as a computed property instead (see `bmi`), never persisted.
    """

    __tablename__ = "nutrition_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender"), nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity_level: Mapped[ActivityLevel | None] = mapped_column(
        Enum(ActivityLevel, name="activity_level"), nullable=True
    )
    medical_conditions: Mapped[list[str]] = mapped_column(JSONVariant, nullable=False, default=list)
    food_allergies: Mapped[list[str]] = mapped_column(JSONVariant, nullable=False, default=list)
    diet_preference: Mapped[DietPreference | None] = mapped_column(
        Enum(DietPreference, name="diet_preference"), nullable=True
    )
    fitness_goal: Mapped[FitnessGoal | None] = mapped_column(
        Enum(FitnessGoal, name="fitness_goal"), nullable=True
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship()

    @property
    def bmi(self) -> float | None:
        if not self.height_cm or not self.weight_kg:
            return None
        height_m = self.height_cm / 100
        return round(self.weight_kg / (height_m**2), 1)

    def __repr__(self) -> str:
        return f"<NutritionProfile user_id={self.user_id} bmi={self.bmi}>"
