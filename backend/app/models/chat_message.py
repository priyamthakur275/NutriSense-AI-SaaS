from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import TimestampMixin, UUIDMixin
from app.db.session import Base
from app.models.enums import ChatRole

if TYPE_CHECKING:
    from app.models.chat_conversation import ChatConversation


class ChatMessage(Base, UUIDMixin, TimestampMixin):
    """One turn in a ChatConversation. Not soft-deletable and has no
    `updated_at` beyond what TimestampMixin gives for free — a sent message
    is immutable, matching Attendance/AuditLog's rationale elsewhere in
    this schema."""

    __tablename__ = "chat_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[ChatRole] = mapped_column(Enum(ChatRole, name="chat_role"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # --- Relationships ---
    conversation: Mapped["ChatConversation"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} role={self.role.value}>"
