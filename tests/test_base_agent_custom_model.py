"""Tests for custom model handling in :class:`BaseAgent`."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from autogen_core.models import ModelFamily
from config.agents.base_agent import BaseAgent
from llm_config import LLMConfig  # type: ignore


def _setup_defaults() -> tuple[str, dict[str, dict[str, object]]]:
    original_default = LLMConfig.default_model
    original_infos = LLMConfig.model_infos.copy()
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
    return original_default, original_infos


def _restore_defaults(default: str, infos: dict[str, dict[str, object]]) -> None:
    LLMConfig.default_model = default
    LLMConfig.model_infos = infos


def test_base_agent_accepts_model_string(monkeypatch) -> None:
    """Providing a model name string should merge with defaults."""
    default, infos = _setup_defaults()
    try:
        monkeypatch.setattr(BaseAgent, "_create_agent", lambda self: None)
        agent = BaseAgent("Test", "msg", llm_config="custom-model")
        assert agent.llm_config["model"] == "custom-model"
        assert agent.llm_config["model_info"] == LLMConfig.model_infos["fallback-model"]
    finally:
        _restore_defaults(default, infos)


def test_base_agent_merges_config_dict(monkeypatch) -> None:
    """Custom configuration dictionaries should override defaults."""
    default, infos = _setup_defaults()
    try:
        monkeypatch.setattr(BaseAgent, "_create_agent", lambda self: None)
        agent = BaseAgent(
            "Test",
            "msg",
            llm_config={"model": "custom-model", "temperature": 0.7},
        )
        assert agent.llm_config["model"] == "custom-model"
        assert agent.llm_config["model_info"] == LLMConfig.model_infos["fallback-model"]
        assert agent.llm_config["temperature"] == 0.7
    finally:
        _restore_defaults(default, infos)
