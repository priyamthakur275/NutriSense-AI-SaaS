"""Kitchen operations: one row per meal service (e.g. "Tuesday lunch") and one
row per dish cooked in that service.

Waste is split the way kitchens actually see it:
  - pot leftover  = cooked but never served (over-production)
  - plate waste   = served but scraped off returned plates (not eaten)
  - eaten         = prepared - pot leftover - plate waste
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import MealType


class KitchenService(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "kitchen_services"
    __table_args__ = (Index("ix_kitchen_services_owner_date", "owner_id", "service_date"),)

    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Non-native enum (VARCHAR + check): avoids clashing with the Postgres
    # "meal_type" type the meals table already owns.
    meal_type: Mapped[MealType] = mapped_column(
        Enum(MealType, name="kitchen_meal_type", native_enum=False, length=20), nullable=False
    )
    plates_served: Mapped[int] = mapped_column(Integer, nullable=False)
    is_sample: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(String(300), nullable=True)

    dishes: Mapped[list["KitchenServiceDish"]] = relationship(
        back_populates="service", cascade="all, delete-orphan", lazy="selectin"
    )


class KitchenServiceDish(Base, UUIDMixin):
    __tablename__ = "kitchen_service_dishes"

    service_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("kitchen_services.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dish_key: Mapped[str] = mapped_column(String(50), nullable=False)
    prepared_kg: Mapped[float] = mapped_column(Float, nullable=False)
    pot_leftover_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    plate_waste_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    service: Mapped[KitchenService] = relationship(back_populates="dishes")
