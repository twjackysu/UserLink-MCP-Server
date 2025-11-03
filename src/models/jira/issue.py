"""Jira issue model."""

import logging
from typing import Any, Literal
from pydantic import Field

from ..base import ApiModel, TimestampMixin
from ..constants import EMPTY_STRING

DEFAULT_ID = "0"
from .common import (
    JiraUser,
    JiraStatus,
    JiraIssueType,
    JiraPriority,
    JiraProject,
    JiraComment,
    JiraWorklog,
)

logger = logging.getLogger(__name__)


class JiraIssue(ApiModel, TimestampMixin):
    """
    Model representing a Jira issue.

    This is a simplified model containing the most common fields
    for Jira issues with slim response support.
    """

    id: str = DEFAULT_ID
    key: str = EMPTY_STRING
    summary: str = EMPTY_STRING
    description: str | None = None
    created: str = EMPTY_STRING
    updated: str = EMPTY_STRING
    status: JiraStatus | None = None
    issue_type: JiraIssueType | None = None
    priority: JiraPriority | None = None
    assignee: JiraUser | None = None
    reporter: JiraUser | None = None
    labels: list[str] = Field(default_factory=list)
    components: list[str] = Field(default_factory=list)
    comments: list[JiraComment] = Field(default_factory=list)
    worklogs: list[JiraWorklog] = Field(default_factory=list)
    url: str | None = None
    project: JiraProject | None = None
    duedate: str | None = None
    resolutiondate: str | None = None
    parent: dict | None = None
    subtasks: list[dict] = Field(default_factory=list)
    requested_fields: Literal["*all"] | list[str] | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "JiraIssue":
        """Create JiraIssue from API response."""
        if not data or not isinstance(data, dict):
            return cls()

        # Extract fields
        fields = data.get("fields", {})
        if not isinstance(fields, dict):
            fields = {}

        # Parse user fields
        assignee_data = fields.get("assignee")
        assignee = JiraUser.from_api_response(assignee_data) if assignee_data else None

        reporter_data = fields.get("reporter")
        reporter = JiraUser.from_api_response(reporter_data) if reporter_data else None

        # Parse status
        status_data = fields.get("status")
        status = JiraStatus.from_api_response(status_data) if status_data else None

        # Parse issue type
        issuetype_data = fields.get("issuetype")
        issue_type = (
            JiraIssueType.from_api_response(issuetype_data)
            if issuetype_data
            else None
        )

        # Parse priority
        priority_data = fields.get("priority")
        priority = (
            JiraPriority.from_api_response(priority_data) if priority_data else None
        )

        # Parse project
        project_data = fields.get("project")
        project = JiraProject.from_api_response(project_data) if project_data else None

        # Parse description (handle ADF format)
        description = fields.get("description")
        if isinstance(description, dict):
            description = cls._extract_text_from_adf(description)

        # Parse labels
        labels = fields.get("labels", [])
        if not isinstance(labels, list):
            labels = []

        # Parse components
        components_data = fields.get("components", [])
        components = []
        if isinstance(components_data, list):
            for comp in components_data:
                if isinstance(comp, dict):
                    components.append(comp.get("name", ""))

        # Parse comments
        comments = []
        comment_data = fields.get("comment", {})
        if isinstance(comment_data, dict):
            comments_list = comment_data.get("comments", [])
            if isinstance(comments_list, list):
                for c in comments_list:
                    if c:
                        comments.append(JiraComment.from_api_response(c))

        # Get requested fields from kwargs
        requested_fields = kwargs.get("requested_fields")

        # Build URL
        issue_key = data.get("key", EMPTY_STRING)
        issue_id = data.get("id", DEFAULT_ID)
        url = None
        if issue_key:
            # URL will be set by the service layer with the proper base URL
            url = f"/browse/{issue_key}"

        return cls(
            id=str(issue_id),
            key=issue_key,
            summary=fields.get("summary", EMPTY_STRING),
            description=description,
            created=fields.get("created", EMPTY_STRING),
            updated=fields.get("updated", EMPTY_STRING),
            status=status,
            issue_type=issue_type,
            priority=priority,
            assignee=assignee,
            reporter=reporter,
            labels=labels,
            components=components,
            comments=comments,
            url=url,
            project=project,
            duedate=fields.get("duedate"),
            resolutiondate=fields.get("resolutiondate"),
            parent=fields.get("parent"),
            subtasks=fields.get("subtasks", []),
            requested_fields=requested_fields,
        )

    @staticmethod
    def _extract_text_from_adf(adf: dict) -> str:
        """Extract plain text from ADF (Atlassian Document Format)."""
        if not adf or not isinstance(adf, dict):
            return EMPTY_STRING

        content = adf.get("content", [])
        if not content:
            return EMPTY_STRING

        texts = []

        def extract_from_content(items):
            for item in items:
                if not isinstance(item, dict):
                    continue

                item_type = item.get("type")

                if item_type == "text":
                    text = item.get("text", "")
                    if text:
                        texts.append(text)

                if item_type == "paragraph":
                    paragraph_content = item.get("content", [])
                    extract_from_content(paragraph_content)
                    texts.append("\n")

                if item_type in ["listItem", "orderedList", "bulletList"]:
                    list_content = item.get("content", [])
                    extract_from_content(list_content)

        extract_from_content(content)
        return " ".join(texts).strip()

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        result: dict[str, Any] = {
            "id": self.id,
            "key": self.key,
        }

        # Helper method to check if a field should be included
        def should_include_field(field_name: str) -> bool:
            return (
                self.requested_fields == "*all"
                or not isinstance(self.requested_fields, list)
                or field_name in self.requested_fields
            )

        # Add summary (almost always needed)
        if should_include_field("summary"):
            result["summary"] = self.summary

        # Add URL if available
        if self.url and should_include_field("url"):
            result["url"] = self.url

        # Add description if available
        if self.description and should_include_field("description"):
            result["description"] = self.description

        # Add status if available
        if self.status and should_include_field("status"):
            result["status"] = self.status.to_simplified_dict()

        # Add issue type if available
        if self.issue_type and should_include_field("issuetype"):
            result["issue_type"] = self.issue_type.to_simplified_dict()

        # Add priority if available
        if self.priority and should_include_field("priority"):
            result["priority"] = self.priority.to_simplified_dict()

        # Add project if available
        if self.project and should_include_field("project"):
            result["project"] = self.project.to_simplified_dict()

        # Add dates if available
        if self.duedate and should_include_field("duedate"):
            result["duedate"] = self.duedate

        if self.resolutiondate and should_include_field("resolutiondate"):
            result["resolutiondate"] = self.resolutiondate

        # Add assignee
        if should_include_field("assignee"):
            if self.assignee:
                result["assignee"] = self.assignee.to_simplified_dict()
            else:
                result["assignee"] = {"display_name": "Unassigned"}

        # Add reporter if available
        if self.reporter and should_include_field("reporter"):
            result["reporter"] = self.reporter.to_simplified_dict()

        # Add lists if available
        if self.labels and should_include_field("labels"):
            result["labels"] = self.labels

        if self.components and should_include_field("components"):
            result["components"] = self.components

        # Add timestamps
        if self.created and should_include_field("created"):
            result["created"] = self.created

        if self.updated and should_include_field("updated"):
            result["updated"] = self.updated

        # Add comments if available
        if self.comments and should_include_field("comment"):
            result["comments"] = [
                comment.to_simplified_dict() for comment in self.comments
            ]

        # Add worklogs if available
        if self.worklogs and should_include_field("worklog"):
            result["worklogs"] = [
                worklog.to_simplified_dict() for worklog in self.worklogs
            ]

        # Add parent and subtasks if available
        if self.parent and should_include_field("parent"):
            result["parent"] = self.parent

        if self.subtasks and should_include_field("subtasks"):
            result["subtasks"] = self.subtasks

        return result
