"""FastAPI router for interacting with agent teams."""

from __future__ import annotations

import asyncio
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional


from fastapi import APIRouter
from pydantic import BaseModel

from .agent_base import AutoPattern
from utils.error_handler import handle_errors
from .team_builder import create_team, AGENT_KEYWORDS


class ChatRequest(BaseModel):
    """Input payload for the chat endpoint."""

    message: str
    model: str | None = None
    max_rounds: int | None = 8
    temperature: float | None = None

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


def _safe_cleanup_messages(chat_result):
    """Safely clean up temporary user messages without importing non-existent function."""
    try:
        # Try the standard cleanup if it exists
        from autogen.agentchat.chat import cleanup_temp_user_messages

        cleanup_temp_user_messages(chat_result)
    except ImportError:
        # If the function doesn't exist, perform manual cleanup
        if hasattr(chat_result, "chat_history") and isinstance(
            chat_result.chat_history, list
        ):
            # Remove any temporary or system messages that shouldn't be in final history
            cleaned_history = []
            for msg in chat_result.chat_history:
                if isinstance(msg, dict):
                    # Skip messages that are temporary or system-generated
                    if not msg.get("role") == "system" and not msg.get("temp", False):
                        cleaned_history.append(msg)
            chat_result.chat_history = cleaned_history
    except Exception as e:  # pragma: no cover - defensive
        # Log the error but don't fail the whole operation
        print(f"Warning: Could not clean up messages: {e}")


def _determine_best_agent(message: str, agents: List) -> Optional[Any]:
    """
    Intelligently determine the most suitable agent based on message content.
    This helps avoid unnecessary agent switching and reduces redundant calls.
    """
    message_lower = message.lower()

    # Score each agent based on keyword matches using configured keywords
    agent_scores: Dict[str, int] = {}
    for agent in agents:
        if hasattr(agent, "name") and agent.name in AGENT_KEYWORDS:
            keywords = AGENT_KEYWORDS.get(agent.name, [])
            score = sum(1 for keyword in keywords if keyword in message_lower)
            agent_scores[agent.name] = score

    # Return agent with highest score, or None if no clear match
    if agent_scores:
        best_agent_name = max(agent_scores, key=lambda name: agent_scores.get(name, 0))
        if agent_scores[best_agent_name] > 0:
            return next(
                (a for a in agents if hasattr(a, "name") and a.name == best_agent_name),
                None,
            )

    return None


def _run_group_chat(pattern: AutoPattern, message: str, max_rounds: int):
    """Run a group chat with optimizations to reduce redundant agent calls."""

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
        content = msg.get("content", "")
        if isinstance(content, str):
            content_stripped = content.rstrip()
            return (
                content_stripped.endswith("TERMINATE")
                or content_stripped.endswith("KẾT THÚC")
                or "hoàn thành" in content_stripped.lower()
                or "completed" in content_stripped.lower()
            )
        return False

    # Enhanced termination detection
    setattr(manager, "_is_termination_msg", is_termination_msg)

    # Try to select the most appropriate agent based on message content
    agents = getattr(pattern, "agents", [])
    suggested_agent = _determine_best_agent(message, agents)

    if suggested_agent and len(processed_messages) <= 1:
        # If we have a clear subject match, start with that agent
        last_agent = suggested_agent

    if len(processed_messages) > 1:
        last_agent, last_message = manager.resume(messages=processed_messages)
        clear_history = False
    else:
        last_message = processed_messages[0] if processed_messages else message
        clear_history = True

    if last_agent is None:
        # Fallback to Info_Agent if no agent selected
        last_agent = next(
            (a for a in agents if hasattr(a, "name") and a.name == "Info_Agent"), None
        )
        if last_agent is None:
            raise ValueError("No agent available to start the conversation")

    # Set a more conservative max_rounds to prevent excessive back-and-forth
    max_group_rounds = int(os.getenv("MAX_GROUP_CHAT_ROUNDS", "6"))
    effective_max_rounds = min(max_rounds, max_group_rounds)
    chat_result = last_agent.initiate_chat(
        manager,
        message=last_message,
        clear_history=clear_history,
        summary_method=pattern.summary_method,
        max_turns=effective_max_rounds,  # Prevent infinite loops
    )

    # Use safe cleanup function
    _safe_cleanup_messages(chat_result)

    return chat_result, context_variables, manager.last_speaker


@handle_errors
@router.post(
    "/", response_model=ChatResponse, summary="Run a chat with the expert team"
)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """Execute a group chat and return the final result."""
    # Limit max_rounds to prevent excessive processing
    max_chat_rounds = int(os.getenv("MAX_CHAT_ROUNDS", "10"))
    effective_max_rounds = min(payload.max_rounds, max_chat_rounds)

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
        effective_max_rounds,
    )

    # Enhanced result extraction
    final_result = ""
    if isinstance(result, str):
        final_result = result
    elif hasattr(result, "summary") and result.summary:
        final_result = str(result.summary)
    elif hasattr(result, "chat_history") and result.chat_history:
        try:
            # Get the last meaningful message from chat history
            for msg in reversed(result.chat_history):
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    if (
                        content
                        and not content.strip().startswith("[")
                        and len(content.strip()) > 10
                    ):
                        final_result = content
                        break
            if not final_result and result.chat_history:
                final_result = str(result.chat_history[-1].get("content", ""))
        except (IndexError, AttributeError, TypeError):  # pragma: no cover - defensive
            final_result = str(result)
    else:
        final_result = str(result)

    # Clean up the result
    final_result = final_result.replace("TERMINATE", "").replace("KẾT THÚC", "").strip()

    # If result is still empty or too short, provide a default response
    if len(final_result.strip()) < 5:
        final_result = "Xin lỗi, tôi không thể xử lý yêu cầu này. Vui lòng thử lại với câu hỏi cụ thể hơn."

    return ChatResponse(result=final_result)


@router.get("/agents", response_model=List[AgentInfo], summary="List available agents")
@handle_errors
async def list_agents() -> List[AgentInfo]:
    """Return the names and descriptions of all expert agents."""
    try:
        agents, *_ = _get_cached_team()
        return [
            AgentInfo(
                name=getattr(a, "name", "Unknown"),
                description=getattr(a, "description", "No description available"),
            )
            for a in agents
            if hasattr(a, "name")
        ]
    except Exception as e:  # pragma: no cover - defensive
        print(f"Error listing agents: {e}")
        return []


__all__ = ["router", "create_team"]
