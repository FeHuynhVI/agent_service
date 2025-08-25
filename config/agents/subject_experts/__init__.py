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

from .base_agent import BaseAgent, SubjectExpertAgent  # noqa: F401
from .info_agent import InfoAgent  # noqa: F401

# Import subject experts into the package namespace for convenience
from .subject_experts.cs_expert import CSExpertAgent
from .subject_experts.math_expert import MathExpertAgent
from .subject_experts.english_expert import EnglishExpertAgent
from .subject_experts.biology_expert import BiologyExpertAgent
from .subject_experts.physics_expert import PhysicsExpertAgent
from .subject_experts.chemistry_expert import ChemistryExpertAgent
from .subject_experts.literature_expert import LiteratureExpertAgent 

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