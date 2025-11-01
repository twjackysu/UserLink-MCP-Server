"""Jira service implementation."""

from typing import Any, Optional, List
from .base import AtlassianClient


class JiraService:
    """Service for Jira operations."""

    def __init__(self, client: AtlassianClient) -> None:
        """
        Initialize Jira service.

        Args:
            client: Atlassian API client instance
        """
        self.client = client

    async def search_issues(
        self,
        project: Optional[str] = None,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        issue_type: Optional[str] = None,
        max_results: int = 50
    ) -> dict[str, Any]:
        """
        Search Jira issues with filters.

        Args:
            project: Project key to filter by (optional)
            status: Status to filter by (optional)
            assignee: Assignee email or name (optional)
            issue_type: Issue type to filter by (optional)
            max_results: Maximum number of results (default: 50)

        Returns:
            Search results containing matching issues
        """
        # Build JQL query
        jql_parts = []

        if project:
            jql_parts.append(f'project = "{project}"')
        if status:
            jql_parts.append(f'status = "{status}"')
        if assignee:
            jql_parts.append(f'assignee = "{assignee}"')
        if issue_type:
            jql_parts.append(f'issuetype = "{issue_type}"')

        jql = " AND ".join(jql_parts) if jql_parts else "ORDER BY created DESC"

        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,created,updated,priority,issuetype,description"
        }
        return await self.client.get(endpoint, params=params)

    async def search_issues_by_jql(
        self,
        jql: str,
        max_results: int = 50
    ) -> dict[str, Any]:
        """
        Search Jira issues using custom JQL query.

        Args:
            jql: Custom JQL query string
            max_results: Maximum number of results (default: 50)

        Returns:
            Search results containing matching issues
        """
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,created,updated,priority,issuetype,description"
        }
        return await self.client.get(endpoint, params=params)

    async def count_issues_by_jql(self, jql: str) -> dict[str, Any]:
        """
        Count Jira issues matching JQL query.

        Args:
            jql: JQL query string

        Returns:
            Count of matching issues
        """
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": 0,  # We only want the count
            "fields": "summary"  # Minimal fields
        }
        response = await self.client.get(endpoint, params=params)
        return {"total": response.get("total", 0), "jql": jql}

    async def get_issue(self, issue_key: str) -> dict[str, Any]:
        """
        Get details of a specific Jira issue.

        Args:
            issue_key: Issue key (e.g., PROJ-123)

        Returns:
            Issue details
        """
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/issue/{issue_key}"
        return await self.client.get(endpoint)

    async def get_all_projects(self) -> dict[str, Any]:
        """
        Get all Jira projects.

        Returns:
            List of all projects
        """
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/project"
        return await self.client.get(endpoint)

    async def get_project_issues(
        self,
        project_key: str,
        max_results: int = 50
    ) -> dict[str, Any]:
        """
        Get issues for a specific project.

        Args:
            project_key: Project key
            max_results: Maximum number of results (default: 50)

        Returns:
            Issues in the project
        """
        jql = f'project = "{project_key}" ORDER BY created DESC'
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,created,updated,priority,issuetype,description"
        }
        return await self.client.get(endpoint, params=params)

    async def get_sprint_issues(
        self,
        sprint_id: str,
        max_results: int = 100
    ) -> dict[str, Any]:
        """
        Get issues in a specific sprint.

        Args:
            sprint_id: Sprint ID
            max_results: Maximum number of results (default: 100)

        Returns:
            Issues in the sprint
        """
        jql = f'sprint = {sprint_id} ORDER BY rank ASC'
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,created,updated,priority,issuetype,description,customfield_10016"
        }
        return await self.client.get(endpoint, params=params)
