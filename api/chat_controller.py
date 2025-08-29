"""FastAPI router for interacting with agent teams.

This module only defines the API surface and delegates logic to services.
"""

from __future__ import annotations

from typing import List


from fastapi import APIRouter

from utils.error_handler import handle_errors
from .schemas import ChatRequest, ChatResponse, AgentInfo
from .chat_service import run_chat, list_agents_info


router = APIRouter(prefix="/chat", tags=["chat"])




@handle_errors
@router.post(
    "/", response_model=ChatResponse, summary="Run a chat with the expert team"
)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """Execute a group chat and return the final result."""
    result = await run_chat(
        model=payload.model,
        message=payload.message,
        context=payload.context,
        temperature=payload.temperature,
        max_rounds=payload.max_rounds or 10,
    )
    return ChatResponse(result=result)


@handle_errors
@router.get("/agents", response_model=List[AgentInfo], summary="List available agents")
async def list_agents() -> List[AgentInfo]:
    """Return the names and descriptions of all expert agents."""
    data = list_agents_info()
    return [AgentInfo(**item) for item in data]


__all__ = ["router"]
