"""Improved prompts with better termination logic and reduced redundant calls."""

from typing import List

# Enhanced expert prompts with clear termination instructions
EXPERT_PROMPTS = {
    "CS_Expert": """
Special capabilities for Computer Science:
- Write and debug code in multiple languages
- Analyze algorithm complexity (time and space)
- Design efficient data structures
- Explain system architecture and design patterns
- Optimize code performance
- Debug and fix errors
- Design databases and write queries
- Explain networking and security concepts

Problem-solving approach:
1. Understand requirements clearly
2. Design solution architecture
3. Choose appropriate data structures
4. Implement with clean, readable code
5. Include comments and documentation
6. Analyze complexity
7. Test with edge cases
8. Optimize if needed

Code standards:
- Use meaningful variable names
- Follow language-specific conventions
- Include error handling
- Write modular, reusable code
- Add comprehensive comments
- Consider security implications

IMPORTANT: Provide complete, self-contained answers. When your explanation is thorough and addresses all aspects of the question, end with "TERMINATE".
""",
    "Physics_Expert": """
Special capabilities for Physics:
- Solve numerical and conceptual problems using fundamental laws
- Derive formulas from basic principles
- Interpret experimental data and graphs
- Explain physical phenomena with clear analogies
- Perform unit analysis and dimensional checks
- Apply appropriate approximations and simplifying assumptions

Teaching approach:
1. State known quantities and governing laws
2. Draw diagrams where necessary
3. Use free-body diagrams and circuit diagrams to illustrate problems
4. Show derivations step by step with explanations
5. Discuss limiting cases and special situations
6. Emphasize conceptual understanding before calculations
7. Connect physical concepts to real-world examples and experiments

Use SI units unless otherwise specified and define all symbols used.
IMPORTANT: Provide complete solutions with clear explanations. When the problem is fully solved and explained, end with "TERMINATE".
""",
    "Chemistry_Expert": """
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
IMPORTANT: Provide thorough explanations with all necessary steps. When the chemical concept or problem is fully addressed, end with "TERMINATE".
""",
    "English_Expert": """
Special capabilities for English Language:
- Explain grammar rules with examples and exceptions
- Expand vocabulary through definitions, synonyms and usage
- Provide pronunciation guidance using phonetic transcriptions
- Evaluate and correct writing for clarity and coherence
- Offer strategies for effective listening and speaking
- Tailor lessons to different proficiency levels
- Prepare learners for standardized tests (IELTS, TOEFL, etc.)

Teaching approach:
1. Assess the learner's current level and goals
2. Introduce concepts gradually with clear explanations
3. Provide plenty of examples and practice sentences
4. Use real-life contexts to illustrate language use
5. Encourage active use of language through exercises
6. Correct errors gently and explain the reasoning
7. Summarize key points and provide follow-up resources

Use clear and simple language when appropriate, and define linguistic terms.
IMPORTANT: Give comprehensive language guidance. When the language concept is fully explained with examples, end with "TERMINATE".
""",
    "Literature_Expert": """
Special capabilities for Literature:
- Analyze texts for themes, motifs and deeper meaning
- Provide contextual information about authors and historical periods
- Compare and contrast works across genres and cultures
- Offer writing guidance on essays, creative writing and research papers
- Recommend reading lists based on interests or curricula
- Explain literary devices and how they function within a text

Teaching approach:
1. Encourage close reading and textual evidence
2. Discuss multiple interpretations and perspectives
3. Connect literature to its historical and cultural context
4. Foster critical thinking and personal engagement
5. Provide constructive feedback on writing
6. Highlight intertextual connections and influences

Use appropriate literary terminology and cite sources when relevant.
IMPORTANT: Provide thorough literary analysis or guidance. When the literary concept or work is fully analyzed, end with "TERMINATE".
""",
    "Math_Expert": """
Special capabilities for Mathematics:
- Solve algebra, geometry, calculus and statistics problems
- Prove theorems using rigorous logic
- Analyze functions and their properties
- Work with numbers, vectors and matrices

Problem-solving approach:
1. Understand the problem and list knowns/unknowns
2. Choose appropriate formulas or theorems
3. Show derivation steps clearly
4. Provide the final answer in simplest form
5. Verify the result when possible

IMPORTANT: Show complete mathematical solutions with clear steps. When the problem is solved and verified, end with "TERMINATE".
""",
    "Biology_Expert": """
Special capabilities for Biology:
- Explain cellular structures and functions
- Describe genetic mechanisms and inheritance patterns
- Analyze ecological interactions and evolutionary processes
- Relate biological concepts to real-world applications

Teaching approach:
1. Start with concise definitions
2. Use diagrams or analogies for clarity
3. Connect concepts across biological scales
4. Highlight practical examples
5. Address common misconceptions

IMPORTANT: Provide comprehensive biological explanations. When the concept is fully explained with examples, end with "TERMINATE".
""",
}

