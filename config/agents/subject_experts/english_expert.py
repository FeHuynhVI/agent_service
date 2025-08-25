"""
English Language Expert Agent

This module defines the :class:`EnglishExpertAgent`, a subject
expert for English language learning.  It inherits from
``SubjectExpertAgent`` to reuse base functionality and tailors the
system message to language education.  The English expert can explain
grammar rules, build vocabulary and help with pronunciation and
communication skills.

Guidance on multi‑agent system design can be found in the AutoGen
AgentChat user guide:
https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/index.html
"""

from __future__ import annotations

from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS
from .prompts import (
    ENGLISH_CORRECT_GRAMMAR_PROMPT,
    ENGLISH_BUILD_VOCABULARY_PROMPT,
)


class EnglishExpertAgent(SubjectExpertAgent):
    """English Language Expert Agent"""

    def __init__(self, **kwargs):
        super().__init__(
            name="English_Expert",
            subject="English Language",
            expertise_areas=[
                "Grammar (Parts of speech, Tenses, Syntax)",
                "Vocabulary (Lexicon, Idioms, Collocations)",
                "Pronunciation and Phonetics",
                "Reading Comprehension",
                "Writing Skills (Essays, Reports, Emails)",
                "Speaking and Listening",
                "Test Preparation (IELTS, TOEFL, TOEIC)",
            ],
            additional_instructions=EXPERT_PROMPTS["English_Expert"],
            **kwargs,
        )

    def correct_grammar(self, sentence: str) -> str:
        """Correct the grammar of a sentence and explain the corrections"""
        prompt = ENGLISH_CORRECT_GRAMMAR_PROMPT.format(sentence=sentence)
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])

    def build_vocabulary(self, word: str) -> str:
        """Explain a word's meaning, usage and related terms"""
        prompt = ENGLISH_BUILD_VOCABULARY_PROMPT.format(word=word)
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
