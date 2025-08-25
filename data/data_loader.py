"""
Data loader for subject materials
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

class SubjectDataLoader:
    """Load and manage subject data"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.subjects = ["math", "physics", "chemistry", "biology", "cs", "literature", "english"]
        self._ensure_directory_structure()
    
    def _ensure_directory_structure(self):
        """Create directory structure for all subjects"""
        for subject in self.subjects:
            subject_path = self.base_path / subject
            subject_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (subject_path / "materials").mkdir(exist_ok=True)
            (subject_path / "quizzes").mkdir(exist_ok=True)
            (subject_path / "audio").mkdir(exist_ok=True)
            (subject_path / "video").mkdir(exist_ok=True)
            
            # Create default syllabus if not exists
            syllabus_file = subject_path / "syllabus.json"
            if not syllabus_file.exists():
                self._create_default_syllabus(subject, syllabus_file)
            
            # Create sample materials if empty
            materials_dir = subject_path / "materials"
            if not any(materials_dir.glob("*.json")):
                self._create_sample_materials(subject, materials_dir)
    
    def _create_default_syllabus(self, subject: str, file_path: Path):
        """Create default syllabus for a subject"""
        syllabi_templates = {
            "math": {
                "subject": "Mathematics",
                "description": "Comprehensive mathematics curriculum",
                "modules": [
                    {
                        "name": "Algebra",
                        "topics": ["Linear Equations", "Quadratic Equations", "Systems of Equations"],
                        "duration": "6 weeks",
                        "difficulty": "intermediate"
                    },
                    {
                        "name": "Calculus",
                        "topics": ["Limits", "Derivatives", "Integrals", "Applications"],
                        "duration": "8 weeks",
                        "difficulty": "advanced"
                    }
                ]
            },
            "physics": {
                "subject": "Physics",
                "description": "Fundamental physics concepts and applications",
                "modules": [
                    {
                        "name": "Mechanics",
                        "topics": ["Kinematics", "Dynamics", "Work and Energy"],
                        "duration": "6 weeks",
                        "difficulty": "intermediate"
                    },
                    {
                        "name": "Electromagnetism",
                        "topics": ["Electric Fields", "Magnetic Fields", "EM Waves"],
                        "duration": "6 weeks",
                        "difficulty": "advanced"
                    }
                ]
            }
            # Add more subjects as needed
        }
        
        template = syllabi_templates.get(subject, {
            "subject": subject.title(),
            "description": f"Curriculum for {subject}",
            "modules": []
        })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
    
    def _create_sample_materials(self, subject: str, materials_dir: Path):
        """Create sample materials for a subject"""
        sample_materials = {
            "math": [
                {
                    "id": "math_001",
                    "title": "Introduction to Linear Algebra",
                    "type": "document",
                    "content": "Basic concepts of linear algebra including vectors, matrices, and linear transformations.",
                    "difficulty": "beginner",
                    "tags": ["algebra", "linear", "vectors"]
                },
                {
                    "id": "math_002",
                    "title": "Calculus Problem Set 1",
                    "type": "exercise",
                    "content": "Practice problems on limits and continuity",
                    "difficulty": "intermediate",
                    "tags": ["calculus", "limits", "practice"]
                }
            ],
            "physics": [
                {
                    "id": "phys_001",
                    "title": "Newton's Laws of Motion",
                    "type": "document",
                    "content": "Comprehensive guide to Newton's three laws of motion with examples",
                    "difficulty": "beginner",
                    "tags": ["mechanics", "forces", "motion"]
                }
            ]
            # Add more subjects
        }
        
        materials = sample_materials.get(subject, [{
            "id": f"{subject}_001",
            "title": f"Introduction to {subject.title()}",
            "type": "document",
            "content": f"Basic concepts in {subject}",
            "difficulty": "beginner",
            "tags": [subject]
        }])
        
        for i, material in enumerate(materials):
            file_path = materials_dir / f"material_{i+1}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(material, f, indent=2, ensure_ascii=False)
    
    def load_syllabus(self, subject: str) -> Dict[str, Any]:
        """Load syllabus for a subject"""
        syllabus_file = self.base_path / subject / "syllabus.json"
        if syllabus_file.exists():
            with open(syllabus_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_materials(self, subject: str, material_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load materials for a subject"""
        materials = []
        materials_dir = self.base_path / subject / "materials"
        
        if materials_dir.exists():
            for file_path in materials_dir.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    material = json.load(f)
                    if material_type is None or material.get("type") == material_type:
                        materials.append(material)
        
        return materials
    
    def load_quizzes(self, subject: str, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load quiz questions for a subject"""
        quizzes = []
        quiz_dir = self.base_path / subject / "quizzes"
        
        if quiz_dir.exists():
            for file_path in quiz_dir.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    quiz = json.load(f)
                    if topic is None or quiz.get("topic") == topic:
                        quizzes.append(quiz)
        
        # Create sample quiz if none exist
        if not quizzes:
            quizzes = self._create_sample_quiz(subject, topic)
        
        return quizzes
    
    def _create_sample_quiz(self, subject: str, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """Create sample quiz questions"""
        sample_quizzes = {
            "math": {
                "id": "quiz_math_001",
                "subject": "math",
                "topic": topic or "algebra",
                "questions": [
                    {
                        "question": "Solve for x: 2x + 5 = 13",
                        "type": "multiple_choice",
                        "options": ["x = 4", "x = 3", "x = 5", "x = 6"],
                        "correct_answer": 0,
                        "explanation": "2x + 5 = 13 → 2x = 8 → x = 4"
                    }
                ]
            }
        }
        
        quiz = sample_quizzes.get(subject, {
            "id": f"quiz_{subject}_001",
            "subject": subject,
            "topic": topic or "general",
            "questions": []
        })
        
        return [quiz]
    
    def save_material(self, subject: str, material: Dict[str, Any]):
        """Save a new material"""
        materials_dir = self.base_path / subject / "materials"
        materials_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        existing_files = list(materials_dir.glob("*.json"))
        file_number = len(existing_files) + 1
        file_path = materials_dir / f"material_{file_number}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(material, f, indent=2, ensure_ascii=False)
    
    def search_materials(self, query: str, subject: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search materials across subjects"""
        results = []
        search_subjects = [subject] if subject else self.subjects
        
        for subj in search_subjects:
            materials = self.load_materials(subj)
            for material in materials:
                # Simple search in title and content
                if (query.lower() in material.get("title", "").lower() or 
                    query.lower() in material.get("content", "").lower() or
                    query.lower() in str(material.get("tags", [])).lower()):
                    material["subject"] = subj
                    results.append(material)
        
        return results