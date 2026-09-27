from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.institution import Institution

JSONVariant = JSON().with_variant(JSONB(), "postgresql")

# Feature flags an institution can individually enable/disable — kept as a
# JSON dict (feature_key -> bool) rather than one boolean column per
# feature, so adding a new toggleable feature never needs a migration.
DEFAULT_FEATURE_FLAGS: dict[str, bool] = {
    "ai_vision_analysis": True,
    "ai_chat_assistant": True,
    "ai_recommendations": True,
    "parent_portal": True,
}


class InstitutionSettings(Base, UUIDMixin, TimestampMixin):
    """Per-institution branding and configuration — one-to-one with
    Institution, same rationale as UserSettings/NutritionProfile: optional,
    lazily-created data kept out of the core Institution table so branding
    changes don't churn a row every other institution-scoped query joins
    against.
    """

    __tablename__ = "institution_settings"

    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    primary_color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # "#RRGGBB"
    custom_domain: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Kolkata")
    locale: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    feature_flags: Mapped[dict[str, Any]] = mapped_column(
        JSONVariant, nullable=False, default=lambda: dict(DEFAULT_FEATURE_FLAGS)
    )
    allow_self_registration: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # --- Relationships ---
    institution: Mapped["Institution"] = relationship(back_populates="settings")

    def is_feature_enabled(self, feature_key: str) -> bool:
        """Falls back to the platform default if this institution hasn't
        explicitly overridden a given flag (e.g. a new feature shipped
        after this row was created won't silently read as disabled)."""
        return self.feature_flags.get(feature_key, DEFAULT_FEATURE_FLAGS.get(feature_key, False))

    def __repr__(self) -> str:
        return f"<InstitutionSettings institution_id={self.institution_id}>"
