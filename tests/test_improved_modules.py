"""
Comprehensive tests for improved Jira CSV upload modules.
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
import os
from atlassian.errors import ApiError

# Mock the atlassian import to avoid real network calls
with patch.dict(
    "sys.modules",
    {
        "atlassian": Mock(),
        "atlassian.errors": Mock(),
    },
):
    from src.config import JiraConfig, AppConfig  # noqa
    from src.models import JiraIssueData, JiraSubtaskData, CSVRow
    from src.csv_processor import CSVProcessor
    from src.jira_client import JiraClient


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
            with self.assertRaises(ValueError):
                config.validate()


class TestAppConfig(unittest.TestCase):
    """Test AppConfig class."""

    @patch.dict(
        os.environ, {"LOG_LEVEL": "DEBUG", "BATCH_SIZE": "20", "RETRY_ATTEMPTS": "5"}
    )
    def test_config_with_env_vars(self):
        """Test configuration with environment variables."""
        config = AppConfig()
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.batch_size, 20)
        self.assertEqual(config.retry_attempts, 5)

    def test_config_defaults(self):
        """Test configuration defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig()
            self.assertEqual(config.log_level, "INFO")
            self.assertEqual(config.batch_size, 10)
            self.assertEqual(config.retry_attempts, 3)


class TestModels(unittest.TestCase):
    """Test data models."""

    def test_jira_issue_data_valid(self):
        """Test valid JiraIssueData creation."""
        issue_data = JiraIssueData(
            project_key="TEST",
            summary="Test Issue",
            description="Test Description",
            issue_type="Task",
        )
        self.assertEqual(issue_data.project_key, "TEST")
        self.assertEqual(issue_data.summary, "Test Issue")

    def test_jira_issue_data_validation(self):
        """Test JiraIssueData validation."""
        with self.assertRaises(ValueError):
            JiraIssueData(
                project_key="",
                summary="Test Issue",
                description="Test Description",
                issue_type="Task",
            )

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

    def test_csv_row_to_issue_data(self):
        """Test conversion to JiraIssueData."""
        row = CSVRow(
            id="1",
            project_key="TEST",
            summary="Test Issue",
            description="Test Description",
            issue_type="Task",
        )
        issue_data = row.to_issue_data()
        self.assertIsInstance(issue_data, JiraIssueData)
        self.assertEqual(issue_data.summary, "Test Issue")

    def test_csv_row_to_subtask_data(self):
        """Test conversion to JiraSubtaskData."""
        row = CSVRow(
            id="1",
            project_key="TEST",
            summary="Test Issue",
            description="Test Description",
            issue_type="Task",
            subtask_summary="Test Subtask",
            subtask_description="Test Subtask Description",
        )
        subtask_data = row.to_subtask_data("parent-123")
        self.assertIsInstance(subtask_data, JiraSubtaskData)
        self.assertEqual(subtask_data.parent_id, "parent-123")


class TestCSVProcessor(unittest.TestCase):
    """Test CSVProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.temp_dir, "test.csv")

        # Create a test CSV file with simpler structure
        csv_content = """ID,Project Key,Summary,Description,Issue Type,Subtask Summary,Subtask Description
1,TEST,Main Issue 1,Description 1,Task,,
2,TEST,Main Issue 2,Description 2,Task,Subtask 2.1,Subtask Description 2.1
"""
        with open(self.csv_file, "w") as f:
            f.write(csv_content)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

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


class TestJiraClient(unittest.TestCase):
    """Test JiraClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.jira_patcher = patch("src.jira_client.Jira")
        self.mock_jira_class = self.jira_patcher.start()
        self.mock_jira_instance = self.mock_jira_class.return_value

        with patch.dict(
            os.environ,
            {
                "JIRA_BASE_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            self.client = JiraClient()
            self.client.jira = self.mock_jira_instance

    def tearDown(self):
        """Tear down test fixtures."""
        self.jira_patcher.stop()

    def test_test_connection_success(self):
        """Test successful connection test."""
        self.mock_jira_instance.server_info.return_value = {
            "serverTitle": "Test Server"
        }
        self.assertTrue(self.client.test_connection())

    def test_test_connection_failure(self):
        """Test failed connection test."""
        self.mock_jira_instance.server_info.side_effect = Exception(
            "Connection failed"
        )
        self.assertFalse(self.client.test_connection())

    def test_create_issue_success(self):
        """Test successful issue creation."""
        self.mock_jira_instance.issue_create.return_value = {
            "key": "TEST-123",
            "id": "12345",
        }

        issue_data = JiraIssueData(
            project_key="TEST",
            summary="Test Issue",
            description="Test Description",
            issue_type="Task",
        )
        created_issue = self.client.create_issue(issue_data.model_dump())

        self.assertIsNotNone(created_issue)
        self.assertEqual(created_issue["key"], "TEST-123")
        self.mock_jira_instance.issue_create.assert_called_once()

    def test_create_issue_failure(self):
        """Test failed issue creation."""
        # Create a mock ApiError that inherits from Exception
        mock_api_error = Exception("Server Error")
        mock_api_error.status_code = 500
        self.mock_jira_instance.issue_create.side_effect = mock_api_error

        issue_data = JiraIssueData(
            project_key="TEST",
            summary="Test Issue",
            description="Test Description",
            issue_type="Task",
        )
        with self.assertRaises(Exception):
            self.client.create_issue(issue_data.model_dump())

    def test_create_subtask_success(self):
        """Test successful subtask creation."""
        self.mock_jira_instance.issue_create.return_value = {
            "key": "TEST-124",
            "id": "12346",
        }

        subtask_data = JiraSubtaskData(
            project_key="TEST",
            summary="Test Subtask",
            description="Test Subtask Description",
            issue_type="Sub-task",
            parent_id="TEST-123",
        )
        created_subtask = self.client.create_subtask(subtask_data.model_dump())

        self.assertIsNotNone(created_subtask)
        self.assertEqual(created_subtask["key"], "TEST-124")
        self.mock_jira_instance.issue_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
