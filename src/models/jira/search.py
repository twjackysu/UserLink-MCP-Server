"""Jira search result models."""

import logging
from typing import Any
from pydantic import Field

from ..base import ApiModel
from .issue import JiraIssue

logger = logging.getLogger(__name__)


class JiraSearchResult(ApiModel):
    """Model representing a Jira search (JQL) result."""

    total: int = 0
    start_at: int = 0
    max_results: int = 0
    issues: list[JiraIssue] = Field(default_factory=list)

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "JiraSearchResult":
        """
        Create a JiraSearchResult from a Jira API response.

        Args:
            data: The search result data from the Jira API
            **kwargs: Additional arguments (e.g., requested_fields, base_url)

        Returns:
            A JiraSearchResult instance
        """
        if not data or not isinstance(data, dict):
            logger.debug("Received non-dictionary data, returning default instance")
            return cls()

        issues = []
        issues_data = data.get("issues", [])
        if isinstance(issues_data, list):
            for issue_data in issues_data:
                if issue_data:
                    issue = JiraIssue.from_api_response(issue_data, **kwargs)
                    
                    # Set full URL if base_url is provided
                    base_url = kwargs.get("base_url")
                    if base_url and issue.url:
                        issue.url = f"{base_url}{issue.url}"
                    
                    issues.append(issue)

        raw_total = data.get("total")
        raw_start_at = data.get("startAt")
        raw_max_results = data.get("maxResults")

        try:
            total = int(raw_total) if raw_total is not None else 0
        except (ValueError, TypeError):
            total = 0

        try:
            start_at = int(raw_start_at) if raw_start_at is not None else 0
        except (ValueError, TypeError):
            start_at = 0

        try:
            max_results = int(raw_max_results) if raw_max_results is not None else 0
        except (ValueError, TypeError):
            max_results = 0

        return cls(
            total=total,
            start_at=start_at,
            max_results=max_results,
            issues=issues,
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        return {
            "total": self.total,
            "start_at": self.start_at,
            "max_results": self.max_results,
            "issues": [issue.to_simplified_dict() for issue in self.issues],
        }
