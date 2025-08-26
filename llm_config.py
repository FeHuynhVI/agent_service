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
    def get_config(
        cls,
        model: str | None = None,
        api_key: str | None = None,
        **overrides: Any,
    ) -> Dict[str, Any]:
        """Return a base configuration for the language model.

        Parameters
        ----------
        model:
            The model name to use. If ``None``, the class ``default_model`` is used.
        api_key:
            API key to use for this configuration. If ``None``, falls back to
            :attr:`api_key`.
        **overrides:
            Additional configuration options to merge into the result.
        """
        config: Dict[str, Any] = {
            "model": model or cls.default_model,
            "temperature": 0,
        }
        if cls.base_url:
            config["base_url"] = cls.base_url
        key = api_key or cls.api_key
        if key:
            config["api_key"] = key
        model_name = config["model"]
        # Ensure ``model_info`` is always populated for non-OpenAI models.
        # ``OpenAIChatCompletionClient`` requires capability metadata when the
        # model name is unknown to the service. We therefore fall back to the
        # default model's information when the requested model lacks a
        # dedicated entry.
        config["model_info"] = (
            cls.model_infos.get(model_name)
            or cls.model_infos.get(cls.default_model)
            or {}
        )
        config.update(overrides)
        return config

    @classmethod
    def get_agent_config(
        cls,
        agent_name: str,
        api_key: str | None = None,
        **overrides: Any,
    ) -> Dict[str, Any]:
        """Return configuration for a specific agent.

        This looks up ``agent_name`` in :attr:`agent_models` and falls back to
        :attr:`default_model` when no specific mapping is provided.
        """
        model = overrides.pop("model", cls.agent_models.get(agent_name))
        return cls.get_config(model=model, api_key=api_key, **overrides)

    @classmethod
    def get_expert_config(
        cls,
        agent_name: str,
        api_key: str | None = None,
        **overrides: Any,
    ) -> Dict[str, Any]:
        """Return a configuration tuned for expert agents.

        Expert agents default to a slightly higher temperature for more
        detailed responses while still supporting per-agent model overrides.
        """
        temp = overrides.pop("temperature", 0.2)
        base = cls.get_agent_config(agent_name, api_key=api_key, **overrides)
        base["temperature"] = temp
        return base

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
        return OpenAIChatCompletionClient(**config)


__all__ = ["LLMConfig"]
