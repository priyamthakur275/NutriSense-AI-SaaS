from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.chat_room import ChatRoom
    from app.models.user import User


class RoomMessage(Base, UUIDMixin, TimestampMixin):
    """A message in a ChatRoom. Persisted unconditionally regardless of
    recipient online status — this IS the offline-message queue; a client
    reconnecting fetches history via the existing paginated REST list."""

    __tablename__ = "room_messages"

    room_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    room: Mapped["ChatRoom"] = relationship(back_populates="messages")
    sender: Mapped["User | None"] = relationship()

    def __repr__(self) -> str:
        return f"<RoomMessage id={self.id} room_id={self.room_id}>"
