"""
Computer Science Expert Agent
"""
from ..base_agent import SubjectExpertAgent
from config.expert_prompts import EXPERT_PROMPTS

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
        prompt = f"""
Write {language} code to solve:
{problem}

Include:
1. Problem analysis
2. Algorithm explanation
3. Complete, working code
4. Time/space complexity analysis
5. Test cases
6. Possible optimizations
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
    
    def debug_code(self, code: str, error: str = "") -> str:
        """Debug code and fix errors"""
        prompt = f"""
Debug the following code:
```
{code}
```
Error message: {error if error else "Unknown error"}

Provide:
1. Error identification
2. Root cause analysis
3. Fixed code
4. Explanation of changes
5. Prevention tips
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
    
    def explain_algorithm(self, algorithm: str) -> str:
        """Explain an algorithm in detail"""
        prompt = f"""
Explain the {algorithm} algorithm:

Include:
1. Concept and purpose
2. Step-by-step process
3. Pseudocode
4. Implementation example
5. Time and space complexity
6. Use cases
7. Advantages and limitations
"""
        return self.agent.generate_reply(messages=[{"content": prompt, "role": "user"}])