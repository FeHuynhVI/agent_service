"""Shared agent imports and logging setup.

This module handles the optional availability of the `ag2` package.
If `ag2` is not installed, it falls back to `autogen`.
"""

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

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
