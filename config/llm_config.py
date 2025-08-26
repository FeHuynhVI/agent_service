"""Wrapper for LLM configuration utilities.

This module re-exports the :class:`LLMConfig` from the project root module
:mod:`llm_config` so that code written for a package structure
(`config.llm_config`) continues to function. The real implementation of
:class:`LLMConfig` resides in :mod:`llm_config` at the project root.
"""

from __future__ import annotations

from llm_config import LLMConfig  # noqa: F401

__all__ = ["LLMConfig"]
