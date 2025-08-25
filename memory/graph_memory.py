"""Graph-based memory using MongoDB (Motor) for persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except Exception:  # pragma: no cover - optional dependency
    AsyncIOMotorClient = None  # type: ignore


@dataclass
class GraphMemory:
    """Store agent interactions in MongoDB."""

    mongo_uri: str

    def __post_init__(self) -> None:
        if AsyncIOMotorClient is None:
            raise ImportError("motor is required for MongoDB integration")

        self.mongo_client = AsyncIOMotorClient(self.mongo_uri)
        self.mongo_db = self.mongo_client["agent_memory"]

    async def store_interaction(
        self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Persist a user interaction.

        Returns the MongoDB document ID.
        """
        document = {
            "user_id": user_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow(),
        }
        result = await self.mongo_db.interactions.insert_one(document)
        return str(result.inserted_id)

    async def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent interactions for a user from MongoDB."""
        cursor = (
            self.mongo_db.interactions.find({"user_id": user_id})
            .sort("timestamp", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    def close(self) -> None:
        """Clean up database connections."""
        self.mongo_client.close()
