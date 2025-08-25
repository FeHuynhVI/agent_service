"""Computer Science Expert Agent"""

from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS
from .prompts import (
    CS_WRITE_CODE_PROMPT,
    CS_DEBUG_CODE_PROMPT,
    CS_EXPLAIN_ALGORITHM_PROMPT,
)

class CSExpertAgent(SubjectExpertAgent):
    """Computer Science Expert Agent"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="CS_Expert",
            subject="Computer Science",
            expertise_areas=[
                "Programming (Python, Java, C++, JavaScript)",
                "Data Structures (Arrays, Trees, Graphs, Hash Tables)",
                "Algorithms (Sorting, Searching, Dynamic Programming)",
                "Software Engineering (Design Patterns, Testing, Agile)",
                "Databases (SQL, NoSQL, Design)",
                "Operating Systems (Processes, Memory, File Systems)",
                "Computer Networks (TCP/IP, HTTP, Security)",
                "Artificial Intelligence and Machine Learning",
                "Web Development (Frontend, Backend, APIs)"
            ],
            additional_instructions=EXPERT_PROMPTS["CS_Expert"],
            **kwargs
        )
    
    def write_code(self, problem: str, language: str = "Python") -> str:
        """Write code to solve a problem"""
        prompt = CS_WRITE_CODE_PROMPT.format(language=language, problem=problem)
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
    
    def debug_code(self, code: str, error: str = "") -> str:
        """Debug code and fix errors"""
        prompt = CS_DEBUG_CODE_PROMPT.format(
            code=code, error=error if error else "Unknown error"
        )
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
    
    def explain_algorithm(self, algorithm: str) -> str:
        """Explain an algorithm in detail"""
        prompt = CS_EXPLAIN_ALGORITHM_PROMPT.format(algorithm=algorithm)
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])