from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import UUIDMixin
from app.db.session import Base
from app.utils.datetime_utils import ensure_aware

if TYPE_CHECKING:
    from app.models.user import User


class PasswordResetToken(Base, UUIDMixin):
    """A single-use, short-lived token issued for the forgot-password flow.
    Only the SHA-256 hash is stored — same rationale as `RefreshToken`."""

    __tablename__ = "password_reset_tokens"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    user: Mapped["User"] = relationship()

    @property
    def is_valid(self) -> bool:
        return self.used_at is None and ensure_aware(self.expires_at) > datetime.now(timezone.utc)

    def mark_used(self) -> None:
        self.used_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<PasswordResetToken id={self.id} user_id={self.user_id} valid={self.is_valid}>"
