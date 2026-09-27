from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.utils.datetime_utils import ensure_aware

if TYPE_CHECKING:
    from app.models.attendance import Attendance
    from app.models.audit_log import AuditLog
    from app.models.notification import Notification
    from app.models.refresh_token import RefreshToken
    from app.models.staff import Staff
    from app.models.student import Student
    from app.models.user_settings import UserSettings


class UserRole(str, enum.Enum):
    """Business-facing role names, mapped to DB-stored values:
    - STUDENT           -> "student"
    - PARENT            -> "parent"
    - STAFF             -> "staff"          (general institutional staff)
    - NUTRITIONIST      -> "nutritionist"   (staff specialization)
    - ADMIN             -> "admin"          (Institution Admin — DB value
                             kept as "admin" for backward compatibility with
                             already-issued tokens/rows; renamed at the RBAC
                             display layer, not the DB layer)
    - SUPER_ADMIN       -> "super_admin"    (platform-level admin)
    """

    STUDENT = "student"
    PARENT = "parent"
    STAFF = "staff"
    NUTRITIONIST = "nutritionist"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.STUDENT, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- Added for schema-wide consistency (Phase 4B) ---
    # NOTE: kept as explicit columns rather than the shared TimestampMixin/
    # SoftDeleteMixin, so the pre-existing `created_at` column (and its
    # already-migrated default strategy) is left completely untouched.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    # --- Added for Phase 4C (Authentication & RBAC) ---
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_login_attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @property
    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        return ensure_aware(self.locked_until) > datetime.now(timezone.utc)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        self.deleted_at = None

    # --- Relationships (one-to-one profile extensions) ---
    student_profile: Mapped["Student | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    staff_profile: Mapped["Staff | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    settings: Mapped["UserSettings | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    # --- Relationships (one-to-many) ---
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")
    attendances: Mapped[list["Attendance"]] = relationship(back_populates="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    # Attendance is intentionally NOT cascade-deleted with the user record
    # (see Attendance.user_id's ondelete="RESTRICT") — institutional
    # attendance history must survive even if an account is later removed;
    # in practice users are soft-deleted (deleted_at), never hard-deleted.

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role.value}>"
