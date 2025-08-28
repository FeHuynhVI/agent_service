"""Create groups of conversational agents and run demo chats."""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Any, cast

from .agent_base import (
    ContextVariables,
    ConversableAgent,
    AssistantAgent,
    LLMConfig,
)
from .prompts import (
    build_subject_system_message,
    INFO_AGENT_PROMPT,
    GROUP_CHAT_MANAGER_PROMPT,
)
from .personalization import make_personalization_updater, chain_updaters


DEFAULT_CONTEXT: Dict[str, str] = {
    "language": "vi",
    "student_level": "HS phổ thông",
    "curriculum": "VN K-12",
    "goals": "Hiểu sâu khái niệm và làm bài tập có hướng dẫn",
}

from dotenv import load_dotenv

load_dotenv()

def _make_expert_agent(
    name: str,
    subject: str,
    expertise: List[str],
    description: str,
    **_: object,
) -> AssistantAgent:
    """Build a subject expert agent with common defaults.

    Extra keyword arguments are ignored so ``EXPERT_DEFINITIONS`` can contain
    additional configuration without needing to update this helper. This makes
    the agent creation logic more flexible and extensible.
    """

    agent = AssistantAgent(
        name=name,
        system_message=build_subject_system_message(subject, expertise, name),
        human_input_mode="NEVER",
    )
    agent.description = description
    return agent


EXPERT_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "CS_Expert",
        "subject": "Computer Science",
        "expertise": [
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
        "description": (
            "Answers programming/CS questions; writes & debugs code; algorithms; systems; "
            "databases; networks."
        ),
        "keywords": [
            "programming",
            "code",
            "algorithm",
            "data structure",
            "software",
            "python",
            "java",
            "javascript",
            "database",
            "network",
            "computer",
            "lập trình",
            "thuật toán",
            "cơ sở dữ liệu",
        ],
    },
    {
        "name": "Math_Expert",
        "subject": "Mathematics",
        "expertise": ["Algebra", "Geometry", "Calculus", "Statistics", "Linear Algebra"],
        "description": (
            "Solves math problems step-by-step; proofs; functions; calculus; statistics."
        ),
        "keywords": [
            "math",
            "mathematics",
            "algebra",
            "geometry",
            "calculus",
            "statistics",
            "equation",
            "formula",
            "derivative",
            "integral",
            "probability",
            "solve",
            "calculate",
            "compute",
            "tính",
            "toán",
            "phương trình",
        ],
    },
    {
        "name": "English_Expert",
        "subject": "English Language",
        "expertise": [
            "Grammar",
            "Vocabulary",
            "Pronunciation",
            "IELTS/TOEFL",
            "Writing/Listening/Speaking",
        ],
        "description": (
            "English language instruction: grammar, IELTS/TOEFL, pronunciation, writing feedback."
        ),
        "keywords": [
            "english",
            "grammar",
            "vocabulary",
            "pronunciation",
            "ielts",
            "toefl",
            "writing",
            "speaking",
            "listening",
            "tiếng anh",
            "ngữ pháp",
        ],
    },
    {
        "name": "Biology_Expert",
        "subject": "Biology",
        "expertise": ["Cell biology", "Genetics", "Ecology", "Evolution", "Physiology"],
        "description": (
            "Explains biology: cells, genetics, ecology, evolution; clear analogies."
        ),
        "keywords": [
            "biology",
            "cell",
            "genetic",
            "dna",
            "evolution",
            "ecology",
            "organism",
            "protein",
            "enzyme",
            "photosynthesis",
            "sinh học",
            "tế bào",
            "gen",
            "tiến hóa",
        ],
    },
    {
        "name": "Physics_Expert",
        "subject": "Physics",
        "expertise": [
            "Mechanics",
            "Electricity & Magnetism",
            "Waves",
            "Thermodynamics",
            "Modern Physics",
        ],
        "description": (
            "Solves physics problems; diagrams; derivations; unit analysis; conceptual clarity."
        ),
        "keywords": [
            "physics",
            "force",
            "energy",
            "momentum",
            "acceleration",
            "velocity",
            "electric",
            "magnetic",
            "wave",
            "thermodynamics",
            "quantum",
            "vật lý",
            "lực",
            "năng lượng",
            "gia tốc",
            "vận tốc",
        ],
    },
    {
        "name": "Chemistry_Expert",
        "subject": "Chemistry",
        "expertise": [
            "Stoichiometry",
            "Thermochemistry",
            "Equilibrium",
            "Organic",
            "Inorganic",
            "Spectroscopy",
        ],
        "description": (
            "Chemistry problem solving: equations, mechanisms, yields, structures, "
            "spectroscopic reasoning."
        ),
        "keywords": [
            "chemistry",
            "chemical",
            "reaction",
            "molecule",
            "atom",
            "bond",
            "organic",
            "inorganic",
            "stoichiometry",
            "equilibrium",
            "hóa học",
            "phản ứng",
            "phân tử",
            "nguyên tử",
        ],
    },
    {
        "name": "Literature_Expert",
        "subject": "Literature",
        "expertise": [
            "Close reading",
            "Themes/Motifs",
            "Comparative analysis",
            "Essay guidance",
            "Literary devices",
        ],
        "description": (
            "Analyzes literature; historical context; writing guidance; literary devices."
        ),
        "keywords": [
            "literature",
            "poem",
            "novel",
            "story",
            "author",
            "character",
            "theme",
            "analysis",
            "văn học",
            "thơ",
            "tiểu thuyết",
        ],
    },
]

