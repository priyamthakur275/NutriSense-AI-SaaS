from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.recommendations.recommendation_engine import generate_recommendations
from app.api.deps import get_current_user
from app.core.exceptions import ValidationAppError
from app.core.rate_limit import RateLimiter
from app.db.session import get_db
from app.models.staff import Staff
from app.models.student import Student
from app.models.user import User
from app.schemas.ai_recommendation_engine import RecommendationGenerationResponse

router = APIRouter(prefix="/ai/recommendations", tags=["AI Recommendations"])


def _resolve_institution_id(db: Session, user: User):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if student:
        return student.institution_id
    staff = db.query(Staff).filter(Staff.user_id == user.id).first()
    if staff:
        return staff.institution_id
    raise ValidationAppError(
        "This account has no Student or Staff profile linking it to an institution — "
        "recommendations require institutional context"
    )


@router.post(
    "/generate",
    response_model=RecommendationGenerationResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60, scope="ai_recommendations_generate"))],
)
async def generate_my_recommendations(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> RecommendationGenerationResponse:
    """Generates and persists personalized recommendations for the
    authenticated user, based on their NutritionProfile and their last
    7 days of attended, nutrition-analyzed meals."""
    institution_id = _resolve_institution_id(db, current_user)
    return await generate_recommendations(db, current_user, institution_id=institution_id)
