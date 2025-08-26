"""
Base Agent class for all AutoGen agents
"""
from autogen import AssistantAgent
from config.settings import settings
from config.llm_config import LLMConfig
from config.prompts import SUBJECT_EXPERT_PROMPT_TEMPLATE
from typing import Any, Dict, List, Optional, Literal, cast, Union
from inspect import signature

HumanInputMode = Literal["ALWAYS", "NEVER", "TERMINATE"]


class BaseAgent:
    """Base class for all agents in the system"""

    def __init__(
        self,
        name: str,
        system_message: str,
        llm_config: Optional[Union[Dict[str, Any], str]] = None,
        api_key: str | None = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[HumanInputMode] = None,
    ):
        self.name = name
        self.system_message = system_message
        # Merge any custom configuration with defaults so required fields like
        # ``model_info`` are always present.  ``llm_config`` may be either a
        # configuration dictionary or simply a model name string.
        if isinstance(llm_config, dict):
            if "model_info" in llm_config and "model" in llm_config:
                self.llm_config = dict(llm_config)
            else:
                self.llm_config = LLMConfig.get_agent_config(
                    name, api_key=api_key, **llm_config
                )
        else:
            overrides: Dict[str, Any] = (
                {"model": llm_config} if isinstance(llm_config, str) else {}
            )
            self.llm_config = LLMConfig.get_agent_config(
                name, api_key=api_key, **overrides
            )
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
        params = signature(AssistantAgent.__init__).parameters
        if "model_client" in params:
            model_client = LLMConfig.build_model_client(self.llm_config)
            return AssistantAgent(
                name=self.name,
                system_message=self.system_message,
                model_client=model_client,
                max_consecutive_auto_reply=self.max_consecutive_auto_reply,
                human_input_mode=self.human_input_mode,
            )
        # Fallback for older AutoGen versions that use ``llm_config`` instead
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
        api_key: str | None = None,
        **kwargs
    ):
        self.subject = subject
        self.expertise_areas = expertise_areas
        
        system_message = self._create_system_message(
            subject, 
            expertise_areas, 
            additional_instructions
        )

        # Get specialized config for the subject, allowing callers to override
        # individual fields or provide a simple model name string.
        raw_cfg = kwargs.pop('llm_config', None)
        overrides: Dict[str, Any]
        if isinstance(raw_cfg, str):
            overrides = {"model": raw_cfg}
        elif isinstance(raw_cfg, dict):
            overrides = raw_cfg
        else:
            overrides = {}
        llm_config = LLMConfig.get_expert_config(
            name, api_key=api_key, **overrides
        )

        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            api_key=api_key,
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
