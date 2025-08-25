"""Mathematics expert agent implementation."""

from __future__ import annotations

from typing import cast

from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS
from .prompts import MATH_SOLVE_PROBLEM_PROMPT


class MathExpertAgent(SubjectExpertAgent):
    """Mathematics Expert Agent."""

    def __init__(self, **kwargs):
        super().__init__(
            name="Math_Expert",
            subject="Mathematics",
            expertise_areas=[
                "Algebra",
                "Geometry",
                "Calculus",
                "Statistics",
                "Number Theory",
                "Discrete Mathematics",
            ],
            additional_instructions=EXPERT_PROMPTS["Math_Expert"],
            **kwargs,
        )

    def solve_problem(self, problem: str) -> str:
        """Solve a mathematics problem with step-by-step reasoning."""
        prompt = MATH_SOLVE_PROBLEM_PROMPT.format(problem=problem)
        return cast(
            str,
            self.agent.generate_reply(
                messages=[{"content": prompt, "role": "user"}]
            ),
        )


__all__ = ["MathExpertAgent"]