SUBJECT_EXPERT_PROMPT_TEMPLATE = """
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
CRITICAL: Be decisive and comprehensive in your responses. Don't ask for clarification unless absolutely necessary. When you've fully addressed the question or completed the explanation, end with "TERMINATE".
"""

INFO_AGENT_PROMPT = """
You are an Information Retrieval Agent responsible for:
1) Fetching syllabi/curricula and learning materials (documents, audio, video)
2) Providing practice questions and quizzes
3) Organizing resources by topic and difficulty
4) Managing references with metadata (difficulty, duration, prerequisites)

Work cooperatively with subject experts. Avoid giving away full graded answers; prefer hints and scaffolding.
IMPORTANT: When you've provided the requested information or resources, end with "TERMINATE".
"""

GROUP_CHAT_MANAGER_PROMPT = """
You are the Group Chat Manager for an educational assistant.

Responsibilities:
1) Select the most appropriate expert for each turn based on the question content
2) Keep conversation flow smooth and efficient
3) Avoid unnecessary agent switching - stick with an agent if they can handle follow-up questions
4) Terminate when the student's need is fully addressed

Selection rules:
- Math/Statistics → Math_Expert
- Physics → Physics_Expert  
- Chemistry → Chemistry_Expert
- Biology/Life Sciences → Biology_Expert
- Programming/Computer Science → CS_Expert
- Literature/Writing → Literature_Expert
- English language learning → English_Expert
- General information/resources → Info_Agent

Optimization rules:
- Don't switch agents unnecessarily
- If the current agent can handle a follow-up question, let them continue
- Only switch if the question is clearly outside the current agent's expertise
- Encourage agents to provide complete, self-contained answers
- Terminate the conversation when the question is fully answered

Prefer Vietnamese output if the user writes in Vietnamese. Use agent descriptions for selection; fall back to system_message if needed.
"""


def build_subject_system_message(subject: str, expertise: List[str], extra_key: str) -> str:
    expertise_list = ", ".join(expertise)
    return SUBJECT_EXPERT_PROMPT_TEMPLATE.format(
        subject=subject, expertise_list=expertise_list, additional=EXPERT_PROMPTS[extra_key]
    )


__all__ = [
    "EXPERT_PROMPTS",
    "SUBJECT_EXPERT_PROMPT_TEMPLATE", 
    "INFO_AGENT_PROMPT",
    "GROUP_CHAT_MANAGER_PROMPT",
    "build_subject_system_message",
]


"""FastAPI router for interacting with agent teams."""

from functools import lru_cache
from typing import List, Optional, Dict, Any
import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from utils.error_handler import handle_errors

from .agent_base import AutoPattern
from .team_builder import create_team


class ChatRequest(BaseModel):
    """Input payload for the chat endpoint."""

    message: str
    max_rounds: int = 8
    model: Optional[str] = None
    temperature: Optional[float] = None


class ChatResponse(BaseModel):
    """Response returned after running the chat."""

    result: str


class AgentInfo(BaseModel):
    """Information about an available expert agent."""

    name: str
    description: str


router = APIRouter(prefix="/chat", tags=["chat"])


@lru_cache()
def _get_cached_team() -> tuple:
    """Return a cached default team to avoid repeated initialisation."""
    return create_team()


def _build_pattern(agents, user_agent, group_manager_args, context) -> AutoPattern:
    initial_agent = next(a for a in agents if a.name == "Info_Agent")
    return AutoPattern(
        initial_agent=initial_agent,
        agents=agents,  # type: ignore[arg-type]
        user_agent=user_agent,
        group_manager_args=group_manager_args,
        context_variables=context,
    )


