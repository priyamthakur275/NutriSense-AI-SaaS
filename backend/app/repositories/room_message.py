from app.models.room_message import RoomMessage
from app.repositories.base import BaseRepository


class RoomMessageRepository(BaseRepository[RoomMessage]):
    model = RoomMessage
