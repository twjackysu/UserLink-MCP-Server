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

        jql = " AND ".join(jql_parts) if jql_parts else "project is not EMPTY ORDER BY created DESC"

        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search/jql"
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
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search/jql"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,created,updated,priority,issuetype,description"
        }
        return await self.client.get(endpoint, params=params)

    async def count_issues_by_jql(self, jql: str) -> dict[str, Any]:
        """
        Count Jira issues matching JQL query.
        
        This method fetches all matching issues across multiple pages (if needed)
        and returns the complete count and all issue keys.
        Uses maxResults=100 (Jira Cloud API maximum) to minimize API calls.

        Args:
            jql: JQL query string

        Returns:
            Total count of matching issues and all matching issue keys
        """
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search/jql"
        all_issues = []
        start_at = 0
        max_results_per_page = 100  # Jira Cloud API maximum
        total = None
        max_iterations = 10000  # Safety limit to prevent infinite loops
        iteration_count = 0
        
        while iteration_count < max_iterations:
            iteration_count += 1
            
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results_per_page,
                "fields": "key"  # Only fetch the key field to minimize data transfer
            }
            response = await self.client.get(endpoint, params=params)
            
            issues = response.get("issues", [])
            all_issues.extend(issues)
            total = response.get("total", 0)
            
            # Stop if we've fetched all results or got no more issues
            if len(issues) == 0 or len(all_issues) >= total:
                break
            
            start_at += max_results_per_page
        
        return {
            "count": len(all_issues),
            "total_available": total if total is not None else len(all_issues),
            "jql": jql,
            "issue_keys": [issue.get("key") for issue in all_issues]
        }

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
            Dict containing list of all projects
        """
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/project"
        projects = await self.client.get(endpoint)
        return {"projects": projects, "total": len(projects) if isinstance(projects, list) else 0}

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
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search/jql"
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
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/search/jql"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,created,updated,priority,issuetype,description,customfield_10016"
        }
        return await self.client.get(endpoint, params=params)

    async def get_issue_comments(self, issue_key: str) -> dict[str, Any]:
        """
        Get all comments for a specific Jira issue.

        Args:
            issue_key: Issue key (e.g., PROJ-123)

        Returns:
            List of comments with author, creation time, and content
        """
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/issue/{issue_key}/comment"
        return await self.client.get(endpoint)

    async def get_issue_worklogs(self, issue_key: str) -> dict[str, Any]:
        """
        Get all worklogs (time tracking entries) for a specific Jira issue.

        Args:
            issue_key: Issue key (e.g., PROJ-123)

        Returns:
            List of worklogs with author, time spent, and work description
        """
        endpoint = f"/ex/jira/{self.client.cloud_id}/rest/api/3/issue/{issue_key}/worklog"
        return await self.client.get(endpoint)
