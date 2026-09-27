from app.models.nutrition_record import NutritionRecord
from app.repositories.base import BaseRepository


class NutritionRecordRepository(BaseRepository[NutritionRecord]):
    model = NutritionRecord
