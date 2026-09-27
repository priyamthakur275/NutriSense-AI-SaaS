from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

from app.models.user import UserRole
from app.schemas.validators import validate_password_strength


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def _password_strength(cls, value: str) -> str:
        return validate_password_strength(value)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: UserRole
    is_active: bool


class UserPublic(BaseModel):
    """Camel-cased shape consumed directly by the frontend auth store."""

    id: str
    email: EmailStr
    fullName: str
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user: UserPublic


class UserAdminCreate(UserCreate):
    """Used by admins creating an account on someone else's behalf (staff
    onboarding a student, etc.) — same validation as self-registration, plus
    an explicit role."""

    role: UserRole = UserRole.STUDENT


class UserAdminUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class BulkUserIds(BaseModel):
    user_ids: list[str] = Field(min_length=1, max_length=500)


class BulkOperationResult(BaseModel):
    succeeded: list[str]
    failed: list[str]
