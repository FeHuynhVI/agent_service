"""Minimal LLM configuration utilities."""

from __future__ import annotations

import os
from typing import Any, Dict

try:  # pragma: no cover - optional dependency
    from autogen_core.models import ModelFamily  # type: ignore
except Exception:  # pragma: no cover - fallback when autogen_core is missing
    from enum import Enum

    class ModelFamily(str, Enum):  # type: ignore[no-redef]
        """Minimal fallback enum used when ``autogen_core`` isn't installed."""

        UNKNOWN = "unknown"

try:  # pragma: no cover - optional dependency
    from autogen_ext.models.openai import OpenAIChatCompletionClient
except Exception:  # pragma: no cover - autogen-ext may not be installed
    OpenAIChatCompletionClient = None  # type: ignore


class LLMConfig:
    """Utility helpers to construct LLM configuration dictionaries."""

    #: Default model to use when an agent specific model is not provided
    default_model: str = os.getenv(
        "LLM_BASE_MODEL", "unknown"
    )
    #: Optional base URL for the LLM API
    base_url: str = os.getenv("LLM_BASE_URL", "")
    #: API key used to authenticate with the LLM provider
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    #: Mapping of agent names to the model they should use
    agent_models: Dict[str, str] = {}
    #: Optional model capability descriptions for non-OpenAI models
    model_infos: Dict[str, Dict[str, Any]] = {
        default_model: {
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "structured_output": False,
            "family": ModelFamily.UNKNOWN,
        }
    }

    @classmethod
    def get_agent_config(
        cls,
        agent_name: str,
        api_key: str | None = None,
        **overrides: Any,
    ) -> Dict[str, Any]:
        """Return configuration for a specific agent.

        This first resolves the model for the given ``agent_name`` and then
        constructs the base configuration, ensuring required metadata like
        ``model_info`` is always included. If ``agent_name`` is not mapped in
        :attr:`agent_models`, the :attr:`default_model` is used.
        """
        model = overrides.pop(
            "model", cls.agent_models.get(agent_name) or cls.default_model
        )
        config: Dict[str, Any] = {
            "model": model,
            "temperature": 0,
        }
        if cls.base_url:
            config["base_url"] = cls.base_url
        key = api_key or cls.api_key
        if key:
            config["api_key"] = key
        config["model_info"] = (
            cls.model_infos.get(model)
            or cls.model_infos.get(cls.default_model)
            or {}
        )
        config.update(overrides)
        return config

    @staticmethod
    def build_model_client(config: Dict[str, Any]):
        """Instantiate the OpenAI chat completion client.

        Centralises the import of :class:`OpenAIChatCompletionClient` so that
        callers need not handle the optional dependency themselves.
        """
        if OpenAIChatCompletionClient is None:
            raise RuntimeError(
                "OpenAIChatCompletionClient is required. "
                "Install it with 'pip install \"autogen-ext[openai]\"'.",
            )
        cfg = dict(config)
        cfg.pop("model_info", None)
        return OpenAIChatCompletionClient(**cfg)


__all__ = ["LLMConfig"]
