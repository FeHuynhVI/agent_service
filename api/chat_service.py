"""Chat orchestration service: builds patterns, runs chats, extracts results.

This keeps heavy logic out of the FastAPI controllers.
"""

from __future__ import annotations

import os
import time
import asyncio
from functools import lru_cache

from autogen import AssistantAgent

from api.prompts import CLASSIFICATION_AGENT_PROMPT
from .team_builder import create_team
from typing import Any, List, Optional, Dict
from .agent_base import AutoPattern, logger, initiate_group_chat


@lru_cache()
def _get_cached_team() -> tuple:
    """Return a cached default team to avoid repeated initialisation."""
    return create_team()


# No manual agent scoring or selection. Let AutoPattern manage speakers.


def _build_pattern(
    agents,
    user_agent,
    group_manager_args,
    context,
    *,
    message: Optional[str] = None,
) -> AutoPattern:
    # Use all agents; let AutoPattern route internally
    candidate_agents = agents

    logger.debug(
        "Building pattern with %d agents (auto routing)",
        len(candidate_agents),
    )
    
    triage_agent = AssistantAgent(
        name="Triage_Agent",
        system_message=CLASSIFICATION_AGENT_PROMPT,
    )

    return AutoPattern(
        initial_agent=triage_agent,
        context_variables=context,
        user_agent=user_agent,
        group_manager_args=group_manager_args,
        agents=[triage_agent, *candidate_agents],
    )


# No extra cleanup; rely on library's default handling.


def _extract_final_result(result: Any) -> str:
    final_result = ""
    if isinstance(result, str):
        final_result = result
    elif hasattr(result, "summary") and result.summary:
        final_result = str(result.summary)
    elif hasattr(result, "chat_history") and result.chat_history:
        try:
            for msg in reversed(result.chat_history):
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    if content and not content.strip().startswith("[") and len(content.strip()) > 10:
                        final_result = content
                        break
            if not final_result and result.chat_history:
                final_result = str(result.chat_history[-1].get("content", ""))
        except Exception:
            final_result = str(result)
    else:
        final_result = str(result)

    final_result = final_result.replace("TERMINATE", "").replace("KẾT THÚC", "").strip()
    if len(final_result.strip()) < 5:
        final_result = (
            "Xin lỗi, tôi không thể xử lý yêu cầu này. Vui lòng thử lại với câu hỏi cụ thể hơn."
        )
    return final_result


def _run_group_chat_sync(message: str, max_rounds: int, model: Optional[str], temperature: Optional[float]) -> str:
    # Build or reuse the team
    if model or temperature is not None:
        agents, user_agent, group_manager_args, context = create_team(
            model=model or os.getenv("LLM_BASE_MODEL", "gpt-oss-120b"),
            temperature=temperature if temperature is not None else 0.2,
        )
    else:
        agents, user_agent, group_manager_args, context = _get_cached_team()

    pattern = _build_pattern(
        agents,
        user_agent,
        group_manager_args,
        context,
        message=message,
    )

    chat_result, _ctx, _last_agent = initiate_group_chat(
        pattern=pattern,
        messages=message,
        max_rounds=max_rounds,
    )

    return _extract_final_result(chat_result)


async def run_chat(message: str, model: Optional[str], temperature: Optional[float], max_rounds: int) -> str:
    """Run a chat end-to-end and return the final result string.

    No explicit timeout is enforced here; rely on the underlying library.
    """
    max_chat_rounds = int(os.getenv("MAX_CHAT_ROUNDS", "10"))
    effective_max_rounds = max(max_rounds, max_chat_rounds)

    start = time.perf_counter()
    logger.info(
        "Chat start | rounds=%s model=%s temp=%s",
        effective_max_rounds,
        model or "(default)",
        temperature if temperature is not None else "(default)",
    )
    result = await asyncio.to_thread(
        _run_group_chat_sync, message, effective_max_rounds, model, temperature
    )
    logger.info("Chat done | elapsed=%.2fs", time.perf_counter() - start)
    return result


def list_agents_info() -> List[Dict[str, str]]:
    try:
        agents, *_ = _get_cached_team()
        return [
            {
                "name": getattr(a, "name", "Unknown"),
                "description": getattr(a, "description", "No description available"),
            }
            for a in agents
            if hasattr(a, "name")
        ]
    except Exception as e:  # pragma: no cover - defensive
        logger.warning("Error listing agents: %s", e)
        return []


__all__ = ["run_chat", "list_agents_info"]
