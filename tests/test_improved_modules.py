"""
Tests for Jira CSV upload modules.
"""

import unittest
from unittest.mock import patch
import tempfile
import os

from jira_csv_upload.config import JiraConfig, AppConfig
from jira_csv_upload.models import CSVRow
from jira_csv_upload.csv_processor import CSVProcessor
from jira_csv_upload.jira_client import JiraClient


class TestJiraConfig(unittest.TestCase):
    """Test JiraConfig class."""

    @patch.dict(
        os.environ,
        {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "test@example.com",
            "JIRA_API_TOKEN": "test-token",
        },
    )
    def test_valid_config(self):
        """Test configuration with valid environment variables."""
        config = JiraConfig()
        self.assertEqual(config.base_url, "https://test.atlassian.net")
        self.assertEqual(config.username, "test@example.com")
        self.assertEqual(config.password, "test-token")
        self.assertTrue(config.validate())

    def test_invalid_config(self):
        """Test configuration validation with missing values."""
        with patch.dict(os.environ, {}, clear=True):
            config = JiraConfig()
            with self.assertRaises(ValueError) as ctx:
                config.validate()
            self.assertIn("JIRA_BASE_URL", str(ctx.exception))

    def test_subtask_issue_type_default(self):
        """Test subtask issue type defaults to Sub-task."""
        with patch.dict(os.environ, {}, clear=True):
            config = JiraConfig()
            self.assertEqual(config.subtask_issue_type, "Sub-task")

    @patch.dict(os.environ, {"JIRA_SUBTASK_ISSUE_TYPE": "Subtarea"})
    def test_subtask_issue_type_override(self):
        """Test subtask issue type can be overridden."""
        config = JiraConfig()
        self.assertEqual(config.subtask_issue_type, "Subtarea")


