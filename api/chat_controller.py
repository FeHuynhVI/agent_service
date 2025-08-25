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
from config.llm_config import LLMConfig

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_group_chat(api_key: str | None = None) -> SelectorGroupChat:
    agents = [
        MathExpertAgent(
            llm_config=LLMConfig.get_expert_config("Math_Expert", api_key=api_key)
        ).get_agent(),
        PhysicsExpertAgent(
            llm_config=LLMConfig.get_expert_config("Physics_Expert", api_key=api_key)
        ).get_agent(),
        ChemistryExpertAgent(
            llm_config=LLMConfig.get_expert_config("Chemistry_Expert", api_key=api_key)
        ).get_agent(),
        BiologyExpertAgent(
            llm_config=LLMConfig.get_expert_config("Biology_Expert", api_key=api_key)
        ).get_agent(),
        CSExpertAgent(
            llm_config=LLMConfig.get_expert_config("CS_Expert", api_key=api_key)
        ).get_agent(),
        LiteratureExpertAgent(
            llm_config=LLMConfig.get_expert_config("Literature_Expert", api_key=api_key)
        ).get_agent(),
        EnglishExpertAgent(
            llm_config=LLMConfig.get_expert_config("English_Expert", api_key=api_key)
        ).get_agent(),
        InfoAgent(
            llm_config=LLMConfig.get_agent_config("Info_Agent", api_key=api_key)
        ).get_agent(),
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

