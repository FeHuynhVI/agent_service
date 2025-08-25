"""
Wrapper for settings configuration.

This module re‑exports the :mod:`settings` module from the project
root to preserve compatibility with code that expects a
``config.settings`` package.  By importing :class:`Settings` and the
``settings`` instance from here, other modules can continue to work
without changes after refactoring the project structure.
"""

from __future__ import annotations

from settings import Settings, settings  # noqa: F401

__all__ = ["Settings", "settings"]