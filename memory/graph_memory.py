"""Graph-based memory using MongoDB for persistence and Memgraph for relationships."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from pymongo import MongoClient
except Exception:  # pragma: no cover - optional dependency
    MongoClient = None  # type: ignore

try:
    import mgclient
except Exception:  # pragma: no cover - optional dependency
    mgclient = None  # type: ignore


@dataclass
class GraphMemory:
    """Store agent interactions in MongoDB and link them in Memgraph."""

    mongo_uri: str
    memgraph_host: str = "127.0.0.1"
    memgraph_port: int = 7687

    def __post_init__(self) -> None:
        if MongoClient is None:
            raise ImportError("pymongo is required for MongoDB integration")
        if mgclient is None:
            raise ImportError("mgclient is required for Memgraph integration")

        self.mongo_client = MongoClient(self.mongo_uri)
        self.mongo_db = self.mongo_client["agent_memory"]
        self.memgraph_conn = mgclient.connect(host=self.memgraph_host, port=self.memgraph_port)
        self.memgraph_cursor = self.memgraph_conn.cursor()

    def store_interaction(self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Persist a user interaction and create a corresponding node in Memgraph.

        Returns the MongoDB document ID for further graph linking.
        """
        document = {
            "user_id": user_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow(),
        }
        result = self.mongo_db.interactions.insert_one(document)
        mongo_id = str(result.inserted_id)

        self.memgraph_cursor.execute(
            """
            MERGE (u:User {id: $user_id})
            CREATE (u)-[:SENT {mongo_id: $mongo_id, timestamp: $timestamp}]->(m:Message {content: $content})
            """,
            {
                "user_id": user_id,
                "mongo_id": mongo_id,
                "timestamp": document["timestamp"].isoformat(),
                "content": content,
            },
        )
        return mongo_id

    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent interactions for a user from MongoDB."""
        cursor = (
            self.mongo_db.interactions.find({"user_id": user_id})
            .sort("timestamp", -1)
            .limit(limit)
        )
        return list(cursor)

    def close(self) -> None:
        """Clean up database connections."""
        self.mongo_client.close()
        self.memgraph_cursor.close()
        self.memgraph_conn.close()
