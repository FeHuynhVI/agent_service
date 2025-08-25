"""
Base Agent class for all AutoGen agents
"""
from config.settings import settings
from config.llm_config import LLMConfig
from typing import Dict, Any, Optional, List
from autogen import AssistantAgent, UserProxyAgent

class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(
        self,
        name: str,
        system_message: str,
        llm_config: Optional[Dict[str, Any]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[str] = None
    ):
        self.name = name
        self.system_message = system_message
        self.llm_config = llm_config or LLMConfig.get_config()
        self.max_consecutive_auto_reply = max_consecutive_auto_reply or settings.max_consecutive_auto_reply
        self.human_input_mode = human_input_mode or settings.human_input_mode
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AssistantAgent:
        """Create the AutoGen agent"""
        return AssistantAgent(
            name=self.name,
            system_message=self.system_message,
            llm_config=self.llm_config,
            max_consecutive_auto_reply=self.max_consecutive_auto_reply,
            human_input_mode=self.human_input_mode,
        )
    
    def get_agent(self) -> AssistantAgent:
        """Get the underlying AutoGen agent"""
        return self.agent
    
    def update_system_message(self, new_message: str):
        """Update the agent's system message"""
        self.system_message = new_message
        self.agent.update_system_message(new_message)

class SubjectExpertAgent(BaseAgent):
    """Base class for subject expert agents"""
    
    def __init__(
        self,
        name: str,
        subject: str,
        expertise_areas: List[str],
        additional_instructions: str = "",
        **kwargs
    ):
        self.subject = subject
        self.expertise_areas = expertise_areas
        
        system_message = self._create_system_message(
            subject, 
            expertise_areas, 
            additional_instructions
        )
        
        # Get specialized config for the subject
        llm_config = kwargs.pop('llm_config', None) or LLMConfig.get_expert_config(subject.lower())
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs
        )
    
    def _create_system_message(
        self, 
        subject: str, 
        expertise_areas: List[str], 
        additional: str
    ) -> str:
        """Create a comprehensive system message for the expert"""
        expertise_list = ", ".join(expertise_areas)
        return f"""
You are an expert in {subject} with deep knowledge in: {expertise_list}.

Your responsibilities:
1. Provide accurate, detailed explanations in your subject area
2. Help students understand complex concepts through clear examples
3. Solve problems step-by-step with detailed reasoning
4. Create practice exercises and quizzes when requested
5. Adapt your teaching style to the student's level
6. Use visual representations and analogies when helpful
7. Provide references and additional resources when appropriate

Teaching approach:
- Start with fundamentals and build up complexity gradually
- Use real-world examples to illustrate abstract concepts
- Encourage critical thinking and problem-solving skills
- Be patient and supportive with struggling students
- Celebrate progress and understanding

{additional}

Always maintain academic integrity and encourage genuine learning.
When you've completed explaining a concept or solving a problem, end with "TERMINATE" if the query is fully addressed.
"""