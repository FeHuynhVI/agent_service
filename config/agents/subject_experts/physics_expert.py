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

from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS


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
        prompt = f"""
Solve the following physics problem:
{problem}

Instructions:
1. Restate the problem concisely
2. Identify the physical quantities and laws involved
3. Draw or describe diagrams if helpful
4. Write down relevant equations
5. Solve algebraically, showing each step
6. Plug in numerical values with appropriate units
7. Provide the final numerical answer with units
8. Comment on the physical interpretation of the result
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])

    def explain_concept(self, concept: str) -> str:
        """Explain a physics concept in detail"""
        prompt = f"""
Explain the following physics concept:
{concept}

Include in your explanation:
1. A definition and the fundamental principles underlying the concept
2. Key equations and how they are derived
3. Example problems or scenarios that illustrate the concept
4. Visual or descriptive representation (what diagrams would show)
5. Applications in everyday life or technology
6. Common misconceptions or pitfalls
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
