"""Chemistry Expert Agent."""

from typing import cast

from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS
from .prompts import (
    CHEM_BALANCE_EQUATION_PROMPT,
    CHEM_PREDICT_REACTION_PROMPT,
)

class ChemistryExpertAgent(SubjectExpertAgent):
    """Chemistry Expert Agent"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Chemistry_Expert",
            subject="Chemistry",
            expertise_areas=[
                "Inorganic Chemistry (Periodic trends, Coordination compounds)",
                "Organic Chemistry (Reactions, Mechanisms, Synthesis)",
                "Physical Chemistry (Thermodynamics, Kinetics, Quantum)",
                "Analytical Chemistry (Qualitative, Quantitative analysis)",
                "Biochemistry (Proteins, Enzymes, Metabolism)",
                "Environmental Chemistry",
                "Electrochemistry",
                "Nuclear Chemistry",
                "Polymer Chemistry"
            ],
            additional_instructions=EXPERT_PROMPTS["Chemistry_Expert"],
            **kwargs
        )
    
    def balance_equation(self, equation: str) -> str:
        """Balance a chemical equation"""
        prompt = CHEM_BALANCE_EQUATION_PROMPT.format(equation=equation)
        return cast(
            str,
            self.agent.generate_reply(
                messages=[{"content": prompt, "role": "user"}]
            ),
        )
    
    def predict_reaction(self, reactants: str, conditions: str = "") -> str:
        """Predict reaction products and mechanism"""
        prompt = CHEM_PREDICT_REACTION_PROMPT.format(
            reactants=reactants,
            conditions=conditions if conditions else "Standard conditions",
        )
        return cast(
            str,
            self.agent.generate_reply(
                messages=[{"content": prompt, "role": "user"}]
            ),
        )
