"""AI chat assistant: multi-turn context and graceful degradation tests."""

import pytest

from app.agents.chat.chat_service import send_message
from app.agents.exceptions import AIProviderUnavailableError
from app.agents.providers import factory
from app.agents.providers.base import LLMResponse
from app.core.config import settings
from app.models.chat_conversation import ChatConversation
from app.schemas.ai_chat import ChatRequest


@pytest.mark.asyncio
async def test_multi_turn_conversation_carries_context(db_session, make_user):
    user = make_user()
    captured_prompts = []
    call_count = {"n": 0}

    class StubChatProvider:
        name = "stub-chat"

        async def generate_text(self, prompt, **kwargs):
            captured_prompts.append(prompt)
            call_count["n"] += 1
            if call_count["n"] == 1:
                return LLMResponse(content="A banana has about 105 calories.", provider="stub-chat", model="stub")
            return LLMResponse(content="Bananas have about 1.3g of protein.", provider="stub-chat", model="stub")

        async def generate_from_image(self, *a, **kw):
            raise NotImplementedError

    factory._BUILDERS["stub-chat"] = lambda: StubChatProvider()
    settings.AI_PROVIDER = "stub-chat"
    settings.AI_FALLBACK_PROVIDERS = []

    r1 = await send_message(db_session, user, ChatRequest(message="How many calories are in a banana?"))
    r2 = await send_message(
        db_session, user, ChatRequest(message="What about protein?", conversation_id=r1.conversation_id)
    )

    assert r1.reply.content != r2.reply.content
    # The key proof: turn 2's user message alone says nothing about bananas,
    # yet the prompt actually sent to the LLM carried turn 1's full exchange.
    assert "banana" in captured_prompts[1].lower()
    assert "105 calories" in captured_prompts[1]

    conversation = db_session.query(ChatConversation).filter(ChatConversation.id == r1.conversation_id).first()
    assert len(conversation.messages) == 4
    assert conversation.title == "How many calories are in a banana?"


@pytest.mark.asyncio
async def test_chat_degrades_gracefully_on_total_provider_outage(db_session, make_user):
    user = make_user()

    class AlwaysDownProvider:
        name = "always-down"

        async def generate_text(self, prompt, **kwargs):
            raise AIProviderUnavailableError("always-down", detail="simulated outage")

        async def generate_from_image(self, *a, **kw):
            raise NotImplementedError

    factory._BUILDERS["always-down"] = lambda: AlwaysDownProvider()
    settings.AI_PROVIDER = "always-down"
    settings.AI_FALLBACK_PROVIDERS = []
    settings.AI_MAX_RETRIES = 0

    response = await send_message(db_session, user, ChatRequest(message="test during outage"))

    assert response.provider_used == "unavailable"
    assert "trouble" in response.reply.content.lower()

    # The user's message must still be persisted even though the AI failed.
    conversation = db_session.query(ChatConversation).filter(ChatConversation.id == response.conversation_id).first()
    assert len(conversation.messages) == 2
    assert conversation.messages[0].content == "test during outage"


@pytest.mark.asyncio
async def test_continuing_another_users_conversation_is_rejected(db_session, make_user):
    from app.core.exceptions import NotFoundError

    owner = make_user()
    intruder = make_user()

    class StubProvider:
        name = "stub-owner"

        async def generate_text(self, prompt, **kwargs):
            return LLMResponse(content="reply", provider="stub-owner", model="stub")

        async def generate_from_image(self, *a, **kw):
            raise NotImplementedError

    factory._BUILDERS["stub-owner"] = lambda: StubProvider()
    settings.AI_PROVIDER = "stub-owner"
    settings.AI_FALLBACK_PROVIDERS = []

    r1 = await send_message(db_session, owner, ChatRequest(message="owner's private message"))

    with pytest.raises(NotFoundError):
        await send_message(
            db_session, intruder, ChatRequest(message="trying to hijack", conversation_id=r1.conversation_id)
        )
