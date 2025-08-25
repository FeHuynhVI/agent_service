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
        prompt = f"""
Correct the following sentence for grammatical errors and explain each correction:

"{sentence}"

Provide:
1. The corrected sentence
2. A breakdown of each error and the corresponding rule
3. Suggestions for how to avoid similar mistakes in the future
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])

    def build_vocabulary(self, word: str) -> str:
        """Explain a word's meaning, usage and related terms"""
        prompt = f"""
Teach the word "{word}" in detail.

Include:
1. Definition and part of speech
2. Pronunciation with phonetic transcription
3. Synonyms and antonyms
4. Example sentences demonstrating correct usage
5. Common collocations or phrases with the word
6. Etymology or origin (if interesting)
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
