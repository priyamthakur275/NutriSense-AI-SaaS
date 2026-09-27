from app.models.institution_settings import InstitutionSettings
from app.repositories.base import BaseRepository


class InstitutionSettingsRepository(BaseRepository[InstitutionSettings]):
    model = InstitutionSettings
