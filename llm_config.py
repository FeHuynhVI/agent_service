"""Fixed LLM configuration utilities for FPT Cloud API."""

from __future__ import annotations

import os
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

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
    """Utility helpers to construct LLM configuration dictionaries for FPT Cloud API."""

    #: Default model to use when an agent specific model is not provided
    default_model: str = os.getenv("LLM_BASE_MODEL", "gpt-oss-120b")
    #: Base URL for FPT Cloud API
    base_url: str = os.getenv("LLM_BASE_URL", "https://mkp-api.fptcloud.com/v1")
    #: FPT Cloud API key
    api_key: str = os.getenv("FCI_API_KEY", "")
    #: Mapping of agent names to the model they should use
    agent_models: Dict[str, str] = {}
    #: Model capability descriptions
    model_infos: Dict[str, Dict[str, Any]] = {
        "gpt-oss-120b": {
            "vision": False,
            "json_output": True,
            "function_calling": False,
            "structured_output": False,
            "family": ModelFamily.UNKNOWN,
        },
        # Fallback for any unknown models
        "default": {
            "vision": False,
            "json_output": False,
            "function_calling": False,
            "structured_output": False,
            "family": ModelFamily.UNKNOWN,
        }
    }

    @classmethod
    def validate_api_key(cls, api_key: str | None = None) -> str:
        """Validate and return API key for FPT Cloud API."""
        key = api_key or cls.api_key
        if not key:
            raise ValueError(
                "No FPT Cloud API key provided. Set FCI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        return key

    @classmethod
    def is_local_server(cls) -> bool:
        """Check if we're using a local model server."""
        return bool(cls.base_url and ("localhost" in cls.base_url or "127.0.0.1" in cls.base_url))

    @classmethod
    def get_agent_config(
        cls,
        agent_name: str,
        api_key: str | None = None,
        **overrides: Any,
    ) -> Dict[str, Any]:
        """Return configuration for a specific agent."""
        model = overrides.pop(
            "model", cls.agent_models.get(agent_name) or cls.default_model
        )
        
        # Validate the API key
        validated_key = cls.validate_api_key(api_key)
        
        config: Dict[str, Any] = {
            "model": model,
            "temperature": overrides.pop("temperature", 0.3),  # Match your retriver_config default
            "api_key": validated_key,
        }
        
        # Always add base_url for FPT Cloud API
        if cls.base_url:
            config["base_url"] = cls.base_url
        
        # Get model info with fallback
        config["model_info"] = (
            cls.model_infos.get(model)
            or cls.model_infos.get(cls.default_model)
            or cls.model_infos["default"]
        )
        
        # Apply any additional overrides
        config.update(overrides)
        return config

    @staticmethod
    def build_model_client(config: Dict[str, Any]):
        """Instantiate the OpenAI-compatible chat completion client for FPT Cloud API."""
        if OpenAIChatCompletionClient is None:
            raise RuntimeError(
                "OpenAIChatCompletionClient is required. "
                "Install it with 'pip install \"autogen-ext[openai]\"'.",
            )
        
        cfg = dict(config)
        cfg.pop("model_info", None)
        
        # Ensure we have a valid API key
        if not cfg.get("api_key"):
            raise ValueError("FPT Cloud API key is required to build model client")
        
        return OpenAIChatCompletionClient(**cfg)

    @classmethod
    def debug_config(cls):
        """Debug current configuration."""
        print("=== LLM Configuration Debug ===")
        print(f"Default Model: {cls.default_model}")
        print(f"Base URL: {cls.base_url}")
        print(f"API Key: {'***' + cls.api_key[-8:] if cls.api_key and len(cls.api_key) > 8 else 'NOT SET'}")
        print(f"Is Local Server: {cls.is_local_server()}")
        print(f"Available Models: {list(cls.model_infos.keys())}")


__all__ = ["LLMConfig"]