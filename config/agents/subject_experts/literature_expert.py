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

from base_agent import SubjectExpertAgent


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
            additional_instructions="""
Special capabilities for Literature:
- Analyze texts for themes, motifs and deeper meaning
- Provide contextual information about authors and historical periods
- Compare and contrast works across genres and cultures
- Offer writing guidance on essays, creative writing and research papers
- Recommend reading lists based on interests or curricula
- Explain literary devices and how they function within a text

Teaching approach:
1. Encourage close reading and textual evidence
2. Discuss multiple interpretations and perspectives
3. Connect literature to its historical and cultural context
4. Foster critical thinking and personal engagement
5. Provide constructive feedback on writing
6. Highlight intertextual connections and influences

Use appropriate literary terminology and cite sources when relevant.
""",
            **kwargs,
        )

    def analyze_text(self, text: str, question: str = "") -> str:
        """Analyze a literary text based on a question or general guidance"""
        # Compose optional question prefix separately to avoid backslashes in f‑string expression
        question_part = f"Question: {question}\n" if question else ""
        prompt = (
            "Analyze the following text:\n\n"
            f"{text}\n\n"
            f"{question_part}Provide:\n"
            "1. A brief summary of the text\n"
            "2. Identification of themes, symbols and stylistic devices\n"
            "3. Analysis of character development and narrative perspective\n"
            "4. Discussion of the historical and cultural context\n"
            "5. Connections to other works or genres\n"
            "6. Your interpretation and critical viewpoint"
        )
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])

    def give_writing_advice(self, assignment: str) -> str:
        """Provide advice for a writing assignment"""
        prompt = f"""
Provide guidance for the following writing assignment:
{assignment}

Your advice should include:
1. Interpretation of the assignment requirements
2. Suggestions for outlining and structuring the response
3. Tips on developing a clear thesis and supporting arguments
4. Advice on style, tone and voice appropriate to the genre
5. Common pitfalls to avoid
6. Recommendations for revision and editing
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
