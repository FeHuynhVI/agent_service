"""
Information Agent for retrieving subject materials
"""
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base_agent import BaseAgent
from config.settings import settings

class InfoAgent(BaseAgent):
    """Agent for retrieving subject information and materials"""
    
    def __init__(self, data_path: Optional[Path] = None, **kwargs):
        self.data_path = data_path or settings.data_path
        
        system_message = """
You are an Information Retrieval Agent responsible for:
1. Fetching subject syllabi and curriculum information
2. Retrieving learning materials (documents, audio, video references)
3. Providing quiz questions and practice materials
4. Managing educational resources and references
5. Organizing content by topic and difficulty level

When asked for subject materials:
- List available resources clearly
- Provide relevant excerpts or summaries
- Suggest appropriate materials based on the query
- Organize information hierarchically
- Include metadata (difficulty, duration, prerequisites)

You work with subject experts to provide them with necessary materials.
"""
        super().__init__(
            name="Info_Agent",
            system_message=system_message,
            **kwargs
        )
        
        # Initialize data storage
        self.subject_data = self._load_subject_data()
    
    def _load_subject_data(self) -> Dict[str, Any]:
        """Load subject data from files"""
        subject_data = {}
        
        # Create data directories if they don't exist
        subjects = ["math", "physics", "chemistry", "biology", "cs", "literature", "english"]
        for subject in subjects:
            subject_path = self.data_path / subject
            subject_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing data files
            subject_data[subject] = self._load_subject_files(subject_path)
        
        return subject_data
    
    def _load_subject_files(self, subject_path: Path) -> Dict[str, Any]:
        """Load all files for a specific subject"""
        data = {
            "syllabus": None,
            "materials": [],
            "quizzes": [],
            "audio": [],
            "videos": [],
            "references": []
        }
        
        # Check for syllabus file
        syllabus_file = subject_path / "syllabus.json"
        if syllabus_file.exists():
            with open(syllabus_file, 'r', encoding='utf-8') as f:
                data["syllabus"] = json.load(f)
        
        # Load materials
        materials_dir = subject_path / "materials"
        if materials_dir.exists():
            for file in materials_dir.glob("*.json"):
                with open(file, 'r', encoding='utf-8') as f:
                    data["materials"].append(json.load(f))
        
        # Load quizzes
        quiz_dir = subject_path / "quizzes"
        if quiz_dir.exists():
            for file in quiz_dir.glob("*.json"):
                with open(file, 'r', encoding='utf-8') as f:
                    data["quizzes"].append(json.load(f))
        
        return data
    
    def get_syllabus(self, subject: str) -> Dict[str, Any]:
        """Get syllabus for a subject"""
        if subject in self.subject_data and self.subject_data[subject]["syllabus"]:
            return self.subject_data[subject]["syllabus"]
        
        # Return default syllabus structure
        return self._generate_default_syllabus(subject)
    
    def _generate_default_syllabus(self, subject: str) -> Dict[str, Any]:
        """Generate a default syllabus structure"""
        syllabi = {
            "math": {
                "subject": "Mathematics",
                "topics": [
                    {"name": "Algebra", "subtopics": ["Linear Equations", "Quadratic Equations", "Polynomials"]},
                    {"name": "Geometry", "subtopics": ["Triangles", "Circles", "Coordinate Geometry"]},
                    {"name": "Calculus", "subtopics": ["Limits", "Derivatives", "Integrals"]}
                ],
                "resources": ["Textbook: Advanced Mathematics", "Online: Khan Academy", "Practice: Problem Sets"]
            },
            "physics": {
                "subject": "Physics",
                "topics": [
                    {"name": "Mechanics", "subtopics": ["Kinematics", "Dynamics", "Energy"]},
                    {"name": "Electricity", "subtopics": ["Circuits", "Magnetism", "Electromagnetic Waves"]},
                    {"name": "Modern Physics", "subtopics": ["Quantum", "Relativity", "Nuclear"]}
                ],
                "resources": ["Textbook: University Physics", "Lab Manual", "Simulations: PhET"]
            },
            "chemistry": {
                "subject": "Chemistry",
                "topics": [
                    {"name": "General Chemistry", "subtopics": ["Atomic Structure", "Bonding", "Stoichiometry"]},
                    {"name": "Organic Chemistry", "subtopics": ["Hydrocarbons", "Functional Groups", "Reactions"]},
                    {"name": "Physical Chemistry", "subtopics": ["Thermodynamics", "Kinetics", "Equilibrium"]}
                ],
                "resources": ["Textbook: Chemistry Principles", "Lab Safety Guide", "Molecular Models"]
            },
            "biology": {
                "subject": "Biology",
                "topics": [
                    {"name": "Cell Biology", "subtopics": ["Cell Structure", "Metabolism", "Division"]},
                    {"name": "Genetics", "subtopics": ["DNA/RNA", "Inheritance", "Evolution"]},
                    {"name": "Ecology", "subtopics": ["Ecosystems", "Populations", "Conservation"]}
                ],
                "resources": ["Textbook: Biology Concepts", "Lab Protocols", "Field Guide"]
            },
            "cs": {
                "subject": "Computer Science",
                "topics": [
                    {"name": "Programming", "subtopics": ["Python", "Data Types", "Control Flow"]},
                    {"name": "Data Structures", "subtopics": ["Arrays", "Trees", "Graphs"]},
                    {"name": "Algorithms", "subtopics": ["Sorting", "Searching", "Dynamic Programming"]}
                ],
                "resources": ["Online: LeetCode", "Textbook: CLRS", "IDE: VS Code"]
            },
            "literature": {
                "subject": "Literature",
                "topics": [
                    {"name": "Literary Analysis", "subtopics": ["Themes", "Characters", "Symbolism"]},
                    {"name": "Writing", "subtopics": ["Essays", "Creative Writing", "Research Papers"]},
                    {"name": "Literary History", "subtopics": ["Periods", "Movements", "Authors"]}
                ],
                "resources": ["Anthology: World Literature", "Style Guide: MLA", "Writing Center"]
            },
            "english": {
                "subject": "English Language",
                "topics": [
                    {"name": "Grammar", "subtopics": ["Parts of Speech", "Tenses", "Sentence Structure"]},
                    {"name": "Vocabulary", "subtopics": ["Word Formation", "Idioms", "Academic Words"]},
                    {"name": "Skills", "subtopics": ["Reading", "Writing", "Speaking", "Listening"]}
                ],
                "resources": ["Grammar Book", "IELTS Preparation", "Language Apps"]
            }
        }
        
        return syllabi.get(subject, {"subject": subject, "topics": [], "resources": []})
    
    def get_quiz(self, subject: str, topic: str = None, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Get quiz questions for a subject/topic"""
        # Check if we have stored quizzes
        if subject in self.subject_data and self.subject_data[subject]["quizzes"]:
            quizzes = self.subject_data[subject]["quizzes"]
            if topic:
                quizzes = [q for q in quizzes if q.get("topic") == topic]
            if difficulty:
                quizzes = [q for q in quizzes if q.get("difficulty") == difficulty]
            if quizzes:
                return quizzes[:5]  # Return up to 5 questions
        
        # Generate sample quiz
        return self._generate_sample_quiz(subject, topic, difficulty)
    
    def _generate_sample_quiz(self, subject: str, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate sample quiz questions"""
        # This is a simplified example - in production, you'd have a proper question bank
        sample_quizzes = {
            "math": [
                {
                    "question": "Solve for x: 2x + 5 = 13",
                    "options": ["x = 4", "x = 3", "x = 5", "x = 6"],
                    "answer": "x = 4",
                    "explanation": "Subtract 5 from both sides: 2x = 8, then divide by 2: x = 4",
                    "difficulty": "easy",
                    "topic": "Algebra"
                }
            ],
            "physics": [
                {
                    "question": "What is the acceleration due to gravity on Earth?",
                    "options": ["9.8 m/s²", "10 m/s²", "8.9 m/s²", "11 m/s²"],
                    "answer": "9.8 m/s²",
                    "explanation": "The standard acceleration due to gravity is approximately 9.8 m/s²",
                    "difficulty": "easy",
                    "topic": "Mechanics"
                }
            ]
        }
        
        return sample_quizzes.get(subject, [{"question": "Sample question", "answer": "Sample answer"}])
    
    def get_materials(self, subject: str, material_type: str = "all") -> List[Dict[str, Any]]:
        """Get learning materials for a subject"""
        if subject not in self.subject_data:
            return []
        
        materials = []
        subject_info = self.subject_data[subject]
        
        if material_type in ["all", "text"]:
            materials.extend(subject_info.get("materials", []))
        if material_type in ["all", "audio"]:
            materials.extend(subject_info.get("audio", []))
        if material_type in ["all", "video"]:
            materials.extend(subject_info.get("videos", []))
        if material_type in ["all", "reference"]:
            materials.extend(subject_info.get("references", []))
        
        return materials