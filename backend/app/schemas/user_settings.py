from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ThemePreference


class UserSettingsUpdate(BaseModel):
    theme: ThemePreference | None = None
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    language: str | None = Field(default=None, max_length=10)
    timezone: str | None = Field(default=None, max_length=64)


class UserSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    theme: ThemePreference
    email_notifications: bool
    push_notifications: bool
    language: str
    timezone: str
