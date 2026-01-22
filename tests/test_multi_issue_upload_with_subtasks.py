import unittest
from unittest.mock import mock_open, patch, Mock
import sys
import os

# Add src to path without importing pydantic modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Mock pydantic before importing
with patch.dict(
    "sys.modules",
    {
        "pydantic": Mock(),
        "pydantic.BaseModel": Mock(),
        "pydantic.Field": Mock(),
        "pydantic.field_validator": Mock(),
    },
):
    from multi_issue_upload_with_subtasks import (
        read_csv,
        create_jira_issue,
        create_jira_subtask,
    )


class TestJiraScript(unittest.TestCase):

    # Test for read_csv function
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="Project Key,Summary,Description,Issue Type\nTest,Ticket 1,Description 1,Task",
    )
    def test_read_csv(self, mock_open_instance):
        rows = read_csv("dummy.csv")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Project Key"], "Test")
        # ... more assertions based on your CSV structure

    # Test for create_jira_issue function
    @patch("multi_issue_upload_with_subtasks.jira")
    def test_create_jira_issue(self, mock_jira):
        mock_jira.issue_create.return_value = {"key": "TEST-123", "id": "001"}

        issue_data = {
            "project": {"key": "Test"},
            "summary": "Ticket 1",
            "description": "Description 1",
            "issuetype": {"name": "Task"},
        }
        response = create_jira_issue(issue_data)
        mock_jira.issue_create.assert_called_once_with(fields=issue_data)
        self.assertEqual(response["key"], "TEST-123")
        # ... more assertions if needed

    # Test for create_jira_subtask function (similar to the one above)
    @patch("multi_issue_upload_with_subtasks.jira")
    def test_create_jira_subtask(self, mock_jira):
        mock_jira.issue_create.return_value = {"key": "TEST-124", "id": "002"}

        subtask_data = {
            "project": {"key": "Test"},
            "summary": "Subtask 1",
            "description": "Subtask Description 1",
            "issuetype": {"name": "Sub-task"},
            "parent": {"id": "001"},
        }
        response = create_jira_subtask(subtask_data)
        mock_jira.issue_create.assert_called_once_with(fields=subtask_data)
        self.assertEqual(response["key"], "TEST-124")
        # ... more assertions if needed


if __name__ == "__main__":
    unittest.main()
