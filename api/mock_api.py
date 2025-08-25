"""Simple FastAPI application exposing subject data.

This mock API allows clients to retrieve basic information about
available subjects, their syllabi, learning materials and quizzes.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException

from data.data_loader import SubjectDataLoader
from utils.error_handler import handle_errors


app = FastAPI(title="Mock Subject Data API")

data_loader = SubjectDataLoader(
    base_path=Path(__file__).resolve().parent.parent / "data"
)


@app.get("/subjects")
@handle_errors
async def list_subjects() -> dict:
    """Return all available subjects."""
    return {"subjects": data_loader.subjects}


@app.get("/subjects/{subject}/syllabus")
@handle_errors
async def get_syllabus(subject: str) -> dict:
    """Return the syllabus for a given subject."""
    subject = subject.lower()
    if subject not in data_loader.subjects:
        raise HTTPException(status_code=404, detail="Subject not found")
    return data_loader.load_syllabus(subject)


@app.get("/subjects/{subject}/materials")
@handle_errors
async def get_materials(subject: str) -> dict:
    """Return learning materials for a given subject."""
    subject = subject.lower()
    if subject not in data_loader.subjects:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"materials": data_loader.load_materials(subject)}


@app.get("/subjects/{subject}/quizzes")
@handle_errors
async def get_quizzes(subject: str) -> dict:
    """Return quiz questions for a given subject."""
    subject = subject.lower()
    if subject not in data_loader.subjects:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"quizzes": data_loader.load_quizzes(subject)}


__all__ = ["app"]
