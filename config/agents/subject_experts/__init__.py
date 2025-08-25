"""Subject expert agent implementations."""


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
    "BiologyExpertAgent",
    "ChemistryExpertAgent",
    "CSExpertAgent",
    "EnglishExpertAgent",
    "LiteratureExpertAgent",
    "MathExpertAgent",
    "PhysicsExpertAgent",
]