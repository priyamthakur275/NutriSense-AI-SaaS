from app.models.user_invite import UserInvite
from app.repositories.base import BaseRepository


class UserInviteRepository(BaseRepository[UserInvite]):
    model = UserInvite
