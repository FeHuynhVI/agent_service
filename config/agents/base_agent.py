"""
Base Agent class for all AutoGen agents
"""
from config.settings import settings
from config.llm_config import LLMConfig
from typing import Any, Dict, List, Optional, Literal, cast
from autogen import AssistantAgent
from config.prompts import SUBJECT_EXPERT_PROMPT_TEMPLATE

HumanInputMode = Literal["ALWAYS", "NEVER", "TERMINATE"]


class BaseAgent:
    """Base class for all agents in the system"""

    def __init__(
        self,
        name: str,
        system_message: str,
        llm_config: Optional[Dict[str, Any]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[HumanInputMode] = None,
    ):
        self.name = name
        self.system_message = system_message
        self.llm_config = llm_config or LLMConfig.get_config()
        self.max_consecutive_auto_reply = (
            max_consecutive_auto_reply or settings.max_consecutive_auto_reply
        )
        default_human_input_mode: HumanInputMode = cast(
            HumanInputMode,
            settings.human_input_mode,
        )
        self.human_input_mode: HumanInputMode = (
            human_input_mode or default_human_input_mode
        )
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
        return SUBJECT_EXPERT_PROMPT_TEMPLATE.format(
            subject=subject,
            expertise_list=expertise_list,
            additional=additional,
        )
