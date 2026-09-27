"""Platform-level admin dashboard — SUPER_ADMIN only, deliberately. This is
distinct from app.api.v1.endpoints.ai_reports (Phase 5), which serves
institution-scoped dashboards to Institution Admins/Nutritionists about
*their own* institution. This module is the platform-operator view across
every institution at once, so it never needs (and never accepts) an
institution_id — scoping it per-institution would defeat its purpose.

AuditLog does not carry an institution_id directly (it logs against a
user, not a tenant) — attempting to scope activity-log access to "my
institution's users only" would require a non-trivial join through
Student/Staff and still leak system-actor entries (user_id=None). Rather
than build that leaky approximation, activity logs are kept SUPER_ADMIN-
only, consistent with the rest of this module.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.rbac import require_roles
from app.db.session import get_db
from app.models.ai_recommendation import AIRecommendation
from app.models.audit_log import AuditLog
from app.models.chat_conversation import ChatConversation
from app.models.chat_message import ChatMessage
from app.models.enums import AIRecommendationStatus, AuditAction
from app.models.institution import Institution
from app.models.nutrition_record import NutritionRecord
from app.models.user import User, UserRole
from app.repositories.audit_log import AuditLogRepository
from app.schemas.admin import AIUsageStats, AuditLogRead, PlatformDashboardData
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"], dependencies=[Depends(require_roles(UserRole.SUPER_ADMIN))])


@router.get("/dashboard", response_model=PlatformDashboardData)
def get_platform_dashboard(db: Session = Depends(get_db)) -> PlatformDashboardData:
    total_institutions = db.query(func.count(Institution.id)).filter(Institution.deleted_at.is_(None)).scalar() or 0
    total_users = db.query(func.count(User.id)).filter(User.deleted_at.is_(None)).scalar() or 0

    role_rows = (
        db.query(User.role, func.count(User.id))
        .filter(User.deleted_at.is_(None))
        .group_by(User.role)
        .all()
    )
    users_by_role = {role.value: count for role, count in role_rows}

    total_meals_analyzed = db.query(func.count(NutritionRecord.id)).scalar() or 0
    total_recommendations = db.query(func.count(AIRecommendation.id)).scalar() or 0
    total_chat_messages = db.query(func.count(ChatMessage.id)).scalar() or 0

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_denials = (
        db.query(func.count(AuditLog.id))
        .filter(AuditLog.action == AuditAction.ACCESS_DENIED, AuditLog.created_at >= since)
        .scalar()
        or 0
    )

    return PlatformDashboardData(
        total_institutions=total_institutions,
        total_users=total_users,
        users_by_role=users_by_role,
        total_meals_analyzed=total_meals_analyzed,
        total_ai_recommendations_generated=total_recommendations,
        total_chat_messages=total_chat_messages,
        recent_access_denials_24h=recent_denials,
    )


@router.get("/ai-usage", response_model=AIUsageStats)
def get_ai_usage_stats(db: Session = Depends(get_db)) -> AIUsageStats:
    total_vision = db.query(func.count(NutritionRecord.id)).scalar() or 0
    total_conversations = db.query(func.count(ChatConversation.id)).scalar() or 0
    total_messages = db.query(func.count(ChatMessage.id)).scalar() or 0
    total_recommendations = db.query(func.count(AIRecommendation.id)).scalar() or 0

    status_rows = (
        db.query(AIRecommendation.status, func.count(AIRecommendation.id))
        .group_by(AIRecommendation.status)
        .all()
    )
    by_status = {s.value: count for s, count in status_rows}
    for status_value in AIRecommendationStatus:
        by_status.setdefault(status_value.value, 0)

    return AIUsageStats(
        total_vision_analyses=total_vision,
        total_chat_conversations=total_conversations,
        total_chat_messages=total_messages,
        total_recommendations_generated=total_recommendations,
        recommendations_by_status=by_status,
    )


@router.get("/activity-logs", response_model=PaginatedResponse[AuditLogRead])
def list_activity_logs(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    user_id: str | None = Query(None),
    action: AuditAction | None = Query(None),
) -> PaginatedResponse[AuditLogRead]:
    repo = AuditLogRepository(db)
    items, total = repo.list(
        pagination=pagination,
        default_sort_field="created_at",
        allowed_sort_fields={"created_at"},
        filters={"user_id": user_id, "action": action},
    )
    return PaginatedResponse.build(
        [AuditLogRead.model_validate(a) for a in items], total_items=total, params=pagination
    )
