"""FastAPI router for interacting with agent teams."""

from functools import lru_cache
from typing import List, Optional
import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from utils.error_handler import handle_errors

from .agent_base import AutoPattern
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


def _run_group_chat(pattern: AutoPattern, message: str, max_rounds: int):
    """Run a group chat and allow early termination when agents output TERMINATE."""

    from autogen.agentchat.chat import cleanup_temp_user_messages

    (
        _,
        _,
        _,
        context_variables,
        _,
        _,
        _,
        _,
        manager,
        processed_messages,
        last_agent,
        _,
        _,
    ) = pattern.prepare_group_chat(max_rounds=max_rounds, messages=message)

    def is_termination_msg(msg: dict) -> bool:
        content = msg.get("content")
        return isinstance(content, str) and content.rstrip().endswith("TERMINATE")

    setattr(manager, "_is_termination_msg", is_termination_msg)

    if len(processed_messages) > 1:
        last_agent, last_message = manager.resume(messages=processed_messages)
        clear_history = False
    else:
        last_message = processed_messages[0]
        clear_history = True

    if last_agent is None:
        raise ValueError("No agent selected to start the conversation")

    chat_result = last_agent.initiate_chat(
        manager,
        message=last_message,
        clear_history=clear_history,
        summary_method=pattern.summary_method,
    )

    cleanup_temp_user_messages(chat_result)

    return chat_result, context_variables, manager.last_speaker


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
        _run_group_chat,
        pattern,
        payload.message,
        payload.max_rounds,
    )

    if not isinstance(result, str):
        if getattr(result, "summary", None):
            result = result.summary  # type: ignore[assignment]
        elif getattr(result, "chat_history", None):
            try:
                result = result.chat_history[-1].get("content", "")  # type: ignore[index]
            except Exception:
                result = str(result)
        else:
            result = str(result)
    result = result.replace("TERMINATE", "").strip()

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
