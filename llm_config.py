"""Utility helpers for constructing LLM configuration dictionaries."""

from typing import Any, Dict
import os


class LLMConfig:
    """Factory for language‑model configuration dictionaries."""

    DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @staticmethod
    def get_config(model: str | None = None, temperature: float = 0.7, **overrides: Any) -> Dict[str, Any]:
        """Return a basic configuration for an LLM call.

        Parameters
        ----------
        model:
            Optional model name to use.  If omitted, ``DEFAULT_MODEL`` is used.
        temperature:
            Sampling temperature for the model.
        overrides:
            Additional keyword arguments are merged into the returned dict.
        """
        config: Dict[str, Any] = {
            "model": model or LLMConfig.DEFAULT_MODEL,
            "temperature": temperature,
        }
        config.update(overrides)
        return config

    @staticmethod
    def get_expert_config(subject: str, **overrides: Any) -> Dict[str, Any]:
        """Return configuration tuned for a particular subject expert.

        Currently this simply proxies to :meth:`get_config`, but the method
        exists to allow easy per‑subject customisation in the future.
        """
        return LLMConfig.get_config(**overrides)


__all__ = ["LLMConfig"]
