from app.models.meal_image import MealImage
from app.repositories.base import BaseRepository


class MealImageRepository(BaseRepository[MealImage]):
    model = MealImage
