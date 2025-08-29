from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    model: str | None = None
    max_rounds: int | None = 8
    temperature: float | None = None
    # Optional per-user/session context for personalization
    context: dict[str, str] | None = None


class ChatResponse(BaseModel):
    result: str


class AgentInfo(BaseModel):
    name: str
    description: str


__all__ = ["ChatRequest", "ChatResponse", "AgentInfo"]
