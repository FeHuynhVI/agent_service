"""Application settings for the AutoGen service."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Basic configuration options.

    The defaults provide sensible values for development and testing
    environments. They can be extended or overridden as needed.
    """

    max_rounds: int = 10
    max_consecutive_auto_reply: int = 3
    human_input_mode: str = "NEVER"
    termination_msg: str = "TERMINATE"
    data_path: Path = Path(__file__).resolve().parent / "data"


# Global settings instance
settings = Settings()


__all__ = ["Settings", "settings"]

