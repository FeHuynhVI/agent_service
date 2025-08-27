"""FastAPI application exposing subject data and chat endpoints."""

from pathlib import Path

from fastapi import FastAPI, HTTPException

from utils.error_handler import handle_errors


app = FastAPI(title="Mock Subject Data API")


__all__ = ["app"]

