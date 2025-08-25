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


# Instantiate a single settings object that can be imported elsewhere
settings = Settings()

__all__ = ["Settings", "settings"]