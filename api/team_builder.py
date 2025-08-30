"""Create groups of conversational agents and run demo chats."""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Any, cast

from .agent_base import (
    LLMConfig,
    AssistantAgent,
    ContextVariables,
    ConversableAgent,
)
from .prompts import (
    DEFAULT_CONTEXT,
    EXPERT_DEFINITIONS,
    INFO_AGENT_PROMPT,
    TUTOR_AGENT_PROMPT,
    build_subject_system_message,
)
from dotenv import load_dotenv
load_dotenv()


def _make_expert_agent(
    name: str,
    subject: str,
    expertise: List[str],
    description: str,
    *,
    level: str = "expert",
    keywords: Optional[List[str]] = None,
    examples: Optional[List[str]] = None,
    is_termination_msg=None,
    cv: Optional[Dict[str, str]] = None, 
    **_: object,  # bỏ qua field dư thừa để EXPERT_DEFINITIONS tự do mở rộng
) -> AssistantAgent:
    """Build a subject expert agent with common defaults.

    Extra keyword arguments are ignored so ``EXPERT_DEFINITIONS`` can contain
    additional configuration without needing to update this helper. This makes
    the agent creation logic more flexible and extensible.
    """

    agent = AssistantAgent(
        name=name,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        system_message=build_subject_system_message(
            cv=cv,
            name=name,
            level=level,
            subject=subject,
            keywords=keywords,
            examples=examples,
            expertise=expertise,
        ),
    )
    agent.description = description
    return agent



def _safe_get(d: Dict[str, Any], key: str, default):
    v = d.get(key, default)
    return v if v is not None else default


def create_team(
    model: Optional[str] = None,
    temperature: float = 0.2,
    context_data: Optional[Dict[str, str]] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Any:
    """Return (agents_list, user_agent, group_manager_args, context_variables)."""

    model = model or os.getenv("LLM_BASE_MODEL", "gpt-oss-120b")
    api_key = api_key or os.getenv("FCI_API_KEY", "")
    base_url = base_url or os.getenv(
        "LLM_BASE_URL", "https://mkp-api.fptcloud.com"
    )

    llm_config = LLMConfig(
        config_list=[{"model": model, "api_key": api_key, "base_url": base_url}],
        temperature=temperature,
    )

    context_values = {
        **DEFAULT_CONTEXT, **(context_data or {})
    }
    context = ContextVariables(data=context_values)

    # Unified termination check used by all recipients
    def is_termination_msg(msg: dict) -> bool:
        content = msg.get("content", "")
        if not isinstance(content, str):
            return False

        text = content.strip()
        low = text.lower()

        termination_phrases = [
            "tutor_session_end",
            "terminate",
            "kết thúc",
            "kết thúc phiên",
            "hoàn thành",
            "xong rồi",
            "đã xong",
            "done",
            "finished",
            "completed",
            "i'm done",
            "i have finished",
        ]

        return any(phrase in low or text.endswith(phrase) for phrase in termination_phrases)

    with llm_config:
        # Build personalized system messages up-front (no runtime monkey-patching)
        info_agent = AssistantAgent(
            name="Info_Agent",
            human_input_mode="NEVER",
            system_message=INFO_AGENT_PROMPT,
            is_termination_msg=is_termination_msg,
        )
        info_agent.description = (
            "Curates curricula and learning materials; generates practice questions; "
            "routes resources."
        )
        
        tutor_agent = AssistantAgent(
            name="Tutor_Agent",
            human_input_mode="NEVER",
            system_message=TUTOR_AGENT_PROMPT,
            is_termination_msg=is_termination_msg,
        )
        
        tutor_agent.description = (
            "Provides personalized explanations, adaptive guidance, and self-learning strategies "
            "to support deep understanding and critical thinking."
        )

        subject_agents = []
        for cfg in EXPERT_DEFINITIONS:
             agent = _make_expert_agent(
                name=cast(str, cfg["name"]),
                subject=cast(str, cfg["subject"]),
                level=cast(str, _safe_get(cfg, "level", "expert")),
                description=cast(str, _safe_get(cfg, "description", "")),
                expertise=cast(List[str], _safe_get(cfg, "expertise", [])),
                keywords=cast(List[str], _safe_get(cfg, "keywords", [])),
                examples=cast(List[str], _safe_get(cfg, "examples", [])),
                is_termination_msg=is_termination_msg,
                cv=context_values,)
             subject_agents.append(agent)

        all_agents = [info_agent, tutor_agent, *subject_agents]

        # Construct the user agent with termination behavior via constructor
        user_agent = ConversableAgent(
            name="student",
            human_input_mode="NEVER",
            system_message="You are a student asking questions.",
            is_termination_msg=is_termination_msg,
        )

    group_manager_args = {
        "llm_config": llm_config
    }

    return all_agents, user_agent, group_manager_args, context


__all__ = ["create_team"]

