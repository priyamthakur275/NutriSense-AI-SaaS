from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import ChatRoomType

if TYPE_CHECKING:
    from app.models.institution import Institution
    from app.models.user import User


class ChatRoom(Base, UUIDMixin, TimestampMixin):
    """Multi-user chat room — distinct from ChatConversation (the AI
    assistant chat), this is human-to-human. `type=DIRECT` rooms have
    exactly 2 members (enforced at the service layer, not a DB
    constraint); `type=GROUP` can have any number."""

    __tablename__ = "chat_rooms"

    institution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[ChatRoomType] = mapped_column(Enum(ChatRoomType, name="chat_room_type"), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    institution: Mapped["Institution"] = relationship()
    created_by: Mapped["User | None"] = relationship(foreign_keys=[created_by_id])
    members: Mapped[list["ChatRoomMember"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    messages: Mapped[list["RoomMessage"]] = relationship(back_populates="room", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatRoom id={self.id} type={self.type.value}>"
