from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):
    enrollment_number: str = Field(min_length=1, max_length=50)
    grade_or_year: str | None = Field(default=None, max_length=50)


class StudentCreate(StudentBase):
    user_id: str
    institution_id: UUID
    department_id: UUID | None = None


class StudentUpdate(BaseModel):
    enrollment_number: str | None = Field(default=None, min_length=1, max_length=50)
    grade_or_year: str | None = Field(default=None, max_length=50)
    department_id: UUID | None = None
    is_active: bool | None = None


class StudentRead(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    institution_id: UUID
    department_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