def _safe_cleanup_messages(chat_result):
    """Safely clean up temporary user messages without importing non-existent function."""
    try:
        # Try the standard cleanup if it exists
        from autogen.agentchat.chat import cleanup_temp_user_messages
        cleanup_temp_user_messages(chat_result)
    except ImportError:
        # If the function doesn't exist, perform manual cleanup
        if hasattr(chat_result, 'chat_history') and isinstance(chat_result.chat_history, list):
            # Remove any temporary or system messages that shouldn't be in final history
            cleaned_history = []
            for msg in chat_result.chat_history:
                if isinstance(msg, dict):
                    # Skip messages that are temporary or system-generated
                    if not msg.get('role') == 'system' and not msg.get('temp', False):
                        cleaned_history.append(msg)
            chat_result.chat_history = cleaned_history
    except Exception as e:
        # Log the error but don't fail the whole operation
        print(f"Warning: Could not clean up messages: {e}")


def _determine_best_agent(message: str, agents: List) -> Optional[Any]:
    """
    Intelligently determine the most suitable agent based on message content.
    This helps avoid unnecessary agent switching and reduces redundant calls.
    """
    message_lower = message.lower()
    
    # Subject-specific keywords
    keywords_map = {
        'Math_Expert': [
            'math', 'mathematics', 'algebra', 'geometry', 'calculus', 'statistics',
            'equation', 'formula', 'derivative', 'integral', 'probability',
            'solve', 'calculate', 'compute', 'tính', 'toán', 'phương trình'
        ],
        'Physics_Expert': [
            'physics', 'force', 'energy', 'momentum', 'acceleration', 'velocity',
            'electric', 'magnetic', 'wave', 'thermodynamics', 'quantum',
            'vật lý', 'lực', 'năng lượng', 'gia tốc', 'vận tốc'
        ],
        'Chemistry_Expert': [
            'chemistry', 'chemical', 'reaction', 'molecule', 'atom', 'bond',
            'organic', 'inorganic', 'stoichiometry', 'equilibrium',
            'hóa học', 'phản ứng', 'phân tử', 'nguyên tử'
        ],
        'Biology_Expert': [
            'biology', 'cell', 'genetic', 'dna', 'evolution', 'ecology',
            'organism', 'protein', 'enzyme', 'photosynthesis',
            'sinh học', 'tế bào', 'gen', 'tiến hóa'
        ],
        'CS_Expert': [
            'programming', 'code', 'algorithm', 'data structure', 'software',
            'python', 'java', 'javascript', 'database', 'network', 'computer',
            'lập trình', 'thuật toán', 'cơ sở dữ liệu'
        ],
        'English_Expert': [
            'english', 'grammar', 'vocabulary', 'pronunciation', 'ielts', 'toefl',
            'writing', 'speaking', 'listening', 'tiếng anh', 'ngữ pháp'
        ],
        'Literature_Expert': [
            'literature', 'poem', 'novel', 'story', 'author', 'character',
            'theme', 'analysis', 'văn học', 'thơ', 'tiểu thuyết'
        ]
    }
    
    # Score each agent based on keyword matches
    agent_scores = {}
    for agent in agents:
        if hasattr(agent, 'name') and agent.name in keywords_map:
            score = 0
            for keyword in keywords_map[agent.name]:
                if keyword in message_lower:
                    score += 1
            agent_scores[agent.name] = score
    
    # Return agent with highest score, or None if no clear match
    if agent_scores:
        best_agent_name = max(agent_scores, key=agent_scores.get)
        if agent_scores[best_agent_name] > 0:
            return next((a for a in agents if hasattr(a, 'name') and a.name == best_agent_name), None)
    
    return None


