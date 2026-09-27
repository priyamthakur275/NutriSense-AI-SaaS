from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.api.tenant_scope import resolve_institution_scope, verify_object_institution_access
from app.db.session import get_db
from app.models.enums import MealStatus, MealType
from app.models.user import User
from app.repositories.meal import MealRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.meal import MealCreate, MealRead, MealUpdate
from app.services import meal_service

router = APIRouter(prefix="/meals", tags=["Meals"])

_SORTABLE_FIELDS = {"name", "meal_type", "status", "served_at", "created_at", "updated_at"}


@router.get("", response_model=PaginatedResponse[MealRead])
def list_meals(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: str | None = Query(None, description="Search by meal name"),
    institution_id: UUID | None = Depends(resolve_institution_scope),
    department_id: UUID | None = Query(None),
    meal_type: MealType | None = Query(None),
    status_: MealStatus | None = Query(None, alias="status"),
    _current_user: User = Depends(get_current_user),
) -> PaginatedResponse[MealRead]:
    repo = MealRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        default_sort_field="served_at",
        search=search,
        search_fields=["name"] if search else None,
        filters={
            "institution_id": institution_id,
            "department_id": department_id,
            "meal_type": meal_type,
            "status": status_,
        },
    )
    return PaginatedResponse.build(
        [MealRead.model_validate(m) for m in items], total_items=total, params=pagination
    )


@router.get("/{meal_id}", response_model=MealRead)
def get_meal(meal_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> MealRead:
    repo = MealRepository(db)
    meal = repo.get_or_404(meal_id)
    verify_object_institution_access(db, current_user, meal.institution_id)
    return MealRead.model_validate(meal)


@router.post(
    "",
    response_model=MealRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.MEALS_CREATE))],
)
def create_meal(
    payload: MealCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> MealRead:
    # `payload.institution_id` is client-supplied — without this check a
    # Staff member at Institution A could log a meal under Institution B
    # just by putting a different ID in the request body.
    verify_object_institution_access(db, current_user, payload.institution_id)
    meal = meal_service.create_meal(db, payload, created_by=current_user)
    return MealRead.model_validate(meal)


@router.patch(
    "/{meal_id}",
    response_model=MealRead,
    dependencies=[Depends(require_permission(Permission.MEALS_CREATE))],
)
def update_meal(
    meal_id: UUID, payload: MealUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> MealRead:
    repo = MealRepository(db)
    meal = repo.get_or_404(meal_id)
    verify_object_institution_access(db, current_user, meal.institution_id)
    meal = repo.update(meal, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(meal)
    return MealRead.model_validate(meal)


@router.delete(
    "/{meal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.MEALS_CREATE))],
)
def delete_meal(meal_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
    repo = MealRepository(db)
    meal = repo.get_or_404(meal_id)
    verify_object_institution_access(db, current_user, meal.institution_id)
    repo.delete(meal)
    db.commit()
