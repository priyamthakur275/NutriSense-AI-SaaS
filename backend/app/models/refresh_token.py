from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import UUIDMixin
from app.db.session import Base
from app.utils.datetime_utils import ensure_aware

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(Base, UUIDMixin):
    """A single issued refresh token, tracked server-side to support
    rotation and revocation.

    Security notes:
    - Only a SHA-256 hash of the token is stored (`token_hash`); the raw
      token is never persisted, mirroring password-hashing practice.
    - `replaced_by_id` forms a rotation chain: on refresh, a new token is
      issued and the old one is marked revoked + linked to its replacement.
      If a revoked token is ever presented again (token reuse — a signal of
      theft), the entire chain can be invalidated by the caller.
    - Not soft-deletable in the usual sense — revocation (`revoked_at`) *is*
      this table's deletion semantics.
    """

    __tablename__ = "refresh_tokens"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("refresh_tokens.id", ondelete="SET NULL"), nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and ensure_aware(self.expires_at) > datetime.now(timezone.utc)

    def revoke(self) -> None:
        self.revoked_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<RefreshToken id={self.id} user_id={self.user_id} active={self.is_active}>"
