"""
Endpoints enabling chat between a user and the team of agents with improved error handling.
"""

import logging
from typing import List, Callable, Dict, Any

# ----------------------------------
# Logging
# ----------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# AG2 và AutoGen là alias; thử import từ ag2 trước, nếu không có thì fallback sang autogen.
try:
    from ag2.agentchat import initiate_group_chat
    from ag2.agentchat.group import ContextVariables
    from ag2.agentchat.group.patterns import AutoPattern
    from ag2 import ConversableAgent, AssistantAgent, LLMConfig, UpdateSystemMessage
    USING_AG2 = True
except ImportError:
    from autogen.agentchat import initiate_group_chat
    from autogen.agentchat.group import ContextVariables
    from autogen.agentchat.group.patterns import AutoPattern
    from autogen import ConversableAgent, AssistantAgent, LLMConfig, UpdateSystemMessage
    USING_AG2 = False

# -----------------------------
#  Prompts (dựa theo dữ kiện bạn cung cấp)
# -----------------------------
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

Use clear and simple language when appropriate, and define linguistic
terms. Adapt explanations to the learner's background and needs.
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
When you've completed explaining a concept or solving a problem, end with "TERMINATE" if the query is fully addressed.
"""

INFO_AGENT_PROMPT = """
You are an Information Retrieval Agent responsible for:
1) Fetching syllabi/curricula and learning materials (documents, audio, video)
2) Providing practice questions and quizzes
3) Organizing resources by topic and difficulty
4) Managing references with metadata (difficulty, duration, prerequisites)
Work cooperatively with subject experts. Avoid giving away full graded answers; prefer hints and scaffolding. End with "TERMINATE" when done.
"""

GROUP_CHAT_MANAGER_PROMPT = """
You are the Group Chat Manager for an educational assistant.

Responsibilities:
1) Select the most appropriate expert for each turn
2) Keep flow smooth, avoid loops, summarize when needed
3) Terminate when the student's need is fully addressed

Selection rules:
- Math → Math_Expert
- Physics → Physics_Expert
- Chemistry → Chemistry_Expert
- Biology → Biology_Expert
- Programming/CS → CS_Expert
- Literature/Writing → Literature_Expert
- English language (IELTS/TOEFL/grammar/pronunciation) → English_Expert
- Requests for materials/resources/quizzes → Info_Agent

