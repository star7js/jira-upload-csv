"""
Data models for Jira CSV upload tool.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CSVRow(BaseModel):
    """Model for CSV row data."""

    id: str = Field(..., description="Unique identifier for grouping rows")
    project_key: str = Field(..., description="Jira project key")
    summary: Optional[str] = Field(None, description="Issue summary")
    description: Optional[str] = Field(None, description="Issue description")
    issue_type: Optional[str] = Field(None, description="Issue type")
    subtask_summary: Optional[str] = Field(None, description="Subtask summary")
    subtask_description: Optional[str] = Field(None, description="Subtask description")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("ID cannot be empty")
        return v.strip()

    @field_validator("project_key")
    @classmethod
    def validate_project_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Project key cannot be empty")
        return v.strip().upper()

    @field_validator(
        "summary",
        "description",
        "issue_type",
        "subtask_summary",
        "subtask_description",
    )
    @classmethod
    def strip_or_none(cls, v: Optional[str]) -> Optional[str]:
        if v is None or not v.strip():
            return None
        return v.strip()

    def has_subtask(self) -> bool:
        """Check if this row contains subtask data."""
        return bool(self.subtask_summary and self.subtask_description)

    def has_main_issue(self) -> bool:
        """Check if this row contains main issue data."""
        return bool(self.summary and self.description and self.issue_type)
