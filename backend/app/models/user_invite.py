from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import InviteStatus
from app.models.user import UserRole
from app.utils.datetime_utils import ensure_aware

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.institution import Institution
    from app.models.user import User


class UserInvite(Base, UUIDMixin, TimestampMixin):
    """An outstanding invitation for someone to join an institution — the
    core of the "invite system" requirement. Distinct from an admin
    directly creating a User (UserAdminCreate, Phase 4D), where the admin
    picks the new account's password: here, the invitee proves control of
    their email via a token and sets their own password on acceptance,
    which is the correct flow for onboarding someone who isn't already a
    trusted operator of the account.

    Same hash-only token storage as RefreshToken / PasswordResetToken /
    EmailVerificationToken (Phase 4C) — the raw token is never persisted.
    """

    __tablename__ = "user_invites"

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    invited_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    status: Mapped[InviteStatus] = mapped_column(
        Enum(InviteStatus, name="invite_status"), nullable=False, default=InviteStatus.PENDING
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    institution: Mapped["Institution"] = relationship()
    department: Mapped["Department | None"] = relationship()
    invited_by: Mapped["User | None"] = relationship(foreign_keys=[invited_by_id])

    @property
    def is_valid(self) -> bool:
        return self.status == InviteStatus.PENDING and ensure_aware(self.expires_at) > datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<UserInvite id={self.id} email={self.email!r} status={self.status.value}>"