class TestAppConfig(unittest.TestCase):
    """Test AppConfig class."""

    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "RETRY_ATTEMPTS": "5"})
    def test_config_with_env_vars(self):
        """Test configuration with environment variables."""
        config = AppConfig()
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.retry_attempts, 5)

    def test_config_defaults(self):
        """Test configuration defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig()
            self.assertEqual(config.log_level, "INFO")
            self.assertEqual(config.retry_attempts, 3)
            self.assertEqual(config.retry_delay, 5)

    @patch.dict(os.environ, {"RETRY_ATTEMPTS": "not-a-number"})
    def test_config_invalid_int(self):
        """Test that a non-integer env var raises a clear error."""
        with self.assertRaises(ValueError) as ctx:
            AppConfig()
        self.assertIn("RETRY_ATTEMPTS", str(ctx.exception))


class TestModels(unittest.TestCase):
    """Test data models."""

    def test_csv_row_valid(self):
        """Test valid CSVRow creation."""
        row = CSVRow(
            id="1",
            project_key="TEST",
            summary="Test Issue",
            description="Test Description",
            issue_type="Task",
            subtask_summary="Test Subtask",
            subtask_description="Test Subtask Description",
        )
        self.assertEqual(row.id, "1")
        self.assertTrue(row.has_subtask())
        self.assertTrue(row.has_main_issue())

    def test_csv_row_no_subtask(self):
        """Test CSVRow without subtask data."""
        row = CSVRow(
            id="1",
            project_key="TEST",
            summary="Test Issue",
            description="Test Description",
            issue_type="Task",
        )
        self.assertFalse(row.has_subtask())

    def test_csv_row_requires_issue_type_for_main_issue(self):
        """A row without an issue type is not a main issue row."""
        row = CSVRow(
            id="1",
            project_key="TEST",
            summary="Test Issue",
            description="Test Description",
            issue_type=None,
        )
        self.assertFalse(row.has_main_issue())

    def test_csv_row_strips_and_normalizes(self):
        """Whitespace is stripped and blank optionals become None."""
        row = CSVRow(
            id=" 1 ",
            project_key=" test ",
            summary="  Test Issue  ",
            description="   ",
        )
        self.assertEqual(row.id, "1")
        self.assertEqual(row.project_key, "TEST")
        self.assertEqual(row.summary, "Test Issue")
        self.assertIsNone(row.description)

    def test_csv_row_empty_id_rejected(self):
        """Empty ID raises a validation error."""
        with self.assertRaises(ValueError):
            CSVRow(id="  ", project_key="TEST")


class TestCSVProcessor(unittest.TestCase):
    """Test CSVProcessor class."""

    HEADER = (
        "ID,Project Key,Summary,Description,Issue Type,"
        "Subtask Summary,Subtask Description\n"
    )

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.temp_dir, "test.csv")

        csv_content = self.HEADER + (
            "1,TEST,Main Issue 1,Description 1,Task,,\n"
            "2,TEST,Main Issue 2,Description 2,Task,Subtask 2.1,Subtask Desc 2.1\n"
        )
        with open(self.csv_file, "w") as f:
            f.write(csv_content)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def _write_csv(self, content):
        path = os.path.join(self.temp_dir, "custom.csv")
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_validate_file_exists(self):
        """Test file existence validation."""
        processor = CSVProcessor(self.csv_file)
        self.assertTrue(processor.validate_file_exists())

        processor = CSVProcessor("nonexistent.csv")
        self.assertFalse(processor.validate_file_exists())

    def test_read_and_validate_csv(self):
        """Test CSV reading and validation."""
        processor = CSVProcessor(self.csv_file)
        rows = processor.read_and_validate_csv()

        self.assertEqual(len(rows), 2)
        self.assertIsInstance(rows[0], CSVRow)
        self.assertEqual(rows[0].project_key, "TEST")

    def test_read_csv_with_invalid_row_raises(self):
        """A row that fails validation fails the whole read."""
        path = self._write_csv(
            self.HEADER + "1,TEST,Main Issue,Description,Task,,\n"
            ",TEST,Bad Row,Description,Task,,\n"  # empty ID
        )
        processor = CSVProcessor(path)
        with self.assertRaises(ValueError) as ctx:
            processor.read_and_validate_csv()
        self.assertIn("invalid row", str(ctx.exception))

    def test_read_csv_missing_columns_raises(self):
        """Missing required columns raise a ValueError."""
        path = self._write_csv("ID,Project Key\n1,TEST\n")
        processor = CSVProcessor(path)
        with self.assertRaises(ValueError):
            processor.read_and_validate_csv()

    def test_get_issue_groups(self):
        """Test issue grouping."""
        processor = CSVProcessor(self.csv_file)
        rows = processor.read_and_validate_csv()
        groups = processor.get_issue_groups(rows)

        self.assertEqual(len(groups), 2)
        self.assertIn("1", groups)
        self.assertIn("2", groups)
        self.assertEqual(len(groups["1"]), 1)
        self.assertEqual(len(groups["2"]), 1)

    def test_validate_issue_groups(self):
        """Test issue group validation."""
        processor = CSVProcessor(self.csv_file)
        rows = processor.read_and_validate_csv()
        groups = processor.get_issue_groups(rows)

        self.assertTrue(processor.validate_issue_groups(groups))

    def test_validate_issue_groups_requires_issue_type(self):
        """A main issue row without an Issue Type fails group validation."""
        path = self._write_csv(
            self.HEADER + "1,TEST,Main Issue,Description,,,\n"  # no Issue Type
        )
        processor = CSVProcessor(path)
        rows = processor.read_and_validate_csv()
        groups = processor.get_issue_groups(rows)

        self.assertFalse(processor.validate_issue_groups(groups))

    def test_validate_issue_groups_multiple_main_rows(self):
        """Two main issue rows in one group fail validation."""
        path = self._write_csv(
            self.HEADER + "1,TEST,Main Issue A,Description,Task,,\n"
            "1,TEST,Main Issue B,Description,Task,,\n"
        )
        processor = CSVProcessor(path)
        rows = processor.read_and_validate_csv()
        groups = processor.get_issue_groups(rows)

        self.assertFalse(processor.validate_issue_groups(groups))


class TestJiraClient(unittest.TestCase):
    """Test JiraClient class."""

    ISSUE_DATA = {
        "project": {"key": "TEST"},
        "summary": "Test Issue",
        "description": "Test Description",
        "issuetype": {"name": "Task"},
    }

    def setUp(self):
        """Set up test fixtures."""
        with patch.dict(
            os.environ,
            {
                "JIRA_BASE_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            self.client = JiraClient()
        self.client.retry_delay = 0  # no sleeping in tests

    def test_test_connection_success(self):
        """Test successful connection test."""
        with patch("jira_csv_upload.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.get_server_info.return_value = {
                "serverTitle": "Test Server"
            }
            self.client.jira = mock_jira_instance
            self.assertTrue(self.client.test_connection())

    def test_test_connection_failure(self):
        """Test failed connection test."""
        with patch("jira_csv_upload.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.get_server_info.side_effect = Exception(
                "Connection failed"
            )
            self.client.jira = mock_jira_instance
            self.assertFalse(self.client.test_connection())

    def test_create_issue_success(self):
        """Test successful issue creation."""
        with patch("jira_csv_upload.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.issue_create.return_value = {
                "key": "TEST-123",
                "id": "12345",
            }
            self.client.jira = mock_jira_instance

            created_issue = self.client.create_issue(self.ISSUE_DATA)

            self.assertEqual(created_issue["key"], "TEST-123")
            mock_jira_instance.issue_create.assert_called_once_with(
                fields=self.ISSUE_DATA
            )

    def test_create_issue_retries_server_errors(self):
        """Server errors are retried and can eventually succeed."""
        with patch("jira_csv_upload.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            server_error = Exception("Server Error")
            server_error.status_code = 500
            mock_jira_instance.issue_create.side_effect = [
                server_error,
                {"key": "TEST-123", "id": "12345"},
            ]
            self.client.jira = mock_jira_instance

            created_issue = self.client.create_issue(self.ISSUE_DATA)

            self.assertEqual(created_issue["key"], "TEST-123")
            self.assertEqual(mock_jira_instance.issue_create.call_count, 2)

    def test_create_issue_does_not_retry_auth_errors(self):
        """Authentication errors are not retried."""
        with patch("jira_csv_upload.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            auth_error = Exception("Unauthorized")
            auth_error.status_code = 401
            mock_jira_instance.issue_create.side_effect = auth_error
            self.client.jira = mock_jira_instance

            with self.assertRaises(Exception):
                self.client.create_issue(self.ISSUE_DATA)

            self.assertEqual(mock_jira_instance.issue_create.call_count, 1)

    def test_create_issue_failure(self):
        """Test failed issue creation after exhausting retries."""
        with patch("jira_csv_upload.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            mock_exception = Exception("Server Error")
            mock_exception.status_code = 500
            mock_jira_instance.issue_create.side_effect = mock_exception
            self.client.jira = mock_jira_instance

            with self.assertRaises(Exception):
                self.client.create_issue(self.ISSUE_DATA)

    def test_create_subtask_success(self):
        """Test successful subtask creation."""
        with patch("jira_csv_upload.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.issue_create.return_value = {
                "key": "TEST-124",
                "id": "12346",
            }
            self.client.jira = mock_jira_instance

            subtask_data = {
                "project": {"key": "TEST"},
                "summary": "Test Subtask",
                "description": "Test Subtask Description",
                "issuetype": {"name": "Sub-task"},
                "parent": {"id": "TEST-123"},
            }
            created_subtask = self.client.create_subtask(subtask_data)

            self.assertEqual(created_subtask["key"], "TEST-124")
            mock_jira_instance.issue_create.assert_called_once_with(fields=subtask_data)


if __name__ == "__main__":
    unittest.main()
