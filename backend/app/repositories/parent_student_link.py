from app.models.parent_student_link import ParentStudentLink
from app.repositories.base import BaseRepository


class ParentStudentLinkRepository(BaseRepository[ParentStudentLink]):
    model = ParentStudentLink
