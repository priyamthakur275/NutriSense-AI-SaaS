from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ChatRole


class ChatMessageRead(BaseModel):
    id: UUID
    role: ChatRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatConversationRead(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatConversationDetail(ChatConversationRead):
    messages: list[ChatMessageRead]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = Field(
        default=None, description="Omit to start a new conversation"
    )


class ChatResponse(BaseModel):
    conversation_id: UUID
    reply: ChatMessageRead
    provider_used: str
