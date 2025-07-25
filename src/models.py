"""
Data models for Jira CSV upload tool.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class JiraIssueData(BaseModel):
    """Model for Jira issue data."""

    project_key: str = Field(..., description="Jira project key")
    summary: str = Field(..., description="Issue summary")
    description: str = Field(..., description="Issue description")
    issue_type: str = Field(..., description="Issue type (e.g., Task, Bug, Story)")

    @field_validator("project_key")
    @classmethod
    def validate_project_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Project key cannot be empty")
        return v.strip().upper()

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Summary cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()


class JiraSubtaskData(JiraIssueData):
    """Model for Jira subtask data."""

    parent_id: Optional[str] = Field(None, description="Parent issue ID")

    @field_validator("parent_id")
    @classmethod
    def validate_parent_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Parent ID cannot be empty if provided")
        return v.strip() if v else None


class CSVRow(BaseModel):
    """Model for CSV row data."""

    id: str = Field(..., description="Row ID")
    project_key: str = Field(..., description="Project key")
    summary: str = Field(..., description="Issue summary")
    description: str = Field(..., description="Issue description")
    issue_type: str = Field(..., description="Issue type")
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
    def validate_project_key_csv(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Project key cannot be empty")
        return v.strip().upper()

    @field_validator("summary")
    @classmethod
    def validate_summary_csv(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Summary cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description_csv(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

    @field_validator("issue_type")
    @classmethod
    def validate_issue_type_csv(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Issue type cannot be empty")
        return v.strip()

    def has_subtask(self) -> bool:
        """Check if this row contains subtask data."""
        return bool(self.subtask_summary and self.subtask_description)

    def to_issue_data(self) -> JiraIssueData:
        """Convert to JiraIssueData."""
        return JiraIssueData(
            project_key=self.project_key,
            summary=self.summary,
            description=self.description,
            issue_type=self.issue_type,
        )

    def to_subtask_data(self, parent_id: str) -> "JiraSubtaskData":
        """Convert to JiraSubtaskData."""
        if not self.has_subtask():
            raise ValueError("Row does not contain subtask data")

        return JiraSubtaskData(
            project_key=self.project_key,
            summary=self.subtask_summary or "",
            description=self.subtask_description or "",
            issue_type="Sub-task",
            parent_id=parent_id,
        )
