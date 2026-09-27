from app.models.chat_conversation import ChatConversation
from app.models.chat_message import ChatMessage
from app.repositories.base import BaseRepository


class ChatConversationRepository(BaseRepository[ChatConversation]):
    model = ChatConversation


class ChatMessageRepository(BaseRepository[ChatMessage]):
    model = ChatMessage
