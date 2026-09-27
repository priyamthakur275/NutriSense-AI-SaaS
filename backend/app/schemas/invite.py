from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import InviteStatus
from app.models.user import UserRole
from app.schemas.user import TokenResponse
from app.schemas.validators import validate_password_strength


class InviteCreate(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.STUDENT
    institution_id: UUID
    department_id: UUID | None = None


class InviteRead(BaseModel):
    id: UUID
    email: str
    role: UserRole
    institution_id: UUID
    department_id: UUID | None
    invited_by_id: str | None
    status: InviteStatus
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteAccept(BaseModel):
    token: str
    full_name: str = Field(min_length=1, max_length=255)
    password: str

    @field_validator("password")
    @classmethod
    def _password_strength(cls, value: str) -> str:
        return validate_password_strength(value)


class InviteAcceptResponse(TokenResponse):
    pass
