from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import AnnouncementAudience

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.institution import Institution
    from app.models.user import User


class Announcement(Base, UUIDMixin, TimestampMixin):
    """An institution-wide (or department-scoped, or audience-targeted)
    broadcast — the record of *that a campaign was sent*, distinct from
    the individual Notification rows it fans out to each recipient.
    Tracking this separately from Notification means "how many
    announcements has this institution sent this month" is a direct
    query, not something inferred by grouping ad-hoc notifications after
    the fact.
    """

    __tablename__ = "announcements"

    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    audience: Mapped[AnnouncementAudience] = mapped_column(
        Enum(AnnouncementAudience, name="announcement_audience"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_count: Mapped[int] = mapped_column(nullable=False, default=0)

    # --- Relationships ---
    institution: Mapped["Institution"] = relationship()
    department: Mapped["Department | None"] = relationship()
    created_by: Mapped["User | None"] = relationship(foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<Announcement id={self.id} title={self.title!r} audience={self.audience.value}>"
