from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import AuditAction


class AuditLogRead(BaseModel):
    id: UUID
    user_id: str | None
    action: AuditAction
    entity_type: str | None
    entity_id: str | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PlatformDashboardData(BaseModel):
    total_institutions: int
    total_users: int
    users_by_role: dict[str, int]
    total_meals_analyzed: int
    total_ai_recommendations_generated: int
    total_chat_messages: int
    recent_access_denials_24h: int


class AIUsageStats(BaseModel):
    total_vision_analyses: int
    total_chat_conversations: int
    total_chat_messages: int
    total_recommendations_generated: int
    recommendations_by_status: dict[str, int]
