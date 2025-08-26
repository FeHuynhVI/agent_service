"""Endpoints enabling chat between a user and the team of agents with improved error handling."""

import logging
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from chat.selector_group_chat import SelectorGroupChat
from config.agents import (
    CSExpertAgent,
    MathExpertAgent,
    EnglishExpertAgent,
    BiologyExpertAgent,
    PhysicsExpertAgent,
    ChemistryExpertAgent,
    LiteratureExpertAgent,
    InfoAgent,
)

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_group_chat(api_key: str | None = None) -> SelectorGroupChat:
    """Build a group chat with all available agents."""
    try:
        agents = [
            InfoAgent(api_key=api_key).get_agent(),
            CSExpertAgent(api_key=api_key).get_agent(),
            MathExpertAgent(api_key=api_key).get_agent(),
            EnglishExpertAgent(api_key=api_key).get_agent(),
            BiologyExpertAgent(api_key=api_key).get_agent(),
            PhysicsExpertAgent(api_key=api_key).get_agent(),
            ChemistryExpertAgent(api_key=api_key).get_agent(),
            LiteratureExpertAgent(api_key=api_key).get_agent(),
        ]
        return SelectorGroupChat(agents=agents, api_key=api_key)
    except ValueError as e:
        logger.error(f"Configuration error when building group chat: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error when building group chat: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to initialize chat system"
        )


class ChatRequest(BaseModel):
    message: str

    class Config:
        schema_extra = {
            "example": {
                "message": "Can you help me solve this math problem: What is the derivative of x^2?"
            }
        }


class ChatResponse(BaseModel):
    messages: list
    status: str = "success"
    agent_count: int


@router.post("/", response_model=ChatResponse)
async def chat_with_team(
    request: ChatRequest,
    openai_api_key: str | None = Header(default=None, alias="OpenAI-Api-Key"),
) -> ChatResponse:
    """Handle a user message and return the conversation history.
    
    Args:
        request: The chat request containing the user's message
        openai_api_key: Optional OpenAI API key passed in headers
        
    Returns:
        ChatResponse with conversation history and metadata
        
    Raises:
        HTTPException: For various error conditions including:
            - 400: Invalid API key or configuration
            - 401: Authentication failed
            - 500: Internal server error
    """
    if not request.message.strip():
        raise HTTPException(
            status_code=400, 
            detail="Message cannot be empty"
        )
    
    try:
        # Build the group chat with error handling
        group_chat = _build_group_chat(api_key=openai_api_key)
        logger.info(f"Starting chat with message: {request.message[:100]}...")
        
        # Start the conversation
        group_chat.start_chat(request.message)
        
        # Get the chat history
        messages = group_chat.get_chat_history()
        
        return ChatResponse(
            messages=messages,
            agent_count=len(group_chat.agents),
            status="success"
        )
        
    except ValueError as e:
        # Configuration or validation errors
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Check if it's an authentication error
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ["401", "authentication", "api key", "token"]):
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=401, 
                detail="Authentication failed. Please check your API key."
            )
        elif "proxy" in error_str or "not found in db" in error_str:
            logger.error(f"Proxy server error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Proxy server authentication failed. You may need to generate a new key via /key/generate endpoint."
            )
        else:
            # Generic server error
            logger.error(f"Unexpected error during chat: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="An error occurred while processing your request"
            )


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "chat"}


@router.get("/agents")
async def list_agents():
    """List all available agents and their capabilities."""
    return {
        "agents": [
            {"name": "Math_Expert", "specialization": "Mathematics, Calculus, Algebra, Geometry"},
            {"name": "Physics_Expert", "specialization": "Physics, Mechanics, Quantum Physics"},
            {"name": "Chemistry_Expert", "specialization": "Chemistry, Chemical Reactions, Molecules"},
            {"name": "Biology_Expert", "specialization": "Biology, Genetics, Ecology, Evolution"},
            {"name": "CS_Expert", "specialization": "Computer Science, Programming, Algorithms"},
            {"name": "Literature_Expert", "specialization": "Literature, Writing, Analysis"},
            {"name": "English_Expert", "specialization": "English Language, Grammar, IELTS/TOEFL"},
            {"name": "Info_Agent", "specialization": "Information Resources, Materials, Quizzes"},
        ]
    }