from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.api.tenant_scope import resolve_institution_scope, verify_object_institution_access
from app.db.session import get_db
from app.models.enums import AIRecommendationStatus, AIRecommendationType
from app.models.user import User
from app.repositories.ai_recommendation import AIRecommendationRepository
from app.schemas.ai_recommendation import (
    AIRecommendationCreate,
    AIRecommendationRead,
    AIRecommendationReview,
    AIRecommendationUpdate,
)
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams

router = APIRouter(prefix="/ai-recommendations", tags=["AI Recommendations"])

_SORTABLE_FIELDS = {"status", "recommendation_type", "created_at", "reviewed_at"}


@router.get("", response_model=PaginatedResponse[AIRecommendationRead])
def list_ai_recommendations(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    institution_id: UUID | None = Depends(resolve_institution_scope),
    status_: AIRecommendationStatus | None = Query(None, alias="status"),
    recommendation_type: AIRecommendationType | None = Query(None),
    _current_user: User = Depends(get_current_user),
) -> PaginatedResponse[AIRecommendationRead]:
    repo = AIRecommendationRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        filters={"institution_id": institution_id, "status": status_, "recommendation_type": recommendation_type},
    )
    return PaginatedResponse.build(
        [AIRecommendationRead.model_validate(r) for r in items], total_items=total, params=pagination
    )


@router.get("/{recommendation_id}", response_model=AIRecommendationRead)
def get_ai_recommendation(
    recommendation_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> AIRecommendationRead:
    repo = AIRecommendationRepository(db)
    recommendation = repo.get_or_404(recommendation_id)
    verify_object_institution_access(db, current_user, recommendation.institution_id)
    return AIRecommendationRead.model_validate(recommendation)


@router.post(
    "",
    response_model=AIRecommendationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.AI_RECOMMENDATIONS_REVIEW))],
)
def create_ai_recommendation(
    payload: AIRecommendationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> AIRecommendationRead:
    """CRUD only — no AI inference happens here. `generated_by_agent` is a
    plain string identifying the source (a future agent name, or "manual"
    for hand-entered recommendations); this endpoint just persists the
    record, exactly like any other resource in this phase."""
    verify_object_institution_access(db, current_user, payload.institution_id)
    repo = AIRecommendationRepository(db)
    data = payload.model_dump()
    data["status"] = AIRecommendationStatus.PENDING
    recommendation = repo.create(data)
    db.commit()
    db.refresh(recommendation)
    return AIRecommendationRead.model_validate(recommendation)


@router.patch(
    "/{recommendation_id}",
    response_model=AIRecommendationRead,
    dependencies=[Depends(require_permission(Permission.AI_RECOMMENDATIONS_REVIEW))],
)
def update_ai_recommendation(
    recommendation_id: UUID,
    payload: AIRecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIRecommendationRead:
    repo = AIRecommendationRepository(db)
    recommendation = repo.get_or_404(recommendation_id)
    verify_object_institution_access(db, current_user, recommendation.institution_id)
    recommendation = repo.update(recommendation, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(recommendation)
    return AIRecommendationRead.model_validate(recommendation)


@router.post(
    "/{recommendation_id}/review",
    response_model=AIRecommendationRead,
    dependencies=[Depends(require_permission(Permission.AI_RECOMMENDATIONS_REVIEW))],
)
def review_ai_recommendation(
    recommendation_id: UUID,
    payload: AIRecommendationReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIRecommendationRead:
    """The one piece of real logic for this resource: `reviewed_by_id` and
    `reviewed_at` are always server-derived from the authenticated caller
    and the current time — never client-supplied, so the audit trail of
    who approved/dismissed a recommendation can't be forged."""
    repo = AIRecommendationRepository(db)
    recommendation = repo.get_or_404(recommendation_id)
    verify_object_institution_access(db, current_user, recommendation.institution_id)
    recommendation = repo.update(
        recommendation,
        {
            "status": payload.status,
            "reviewed_by_id": current_user.id,
            "reviewed_at": datetime.now(timezone.utc),
        },
    )
    db.commit()
    db.refresh(recommendation)
    return AIRecommendationRead.model_validate(recommendation)


@router.delete(
    "/{recommendation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.AI_RECOMMENDATIONS_REVIEW))],
)
def delete_ai_recommendation(
    recommendation_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    repo = AIRecommendationRepository(db)
    recommendation = repo.get_or_404(recommendation_id)
    verify_object_institution_access(db, current_user, recommendation.institution_id)
    repo.delete(recommendation)
    db.commit()
