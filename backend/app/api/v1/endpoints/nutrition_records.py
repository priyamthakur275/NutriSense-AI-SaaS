from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.core.exceptions import DuplicateResourceError
from app.db.session import get_db
from app.models.user import User
from app.repositories.nutrition_record import NutritionRecordRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.nutrition_record import (
    NutritionRecordCreate,
    NutritionRecordRead,
    NutritionRecordUpdate,
)

router = APIRouter(prefix="/nutrition-records", tags=["Nutrition Records"])

_SORTABLE_FIELDS = {"calories_kcal", "compliance_score", "computed_at", "created_at"}


@router.get("", response_model=PaginatedResponse[NutritionRecordRead])
def list_nutrition_records(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    meal_id: UUID | None = Query(None, description="Filter by meal"),
    is_compliant: bool | None = Query(None),
    _current_user: User = Depends(get_current_user),
) -> PaginatedResponse[NutritionRecordRead]:
    repo = NutritionRecordRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        filters={"meal_id": meal_id, "is_compliant": is_compliant},
    )
    return PaginatedResponse.build(
        [NutritionRecordRead.model_validate(n) for n in items], total_items=total, params=pagination
    )


@router.get("/{record_id}", response_model=NutritionRecordRead)
def get_nutrition_record(
    record_id: UUID, db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)
) -> NutritionRecordRead:
    repo = NutritionRecordRepository(db)
    return NutritionRecordRead.model_validate(repo.get_or_404(record_id))


@router.post(
    "",
    response_model=NutritionRecordRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.NUTRITION_REVIEW))],
)
def create_nutrition_record(payload: NutritionRecordCreate, db: Session = Depends(get_db)) -> NutritionRecordRead:
    """One NutritionRecord per Meal (enforced by a unique constraint on
    `meal_id`) — attempting a second one for the same meal is a conflict,
    not a new row; use PATCH to correct an existing record instead."""
    repo = NutritionRecordRepository(db)
    try:
        record = repo.create(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateResourceError("This meal already has a nutrition record") from exc
    db.refresh(record)
    return NutritionRecordRead.model_validate(record)


@router.patch(
    "/{record_id}",
    response_model=NutritionRecordRead,
    dependencies=[Depends(require_permission(Permission.NUTRITION_REVIEW))],
)
def update_nutrition_record(
    record_id: UUID, payload: NutritionRecordUpdate, db: Session = Depends(get_db)
) -> NutritionRecordRead:
    repo = NutritionRecordRepository(db)
    record = repo.get_or_404(record_id)
    record = repo.update(record, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(record)
    return NutritionRecordRead.model_validate(record)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.NUTRITION_REVIEW))],
)
def delete_nutrition_record(record_id: UUID, db: Session = Depends(get_db)) -> None:
    """NutritionRecord has no soft-delete column (like MealImage) — this is
    a hard delete, falling back automatically via BaseRepository.delete()."""
    repo = NutritionRecordRepository(db)
    record = repo.get_or_404(record_id)
    repo.delete(record)
    db.commit()
