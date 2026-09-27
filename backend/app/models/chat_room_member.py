from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.chat_room import ChatRoom
    from app.models.user import User


class ChatRoomMember(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_room_members"
    __table_args__ = (UniqueConstraint("room_id", "user_id", name="uq_chat_room_member"),)

    room_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    room: Mapped["ChatRoom"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<ChatRoomMember room_id={self.room_id} user_id={self.user_id}>"
