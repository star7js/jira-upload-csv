"""
Integration tests for end-to-end workflow.
"""

import unittest
from unittest.mock import patch
import tempfile
import os
import importlib

from src.main import main, process_issue_group
from src.models import CSVRow
from src.jira_client import JiraClient


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflow with mocked Jira API."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.temp_dir, "test.csv")

        # Create a test CSV file
        # fmt: off
        csv_content = """ID,Project Key,Summary,Description,Issue Type,Subtask Summary,Subtask Description
1,TEST,Main Issue 1,Description 1,Task,Subtask 1.1,Subtask Description 1.1
1,TEST,,,,Subtask 1.2,Subtask Description 1.2
2,TEST,Main Issue 2,Description 2,Task,,
"""  # noqa: E501
        # fmt: on
        with open(self.csv_file, "w") as f:
            f.write(csv_content)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    @patch("src.jira_client.Jira")
    def test_end_to_end_workflow_success(self, mock_jira_class):
        """Test complete workflow with successful API calls."""
        # Patch environment and reload config
        with patch.dict(
            os.environ,
            {
                "JIRA_BASE_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            # Reload config module to pick up new environment variables
            from src import config

            importlib.reload(config)
            # Re-import main to use reloaded config
            from src import main as main_module

            importlib.reload(main_module)

            # Setup mock Jira instance
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.server_info.return_value = {"serverTitle": "Test Server"}

            # Mock issue creation
            issue_counter = [0]

            def mock_create_issue(fields):
                issue_counter[0] += 1
                return {
                    "key": f"TEST-{issue_counter[0]}",
                    "id": str(issue_counter[0]),
                }

            mock_jira_instance.issue_create.side_effect = mock_create_issue

            # Run the main function
            result = main_module.main(self.csv_file)

            # Assertions
            self.assertTrue(result)
            # Should create 2 main issues and 2 subtasks = 4 total calls
            self.assertEqual(mock_jira_instance.issue_create.call_count, 4)

    @patch("src.jira_client.Jira")
    def test_end_to_end_workflow_with_api_error(self, mock_jira_class):
        """Test workflow handling of API errors."""
        # Patch environment and reload config
        with patch.dict(
            os.environ,
            {
                "JIRA_BASE_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
                "RETRY_ATTEMPTS": "1",  # Minimize retries for faster test
                "RETRY_DELAY": "0",  # No delay between retries
            },
        ):
            # Reload config module to pick up new environment variables
            from src import config

            importlib.reload(config)
            # Re-import main to use reloaded config
            from src import main as main_module

            importlib.reload(main_module)

            # Setup mock Jira instance
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.server_info.return_value = {"serverTitle": "Test Server"}

            # Mock issue creation with persistent failure on subtask
            # Track unique calls (not retries)
            successful_issues = [0]

            def mock_create_issue_with_error(fields):
                # First call succeeds (main issue)
                if successful_issues[0] == 0:
                    successful_issues[0] += 1
                    return {"key": "TEST-1", "id": "1"}
                # Second unique call fails permanently (subtask) - even on retries
                elif successful_issues[0] == 1:
                    error = Exception("API Error")
                    error.status_code = 500
                    raise error
                # Subsequent calls succeed
                else:
                    successful_issues[0] += 1
                    return {
                        "key": f"TEST-{successful_issues[0]}",
                        "id": str(successful_issues[0]),
                    }

            mock_jira_instance.issue_create.side_effect = mock_create_issue_with_error

            # Run the main function
            result = main_module.main(self.csv_file)

            # Should still complete but with errors
            self.assertFalse(result)  # Should return False due to errors

    @patch.dict(
        os.environ,
        {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "test@example.com",
            "JIRA_API_TOKEN": "test-token",
        },
    )
    def test_invalid_csv_file(self):
        """Test handling of invalid CSV file path."""
        result = main("/nonexistent/file.csv")
        self.assertFalse(result)


class TestProcessIssueGroup(unittest.TestCase):
    """Test process_issue_group function."""

    @patch.dict(
        os.environ,
        {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "test@example.com",
            "JIRA_API_TOKEN": "test-token",
        },
    )
    @patch("src.jira_client.Jira")
    def test_process_issue_group_with_subtasks(self, mock_jira_class):
        """Test processing an issue group with subtasks."""
        # Setup mock
        mock_jira_instance = mock_jira_class.return_value
        mock_jira_instance.issue_create.side_effect = [
            {"key": "TEST-1", "id": "1"},
            {"key": "TEST-2", "id": "2"},
        ]

        jira_client = JiraClient()
        jira_client.jira = mock_jira_instance

        rows = [
            CSVRow(
                id="1",
                project_key="TEST",
                summary="Main Issue",
                description="Description",
                issue_type="Task",
                subtask_summary="Subtask 1",
                subtask_description="Subtask Desc 1",
            ),
        ]

        result = process_issue_group(
            "1", rows, jira_client, "https://test.atlassian.net"
        )

        # Assertions
        self.assertIsNotNone(result["main_issue"])
        self.assertEqual(len(result["subtasks"]), 1)
        self.assertEqual(len(result["errors"]), 0)
        self.assertEqual(result["main_issue"]["key"], "TEST-1")
        self.assertEqual(result["subtasks"][0]["key"], "TEST-2")

    @patch.dict(
        os.environ,
        {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "test@example.com",
            "JIRA_API_TOKEN": "test-token",
        },
    )
    @patch("src.jira_client.Jira")
    def test_process_issue_group_without_main_issue(self, mock_jira_class):
        """Test processing an issue group without main issue data."""
        mock_jira_instance = mock_jira_class.return_value

        jira_client = JiraClient()
        jira_client.jira = mock_jira_instance

        # Row with only subtask data
        rows = [
            CSVRow(
                id="1",
                project_key="TEST",
                summary=None,
                description=None,
                issue_type=None,
                subtask_summary="Subtask 1",
                subtask_description="Subtask Desc 1",
            ),
        ]

        result = process_issue_group(
            "1", rows, jira_client, "https://test.atlassian.net"
        )

        # Assertions
        self.assertIsNone(result["main_issue"])
        self.assertEqual(len(result["subtasks"]), 0)
        self.assertGreater(len(result["errors"]), 0)


if __name__ == "__main__":
    unittest.main()
