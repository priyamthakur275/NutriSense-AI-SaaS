from app.models.ai_recommendation import AIRecommendation
from app.repositories.base import BaseRepository


class AIRecommendationRepository(BaseRepository[AIRecommendation]):
    model = AIRecommendation
