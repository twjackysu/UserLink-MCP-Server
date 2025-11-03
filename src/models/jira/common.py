"""Common Jira models."""

from typing import Any
from pydantic import Field

from ..base import ApiModel
from ..constants import EMPTY_STRING

DEFAULT_ID = "0"


class JiraUser(ApiModel):
    """Jira user model."""

    account_id: str = EMPTY_STRING
    display_name: str = EMPTY_STRING
    email: str | None = None
    active: bool = True
    avatar_url: str | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "JiraUser":
        """Create JiraUser from API response."""
        if not data or not isinstance(data, dict):
            return cls()

        return cls(
            account_id=data.get("accountId", EMPTY_STRING),
            display_name=data.get("displayName", EMPTY_STRING),
            email=data.get("emailAddress"),
            active=data.get("active", True),
            avatar_url=data.get("avatarUrls", {}).get("48x48"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary."""
        result = {
            "account_id": self.account_id,
            "display_name": self.display_name,
        }
        if self.email:
            result["email"] = self.email
        return result


class JiraStatus(ApiModel):
    """Jira status model."""

    id: str = DEFAULT_ID
    name: str = EMPTY_STRING
    category: str | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "JiraStatus":
        """Create JiraStatus from API response."""
        if not data or not isinstance(data, dict):
            return cls()

        return cls(
            id=str(data.get("id", DEFAULT_ID)),
            name=data.get("name", EMPTY_STRING),
            category=data.get("statusCategory", {}).get("name"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary."""
        result = {"name": self.name}
        if self.category:
            result["category"] = self.category
        return result


class JiraIssueType(ApiModel):
    """Jira issue type model."""

    id: str = DEFAULT_ID
    name: str = EMPTY_STRING
    subtask: bool = False

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "JiraIssueType":
        """Create JiraIssueType from API response."""
        if not data or not isinstance(data, dict):
            return cls()

        return cls(
            id=str(data.get("id", DEFAULT_ID)),
            name=data.get("name", EMPTY_STRING),
            subtask=data.get("subtask", False),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary."""
        return {"name": self.name, "subtask": self.subtask}


class JiraPriority(ApiModel):
    """Jira priority model."""

    id: str = DEFAULT_ID
    name: str = EMPTY_STRING

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "JiraPriority":
        """Create JiraPriority from API response."""
        if not data or not isinstance(data, dict):
            return cls()

        return cls(
            id=str(data.get("id", DEFAULT_ID)),
            name=data.get("name", EMPTY_STRING),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary."""
        return {"name": self.name}


class JiraProject(ApiModel):
    """Jira project model."""

    id: str = DEFAULT_ID
    key: str = EMPTY_STRING
    name: str = EMPTY_STRING

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "JiraProject":
        """Create JiraProject from API response."""
        if not data or not isinstance(data, dict):
            return cls()

        return cls(
            id=str(data.get("id", DEFAULT_ID)),
            key=data.get("key", EMPTY_STRING),
            name=data.get("name", EMPTY_STRING),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary."""
        return {"key": self.key, "name": self.name}


class JiraComment(ApiModel):
    """Jira comment model."""

    id: str = DEFAULT_ID
    author: JiraUser | None = None
    body: str = EMPTY_STRING
    created: str = EMPTY_STRING
    updated: str = EMPTY_STRING

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "JiraComment":
        """Create JiraComment from API response."""
        if not data or not isinstance(data, dict):
            return cls()

        author_data = data.get("author")
        author = JiraUser.from_api_response(author_data) if author_data else None

        # Handle ADF (Atlassian Document Format) or plain text
        body = data.get("body", EMPTY_STRING)
        if isinstance(body, dict):
            # ADF format - extract plain text
            body = cls._extract_text_from_adf(body)

        return cls(
            id=str(data.get("id", DEFAULT_ID)),
            author=author,
            body=body,
            created=data.get("created", EMPTY_STRING),
            updated=data.get("updated", EMPTY_STRING),
        )

    @staticmethod
    def _extract_text_from_adf(adf: dict) -> str:
        """Extract plain text from ADF content."""
        if not adf or not isinstance(adf, dict):
            return EMPTY_STRING

        content = adf.get("content", [])
        if not content:
            return EMPTY_STRING

        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "paragraph":
                    paragraph_content = item.get("content", [])
                    for text_item in paragraph_content:
                        if isinstance(text_item, dict) and text_item.get("type") == "text":
                            texts.append(text_item.get("text", ""))
        
        return " ".join(texts)

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary."""
        result = {
            "id": self.id,
            "body": self.body,
            "created": self.created,
        }
        if self.author:
            result["author"] = self.author.to_simplified_dict()
        return result


class JiraWorklog(ApiModel):
    """Jira worklog model."""

    id: str = DEFAULT_ID
    author: JiraUser | None = None
    comment: str = EMPTY_STRING
    time_spent: str = EMPTY_STRING
    time_spent_seconds: int = 0
    created: str = EMPTY_STRING
    started: str = EMPTY_STRING

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "JiraWorklog":
        """Create JiraWorklog from API response."""
        if not data or not isinstance(data, dict):
            return cls()

        author_data = data.get("author")
        author = JiraUser.from_api_response(author_data) if author_data else None

        # Handle ADF or plain text comment
        comment = data.get("comment", EMPTY_STRING)
        if isinstance(comment, dict):
            comment = JiraComment._extract_text_from_adf(comment)

        return cls(
            id=str(data.get("id", DEFAULT_ID)),
            author=author,
            comment=comment,
            time_spent=data.get("timeSpent", EMPTY_STRING),
            time_spent_seconds=data.get("timeSpentSeconds", 0),
            created=data.get("created", EMPTY_STRING),
            started=data.get("started", EMPTY_STRING),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary."""
        result = {
            "id": self.id,
            "time_spent": self.time_spent,
            "started": self.started,
        }
        if self.author:
            result["author"] = self.author.to_simplified_dict()
        if self.comment:
            result["comment"] = self.comment
        return result
