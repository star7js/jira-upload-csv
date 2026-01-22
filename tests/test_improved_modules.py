"""
Comprehensive tests for improved Jira CSV upload modules.
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
import os

# Mock the atlassian import to avoid real network calls
with patch.dict(
    "sys.modules",
    {
        "atlassian": Mock(),
        "atlassian.errors": Mock(),
    },
):
    # Import modules after mocking
    from src.config import JiraConfig, AppConfig  # noqa
    from src.models import JiraIssueData, JiraSubtaskData, CSVRow
    from src.csv_processor import CSVProcessor


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
        # fmt: off
        csv_content = """ID,Project Key,Summary,Description,Issue Type,Subtask Summary,Subtask Description
1,TEST,Main Issue 1,Description 1,Task,,
2,TEST,Main Issue 2,Description 2,Task,Subtask 2.1,Subtask Description 2.1
"""  # noqa: E501
        # fmt: on
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
        # Don't patch during setup to avoid PyO3 issues
        # We'll patch in individual test methods instead

        with patch.dict(
            os.environ,
            {
                "JIRA_BASE_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            # Import JiraClient here to avoid PyO3 issues
            from src.jira_client import JiraClient  # noqa: F811

            self.client = JiraClient()

    def test_test_connection_success(self):
        """Test successful connection test."""
        with patch("src.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.server_info.return_value = {"serverTitle": "Test Server"}
            self.client.jira = mock_jira_instance
            self.assertTrue(self.client.test_connection())

    def test_test_connection_failure(self):
        """Test failed connection test."""
        with patch("src.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.server_info.side_effect = Exception("Connection failed")
            self.client.jira = mock_jira_instance
            self.assertFalse(self.client.test_connection())

    def test_create_issue_success(self):
        """Test successful issue creation."""
        with patch("src.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.issue_create.return_value = {
                "key": "TEST-123",
                "id": "12345",
            }
            self.client.jira = mock_jira_instance

            issue_data = JiraIssueData(
                project_key="TEST",
                summary="Test Issue",
                description="Test Description",
                issue_type="Task",
            )
            created_issue = self.client.create_issue(issue_data.model_dump())

            self.assertIsNotNone(created_issue)
            self.assertEqual(created_issue["key"], "TEST-123")
            mock_jira_instance.issue_create.assert_called_once()

    def test_create_issue_failure(self):
        """Test failed issue creation."""
        with patch("src.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            # Create a mock exception with status_code
            mock_exception = Exception("Server Error")
            mock_exception.status_code = 500
            mock_jira_instance.issue_create.side_effect = mock_exception
            self.client.jira = mock_jira_instance

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
        with patch("src.jira_client.Jira") as mock_jira_class:
            mock_jira_instance = mock_jira_class.return_value
            mock_jira_instance.issue_create.return_value = {
                "key": "TEST-124",
                "id": "12346",
            }
            self.client.jira = mock_jira_instance

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
            mock_jira_instance.issue_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
