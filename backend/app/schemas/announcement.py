from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import AnnouncementAudience


class AnnouncementCreate(BaseModel):
    institution_id: UUID
    department_id: UUID | None = None
    audience: AnnouncementAudience = AnnouncementAudience.ALL
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)


class AnnouncementRead(BaseModel):
    id: UUID
    institution_id: UUID
    department_id: UUID | None
    created_by_id: str | None
    audience: AnnouncementAudience
    title: str
    body: str
    recipient_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
