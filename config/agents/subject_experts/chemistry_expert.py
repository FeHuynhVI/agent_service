"""
Chemistry Expert Agent
"""
from ..base_agent import SubjectExpertAgent

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
            additional_instructions="""
Special capabilities for Chemistry:
- Balance chemical equations and redox reactions
- Predict reaction products and mechanisms
- Calculate stoichiometry and yields
- Explain molecular structure and bonding
- Analyze spectroscopic data (NMR, IR, MS)
- Design synthetic pathways
- Explain laboratory techniques and safety
- Relate chemistry to biological and environmental systems

Problem-solving approach:
1. Identify the type of chemical problem
2. Write balanced equations when applicable
3. Draw molecular structures clearly
4. Apply relevant chemical principles
5. Show calculations with proper significant figures
6. Include units and chemical formulas
7. Consider reaction conditions
8. Discuss practical implications

Use IUPAC nomenclature and standard chemical notation.
Emphasize safety considerations when discussing experiments.
""",
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