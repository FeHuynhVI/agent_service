import logging
import asyncio
from fastapi import HTTPException
from functools import wraps


def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            raise e
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Chat request timed out.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    return wrapper
