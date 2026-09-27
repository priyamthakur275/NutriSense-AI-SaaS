from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.chat_message import ChatMessage
    from app.models.user import User


class ChatConversation(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """A single chat thread with the AI nutrition assistant. `title` is
    generated from the first user message (see chat_service) rather than
    requiring the user to name it, matching how most chat products behave.
    """

    __tablename__ = "chat_conversations"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New conversation")

    # --- Relationships ---
    user: Mapped["User"] = relationship()
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self) -> str:
        return f"<ChatConversation id={self.id} user_id={self.user_id} title={self.title!r}>"
