"""
Configuration module for Jira CSV upload tool.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class JiraConfig:
    """Configuration class for Jira connection settings."""

    def __init__(self):
        self.base_url: str = os.getenv(
            "JIRA_BASE_URL", "https://your-jira-instance-url"
        )
        self.username: str = os.getenv("JIRA_USERNAME", "your-username")
        self.password: str = os.getenv("JIRA_API_TOKEN", "your-api-token")

    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        if self.base_url == "https://your-jira-instance-url":
            raise ValueError("JIRA_BASE_URL environment variable is not set")
        if self.username == "your-username":
            raise ValueError("JIRA_USERNAME environment variable is not set")
        if self.password == "your-api-token":
            raise ValueError("JIRA_API_TOKEN environment variable is not set")
        return True


class AppConfig:
    """Application configuration."""

    def __init__(self):
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.default_csv_path: str = os.getenv(
            "DEFAULT_CSV_PATH", "data/main_and_subtasks_multiple.csv"
        )
        self.batch_size: int = int(os.getenv("BATCH_SIZE", "10"))
        self.retry_attempts: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
        self.retry_delay: int = int(os.getenv("RETRY_DELAY", "5"))


# Global configuration instances
jira_config = JiraConfig()
app_config = AppConfig()
