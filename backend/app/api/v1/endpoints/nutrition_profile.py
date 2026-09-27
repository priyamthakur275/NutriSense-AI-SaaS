from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.nutrition_profile import NutritionProfileRepository
from app.schemas.nutrition_profile import NutritionProfileRead, NutritionProfileUpdate
from app.services import nutrition_profile_service

router = APIRouter(prefix="/nutrition-profile", tags=["Nutrition Profile"])


@router.get("/me", response_model=NutritionProfileRead)
def get_my_nutrition_profile(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> NutritionProfileRead:
    profile = nutrition_profile_service.get_or_create_profile(db, current_user)
    return NutritionProfileRead.model_validate(profile)


@router.patch("/me", response_model=NutritionProfileRead)
def update_my_nutrition_profile(
    payload: NutritionProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NutritionProfileRead:
    repo = NutritionProfileRepository(db)
    profile = nutrition_profile_service.get_or_create_profile(db, current_user)
    profile = repo.update(profile, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(profile)
    return NutritionProfileRead.model_validate(profile)
