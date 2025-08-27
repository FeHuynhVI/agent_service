"""FastAPI application exposing subject data and chat endpoints."""

from fastapi import FastAPI

from utils.error_handler import handle_errors

from .chat_controller import router as chat_router


app = FastAPI(title="Mock Subject Data API")
app.include_router(chat_router)


@app.get("/health", tags=["health"])
@handle_errors
async def health_check() -> dict:
    """Simple health check endpoint."""

    return {"status": "ok"}


__all__ = ["app"]

