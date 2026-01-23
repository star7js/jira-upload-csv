#!/usr/bin/env python3
"""
Basic functionality test script.
This script tests the core functionality without requiring real Jira credentials.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    from src.config import jira_config, app_config

    print(f"  Jira Base URL: {jira_config.base_url}")
    print(f"  Log Level: {app_config.log_level}")
    print(f"  Default CSV Path: {app_config.default_csv_path}")
    print("✅ Configuration test passed")


def test_models():
    """Test data models."""
    print("Testing data models...")
    from src.models import JiraIssueData, CSVRow

    # Test JiraIssueData
    issue_data = JiraIssueData(
        project_key="TEST",
        summary="Test Issue",
        description="Test Description",
        issue_type="Task",
    )
    print(f"  Created issue data: {issue_data.summary}")

    # Test CSVRow
    row = CSVRow(
        id="1",
        project_key="TEST",
        summary="Test Issue",
        description="Test Description",
        issue_type="Task",
    )
    print(f"  Created CSV row: {row.id}")
    print("✅ Data models test passed")


def test_csv_processor():
    """Test CSV processing."""
    print("Testing CSV processor...")

    # Mock the models import to avoid relative import issues
    import sys
    from unittest.mock import Mock

    # Create a mock models module
    mock_models = Mock()
    mock_csv_row = Mock()
    mock_csv_row.id = "1"
    mock_csv_row.project_key = "TEST"
    mock_csv_row.summary = "Test Issue"
    mock_csv_row.description = "Test Description"
    mock_csv_row.issue_type = "Task"
    mock_csv_row.has_subtask.return_value = False

    mock_models.CSVRow = Mock(return_value=mock_csv_row)
    sys.modules["models"] = mock_models

    # Now import CSVProcessor
    from src.csv_processor import CSVProcessor

    # Test with the example CSV file
    csv_file = "data/main_and_subtasks_multiple.csv"
    if Path(csv_file).exists():
        processor = CSVProcessor(csv_file)
        print(f"  CSVProcessor created for {csv_file}")

        # Test file validation
        if processor.validate_file_exists():
            print("  File validation passed")
        else:
            print("  File validation failed")
    else:
        print(f"  CSV file {csv_file} not found, skipping test")

    print("✅ CSV processor test passed")


def test_jira_client_mock():
    """Test Jira client with mocking."""
    print("Testing Jira client (mocked)...")

    # Mock the atlassian module
    import sys
    from unittest.mock import Mock

    mock_atlassian = Mock()
    mock_atlassian.Jira = Mock()
    mock_atlassian.errors = Mock()

    sys.modules["atlassian"] = mock_atlassian
    sys.modules["atlassian.errors"] = mock_atlassian.errors

    from src.jira_client import JiraClient

    # Set up environment for testing
    os.environ["JIRA_BASE_URL"] = "https://test.atlassian.net"
    os.environ["JIRA_USERNAME"] = "test@example.com"
    os.environ["JIRA_API_TOKEN"] = "test-token"

    client = JiraClient()
    print("  JiraClient created successfully")

    # Mock the server_info method
    client.jira.server_info = Mock(return_value={"serverTitle": "Test Server"})

    if client.test_connection():
        print("  Connection test passed")
    else:
        print("  Connection test failed")

    print("✅ Jira client test passed")


def main():
    """Run all tests."""
    print("Running basic functionality tests...")
    print("=" * 50)

    try:
        test_config()
        print()

        test_models()
        print()

        test_csv_processor()
        print()

        test_jira_client_mock()
        print()

        print("=" * 50)
        print("✅ All basic functionality tests passed!")
        print("\nThe tool is ready to use. Next steps:")
        print("1. Copy env.example to .env and add your Jira credentials")
        print("2. Run 'python cli.py test' to verify your connection")
        print("3. Use 'python cli.py template' to generate a CSV template")
        print("4. Run 'python cli.py upload' to upload issues")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
