"""Reusable declarative mixins for SQLAlchemy models.

Usage pattern (SQLAlchemy declarative mixins are combined with `Base` on the
concrete model, not on the mixin itself):

    from app.db.session import Base
    from app.db.base_class import UUIDMixin, TimestampMixin, SoftDeleteMixin

    class Institution(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
        __tablename__ = "institutions"
        name: Mapped[str] = mapped_column(String(255), nullable=False)

This keeps every model's primary key, timestamp, and soft-delete behavior
consistent without duplicating column definitions across the codebase.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """Adds a UUID primary key.

    Renders as native UUID on PostgreSQL and CHAR(32) on SQLite via
    SQLAlchemy's cross-dialect `Uuid` type — no per-model boilerplate needed.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )


class TimestampMixin:
    """Adds timezone-aware created_at / updated_at columns.

    Both are set server-side (via `func.now()`) so the value is authoritative
    even when multiple app instances have slightly different clocks.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Adds soft-delete support via a nullable `deleted_at` timestamp.

    Rows are never physically removed by application code; repositories
    should filter `deleted_at IS NULL` for "active" queries. Use
    `.soft_delete()` / `.restore()` rather than mutating `deleted_at` directly
    so the intent stays explicit at call sites.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        self.deleted_at = None
