"""
Jira client module with error handling and retry logic.
"""

import logging
import time
from typing import Any, Callable, Dict, Optional

from atlassian import Jira

from jira_csv_upload.config import jira_config, app_config

logger = logging.getLogger(__name__)


class JiraClient:
    """Jira client with error handling and retry logic."""

    def __init__(self):
        """Initialize Jira client with configuration."""
        self.jira = Jira(
            url=jira_config.base_url or "",
            username=jira_config.username,
            password=jira_config.password,
        )
        self.retry_attempts = app_config.retry_attempts
        self.retry_delay = app_config.retry_delay

    def _with_retry(
        self, operation: str, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call a Jira API method with retry logic.

        Args:
            operation: Name of the operation for logging
            func: The Jira API method to call
            *args: Arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            API response dictionary

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.retry_attempts):
            try:
                logger.debug(
                    f"Attempting {operation} "
                    f"(attempt {attempt + 1}/{self.retry_attempts})"
                )
                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e
                logger.warning(f"API error on attempt {attempt + 1}: {e}")

                status_code = getattr(e, "status_code", None)
                if status_code is not None:
                    # Don't retry on authentication errors
                    if status_code in (401, 403):
                        logger.error(f"Authentication failed: {e}")
                        raise

                    # Don't retry on client errors (4xx) except rate limiting
                    if 400 <= status_code < 500 and status_code != 429:
                        logger.error(f"Client error {status_code}: {e}")
                        raise

            # Wait before retrying (except on last attempt)
            if attempt < self.retry_attempts - 1:
                wait_time = self.retry_delay * (2**attempt)  # Exponential backoff
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)

        # All retries failed
        logger.error(f"All {self.retry_attempts} attempts failed for {operation}")
        if last_exception is not None:
            raise last_exception
        raise RuntimeError(f"All {self.retry_attempts} attempts failed for {operation}")

    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Jira issue.

        Args:
            issue_data: Issue data dictionary

        Returns:
            Created issue response
        """
        logger.info(f"Creating issue: {issue_data.get('summary', 'Unknown')}")

        try:
            response = self._with_retry(
                "create_issue", self.jira.issue_create, fields=issue_data
            )

            logger.info(f"Successfully created issue: {response.get('key', 'Unknown')}")
            return response

        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            raise

    def create_subtask(self, subtask_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Jira subtask.

        Args:
            subtask_data: Subtask data dictionary

        Returns:
            Created subtask response
        """
        logger.info(f"Creating subtask: {subtask_data.get('summary', 'Unknown')}")

        try:
            response = self._with_retry(
                "create_subtask", self.jira.issue_create, fields=subtask_data
            )

            logger.info(
                f"Successfully created subtask: {response.get('key', 'Unknown')}"
            )
            return response

        except Exception as e:
            logger.error(f"Failed to create subtask: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test the Jira connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get server info as a connection test
            server_info = self.jira.get_server_info() or {}
            logger.info(
                f"Successfully connected to Jira server: "
                f"{server_info.get('serverTitle', 'Unknown')}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            return False
