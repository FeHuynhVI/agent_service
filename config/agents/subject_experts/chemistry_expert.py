"""
Chemistry Expert Agent
"""
from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS

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
        prompt = f"""
Balance the following chemical equation:
{equation}

Show the step-by-step process and explain the method used.
If it's a redox reaction, show the half-reactions.
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
    
    def predict_reaction(self, reactants: str, conditions: str = "") -> str:
        """Predict reaction products and mechanism"""
        prompt = f"""
Predict the products of the following reaction:
Reactants: {reactants}
Conditions: {conditions if conditions else "Standard conditions"}

Include:
1. Predicted products
2. Reaction mechanism (if applicable)
3. Reasoning for the prediction
4. Possible side products
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])