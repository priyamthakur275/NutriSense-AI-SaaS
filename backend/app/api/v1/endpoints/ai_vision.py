from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.agents.nutrition.nutrition_engine import estimate_nutrition, persist_nutrition_record
from app.agents.vision.food_detection_service import analyze_food_image
from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.core.file_validation import validate_upload_file
from app.core.rate_limit import RateLimiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai_pipeline import MealAnalysisResponse

router = APIRouter(prefix="/ai/vision", tags=["AI Vision"])


@router.post(
    "/analyze",
    response_model=MealAnalysisResponse,
    dependencies=[
        Depends(require_permission(Permission.MEALS_CREATE)),
        # Vision calls are the most expensive AI operation in this app (image
        # preprocessing + a vision-model provider call) — rate-limited per
        # caller to bound both abuse and provider spend.
        Depends(RateLimiter(times=10, seconds=60, scope="ai_vision_analyze")),
    ],
)
async def analyze_meal_image(
    file: UploadFile = File(...),
    meal_id: UUID | None = Query(
        default=None, description="If provided, persists a NutritionRecord for this meal"
    ),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> MealAnalysisResponse:
    """Runs the full pipeline: upload validation -> preprocessing -> vision
    detection -> (optionally) nutrition estimation and persistence.

    Validation reuses app.core.file_validation (the same magic-byte/size
    checks every upload path in this app shares) before any AI provider is
    ever called — a malformed or oversized file is rejected for free,
    without spending a provider request on it.
    """
    validated_bytes = await validate_upload_file(file)

    vision_result = await analyze_food_image(validated_bytes)

    if not meal_id or not vision_result.detected_items:
        return MealAnalysisResponse(vision=vision_result)

    nutrition_result = await estimate_nutrition(vision_result.detected_items)
    record = persist_nutrition_record(db, meal_id, nutrition_result)

    return MealAnalysisResponse(
        vision=vision_result, nutrition=nutrition_result, nutrition_record_id=record.id
    )
