from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import ThemePreference

if TYPE_CHECKING:
    from app.models.user import User


class UserSettings(Base, UUIDMixin, TimestampMixin):
    """Per-user application preferences — one-to-one with User. Kept as a
    separate table (rather than columns on `users`) so preference growth
    doesn't churn the auth-critical users table, and so it can be created
    lazily (a user may have no settings row until they first change one)."""

    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    theme: Mapped[ThemePreference] = mapped_column(
        Enum(ThemePreference, name="theme_preference"), nullable=False, default=ThemePreference.SYSTEM
    )
    email_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    push_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Kolkata")

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings user_id={self.user_id} theme={self.theme.value}>"
