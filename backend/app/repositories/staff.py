from app.models.staff import Staff
from app.repositories.base import BaseRepository


class StaffRepository(BaseRepository[Staff]):
    model = Staff