Use agent `description` first; fall back to system_message if needed. Prefer concise, step-by-step pedagogy and Vietnamese output if the user writes in Vietnamese.
"""

# -----------------------------
#  Helper: sinh system_message cho từng môn
# -----------------------------
def build_subject_system_message(subject: str, expertise: List[str], extra_key: str) -> str:
    expertise_list = ", ".join(expertise)
    return SUBJECT_EXPERT_PROMPT_TEMPLATE.format(
        subject=subject, expertise_list=expertise_list, additional=EXPERT_PROMPTS[extra_key]
    )

# -----------------------------
#  Utilities for safe system_message handling
# -----------------------------
def _get_system_message_text(system_message) -> str:
    if isinstance(system_message, str):
        return system_message
    for attr in ("content", "text", "message", "value"):
        if hasattr(system_message, attr):
            val = getattr(system_message, attr)
            if isinstance(val, str):
                return val
    return str(system_message)

def _set_system_message_text(agent, new_text: str) -> None:
    """
    Cập nhật system_message cho nhiều biến thể ag2/autogen:
    1) Nếu có method chính thống: agent.update_system_message(...)
    2) Nếu có trường nội bộ: agent._system_message = ...
    3) Nếu object system_message có field 'content': sửa tại chỗ
    4) Nếu tất cả đều thất bại: log cảnh báo và bỏ qua
    """
    # 1) API chính thống (tùy phiên bản)
    if hasattr(agent, "update_system_message"):
        try:
            # nhiều bản nhận string trực tiếp
            agent.update_system_message(new_text)
            return
        except TypeError:
            pass
        try:
            # một số bản yêu cầu wrapper UpdateSystemMessage
            try:
                _ = UpdateSystemMessage  # xác nhận import ok
            except NameError:
                _ = None
            if _ is not None:
                agent.update_system_message(UpdateSystemMessage(content=new_text)) # type: ignore
                return
        except Exception:
            pass

    # 2) Trường nội bộ phổ biến
    if hasattr(agent, "_system_message"):
        try:
            agent._system_message = new_text
            return
        except Exception:
            pass

    # 3) Sửa tại chỗ nội dung của system_message nếu có 'content'
    sm = getattr(agent, "system_message", None)
    try:
        if hasattr(sm, "content"):
            sm.content = new_text # type: ignore
            return
    except Exception:
        pass

    # 4) Bất khả thi -> cảnh báo (không raise để hook tiếp tục chạy an toàn)
    logger.warning("Could not set system_message on %s; skipping update.", getattr(agent, "name", "agent"))

# -----------------------------
#  Create personalization updater (messages-only signature)
# -----------------------------
def make_personalization_updater(agent, context_variables):
    def update_with_context(messages):
        context_data = context_variables.data
        personalization_msg = (
            f"Always respond in {context_data.get('language', 'vi')}. "
            f"Student level: {context_data.get('student_level', 'HS phổ thông')}. "
            f"Curriculum: {context_data.get('curriculum', 'VN K-12')}. "
            f"Goals: {context_data.get('goals', 'Hiểu sâu khái niệm và làm bài tập có hướng dẫn')}."
        )
        current = _get_system_message_text(getattr(agent, "system_message", ""))
        if not current.endswith(personalization_msg):
            new_text = (current + "\n\n" + personalization_msg).strip()
            _set_system_message_text(agent, new_text)  # ✅ dùng helper an toàn
        logger.debug("Ran personalization updater for %s", getattr(agent, "name", "agent"))
    return update_with_context

# Optional: chain multiple updaters while keeping (messages)->None signature
def chain_updaters(*funcs: Callable[[List[Dict[str, Any]]], None]) -> Callable[[List[Dict[str, Any]]], None]:
    def _runner(messages: List[Dict[str, Any]]) -> None:
        for f in funcs:
            f(messages)
    return _runner

# -----------------------------
#  Tạo đội tác tử
# -----------------------------
def create_team(model: str = "gpt-oss-120b", temperature: float = 0.2):
    """
    Trả về (agents_list, user_agent, group_manager_args, context_variables)
    """
    
    llm_config = {
        "config_list": [{"model": model, "api_key": "sk-SGFmxZPAP8mk5P-aEm3v9Q", "base_url": "https://mkp-api.fptcloud.com"}], 
        "temperature": temperature
    }
    
    llm_config = LLMConfig(config_list=llm_config["config_list"], temperature=llm_config["temperature"])

    context = ContextVariables(
        data={
            "language": "vi",
            "student_level": "HS phổ thông",
            "curriculum": "VN K-12",
            "goals": "Hiểu sâu khái niệm và làm bài tập có hướng dẫn",
        }
    )

    with llm_config:
        # Info agent
        info_agent = AssistantAgent(
            name="Info_Agent",
            system_message=INFO_AGENT_PROMPT,
            human_input_mode="NEVER",
        )
        info_agent.description = "Curates curricula and learning materials; generates practice questions; routes resources."

        # Subject experts
        cs_expert = AssistantAgent(
            name="CS_Expert",
            system_message=build_subject_system_message(
                "Computer Science",
                [
                    "Programming (Python, Java, C++, JavaScript)",
                    "Data Structures (Arrays, Trees, Graphs, Hash Tables)",
                    "Algorithms (Sorting, Searching, Dynamic Programming)",
                    "Software Engineering (Design Patterns, Testing, Agile)",
                    "Databases (SQL, NoSQL, Design)",
                    "Operating Systems",
                    "Computer Networks",
                    "AI/ML",
                    "Web Development",
                ],
                "CS_Expert",
            ),
            human_input_mode="NEVER",
        )
        cs_expert.description = "Answers programming/CS questions; writes & debugs code; algorithms; systems; databases; networks."

        math_expert = AssistantAgent(
            name="Math_Expert",
            system_message=build_subject_system_message(
                "Mathematics",
                ["Algebra", "Geometry", "Calculus", "Statistics", "Linear Algebra"],
                "Math_Expert",
            ),
            human_input_mode="NEVER",
        )
        math_expert.description = "Solves math problems step-by-step; proofs; functions; calculus; statistics."

        eng_expert = AssistantAgent(
            name="English_Expert",
            system_message=build_subject_system_message(
                "English Language",
                ["Grammar", "Vocabulary", "Pronunciation", "IELTS/TOEFL", "Writing/Listening/Speaking"],
                "English_Expert",
            ),
            human_input_mode="NEVER",
        )
        eng_expert.description = "English language instruction: grammar, IELTS/TOEFL, pronunciation, writing feedback."

        bio_expert = AssistantAgent(
            name="Biology_Expert",
            system_message=build_subject_system_message(
                "Biology",
                ["Cell biology", "Genetics", "Ecology", "Evolution", "Physiology"],
                "Biology_Expert",
            ),
            human_input_mode="NEVER",
        )
        bio_expert.description = "Explains biology: cells, genetics, ecology, evolution; clear analogies."

        phy_expert = AssistantAgent(
            name="Physics_Expert",
            system_message=build_subject_system_message(
                "Physics",
                ["Mechanics", "Electricity & Magnetism", "Waves", "Thermodynamics", "Modern Physics"],
                "Physics_Expert",
            ),
            human_input_mode="NEVER",
        )
        phy_expert.description = "Solves physics problems; diagrams; derivations; unit analysis; conceptual clarity."

        chem_expert = AssistantAgent(
            name="Chemistry_Expert",
            system_message=build_subject_system_message(
                "Chemistry",
                ["Stoichiometry", "Thermochemistry", "Equilibrium", "Organic", "Inorganic", "Spectroscopy"],
                "Chemistry_Expert",
            ),
            human_input_mode="NEVER",
        )
        chem_expert.description = "Chemistry problem solving: equations, mechanisms, yields, structures, spectroscopic reasoning."

        lit_expert = AssistantAgent(
            name="Literature_Expert",
            system_message=build_subject_system_message(
                "Literature",
                ["Close reading", "Themes/Motifs", "Comparative analysis", "Essay guidance", "Literary devices"],
                "Literature_Expert",
            ),
            human_input_mode="NEVER",
        )
        lit_expert.description = "Analyzes literature; historical context; writing guidance; literary devices."

        # Create and assign per-agent updater with correct signature
        all_agents = [
            info_agent,
            cs_expert,
            math_expert,
            eng_expert,
            bio_expert,
            phy_expert,
            chem_expert,
            lit_expert,
        ]
        for agent in all_agents:
            personalizer = make_personalization_updater(agent, context)  # (messages)->None
            updater_callable = chain_updaters(personalizer)              # still (messages)->None
            # Use setattr to avoid Pylance "cannot assign attribute" warning
            setattr(agent, "update_agent_state_before_reply", updater_callable)

        # User agent đại diện cho học sinh
        user_agent = ConversableAgent(
            name="student",
            human_input_mode="ALWAYS",
            system_message="You are a student asking questions.",
        )

    group_manager_args = {
        "llm_config": llm_config,
        "system_message": GROUP_CHAT_MANAGER_PROMPT,
    }

    return all_agents, user_agent, group_manager_args, context

def run_demo():
    agents, user, group_manager_args, context = create_team()

    initial_agent = next(a for a in agents if a.name == "Info_Agent")

    pattern = AutoPattern(
        initial_agent=initial_agent,
        agents=agents,  # type: ignore
        user_agent=user,
        group_manager_args=group_manager_args,
        context_variables=context,
    )

    messages = (
        "Cô/chú ơi, giúp em 2 việc: (1) giải phương trình bậc hai 2x^2 - 3x - 2 = 0 "
        "và (2) gợi ý cho em vài bài luyện đọc tiếng Anh về chủ đề môi trường."
    )

    result, ctx, last_agent = initiate_group_chat(
        pattern=pattern,
        messages=messages,
        max_rounds=8,
    )

    print("\n===== KẾT QUẢ CUỐI CÙNG =====")
    print(result)

if __name__ == "__main__":
    run_demo()
