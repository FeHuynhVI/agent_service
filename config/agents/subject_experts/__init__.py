"""
Agents package for the AutoGen Education Service.

This package provides backwards‑compatibility wrappers around agent
classes defined at the project root.  It also organizes subject
expert agents under the ``subject_experts`` subpackage to mirror the
expected structure.  Importing from ``agents.base_agent`` or
``agents.subject_experts.math_expert`` will forward to the
corresponding module at the project root.
"""

from __future__ import annotations

from ..base_agent import BaseAgent, SubjectExpertAgent  # noqa: F401
from ..info_agent import InfoAgent  # noqa: F401

# Import subject experts into the package namespace for convenience
from .cs_expert import CSExpertAgent
from .math_expert import MathExpertAgent
from .english_expert import EnglishExpertAgent
from .biology_expert import BiologyExpertAgent
from .physics_expert import PhysicsExpertAgent
from .chemistry_expert import ChemistryExpertAgent
from .literature_expert import LiteratureExpertAgent

__all__ = [
    "BaseAgent",
    "InfoAgent",
    "CSExpertAgent",
    "MathExpertAgent",
    "PhysicsExpertAgent",
    "SubjectExpertAgent",
    "BiologyExpertAgent",
    "EnglishExpertAgent",
    "ChemistryExpertAgent",
    "LiteratureExpertAgent",
]