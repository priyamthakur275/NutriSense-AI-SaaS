from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=500)


class DepartmentCreate(DepartmentBase):
    institution_id: UUID


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=500)


class DepartmentRead(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    institution_id: UUID
    created_at: datetime
    updated_at: datetime
