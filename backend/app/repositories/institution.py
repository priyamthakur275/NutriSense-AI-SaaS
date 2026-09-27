from app.models.institution import Institution
from app.repositories.base import BaseRepository


class InstitutionRepository(BaseRepository[Institution]):
    model = Institution
