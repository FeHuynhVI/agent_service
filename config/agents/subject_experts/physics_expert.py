"""
Physics Expert Agent

This module defines the :class:`PhysicsExpertAgent`, a subject
specialist for physics.  It inherits from :class:`SubjectExpertAgent`
to leverage common functionality such as system message construction and
LLM configuration.  The physics expert has a broad range of knowledge
spanning mechanics, electromagnetism, thermodynamics and modern
physics.  Methods are provided to solve physics problems and explain
concepts in depth.

See the AutoGen AgentChat user guide for guidance on creating
multi‑agent systems:
https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/index.html
"""

from __future__ import annotations

from typing import cast

from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS
from .prompts import (
    PHYSICS_SOLVE_PROBLEM_PROMPT,
    PHYSICS_EXPLAIN_CONCEPT_PROMPT,
)


class PhysicsExpertAgent(SubjectExpertAgent):
    """Physics Expert Agent"""

    def __init__(self, **kwargs):
        super().__init__(
            name="Physics_Expert",
            subject="Physics",
            expertise_areas=[
                "Mechanics (Kinematics, Dynamics, Work and Energy)",
                "Electromagnetism (Electricity, Magnetism, Circuits)",
                "Thermodynamics (Laws, Heat Transfer, Statistical)",
                "Optics (Geometric, Wave, Quantum)",
                "Modern Physics (Quantum Mechanics, Relativity, Nuclear)",
                "Waves and Oscillations",
                "Fluid Dynamics",
                "Astrophysics and Cosmology",
            ],
            additional_instructions=EXPERT_PROMPTS["Physics_Expert"],
            **kwargs,
        )

    def solve_problem(self, problem: str) -> str:
        """Solve a physics problem with full reasoning"""
        prompt = PHYSICS_SOLVE_PROBLEM_PROMPT.format(problem=problem)
        return cast(
            str,
            self.agent.generate_reply(
                messages=[{"content": prompt, "role": "user"}]
            ),
        )

    def explain_concept(self, concept: str) -> str:
        """Explain a physics concept in detail"""
        prompt = PHYSICS_EXPLAIN_CONCEPT_PROMPT.format(concept=concept)
        return cast(
            str,
            self.agent.generate_reply(
                messages=[{"content": prompt, "role": "user"}]
            ),
        )
