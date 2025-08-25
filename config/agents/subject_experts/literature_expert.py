"""
Literature Expert Agent

This module defines the :class:`LiteratureExpertAgent`, a subject
expert focused on literature analysis and writing.  Like other
specialized experts in this project, it inherits from
``SubjectExpertAgent`` to reuse base functionality.  The literature
expert can analyze texts, provide writing advice and discuss literary
history.

Refer to the AutoGen AgentChat user guide for design patterns when
building multi‑agent systems:
https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/index.html
"""

from __future__ import annotations

from typing import cast

from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS
from .prompts import (
    LIT_ANALYZE_TEXT_PROMPT,
    LIT_GIVE_WRITING_ADVICE_PROMPT,
)


class LiteratureExpertAgent(SubjectExpertAgent):
    """Literature Expert Agent"""

    def __init__(self, **kwargs):
        super().__init__(
            name="Literature_Expert",
            subject="Literature",
            expertise_areas=[
                "Literary Analysis (Themes, Characters, Symbolism)",
                "Poetry (Forms, Meter, Figurative Language)",
                "Prose (Novels, Short Stories, Narratology)",
                "Drama (Plays, Stagecraft, Dialogue)",
                "Literary History (Periods, Movements, Canon)",
                "Rhetoric and Composition",
                "Comparative Literature",
            ],
            additional_instructions=EXPERT_PROMPTS["Literature_Expert"],
            **kwargs,
        )

    def analyze_text(self, text: str, question: str = "") -> str:
        """Analyze a literary text based on a question or general guidance"""
        question_part = f"Question: {question}\n" if question else ""
        prompt = LIT_ANALYZE_TEXT_PROMPT.format(
            text=text, question_part=question_part
        )
        return cast(
            str,
            self.agent.generate_reply(
                messages=[{"content": prompt, "role": "user"}]
            ),
        )

    def give_writing_advice(self, assignment: str) -> str:
        """Provide advice for a writing assignment"""
        prompt = LIT_GIVE_WRITING_ADVICE_PROMPT.format(assignment=assignment)
        return cast(
            str,
            self.agent.generate_reply(
                messages=[{"content": prompt, "role": "user"}]
            ),
        )
