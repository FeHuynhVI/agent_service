"""Minimal LLM configuration utilities."""

from typing import Any, Dict


class LLMConfig:
    """Utility helpers to construct LLM configuration dictionaries."""

    default_model: str = "gpt-4o-mini"

    @classmethod
    def get_config(cls, **overrides: Any) -> Dict[str, Any]:
        """Return a base configuration for the language model."""
        config: Dict[str, Any] = {"model": cls.default_model, "temperature": 0}
        config.update(overrides)
        return config

    @classmethod
    def get_expert_config(cls, subject: str, **overrides: Any) -> Dict[str, Any]:
        """Return a configuration tuned for expert agents."""
        # For now this simply returns the base config with a lower temperature.
        base = cls.get_config(temperature=0.2)
        base.update(overrides)
        return base


__all__ = ["LLMConfig"]

