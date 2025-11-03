"""Jira service implementation."""

import logging
from typing import Any, Optional, List, Union
from .base import AtlassianClient
from src.models.jira import JiraIssue, JiraSearchResult, JiraComment, JiraWorklog
from .utils.jira_constants import DEFAULT_READ_JIRA_FIELDS, MINIMAL_JIRA_FIELDS

logger = logging.getLogger(__name__)


class JiraService:
    """Service for Jira operations."""

    def __init__(self, client: AtlassianClient) -> None:
        """
        Initialize Jira service.

        Args:
            client: Atlassian API client instance
        """
        self.client = client
        self.jira = client.jira

    def search_issues(
        self,
        project: Optional[str] = None,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        issue_type: Optional[str] = None,
        max_results: int = 50,
        fields: Optional[Union[str, List[str]]] = None
    ) -> JiraSearchResult:
        """
        Search Jira issues with filters.

        Args:
            project: Project key to filter by (optional)
            status: Status to filter by (optional)
            assignee: Assignee email or name (optional)
            issue_type: Issue type to filter by (optional)
            max_results: Maximum number of results (default: 50)
            fields: List of fields to include (optional)

        Returns:
            JiraSearchResult with matching issues
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

        # Use the common search method
        return self._search_with_models(jql, max_results, fields)

    def search_issues_by_jql(
        self,
        jql: str,
        max_results: int = 50,
        fields: Optional[Union[str, List[str]]] = None
    ) -> JiraSearchResult:
        """
        Search Jira issues using custom JQL query.

        Args:
            jql: Custom JQL query string
            max_results: Maximum number of results (default: 50)
            fields: List of fields to include (optional)

        Returns:
            JiraSearchResult with matching issues
        """
        return self._search_with_models(jql, max_results, fields)

    def _search_with_models(
        self,
        jql: str,
        max_results: int = 50,
        fields: Optional[Union[str, List[str]]] = None
    ) -> JiraSearchResult:
        """
        Internal method to search with Pydantic models.

        Args:
            jql: JQL query string
            max_results: Maximum number of results
            fields: Fields to include - can be:
                - "*all" for all fields
                - comma-separated string (e.g., "summary,status,assignee")
                - list of field names
                - None for default fields

        Returns:
            JiraSearchResult instance
        """
        # Parse fields parameter
        if fields == "*all":
            fields_str = "*all"
            requested_fields = "*all"
        elif isinstance(fields, str) and fields:
            # Comma-separated string
            fields_list = [f.strip() for f in fields.split(",")]
            fields_str = ",".join(fields_list)
            requested_fields = fields_list
        elif isinstance(fields, list) and fields:
            # List of fields
            fields_str = ",".join(fields)
            requested_fields = fields
        else:
            # Default fields for reasonable response size
            fields_str = ",".join(MINIMAL_JIRA_FIELDS)
            requested_fields = MINIMAL_JIRA_FIELDS

        # Execute search
        response = self.jira.jql(jql, limit=max_results, fields=fields_str)

        # Convert to model
        return JiraSearchResult.from_api_response(
            response,
            requested_fields=requested_fields,
            base_url=self.client.jira_url
        )

    def count_issues_by_jql(self, jql: str) -> dict[str, Any]:
        """
        Count Jira issues matching JQL query.
        
        This method fetches all matching issues across multiple pages (if needed)
        and returns the complete count and all issue keys.

        Args:
            jql: JQL query string

        Returns:
            Total count of matching issues and all matching issue keys
        """
        all_issues = []
        start_at = 0
        max_results_per_page = 100  # Jira Cloud API maximum
        total = None
        max_iterations = 10000  # Safety limit to prevent infinite loops
        iteration_count = 0
        
        while iteration_count < max_iterations:
            iteration_count += 1
            
            # Use jql method with pagination
            response = self.jira.jql(
                jql, 
                start=start_at, 
                limit=max_results_per_page,
                fields="key"
            )
            
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

    def get_issue(
        self,
        issue_key: str,
        fields: Optional[Union[str, List[str]]] = None
    ) -> JiraIssue:
        """
        Get details of a specific Jira issue.

        Args:
            issue_key: Issue key (e.g., PROJ-123)
            fields: Fields to include - can be:
                - "*all" for all fields
                - comma-separated string (e.g., "summary,status,assignee")
                - list of field names
                - None for default fields

        Returns:
            JiraIssue instance
        """
        # Parse fields parameter
        if fields == "*all":
            fields_str = "*all"
            requested_fields = "*all"
        elif isinstance(fields, str) and fields:
            # Comma-separated string
            fields_list = [f.strip() for f in fields.split(",")]
            fields_str = ",".join(fields_list)
            requested_fields = fields_list
        elif isinstance(fields, list) and fields:
            # List of fields
            fields_str = ",".join(fields)
            requested_fields = fields
        else:
            # Default fields for issue details
            fields_str = ",".join(DEFAULT_READ_JIRA_FIELDS)
            requested_fields = DEFAULT_READ_JIRA_FIELDS

        response = self.jira.issue(issue_key, fields=fields_str)

        # Convert to model
        issue = JiraIssue.from_api_response(
            response,
            requested_fields=requested_fields
        )

        # Set full URL
        if issue.url:
            issue.url = f"{self.client.jira_url}{issue.url}"

        return issue

    def get_all_projects(self) -> dict[str, Any]:
        """
        Get all Jira projects.

        Returns:
            Dict containing list of all projects
        """
        projects = self.jira.projects()
        return {"projects": projects, "total": len(projects) if isinstance(projects, list) else 0}

    def get_project_issues(
        self,
        project_key: str,
        max_results: int = 50,
        fields: Optional[Union[str, List[str]]] = None
    ) -> JiraSearchResult:
        """
        Get issues for a specific project.

        Args:
            project_key: Project key
            max_results: Maximum number of results (default: 50)
            fields: List of fields to include (optional)

        Returns:
            JiraSearchResult with project issues
        """
        jql = f'project = "{project_key}" ORDER BY created DESC'
        return self._search_with_models(jql, max_results, fields)

    def get_sprint_issues(
        self,
        sprint_id: str,
        max_results: int = 100,
        fields: Optional[Union[str, List[str]]] = None
    ) -> JiraSearchResult:
        """
        Get issues in a specific sprint.

        Args:
            sprint_id: Sprint ID
            max_results: Maximum number of results (default: 100)
            fields: List of fields to include (optional)

        Returns:
            JiraSearchResult with sprint issues
        """
        jql = f'sprint = {sprint_id} ORDER BY rank ASC'
        return self._search_with_models(jql, max_results, fields)

    def get_issue_comments(self, issue_key: str) -> List[JiraComment]:
        """
        Get all comments for a specific Jira issue.

        Args:
            issue_key: Issue key (e.g., PROJ-123)

        Returns:
            List of JiraComment instances
        """
        response = self.jira.issue_get_comments(issue_key)

        comments = []
        if isinstance(response, dict):
            comments_data = response.get("comments", [])
            if isinstance(comments_data, list):
                for comment_data in comments_data:
                    if comment_data:
                        comments.append(JiraComment.from_api_response(comment_data))

        return comments

    def get_issue_worklogs(self, issue_key: str) -> List[JiraWorklog]:
        """
        Get all worklogs (time tracking entries) for a specific Jira issue.

        Args:
            issue_key: Issue key (e.g., PROJ-123)

        Returns:
            List of JiraWorklog instances
        """
        response = self.jira.issue_get_worklog(issue_key)

        worklogs = []
        if isinstance(response, dict):
            worklogs_data = response.get("worklogs", [])
            if isinstance(worklogs_data, list):
                for worklog_data in worklogs_data:
                    if worklog_data:
                        worklogs.append(JiraWorklog.from_api_response(worklog_data))

        return worklogs


