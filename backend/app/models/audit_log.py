from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from app.db.session import Base
from app.models.enums import AuditAction

if TYPE_CHECKING:
    from app.models.user import User

JSONVariant = JSON().with_variant(JSONB(), "postgresql")


class AuditLog(Base):
    """An immutable record of a security- or compliance-relevant action.

    Deliberately does NOT use UUIDMixin/TimestampMixin/SoftDeleteMixin:
    - no `updated_at` — an audit entry is never modified after creation
    - no soft delete — audit logs must not be hideable, only retained
    - `user_id` is nullable + ON DELETE SET NULL — the log entry survives
      even if the acting user's account is later removed, which is the
      entire point of an audit trail.
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction, name="audit_action"), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONVariant, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6-safe length
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    user: Mapped["User | None"] = relationship(back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action.value} entity_type={self.entity_type!r}>"
