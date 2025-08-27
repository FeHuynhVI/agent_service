"""Create groups of conversational agents and run demo chats."""

from .agent_base import (
    initiate_group_chat,
    ContextVariables,
    AutoPattern,
    ConversableAgent,
    AssistantAgent,
    LLMConfig,
    logger,
)
from .prompts import (
    build_subject_system_message,
    INFO_AGENT_PROMPT,
    GROUP_CHAT_MANAGER_PROMPT,
)
from .personalization import make_personalization_updater, chain_updaters


def create_team(model: str = "gpt-oss-120b", temperature: float = 0.2):
    """Trả về (agents_list, user_agent, group_manager_args, context_variables)."""

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
            personalizer = make_personalization_updater(agent, context)
            updater_callable = chain_updaters(personalizer)
            setattr(agent, "update_agent_state_before_reply", updater_callable)

        # User agent đại diện cho học sinh
        user_agent = ConversableAgent(
            name="student",
            human_input_mode="NEVER",
            system_message="You are a student asking questions.",
        )

    group_manager_args = {
        "llm_config": llm_config,
        "system_message": GROUP_CHAT_MANAGER_PROMPT,
    }

    return all_agents, user_agent, group_manager_args, context

__all__ = ["create_team"]