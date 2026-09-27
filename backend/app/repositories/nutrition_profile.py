from app.models.nutrition_profile import NutritionProfile
from app.repositories.base import BaseRepository


class NutritionProfileRepository(BaseRepository[NutritionProfile]):
    model = NutritionProfile
