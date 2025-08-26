"""Tests for the :mod:`llm_config` helper utilities."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import llm_config
from llm_config import LLMConfig  # type: ignore
from autogen_core.models import ModelFamily


def test_get_agent_config_falls_back_to_default_model_info() -> None:
    """Unknown models should reuse the default model's information."""
    # Backup current configuration so the test is isolated.
    original_default = LLMConfig.default_model
    original_infos = LLMConfig.model_infos.copy()

    try:
        # Define a minimal default model info entry.
        LLMConfig.default_model = "fallback-model"
        LLMConfig.model_infos = {
            "fallback-model": {
                "vision": False,
                "function_calling": False,
                "json_output": False,
                "structured_output": False,
                "family": ModelFamily.UNKNOWN,
            }
        }

        cfg = LLMConfig.get_agent_config("dummy", model="custom-model")
        assert cfg["model_info"] == LLMConfig.model_infos["fallback-model"]
    finally:
        # Restore original global state for any following tests.
        LLMConfig.default_model = original_default
        LLMConfig.model_infos = original_infos


def test_build_model_client_strips_model_info(monkeypatch) -> None:
    """``model_info`` should not be forwarded to the client."""
    class DummyClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(llm_config, "OpenAIChatCompletionClient", DummyClient)
    cfg = LLMConfig.get_agent_config("dummy")
    client = LLMConfig.build_model_client(cfg)
    assert isinstance(client, DummyClient)
    assert "model_info" not in client.kwargs

