"""
Wrapper for the mathematics expert agent.

This module forwards all exports from the root :mod:`math_expert` module
to maintain the import path ``agents.subject_experts.math_expert``.
"""

from __future__ import annotations

from math_expert import MathExpertAgent  # noqa: F401

__all__ = ["MathExpertAgent"]