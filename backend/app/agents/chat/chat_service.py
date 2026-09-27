"""Conversational assistant service. Our LLMProvider abstraction
(app.agents.providers.base) intentionally exposes a single-prompt
`generate_text`, not a native multi-turn messages array — keeping every
provider's REST payload shape identical and simple. Context-awareness is
achieved instead by formatting recent conversation history directly into
the prompt text (see `_build_context_prompt`), which works identically
regardless of which provider is behind the call.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.exceptions import AIProviderError
from app.agents.prompts.chat_prompts import CHAT_SYSTEM_INSTRUCTION
from app.agents.providers.base import LLMProvider
from app.agents.providers.factory import call_with_failover
from app.core.exceptions import NotFoundError
from app.models.chat_conversation import ChatConversation
from app.models.chat_message import ChatMessage
from app.models.enums import ChatRole
from app.models.user import User
from app.repositories.chat import ChatConversationRepository, ChatMessageRepository
from app.schemas.ai_chat import ChatMessageRead, ChatRequest, ChatResponse

# Bounds how much history is replayed into each prompt — enough for genuine
# follow-up context, capped so a very long-running conversation doesn't
# grow the prompt (and provider cost/latency) unboundedly.
MAX_HISTORY_MESSAGES = 20
TITLE_MAX_LENGTH = 60


def _get_or_create_conversation(
    db: Session, user: User, conversation_id: UUID | None
) -> ChatConversation:
    if conversation_id is None:
        repo = ChatConversationRepository(db)
        conversation = repo.create({"user_id": user.id, "title": "New conversation"})
        db.commit()
        db.refresh(conversation)
        return conversation

    conversation = (
        db.query(ChatConversation)
        .filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == user.id,
            ChatConversation.deleted_at.is_(None),
        )
        .first()
    )
    if conversation is None:
        raise NotFoundError(f"Conversation '{conversation_id}' not found")
    return conversation


def _build_context_prompt(history: list[ChatMessage], new_message: str) -> str:
    if not history:
        return new_message

    recent = history[-MAX_HISTORY_MESSAGES:]
    lines = ["Conversation so far:"]
    for msg in recent:
        speaker = "User" if msg.role == ChatRole.USER else "Assistant"
        lines.append(f"{speaker}: {msg.content}")
    lines.append(f"User: {new_message}")
    lines.append("\nRespond to the latest user message as the Assistant, taking the full conversation above into account.")
    return "\n".join(lines)


async def send_message(db: Session, user: User, request: ChatRequest) -> ChatResponse:
    conversation = _get_or_create_conversation(db, user, request.conversation_id)
    message_repo = ChatMessageRepository(db)

    history = list(conversation.messages)
    prompt = _build_context_prompt(history, request.message)

    user_message = message_repo.create(
        {"conversation_id": conversation.id, "role": ChatRole.USER, "content": request.message}
    )

    if conversation.title == "New conversation":
        conversation.title = request.message[:TITLE_MAX_LENGTH]

    db.commit()
    db.refresh(user_message)

    async def _call(provider: LLMProvider):
        return await provider.generate_text(
            prompt, system_instruction=CHAT_SYSTEM_INSTRUCTION, temperature=0.6, max_output_tokens=800
        )

    try:
        llm_response = await call_with_failover(_call)
        reply_content = llm_response.content
        provider_used = llm_response.provider
    except AIProviderError:
        # A chat assistant should degrade gracefully, not 502 the whole
        # request — the user's message is still saved either way.
        reply_content = (
            "I'm having trouble reaching the AI assistant right now. "
            "Please try again in a moment."
        )
        provider_used = "unavailable"

    assistant_message = message_repo.create(
        {"conversation_id": conversation.id, "role": ChatRole.ASSISTANT, "content": reply_content}
    )
    db.commit()
    db.refresh(assistant_message)

    return ChatResponse(
        conversation_id=conversation.id,
        reply=ChatMessageRead.model_validate(assistant_message),
        provider_used=provider_used,
    )
