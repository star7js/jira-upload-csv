"""
Configuration module for Jira CSV upload tool.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _int_env(name: str, default: int) -> int:
    """Read an integer environment variable, falling back to a default."""
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Environment variable {name} must be an integer, got {value!r}"
        )


class JiraConfig:
    """Configuration class for Jira connection settings."""

    def __init__(self) -> None:
        self.base_url: Optional[str] = os.getenv("JIRA_BASE_URL")
        self.username: Optional[str] = os.getenv("JIRA_USERNAME")
        self.password: Optional[str] = os.getenv("JIRA_API_TOKEN")
        self.subtask_issue_type: str = os.getenv("JIRA_SUBTASK_ISSUE_TYPE", "Sub-task")

    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        required = {
            "JIRA_BASE_URL": self.base_url,
            "JIRA_USERNAME": self.username,
            "JIRA_API_TOKEN": self.password,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        return True


class AppConfig:
    """Application configuration."""

    def __init__(self) -> None:
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.default_csv_path: str = os.getenv(
            "DEFAULT_CSV_PATH", "data/main_and_subtasks_multiple.csv"
        )
        self.retry_attempts: int = _int_env("RETRY_ATTEMPTS", 3)
        self.retry_delay: int = _int_env("RETRY_DELAY", 5)


# Global configuration instances
jira_config = JiraConfig()
app_config = AppConfig()
