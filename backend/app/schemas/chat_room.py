from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.enums import ChatRoomType


class ChatRoomCreate(BaseModel):
    institution_id: UUID
    type: ChatRoomType
    name: str | None = None
    member_ids: list[str] = Field(default_factory=list)


class ChatRoomRead(BaseModel):
    id: UUID
    institution_id: UUID
    type: ChatRoomType
    name: str | None
    created_by_id: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class RoomMessageRead(BaseModel):
    id: UUID
    room_id: UUID
    sender_id: str | None
    content: str
    created_at: datetime
    model_config = {"from_attributes": True}


class DirectRoomRequest(BaseModel):
    institution_id: UUID
    other_user_id: str
