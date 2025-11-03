"""Constants for Jira operations."""

# Default fields returned by Jira read operations
DEFAULT_READ_JIRA_FIELDS = [
    "summary",
    "description",
    "status",
    "assignee",
    "reporter",
    "labels",
    "priority",
    "created",
    "updated",
    "issuetype",
]

# Minimal fields for list operations
MINIMAL_JIRA_FIELDS = [
    "summary",
    "status",
    "assignee",
    "issuetype",
    "priority",
    "created",
    "updated",
]
