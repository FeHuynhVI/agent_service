"""Biology expert agent implementation."""

from __future__ import annotations

from typing import cast

from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS
from .prompts import BIOLOGY_EXPLAIN_CONCEPT_PROMPT


class BiologyExpertAgent(SubjectExpertAgent):
    """Biology Expert Agent."""

    def __init__(self, **kwargs):
        super().__init__(
            name="Biology_Expert",
            subject="Biology",
            expertise_areas=[
                "Cell Biology",
                "Genetics",
                "Evolution",
                "Ecology",
                "Physiology",
                "Biochemistry",
            ],
            additional_instructions=EXPERT_PROMPTS["Biology_Expert"],
            **kwargs,
        )

    def explain_concept(self, concept: str) -> str:
        """Explain a biology concept in detail."""
        prompt = BIOLOGY_EXPLAIN_CONCEPT_PROMPT.format(concept=concept)
        return cast(
            str,
            self.agent.generate_reply(
                messages=[{"content": prompt, "role": "user"}]
            ),
        )


__all__ = ["BiologyExpertAgent"]

