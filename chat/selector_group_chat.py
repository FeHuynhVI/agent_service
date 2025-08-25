"""Selector Group Chat implementation for AutoGen."""

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    Literal,
)
from autogen import GroupChat, GroupChatManager, Agent
from config.settings import settings
from config.llm_config import LLMConfig
from config.prompts import (
    GROUP_CHAT_MANAGER_PROMPT,
    USER_PROXY_PROMPT,
)

class SelectorGroupChat:
    """
    Manages group chat with intelligent agent selection
    """
    
    def __init__(
        self,
        agents: List[Agent],
        max_rounds: Optional[int] = None,
        admin_name: str = "Admin",
        selection_method: str = "auto"  # auto, manual, or custom
    ):
        self.agents = agents
        self.admin_name = admin_name
        self.selection_method = selection_method
        self.max_rounds = max_rounds or settings.max_rounds
        
        # Create group chat
        self.group_chat = self._create_group_chat()
        
        # Create group chat manager
        self.manager = self._create_manager()
    
    def _create_group_chat(self) -> GroupChat:
        """Create the group chat instance"""
        return GroupChat(
            agents=self.agents,
            messages=[],
            max_round=self.max_rounds,
            speaker_selection_method=self._get_selection_method(),
            allow_repeat_speaker=False,
        )
    
    def _create_manager(self) -> GroupChatManager:
        """Create the group chat manager"""
        manager_config = LLMConfig.get_config(temperature=0.3)
        
        return GroupChatManager(
            groupchat=self.group_chat,
            llm_config=manager_config,
            system_message=GROUP_CHAT_MANAGER_PROMPT,
        )
    
    def _get_selection_method(
        self,
    ) -> Union[
        Callable[[Agent, GroupChat], Agent],
        Literal["auto", "manual", "random", "round_robin"],
    ]:
        """Get the speaker selection method."""
        if self.selection_method == "manual":
            return "manual"
        if self.selection_method == "custom" and hasattr(self, "custom_selector"):
            return self.custom_selector
        return "auto"  # Let AutoGen handle selection automatically
    
    def set_custom_selector(self, selector_function: Callable) -> None:
        """Set a custom selector function"""
        self.custom_selector = selector_function
        self.selection_method = "custom"
        self.group_chat.speaker_selection_method = selector_function
    
    def create_subject_selector(self) -> Callable:
        """Create a subject-based selector function"""
        def select_speaker(last_speaker: Agent, groupchat: GroupChat) -> Agent:
            """Custom speaker selection based on message content"""
            messages = groupchat.messages
            if not messages:
                return self.agents[0]  # Return first agent if no messages
            
            last_message = messages[-1]["content"].lower() if messages else ""
            
            # Map keywords to agents
            agent_keywords = {
                "Math_Expert": ["math", "calculus", "algebra", "geometry", "equation", "integral", "derivative"],
                "Physics_Expert": ["physics", "force", "energy", "momentum", "quantum", "relativity", "mechanics"],
                "Chemistry_Expert": ["chemistry", "chemical", "reaction", "molecule", "element", "compound", "acid"],
                "Biology_Expert": ["biology", "cell", "dna", "evolution", "ecology", "organism", "genetics"],
                "CS_Expert": ["programming", "code", "algorithm", "data structure", "computer", "software", "debug"],
                "Literature_Expert": ["literature", "essay", "poem", "story", "writing", "author", "analysis"],
                "English_Expert": ["english", "grammar", "vocabulary", "ielts", "toefl", "pronunciation", "speaking"],
                "Info_Agent": ["material", "resource", "quiz", "syllabus", "document", "audio", "video"]
            }
            
            # Check which agent's keywords appear most in the message
            agent_scores = {}
            for agent_name, keywords in agent_keywords.items():
                score = sum(1 for keyword in keywords if keyword in last_message)
                if score > 0:
                    agent_scores[agent_name] = score
            
            # Select agent with highest score
            if agent_scores:
                selected_name = max(agent_scores, key=lambda k: agent_scores[k])
                for agent in self.agents:
                    if agent.name == selected_name:
                        return agent
            
            # Default to cycling through agents
            last_speaker_index = self.agents.index(last_speaker)
            return self.agents[(last_speaker_index + 1) % len(self.agents)]
        
        return select_speaker
    
    def start_chat(self, initial_message: str, sender: Optional[Agent] = None) -> None:
        """Start the group chat"""
        if sender is None:
            # Create a user proxy to send the initial message
            from autogen import UserProxyAgent
            sender = UserProxyAgent(
                name="User",
                system_message=USER_PROXY_PROMPT,
                llm_config=False,
                human_input_mode="NEVER"
            )
        
        # Initiate the chat
        sender.initiate_chat(
            self.manager,
            message=initial_message,
            clear_history=True
        )
    
    def add_agent(self, agent: Agent) -> None:
        """Add a new agent to the group chat"""
        self.agents.append(agent)
        self.group_chat.agents = self.agents
    
    def remove_agent(self, agent_name: str) -> bool:
        """Remove an agent from the group chat"""
        for i, agent in enumerate(self.agents):
            if agent.name == agent_name:
                self.agents.pop(i)
                self.group_chat.agents = self.agents
                return True
        return False
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get the chat history"""
        return self.group_chat.messages
    
    def clear_history(self) -> None:
        """Clear the chat history"""
        self.group_chat.messages = []
    
    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get an agent by name"""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
