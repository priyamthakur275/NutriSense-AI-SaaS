from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import InstitutionType


class InstitutionBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    type: InstitutionType
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    country: str = Field(default="India", max_length=120)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=32)


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    type: InstitutionType | None = None
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=32)
    is_active: bool | None = None


class InstitutionRead(InstitutionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
