"""Shared agent imports and logging setup.

This module handles the optional availability of the `ag2` package.
If `ag2` is not installed, it falls back to `autogen`.
"""

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

try:
    from ag2.agentchat import initiate_group_chat
    from ag2.agentchat.group import ContextVariables
    from ag2.agentchat.group.patterns import AutoPattern
    from ag2 import ConversableAgent, AssistantAgent, LLMConfig, UpdateSystemMessage
    USING_AG2 = True
except ImportError:
    from autogen.agentchat import initiate_group_chat
    from autogen.agentchat.group import ContextVariables
    from autogen.agentchat.group.patterns import AutoPattern
    from autogen import ConversableAgent, AssistantAgent, LLMConfig, UpdateSystemMessage
    USING_AG2 = False

__all__ = [
    "logger",
    "USING_AG2",
    "LLMConfig",
    "AutoPattern",
    "AssistantAgent",
    "ConversableAgent",
    "ContextVariables",
    "initiate_group_chat",
    "UpdateSystemMessage",
]
