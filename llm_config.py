"""Minimal LLM configuration utilities."""

from __future__ import annotations

import os
from typing import Any, Dict


class LLMConfig:
    """Utility helpers to construct LLM configuration dictionaries."""

    #: Default model to use when an agent specific model is not provided
    default_model: str = "gpt-oss-120b"
    #: Optional base URL for the LLM API
    base_url: str = os.getenv("LLM_BASE_URL", "")
    #: API key used to authenticate with the LLM provider
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    #: Mapping of agent names to the model they should use
    agent_models: Dict[str, str] = {}

    @classmethod
    def get_config(cls, model: str | None = None, **overrides: Any) -> Dict[str, Any]:
        """Return a base configuration for the language model.

        Parameters
        ----------
        model:
            The model name to use. If ``None``, the class ``default_model`` is used.
        **overrides:
            Additional configuration options to merge into the result.
        """
        config: Dict[str, Any] = {
            "model": model or cls.default_model,
            "temperature": 0,
        }
        if cls.base_url:
            config["base_url"] = cls.base_url
        if cls.api_key:
            config["api_key"] = cls.api_key
        config.update(overrides)
        return config

    @classmethod
    def get_agent_config(cls, agent_name: str, **overrides: Any) -> Dict[str, Any]:
        """Return configuration for a specific agent.

        This looks up ``agent_name`` in :attr:`agent_models` and falls back to
        :attr:`default_model` when no specific mapping is provided.
        """
        model = cls.agent_models.get(agent_name)
        return cls.get_config(model=model, **overrides)

    @classmethod
    def get_expert_config(cls, agent_name: str, **overrides: Any) -> Dict[str, Any]:
        """Return a configuration tuned for expert agents.

        Expert agents default to a slightly higher temperature for more
        detailed responses while still supporting per-agent model overrides.
        """
        base = cls.get_agent_config(agent_name, temperature=0.2)
        base.update(overrides)
        return base


__all__ = ["LLMConfig"]
