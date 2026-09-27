from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.db.session import get_db
from app.models.user import User
from app.repositories.meal_image import MealImageRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.meal_image import MealImageCreate, MealImageRead

router = APIRouter(prefix="/meal-images", tags=["Meal Images"])

_SORTABLE_FIELDS = {"captured_at", "created_at"}


@router.get("", response_model=PaginatedResponse[MealImageRead])
def list_meal_images(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    meal_id: UUID | None = Query(None, description="Filter by meal"),
    _current_user: User = Depends(get_current_user),
) -> PaginatedResponse[MealImageRead]:
    repo = MealImageRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        default_sort_field="captured_at",
        filters={"meal_id": meal_id},
    )
    return PaginatedResponse.build(
        [MealImageRead.model_validate(m) for m in items], total_items=total, params=pagination
    )


@router.get("/{image_id}", response_model=MealImageRead)
def get_meal_image(
    image_id: UUID, db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)
) -> MealImageRead:
    repo = MealImageRepository(db)
    return MealImageRead.model_validate(repo.get_or_404(image_id))


@router.post(
    "",
    response_model=MealImageRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.MEALS_CREATE))],
)
def create_meal_image(
    payload: MealImageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> MealImageRead:
    repo = MealImageRepository(db)
    data = payload.model_dump()
    data["uploaded_by_id"] = current_user.id
    image = repo.create(data)
    db.commit()
    db.refresh(image)
    return MealImageRead.model_validate(image)


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.MEALS_CREATE))],
)
def delete_meal_image(image_id: UUID, db: Session = Depends(get_db)) -> None:
    """MealImage has no soft-delete column (see the model's docstring) —
    BaseRepository.delete() correctly falls back to a hard delete here."""
    repo = MealImageRepository(db)
    image = repo.get_or_404(image_id)
    repo.delete(image)
    db.commit()
