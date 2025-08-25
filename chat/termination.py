"""
Termination conditions for AutoGen chat
"""
from typing import Dict, Any, Optional
import re
from config.settings import settings

class TerminationHandler:
    """
    Handles termination conditions for group chat
    """
    
    def __init__(
        self,
        termination_msg: Optional[str] = None,
        max_rounds: Optional[int] = None,
        check_solved: bool = True
    ):
        self.termination_msg = termination_msg or settings.termination_msg
        self.max_rounds = max_rounds or settings.max_rounds
        self.check_solved = check_solved
        self.round_count = 0
    
    def is_termination_msg(self, message: Dict[str, Any]) -> bool:
        """Check if message contains termination signal"""
        content = message.get("content", "")
        
        # Check for explicit termination message
        if self.termination_msg in content:
            return True
        
        # Check for other termination patterns
        termination_patterns = [
            r"TERMINATE",
            r"Task completed",
            r"Problem solved",
            r"Query answered",
            r"No further assistance needed"
        ]
        
        for pattern in termination_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def check_max_rounds(self) -> bool:
        """Check if maximum rounds reached"""
        self.round_count += 1
        return self.round_count >= self.max_rounds
    
    def check_problem_solved(self, messages: list) -> bool:
        """Check if the problem appears to be solved"""
        if not self.check_solved or len(messages) < 2:
            return False
        
        # Check recent messages for solution indicators
        recent_messages = messages[-3:]
        
        solution_indicators = [
            "answer is",
            "solution is",
            "the result is",
            "therefore",
            "in conclusion",
            "final answer",
            "correct answer"
        ]
        
        for message in recent_messages:
            content = message.get("content", "").lower()
            for indicator in solution_indicators:
                if indicator in content:
                    # Check if there's been acknowledgment
                    if self._check_acknowledgment(messages):
                        return True
        
        return False
    
    def _check_acknowledgment(self, messages: list) -> bool:
        """Check if solution has been acknowledged"""
        if len(messages) < 2:
            return False
        
        last_message = messages[-1].get("content", "").lower()
        acknowledgment_phrases = [
            "thank you",
            "thanks",
            "that's correct",
            "perfect",
            "great",
            "understood",
            "i see",
            "makes sense"
        ]
        
        return any(phrase in last_message for phrase in acknowledgment_phrases)
    
    def should_terminate(self, message: Dict[str, Any], messages: list) -> bool:
        """Main termination check"""
        # Check explicit termination message
        if self.is_termination_msg(message):
            print("🛑 Termination: Explicit termination message found")
            return True
        
        # Check max rounds
        if self.check_max_rounds():
            print(f"🛑 Termination: Maximum rounds ({self.max_rounds}) reached")
            return True
        
        # Check if problem is solved
        if self.check_problem_solved(messages):
            print("🛑 Termination: Problem appears to be solved")
            return True
        
        return False
    
    def reset(self):
        """Reset termination handler"""
        self.round_count = 0
    
    def get_termination_function(self):
        """Get termination function for AutoGen"""
        def termination_func(message: Dict[str, Any]) -> bool:
            # Simple termination check for AutoGen
            content = message.get("content", "")
            return self.termination_msg in content
        
        return termination_func

class ConversationMonitor:
    """Monitor conversation quality and progress"""
    
    def __init__(self):
        self.turn_count = 0
        self.agent_contributions = {}
        self.topics_discussed = set()
        self.questions_asked = []
        self.answers_provided = []
    
    def update(self, message: Dict[str, Any]):
        """Update monitoring statistics"""
        self.turn_count += 1
        
        # Track agent contributions
        agent_name = message.get("name", "Unknown")
        if agent_name not in self.agent_contributions:
            self.agent_contributions[agent_name] = 0
        self.agent_contributions[agent_name] += 1
        
        # Extract topics (simplified)
        content = message.get("content", "")
        self._extract_topics(content)
        
        # Track questions and answers
        if "?" in content:
            self.questions_asked.append({
                "turn": self.turn_count,
                "agent": agent_name,
                "question": content[:100]  # First 100 chars
            })
        elif any(keyword in content.lower() for keyword in ["answer", "solution", "result"]):
            self.answers_provided.append({
                "turn": self.turn_count,
                "agent": agent_name,
                "answer": content[:100]
            })
    
    def _extract_topics(self, content: str):
        """Extract topics from content"""
        # Simplified topic extraction
        topic_keywords = {
            "mathematics": ["math", "equation", "algebra", "calculus"],
            "physics": ["physics", "force", "energy", "momentum"],
            "chemistry": ["chemistry", "reaction", "element", "compound"],
            "biology": ["biology", "cell", "dna", "evolution"],
            "programming": ["code", "algorithm", "programming", "function"],
            "literature": ["essay", "poem", "writing", "analysis"],
            "english": ["grammar", "vocabulary", "pronunciation"]
        }
        
        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                self.topics_discussed.add(topic)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            "total_turns": self.turn_count,
            "agent_contributions": self.agent_contributions,
            "topics_discussed": list(self.topics_discussed),
            "questions_count": len(self.questions_asked),
            "answers_count": len(self.answers_provided),
            "participation_rate": self._calculate_participation_rate()
        }
    
    def _calculate_participation_rate(self) -> Dict[str, float]:
        """Calculate participation rate for each agent"""
        if self.turn_count == 0:
            return {}
        
        rates = {}
        for agent, count in self.agent_contributions.items():
            rates[agent] = round(count / self.turn_count * 100, 2)
        
        return rates
