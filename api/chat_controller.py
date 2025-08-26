"""Endpoints enabling chat between a user and the team of agents."""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from chat.selector_group_chat import SelectorGroupChat
from config.agents import (
    CSExpertAgent,
    MathExpertAgent,
    EnglishExpertAgent,
    BiologyExpertAgent,
    PhysicsExpertAgent,
    ChemistryExpertAgent,
    LiteratureExpertAgent,
    InfoAgent,
)

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_group_chat(api_key: str | None = None) -> SelectorGroupChat:
    agents = [
        MathExpertAgent(api_key=api_key).get_agent(),
        PhysicsExpertAgent(api_key=api_key).get_agent(),
        ChemistryExpertAgent(api_key=api_key).get_agent(),
        BiologyExpertAgent(api_key=api_key).get_agent(),
        CSExpertAgent(api_key=api_key).get_agent(),
        LiteratureExpertAgent(api_key=api_key).get_agent(),
        EnglishExpertAgent(api_key=api_key).get_agent(),
        InfoAgent(api_key=api_key).get_agent(),
    ]
    return SelectorGroupChat(agents=agents, api_key=api_key)


class ChatRequest(BaseModel):
    message: str


@router.post("/")
async def chat_with_team(
    request: ChatRequest,
    openai_api_key: str | None = Header(default=None, alias="OpenAI-Api-Key"),
) -> dict:
    """Handle a user message and return the conversation history."""
    try:
        group_chat = _build_group_chat(api_key=openai_api_key)
        group_chat.start_chat(request.message)
    except Exception as exc:  # pragma: no cover - runtime errors
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"messages": group_chat.get_chat_history()}