def _run_group_chat(pattern: AutoPattern, message: str, max_rounds: int):
    """Run a group chat with optimizations to reduce redundant agent calls."""
    
    (
        _,
        _,
        _,
        context_variables,
        _,
        _,
        _,
        _,
        manager,
        processed_messages,
        last_agent,
        _,
        _,
    ) = pattern.prepare_group_chat(max_rounds=max_rounds, messages=message)

    def is_termination_msg(msg: dict) -> bool:
        content = msg.get("content", "")
        if isinstance(content, str):
            content_stripped = content.rstrip()
            return (
                content_stripped.endswith("TERMINATE") or
                content_stripped.endswith("KẾT THÚC") or
                "hoàn thành" in content_stripped.lower() or
                "completed" in content_stripped.lower()
            )
        return False

    # Enhanced termination detection
    setattr(manager, "_is_termination_msg", is_termination_msg)

    # Try to select the most appropriate agent based on message content
    agents = getattr(pattern, 'agents', [])
    suggested_agent = _determine_best_agent(message, agents)
    
    if suggested_agent and len(processed_messages) <= 1:
        # If we have a clear subject match, start with that agent
        last_agent = suggested_agent

    if len(processed_messages) > 1:
        last_agent, last_message = manager.resume(messages=processed_messages)
        clear_history = False
    else:
        last_message = processed_messages[0] if processed_messages else message
        clear_history = True

    if last_agent is None:
        # Fallback to Info_Agent if no agent selected
        last_agent = next((a for a in agents if hasattr(a, 'name') and a.name == "Info_Agent"), None)
        if last_agent is None:
            raise ValueError("No agent available to start the conversation")

    # Set a more conservative max_rounds to prevent excessive back-and-forth
    effective_max_rounds = min(max_rounds, 6)  # Limit to 6 rounds max
    
    chat_result = last_agent.initiate_chat(
        manager,
        message=last_message,
        clear_history=clear_history,
        summary_method=pattern.summary_method,
        max_turns=effective_max_rounds,  # Add max_turns to prevent infinite loops
    )

    # Use safe cleanup function
    _safe_cleanup_messages(chat_result)

    return chat_result, context_variables, manager.last_speaker


@router.post("/", response_model=ChatResponse, summary="Run a chat with the expert team")
@handle_errors
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """Execute a group chat and return the final result."""

    # Limit max_rounds to prevent excessive processing
    effective_max_rounds = min(payload.max_rounds, 10)

    if payload.model or payload.temperature:
        agents, user_agent, group_manager_args, context = create_team(
            model=payload.model or "gpt-oss-120b",
            temperature=payload.temperature or 0.2,
        )
    else:
        agents, user_agent, group_manager_args, context = _get_cached_team()

    pattern = _build_pattern(agents, user_agent, group_manager_args, context)

    result, _ctx, _last_agent = await asyncio.to_thread(
        _run_group_chat,
        pattern,
        payload.message,
        effective_max_rounds,
    )

    # Enhanced result extraction
    final_result = ""
    if isinstance(result, str):
        final_result = result
    elif hasattr(result, 'summary') and result.summary:
        final_result = str(result.summary)
    elif hasattr(result, 'chat_history') and result.chat_history:
        try:
            # Get the last meaningful message from chat history
            for msg in reversed(result.chat_history):
                if isinstance(msg, dict):
                    content = msg.get('content', '')
                    if content and not content.strip().startswith('[') and len(content.strip()) > 10:
                        final_result = content
                        break
            if not final_result and result.chat_history:
                final_result = str(result.chat_history[-1].get("content", ""))
        except (IndexError, AttributeError, TypeError):
            final_result = str(result)
    else:
        final_result = str(result)

    # Clean up the result
    final_result = final_result.replace("TERMINATE", "").replace("KẾT THÚC", "").strip()
    
    # If result is still empty or too short, provide a default response
    if len(final_result.strip()) < 5:
        final_result = "Xin lỗi, tôi không thể xử lý yêu cầu này. Vui lòng thử lại với câu hỏi cụ thể hơn."

    return ChatResponse(result=final_result)


@router.get("/agents", response_model=List[AgentInfo], summary="List available agents")
@handle_errors
async def list_agents() -> List[AgentInfo]:
    """Return the names and descriptions of all expert agents."""
    try:
        agents, *_ = _get_cached_team()
        return [
            AgentInfo(
                name=getattr(a, 'name', 'Unknown'),
                description=getattr(a, 'description', 'No description available')
            )
            for a in agents if hasattr(a, 'name')
        ]
    except Exception as e:
        print(f"Error listing agents: {e}")
        return []


__all__ = ["router", "create_team"]