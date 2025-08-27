"""FastAPI router for interacting with agent teams."""

from functools import lru_cache
from typing import List, Optional
import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from utils.error_handler import handle_errors

from .agent_base import AutoPattern, initiate_group_chat
from .team_builder import create_team


class ChatRequest(BaseModel):
    """Input payload for the chat endpoint."""

    message: str
    max_rounds: int = 8
    model: Optional[str] = None
    temperature: Optional[float] = None


class ChatResponse(BaseModel):
    """Response returned after running the chat."""

    result: str


class AgentInfo(BaseModel):
    """Information about an available expert agent."""

    name: str
    description: str


router = APIRouter(prefix="/chat", tags=["chat"])


@lru_cache()
def _get_cached_team() -> tuple:
    """Return a cached default team to avoid repeated initialisation."""

    return create_team()


def _build_pattern(agents, user_agent, group_manager_args, context) -> AutoPattern:
    initial_agent = next(a for a in agents if a.name == "Info_Agent")
    return AutoPattern(
        initial_agent=initial_agent,
        agents=agents,  # type: ignore[arg-type]
        user_agent=user_agent,
        group_manager_args=group_manager_args,
        context_variables=context,
    )


@router.post("/", response_model=ChatResponse, summary="Run a chat with the expert team")
@handle_errors
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """Execute a group chat and return the final result."""

    if payload.model or payload.temperature:
        agents, user_agent, group_manager_args, context = create_team(
            model=payload.model or "gpt-oss-120b",
            temperature=payload.temperature or 0.2,
        )
    else:
        agents, user_agent, group_manager_args, context = _get_cached_team()

    pattern = _build_pattern(agents, user_agent, group_manager_args, context)

    result, _ctx, _last_agent = await asyncio.to_thread(
        initiate_group_chat,
        pattern=pattern,
        messages=payload.message,
        max_rounds=payload.max_rounds,
    )

    return ChatResponse(result=result)


@router.get("/agents", response_model=List[AgentInfo], summary="List available agents")
@handle_errors
async def list_agents() -> List[AgentInfo]:
    """Return the names and descriptions of all expert agents."""

    agents, *_ = _get_cached_team()
    return [
        AgentInfo(name=a.name, description=getattr(a, "description", ""))
        for a in agents
    ]


__all__ = ["router", "create_team"]
