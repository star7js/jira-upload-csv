"""
CSV processing module with validation and error handling.
"""

import csv
import logging
from pathlib import Path
from typing import List, Dict
from pydantic import ValidationError

from jira_csv_upload.models import CSVRow

logger = logging.getLogger(__name__)


class CSVProcessor:
    """CSV processor with validation and error handling."""

    def __init__(self, file_path: str):
        """
        Initialize CSV processor.

        Args:
            file_path: Path to the CSV file
        """
        self.file_path = Path(file_path)
        self.required_columns = [
            "ID",
            "Project Key",
            "Summary",
            "Description",
            "Issue Type",
            "Subtask Summary",
            "Subtask Description",
        ]

    def validate_file_exists(self) -> bool:
        """
        Validate that the CSV file exists.

        Returns:
            True if file exists, False otherwise
        """
        if not self.file_path.exists():
            logger.error(f"CSV file not found: {self.file_path}")
            return False
        return True

    def validate_csv_structure(self, reader: csv.DictReader) -> bool:
        """
        Validate CSV structure and required columns.

        Args:
            reader: CSV DictReader object

        Returns:
            True if structure is valid, False otherwise
        """
        fieldnames = reader.fieldnames
        if not fieldnames:
            logger.error("CSV file has no headers")
            return False

        missing_columns = set(self.required_columns) - set(fieldnames)
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False

        logger.info(f"CSV structure validated. Found columns: {fieldnames}")
        return True

    def read_and_validate_csv(self) -> List[CSVRow]:
        """
        Read and validate CSV data.

        Returns:
            List of validated CSVRow objects

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV structure is invalid or any row fails validation
        """
        if not self.validate_file_exists():
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")

        validated_rows = []
        errors = []

        try:
            with open(self.file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                if not self.validate_csv_structure(reader):
                    raise ValueError("Invalid CSV structure")

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 because row 1 is header
                    try:
                        csv_row = CSVRow(
                            id=row["ID"],
                            project_key=row["Project Key"],
                            summary=row["Summary"] or None,
                            description=row["Description"] or None,
                            issue_type=row["Issue Type"] or None,
                            subtask_summary=row["Subtask Summary"] or None,
                            subtask_description=row["Subtask Description"] or None,
                        )
                        validated_rows.append(csv_row)

                    except ValidationError as e:
                        error_msg = f"Row {row_num}: Validation error - {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)

        except (ValueError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise

        if errors:
            raise ValueError(
                f"CSV contains {len(errors)} invalid row(s); "
                "fix them and re-run (see log for details)"
            )

        logger.info(f"Successfully processed {len(validated_rows)} valid rows from CSV")
        return validated_rows

    def get_issue_groups(self, rows: List[CSVRow]) -> Dict[str, List[CSVRow]]:
        """
        Group CSV rows by issue ID.

        Args:
            rows: List of validated CSVRow objects

        Returns:
            Dictionary mapping issue IDs to lists of rows
        """
        issue_groups: Dict[str, List[CSVRow]] = {}

        for row in rows:
            issue_groups.setdefault(row.id, []).append(row)

        logger.info(f"Grouped {len(rows)} rows into {len(issue_groups)} issue groups")
        return issue_groups

    def validate_issue_groups(self, issue_groups: Dict[str, List[CSVRow]]) -> bool:
        """
        Validate that each issue group has exactly one main issue row.

        Args:
            issue_groups: Dictionary of issue groups

        Returns:
            True if all groups are valid, False otherwise
        """
        errors = []

        for issue_id, rows in issue_groups.items():
            main_issue_rows = [row for row in rows if row.has_main_issue()]

            if len(main_issue_rows) == 0:
                errors.append(
                    f"Issue ID {issue_id}: No main issue data found "
                    "(Summary, Description, and Issue Type are all required)"
                )
            elif len(main_issue_rows) > 1:
                errors.append(f"Issue ID {issue_id}: Multiple main issue rows found")

        if errors:
            for error in errors:
                logger.error(error)
            return False

        logger.info("All issue groups validated successfully")
        return True
