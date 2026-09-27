from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.chat.chat_service import send_message
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.core.rate_limit import RateLimiter
from app.db.session import get_db
from app.models.chat_conversation import ChatConversation
from app.models.user import User
from app.repositories.chat import ChatConversationRepository
from app.schemas.ai_chat import (
    ChatConversationDetail,
    ChatConversationRead,
    ChatRequest,
    ChatResponse,
)
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/ai/chat", tags=["AI Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    dependencies=[Depends(RateLimiter(times=20, seconds=60, scope="ai_chat_send"))],
)
async def chat(
    payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ChatResponse:
    """Sends a message and gets a reply. Omit `conversation_id` to start a
    new conversation; include it to continue an existing one with full
    context from prior turns."""
    return await send_message(db, current_user, payload)


@router.get("/conversations", response_model=PaginatedResponse[ChatConversationRead])
def list_conversations(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ChatConversationRead]:
    repo = ChatConversationRepository(db)
    items, total = repo.list(
        pagination=pagination,
        default_sort_field="updated_at",
        filters={"user_id": current_user.id},
    )
    return PaginatedResponse.build(
        [ChatConversationRead.model_validate(c) for c in items], total_items=total, params=pagination
    )


@router.get("/conversations/{conversation_id}", response_model=ChatConversationDetail)
def get_conversation(
    conversation_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ChatConversationDetail:
    conversation = (
        db.query(ChatConversation)
        .filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id,
            ChatConversation.deleted_at.is_(None),
        )
        .first()
    )
    if conversation is None:
        raise NotFoundError(f"Conversation '{conversation_id}' not found")
    return ChatConversationDetail.model_validate(conversation)


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    repo = ChatConversationRepository(db)
    conversation = (
        db.query(ChatConversation)
        .filter(ChatConversation.id == conversation_id, ChatConversation.user_id == current_user.id)
        .first()
    )
    if conversation is None:
        raise NotFoundError(f"Conversation '{conversation_id}' not found")
    repo.delete(conversation)
    db.commit()