# Map agent names to keyword lists for flexible subject routing
AGENT_KEYWORDS: Dict[str, List[str]] = {
    cast(str, cfg["name"]): cast(List[str], cfg.get("keywords", []))
    for cfg in EXPERT_DEFINITIONS
}


def create_team(
    model: Optional[str] = None,
    temperature: float = 0.2,
    context_data: Optional[Dict[str, str]] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
):
    """Return (agents_list, user_agent, group_manager_args, context_variables)."""

    model = model or os.getenv("LLM_BASE_MODEL", "gpt-oss-120b")
    api_key = api_key or os.getenv("FCI_API_KEY", "")
    base_url = base_url or os.getenv(
        "LLM_BASE_URL", "https://mkp-api.fptcloud.com"
    )

    llm_config = LLMConfig(
        config_list=[{"model": model, "api_key": api_key, "base_url": base_url}],
        temperature=temperature,
    )

    context_values = {**DEFAULT_CONTEXT, **(context_data or {})}
    context = ContextVariables(data=context_values)

    with llm_config:
        info_agent = AssistantAgent(
            name="Info_Agent",
            system_message=INFO_AGENT_PROMPT,
            human_input_mode="NEVER",
        )
        info_agent.description = (
            "Curates curricula and learning materials; generates practice questions; "
            "routes resources."
        )

        subject_agents = [
            _make_expert_agent(
                name=cast(str, cfg["name"]),
                subject=cast(str, cfg["subject"]),
                expertise=cast(List[str], cfg["expertise"]),
                description=cast(str, cfg["description"]),
            )
            for cfg in EXPERT_DEFINITIONS
        ]

        all_agents = [info_agent, *subject_agents]

        def is_termination_msg(msg: dict) -> bool:
            content = msg.get("content")
            return isinstance(content, str) and content.rstrip().endswith("TERMINATE")

        for agent in all_agents:
            personalizer = make_personalization_updater(agent, context)
            updater_callable = chain_updaters(personalizer)
            setattr(agent, "update_agent_state_before_reply", updater_callable)
            setattr(agent, "_is_termination_msg", is_termination_msg)

        user_agent = ConversableAgent(
            name="student",
            human_input_mode="NEVER",
            system_message="You are a student asking questions.",
        )
        setattr(user_agent, "_is_termination_msg", is_termination_msg)

    group_manager_args = {
        "llm_config": llm_config,
        "system_message": GROUP_CHAT_MANAGER_PROMPT,
    }

    return all_agents, user_agent, group_manager_args, context


__all__ = ["create_team", "AGENT_KEYWORDS"]

