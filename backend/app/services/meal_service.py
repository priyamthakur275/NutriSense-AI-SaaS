"""The one piece of genuine business logic in meal creation: `created_by`
is always the authenticated caller, never a client-supplied value (a staff
member can't log a meal "as" someone else), and new meals always start in
MealStatus.PENDING regardless of what's in the request body. Everything
else about Meal CRUD is plain passthrough, handled directly in the endpoint
via MealRepository — no service methods needed for that.
"""

from sqlalchemy.orm import Session

from app.models.enums import MealStatus
from app.models.meal import Meal
from app.models.user import User
from app.repositories.meal import MealRepository
from app.schemas.meal import MealCreate


def create_meal(db: Session, payload: MealCreate, *, created_by: User) -> Meal:
    repo = MealRepository(db)
    data = payload.model_dump()
    data["created_by_id"] = created_by.id
    data["status"] = MealStatus.PENDING
    meal = repo.create(data)
    db.commit()
    db.refresh(meal)
    return meal
