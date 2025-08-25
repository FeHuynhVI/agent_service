"""
Configuration package for the AutoGen Education Service.

This package provides backwards‑compatibility wrappers around the
configuration modules located at the project root.  Importing from
``config.settings`` will forward to the shared :mod:`settings` module,
and importing from ``config.llm_config`` will forward to
:mod:`llm_config`.  These wrappers exist so that legacy code written
against a package layout (``config/settings.py``) continues to work
without modification.
"""

from __future__ import annotations

from .settings import settings  # noqa: F401
from .llm_config import LLMConfig  # noqa: F401

__all__ = ["settings", "LLMConfig"]