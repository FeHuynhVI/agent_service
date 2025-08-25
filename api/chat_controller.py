"""Endpoints enabling chat between a user and the team of agents."""

from fastapi import APIRouter, HTTPException
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


def _build_group_chat() -> SelectorGroupChat:
    agents = [
        MathExpertAgent().get_agent(),
        PhysicsExpertAgent().get_agent(),
        ChemistryExpertAgent().get_agent(),
        BiologyExpertAgent().get_agent(),
        CSExpertAgent().get_agent(),
        LiteratureExpertAgent().get_agent(),
        EnglishExpertAgent().get_agent(),
        InfoAgent().get_agent(),
    ]
    return SelectorGroupChat(agents=agents)


group_chat = _build_group_chat()


class ChatRequest(BaseModel):
    message: str


@router.post("/")
async def chat_with_team(request: ChatRequest) -> dict:
    """Handle a user message and return the conversation history."""
    try:
        group_chat.start_chat(request.message)
    except Exception as exc:  # pragma: no cover - runtime errors
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"messages": group_chat.get_chat_history()}

