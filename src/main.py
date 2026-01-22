"""
Main module for Jira CSV upload tool.
"""

import logging
import sys
from typing import Dict, Any, Optional, List, Union

from src.config import jira_config, app_config
from src.jira_client import JiraClient
from src.csv_processor import CSVProcessor
from src.constants import SUBTASK_ISSUE_TYPE
from src.models import CSVRow


def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    handlers: List[Union[logging.StreamHandler, logging.FileHandler]] = [
        logging.StreamHandler(sys.stdout)
    ]

    # Try to add file handler, but don't fail if we can't create the log file
    try:
        file_handler = logging.FileHandler("jira_upload.log")
        handlers.append(file_handler)
    except (PermissionError, OSError) as e:
        # If we can't create the log file, just log to stdout
        print(f"Warning: Could not create log file: {e}", file=sys.stderr)

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def create_issue_data(csv_row: CSVRow) -> Dict[str, Any]:
    """
    Create Jira issue data from CSV row.

    Args:
        csv_row: CSVRow object

    Returns:
        Dictionary with Jira issue data
    """
    return {
        "project": {"key": csv_row.project_key},
        "summary": csv_row.summary,
        "description": csv_row.description,
        "issuetype": {"name": csv_row.issue_type},
    }


def create_subtask_data(csv_row: CSVRow, parent_id: str) -> Dict[str, Any]:
    """
    Create Jira subtask data from CSV row.

    Args:
        csv_row: CSVRow object
        parent_id: Parent issue ID

    Returns:
        Dictionary with Jira subtask data
    """
    return {
        "project": {"key": csv_row.project_key},
        "summary": csv_row.subtask_summary,
        "description": csv_row.subtask_description,
        "issuetype": {"name": SUBTASK_ISSUE_TYPE},
        "parent": {"id": parent_id},
    }


def process_issue_group(
    issue_id: str, rows: List[CSVRow], jira_client: JiraClient, base_url: str
) -> Dict[str, Any]:
    """
    Process a group of rows for a single issue.

    Args:
        issue_id: Issue ID
        rows: List of CSVRow objects for this issue
        jira_client: JiraClient instance
        base_url: Jira base URL

    Returns:
        Dictionary with processing results
    """
    logger = logging.getLogger(__name__)
    results: Dict[str, Any] = {
        "issue_id": issue_id,
        "main_issue": None,
        "subtasks": [],
        "errors": [],
    }

    # Find the main issue row (the one with summary and description)
    main_issue_row = None
    for row in rows:
        if row.summary and row.description:
            main_issue_row = row
            break

    if not main_issue_row:
        error_msg = f"No main issue data found for issue ID {issue_id}"
        logger.error(error_msg)
        results["errors"].append(error_msg)
        return results

    try:
        # Create main issue
        issue_data = create_issue_data(main_issue_row)
        main_issue = jira_client.create_issue(issue_data)

        results["main_issue"] = {
            "key": main_issue["key"],
            "id": main_issue["id"],
            "url": f"{base_url}/browse/{main_issue['key']}",
            "summary": main_issue_row.summary,
        }

        logger.info(f"Created main issue {main_issue['key']}: {main_issue_row.summary}")

        # Create subtasks
        for row in rows:
            if row.has_subtask():
                try:
                    subtask_data = create_subtask_data(row, main_issue["id"])
                    subtask = jira_client.create_subtask(subtask_data)

                    subtask_result = {
                        "key": subtask["key"],
                        "id": subtask["id"],
                        "url": f"{base_url}/browse/{subtask['key']}",
                        "summary": row.subtask_summary,
                    }

                    results["subtasks"].append(subtask_result)
                    logger.info(
                        f"Created subtask {subtask['key']}: {row.subtask_summary}"
                    )

                except Exception as e:
                    error_msg = f"Failed to create subtask '{row.subtask_summary}': {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

    except Exception as e:
        error_msg = f"Failed to create main issue '{main_issue_row.summary}': {e}"
        logger.error(error_msg)
        results["errors"].append(error_msg)

    return results


def main(csv_file_path: Optional[str] = None) -> bool:
    """
    Main function to process CSV and create Jira issues.

    Args:
        csv_file_path: Optional path to CSV file. If None, uses default from config.

    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        # Setup logging
        setup_logging(app_config.log_level)
        logger.info("Starting Jira CSV upload process")

        # Validate configuration
        jira_config.validate()
        logger.info("Configuration validated successfully")

        # Initialize Jira client
        jira_client = JiraClient()

        # Test Jira connection
        if not jira_client.test_connection():
            logger.error("Failed to connect to Jira. Please check your credentials.")
            return False

        # Initialize CSV processor
        csv_path = csv_file_path or app_config.default_csv_path
        csv_processor = CSVProcessor(csv_path)

        # Read and validate CSV
        logger.info(f"Processing CSV file: {csv_path}")
        rows = csv_processor.read_and_validate_csv()

        if not rows:
            logger.warning("No valid rows found in CSV file")
            return True

        # Group rows by issue ID
        issue_groups = csv_processor.get_issue_groups(rows)

        # Validate issue groups
        if not csv_processor.validate_issue_groups(issue_groups):
            logger.error("Issue group validation failed")
            return False

        # Process each issue group
        all_results = []
        success_count = 0
        error_count = 0

        for issue_id, group_rows in issue_groups.items():
            logger.info(
                f"Processing issue group {issue_id} " f"with {len(group_rows)} rows"
            )

            result = process_issue_group(
                issue_id, group_rows, jira_client, jira_config.base_url
            )

            all_results.append(result)

            if result["errors"]:
                error_count += 1
            else:
                success_count += 1

        # Print summary
        logger.info("=" * 50)
        logger.info("PROCESSING SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total issue groups processed: {len(all_results)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"With errors: {error_count}")

        for result in all_results:
            if result["main_issue"]:
                logger.info(
                    f"Issue {result['main_issue']['key']}: {result['main_issue']['summary']}"  # noqa: E501
                )
                logger.info(f"  URL: {result['main_issue']['url']}")

                if result["subtasks"]:
                    logger.info(f"  Subtasks created: {len(result['subtasks'])}")
                    for subtask in result["subtasks"]:
                        logger.info(f"    - {subtask['key']}: {subtask['summary']}")
                        logger.info(f"      URL: {subtask['url']}")

                if result["errors"]:
                    logger.warning(f"  Errors: {len(result['errors'])}")
                    for error in result["errors"]:
                        logger.warning(f"    - {error}")

        logger.info("Jira CSV upload process completed")
        return error_count == 0

    except Exception as e:
        logger.error(f"Unexpected error in main process: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
