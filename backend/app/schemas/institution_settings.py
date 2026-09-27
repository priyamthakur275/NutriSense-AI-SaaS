from uuid import UUID

from pydantic import BaseModel, Field


class InstitutionSettingsUpdate(BaseModel):
    logo_url: str | None = Field(default=None, max_length=1000)
    primary_color: str | None = Field(default=None, min_length=7, max_length=7, description="#RRGGBB")
    custom_domain: str | None = Field(default=None, max_length=255)
    timezone: str | None = Field(default=None, max_length=64)
    locale: str | None = Field(default=None, max_length=10)
    feature_flags: dict[str, bool] | None = None
    allow_self_registration: bool | None = None


class InstitutionSettingsRead(BaseModel):
    id: UUID
    institution_id: UUID
    logo_url: str | None
    primary_color: str | None
    custom_domain: str | None
    timezone: str
    locale: str
    feature_flags: dict[str, bool]
    allow_self_registration: bool

    model_config = {"from_attributes": True}
