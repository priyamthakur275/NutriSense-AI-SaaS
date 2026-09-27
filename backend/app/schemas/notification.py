from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import NotificationType


class NotificationCreate(BaseModel):
    user_id: str
    type: NotificationType
    title: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1)


class NotificationUpdate(BaseModel):
    is_read: bool | None = None


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    type: NotificationType
    title: str
    message: str
    is_read: bool
    read_at: datetime | None
    created_at: datetime
