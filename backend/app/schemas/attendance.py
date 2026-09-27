from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import AttendanceMethod


class AttendanceCreate(BaseModel):
    user_id: str
    meal_id: UUID
    method: AttendanceMethod = AttendanceMethod.MANUAL


class AttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    meal_id: UUID
    method: AttendanceMethod
    attended_at: datetime
