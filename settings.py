"""Application configuration settings."""

from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class Settings:
    """Runtime configuration loaded from environment variables.

    The class provides sensible defaults so the package can operate in
    a development environment without additional configuration."""

    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    azure_openai_api_key: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    max_rounds: int = field(default_factory=lambda: int(os.getenv("MAX_ROUNDS", "10")))
    termination_msg: str = field(default_factory=lambda: os.getenv("TERMINATION_MSG", "TERMINATE"))
    max_consecutive_auto_reply: int = field(
        default_factory=lambda: int(os.getenv("MAX_CONSECUTIVE_AUTO_REPLY", "3"))
    )
    human_input_mode: str = field(default_factory=lambda: os.getenv("HUMAN_INPUT_MODE", "NEVER"))
    data_path: Path = field(default_factory=lambda: Path(os.getenv("DATA_PATH", "data")))
    mongo_uri: str = field(
        default_factory=lambda: os.getenv("MONGO_URI", "mongodb://localhost:27017")
    )
    memgraph_host: str = field(default_factory=lambda: os.getenv("MEMGRAPH_HOST", "127.0.0.1"))
    memgraph_port: int = field(
        default_factory=lambda: int(os.getenv("MEMGRAPH_PORT", "7687"))
    )


# Instantiate a single settings object that can be imported elsewhere
settings = Settings()

__all__ = ["Settings", "settings"]
