from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StaffBase(BaseModel):
    employee_id: str = Field(min_length=1, max_length=50)
    job_title: str | None = Field(default=None, max_length=120)


class StaffCreate(StaffBase):
    user_id: str
    institution_id: UUID
    department_id: UUID | None = None


class StaffUpdate(BaseModel):
    employee_id: str | None = Field(default=None, min_length=1, max_length=50)
    job_title: str | None = Field(default=None, max_length=120)
    department_id: UUID | None = None
    is_active: bool | None = None


class StaffRead(StaffBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    institution_id: UUID
    department_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
