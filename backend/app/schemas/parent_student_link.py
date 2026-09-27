from uuid import UUID

from pydantic import BaseModel

from app.models.enums import ParentRelationship


class ParentStudentLinkCreate(BaseModel):
    parent_user_id: str
    student_id: UUID
    relationship_type: ParentRelationship = ParentRelationship.GUARDIAN
    is_primary_contact: bool = False


class ParentStudentLinkRead(BaseModel):
    id: UUID
    parent_user_id: str
    student_id: UUID
    relationship_type: ParentRelationship
    is_primary_contact: bool

    model_config = {"from_attributes": True}
