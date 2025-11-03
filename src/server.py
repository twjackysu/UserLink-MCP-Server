"""Main MCP Server for UserLink - Tool registration and server setup."""

from fastmcp import FastMCP
from typing import Any

from src.config import config
from src.middlewares import HeadersCaptureMiddleware
from src.middlewares.headers import current_request_headers
from src.utils.auth import (
    extract_microsoft_token,
    extract_atlassian_token,
    extract_atlassian_cloud_id,
    validate_token,
    validate_cloud_id,
    ProviderTokenHeader
)
from src.providers.atlassian.base import AtlassianClient
from src.providers.atlassian.jira import JiraService
from src.providers.atlassian.confluence import ConfluenceService
from src.providers.microsoft.base import MicrosoftGraphClient
from src.providers.microsoft.teams import TeamsService
from src.providers.microsoft.outlook import OutlookService

# Initialize FastMCP server
mcp = FastMCP("UserLink MCP Server")

# Add headers capture middleware
mcp.add_middleware(HeadersCaptureMiddleware())


# Helper functions to get access tokens from ContextVar
def _get_microsoft_token() -> str:
    """
    Extract and validate Microsoft Graph access token from request headers.

    Returns:
        Validated Microsoft Graph access token

    Raises:
        ValueError: If token is missing or invalid
    """
    import logging
    logger = logging.getLogger(__name__)

    headers = current_request_headers.get()
    logger.info(f"🔍 _get_microsoft_token: Retrieved {len(headers)} headers from ContextVar")

    # Log header keys (but not values) for debugging
    header_keys = list(headers.keys())
    logger.info(f"🔍 Available header keys: {header_keys}")

    token = extract_microsoft_token(headers)
    logger.info(f"🔍 Extracted token: {'present' if token else 'missing'}")

    if not token or not validate_token(token):
        raise ValueError(
            "Invalid or missing Microsoft Graph token in request headers (x-microsoft-graph-token)"
        )

    return token


def _get_atlassian_token() -> str:
    """
    Extract and validate Atlassian access token from request headers.

    Returns:
        Validated Atlassian access token

    Raises:
        ValueError: If token is missing or invalid
    """
    headers = current_request_headers.get()
    token = extract_atlassian_token(headers)

    if not token or not validate_token(token):
        raise ValueError(
            "Invalid or missing Atlassian token in request headers (x-atlassian-token)"
        )

    return token


def _get_atlassian_cloud_id() -> str:
    """
    Extract and validate Atlassian Cloud ID from request headers.

    Returns:
        Validated Atlassian Cloud ID

    Raises:
        ValueError: If cloud ID is missing or invalid
    """
    headers = current_request_headers.get()
    cloud_id = extract_atlassian_cloud_id(headers)

    if not cloud_id or not validate_cloud_id(cloud_id):
        raise ValueError(
            "Invalid or missing Atlassian Cloud ID in request headers (x-atlassian-cloud-id)"
        )

    return cloud_id


# ==================== Atlassian Jira Tools ====================

@mcp.tool()
async def jira_search_issues(
    project: str = None,
    status: str = None,
    assignee: str = None,
    issue_type: str = None,
    max_results: int = 50
    
) -> str:
    """
    Search Jira issues with filters.

    Args:
        project: Project key to filter by (optional)
        status: Status to filter by (optional)
        assignee: Assignee email or name (optional)
        issue_type: Issue type to filter by (optional)
        max_results: Maximum number of results (default: 50)

    Returns:
        JSON string of search results with slim issue representations
    """
    import json
    
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = JiraService(client)
    
    search_result = service.search_issues(project, status, assignee, issue_type, max_results)
    return json.dumps(search_result.to_simplified_dict(), indent=2, ensure_ascii=False)


@mcp.tool()
async def jira_search_issues_by_jql(
    jql: str,
    max_results: int = 50,
    fields: str = None
    
) -> str:
    """
    Search Jira issues using JQL (Jira Query Language).

    Args:
        jql: JQL query string. Examples:
            - Find Epics: "issuetype = Epic AND project = BIFO"
            - Find issues in Epic: "parent = BIFO-123"
            - Find by status: "status = 'In Progress' AND project = BIFO"
            - Find by assignee: "assignee = currentUser()"
            - Find recently updated: "updated >= -7d AND project = BIFO"
            - Find by label: "labels = frontend AND project = BIFO"
            - Find by priority: "priority = High AND project = BIFO"
            - Order results: "project = BIFO ORDER BY created DESC"
        max_results: Maximum number of results (default: 50)
        fields: Comma-separated fields to return (e.g., 'summary,status,assignee').
                Use '*all' for all fields, or omit for default fields (summary,status,assignee,issuetype,priority,created,updated)

    Returns:
        JSON string of search results with slim issue representations
    """
    import json
    
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = JiraService(client)
    
    search_result = service.search_issues_by_jql(jql, max_results, fields)
    return json.dumps(search_result.to_simplified_dict(), indent=2, ensure_ascii=False)


@mcp.tool()
async def jira_count_issues_by_jql(
    jql: str
    
) -> dict[str, Any]:
    """
    Count Jira issues matching JQL query.
    
    Fetches all matching issues across multiple pages (if needed) and returns the complete count.
    This operation may take longer for queries with many results.

    Args:
        jql: JQL query string (e.g., 'project=HUB AND status="In Progress"')

    Returns:
        Total count of matching issues, all issue keys, and the JQL query
    """
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = JiraService(client)
    return service.count_issues_by_jql(jql)


@mcp.tool()
async def jira_get_issue(
    issue_key: str,
    fields: str = None
) -> str:
    """
    Get details of a specific Jira issue.

    Args:
        issue_key: Jira issue key (e.g., 'PROJ-123', 'BIFO-456')
        fields: Comma-separated fields to return (e.g., 'summary,status,assignee,description,comment').
                Use '*all' for all fields (including custom fields), or omit for default fields
                (summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype)

    Returns:
        JSON string of issue details with slim representation
    """
    import json
    
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = JiraService(client)
    
    issue = service.get_issue(issue_key, fields)
    return json.dumps(issue.to_simplified_dict(), indent=2, ensure_ascii=False)


@mcp.tool()
async def jira_get_all_projects() -> dict[str, Any]:
    """
    Get all Jira projects.

    Args:

    Returns:
        List of all projects
    """
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = JiraService(client)
    return service.get_all_projects()


@mcp.tool()
async def jira_get_project_issues(
    project_key: str,
    max_results: int = 50
    
) -> str:
    """
    Get issues for a specific project.

    Args:
        project_key: Project key (e.g., 'BIFO', 'HUB')
        max_results: Maximum number of results (default: 50)

    Returns:
        JSON string of search results with slim issue representations
    """
    import json
    
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = JiraService(client)
    
    search_result = service.get_project_issues(project_key, max_results)
    return json.dumps(search_result.to_simplified_dict(), indent=2, ensure_ascii=False)


@mcp.tool()
async def jira_get_sprint_issues(
    sprint_id: str,
    max_results: int = 100
    
) -> str:
    """
    Get issues in a specific sprint.

    Args:
        sprint_id: Sprint ID
        max_results: Maximum number of results (default: 100)

    Returns:
        JSON string of search results with slim issue representations
    """
    import json
    
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = JiraService(client)
    
    search_result = service.get_sprint_issues(sprint_id, max_results)
    return json.dumps(search_result.to_simplified_dict(), indent=2, ensure_ascii=False)


@mcp.tool()
async def jira_get_issue_comments(issue_key: str) -> str:
    """
    Get all comments for a specific Jira issue.

    Args:
        issue_key: Issue key (e.g., PROJ-123, BIFO-456)

    Returns:
        JSON string of comments with slim representation
    """
    import json
    
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = JiraService(client)
    
    comments = service.get_issue_comments(issue_key)
    result = {
        "total": len(comments),
        "comments": [comment.to_simplified_dict() for comment in comments]
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
async def jira_get_issue_worklogs(issue_key: str) -> str:
    """
    Get all worklogs (time tracking entries) for a specific Jira issue.

    Args:
        issue_key: Issue key (e.g., PROJ-123, BIFO-456)

    Returns:
        JSON string of worklogs with slim representation
    """
    import json
    
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = JiraService(client)
    
    worklogs = service.get_issue_worklogs(issue_key)
    result = {
        "total": len(worklogs),
        "worklogs": [worklog.to_simplified_dict() for worklog in worklogs]
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


# ==================== Atlassian Confluence Tools ====================

@mcp.tool()
def confluence_search_content(
    cql: str,
    limit: int = 10
    
) -> dict[str, Any]:
    """
    Search Confluence content using CQL (Confluence Query Language).

    Args:
        cql: CQL query string (e.g., 'type=page AND text~"search term"')
        limit: Maximum number of results (default: 10)

    Returns:
        Search results containing matching content
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    token = _get_atlassian_token()
    cloud_id = _get_atlassian_cloud_id()
    client = AtlassianClient(token, cloud_id)
    service = ConfluenceService(client)
    
    # Check if the query is a simple search term or already a CQL query
    query = cql
    if query and not any(
        x in query for x in ["=", "~", ">", "<", " AND ", " OR ", "currentUser()"]
    ):
        original_query = query
        try:
            query = f'siteSearch ~ "{original_query}"'
            logger.info(
                f"Converting simple search term to CQL using siteSearch: {query}"
            )
            pages = service.search(query, limit=limit)
        except Exception as e:
            logger.warning(f"siteSearch failed ('{e}'), falling back to text search.")
            query = f'text ~ "{original_query}"'
            logger.info(f"Falling back to text search with CQL: {query}")
            pages = service.search(query, limit=limit)
    else:
        pages = service.search(query, limit=limit)
    
    # Convert to simplified dict for response
    search_results = [page.to_simplified_dict() for page in pages]
    return {
        "total": len(search_results),
        "query": query,
        "results": search_results
    }



# ==================== Microsoft Teams Tools ====================

@mcp.tool()
async def teams_get_joined_teams() -> dict[str, Any]:
    """
    Get user's joined Teams.

    Args:

    Returns:
        List of teams the user has joined
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = TeamsService(client)
    return await service.get_joined_teams()


@mcp.tool()
async def teams_get_team_channels(team_id: str) -> dict[str, Any]:
    """
    Get channels in a specific team.

    Args:
        team_id: Microsoft Teams team ID

    Returns:
        List of channels in the team
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = TeamsService(client)
    return await service.get_team_channels(team_id)


@mcp.tool()
async def teams_get_channel_messages(
    team_id: str,
    channel_id: str,
    top: int = 50
    
) -> dict[str, Any]:
    """
    Get messages from a specific Teams channel.

    Args:
        team_id: Microsoft Teams team ID
        channel_id: Channel ID
        top: Maximum number of messages to return (default: 50)

    Returns:
        List of messages from the channel
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = TeamsService(client)
    return await service.get_channel_messages(team_id, channel_id, top)


@mcp.tool()
async def teams_search_messages(
    keyword: str = None,
    from_user: str = None,
    days_back: int = 7,
    max_results: int = 50
    
) -> dict[str, Any]:
    """
    Search Teams messages with various filters.

    Args:
        keyword: Search keyword in message content (optional)
        from_user: Filter messages from specific user email or display name (optional)
        days_back: Number of days to search back (default: 7)
        max_results: Maximum number of results (default: 50)

    Returns:
        Search results containing matching messages
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = TeamsService(client)
    return await service.search_teams_messages(keyword, from_user, days_back, max_results)


@mcp.tool()
async def teams_list_my_chats(
    top: int = 50
) -> dict[str, Any]:
    """
    Get user's chat conversations.

    Args:
        top: Maximum number of chats to return (default: 50)

    Returns:
        List of chat conversations
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = TeamsService(client)
    return await service.list_my_chats(top)


@mcp.tool()
async def teams_list_chat_messages(
    chat_id: str,
    top: int = 50
) -> dict[str, Any]:
    """
    Get messages from a specific chat.

    Args:
        chat_id: Chat ID (get from teams_list_my_chats)
        top: Maximum number of messages to return (default: 50)

    Returns:
        List of messages from the chat
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = TeamsService(client)
    return await service.list_chat_messages(chat_id, top)


# ==================== Microsoft Outlook Tools ====================

@mcp.tool()
async def outlook_get_emails(
    top: int = 10,
    folder: str = None,
    from_address: str = None,
    subject_contains: str = None,
    days_back: int = None,
    is_read: bool = None
    
) -> dict[str, Any]:
    """
    Get user's email messages with advanced filtering.

    Args:
        top: Number of messages to return (default: 10)
        folder: Folder name to search in (e.g., 'inbox', 'sent') (optional)
        from_address: Filter emails from specific sender (optional)
        subject_contains: Filter emails with subject containing text (optional)
        days_back: Number of days to search back (optional)
        is_read: Filter by read status (optional)

    Returns:
        List of email messages matching the filters
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = OutlookService(client)
    return await service.get_emails(top, folder, from_address, subject_contains, days_back, is_read)


@mcp.tool()
async def outlook_get_message(message_id: str) -> dict[str, Any]:
    """
    Get details of a specific email message.

    Args:
        message_id: Outlook message ID

    Returns:
        Message details
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = OutlookService(client)
    return await service.get_message(message_id)


@mcp.tool()
async def outlook_search_emails(
    query: str,
    top: int = 10
) -> dict[str, Any]:
    """
    Search emails using Keyword Query Language (KQL).

    Args:
        query: KQL query string (e.g., 'from:user@example.com subject:report')
        top: Maximum number of results (default: 10, max: 25)

    Returns:
        List of email messages matching the search query
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = OutlookService(client)
    return await service.search_emails(query, top)


@mcp.tool()
async def outlook_get_calendar_events(
    days_ahead: int = 7,
    top: int = 50
    
) -> dict[str, Any]:
    """
    Get upcoming calendar events.

    Args:
        days_ahead: Number of days ahead to fetch events (default: 7)
        top: Maximum number of events to return (default: 50)

    Returns:
        List of calendar events
    """
    token = _get_microsoft_token()
    client = MicrosoftGraphClient(token)
    service = OutlookService(client)
    return await service.get_calendar_events(days_ahead, top)


# ==================== Server Entry Point ====================

def run_server() -> None:
    """Run the MCP server."""
    import logging
    logger = logging.getLogger(__name__)

    # Configure transport based on environment variable
    transport = config.MCP_TRANSPORT

    if transport == "stdio":
        # stdio transport doesn't use host/port
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        # For HTTP transport, middleware is already registered via mcp.add_middleware()
        logger.info(f"Starting MCP Server with streamable-http transport on {config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}...")

        # FastMCP requires uvicorn to run HTTP transport
        # This is a dependency of FastMCP itself
        import uvicorn
        app = mcp.streamable_http_app()
        uvicorn.run(app, host=config.MCP_SERVER_HOST, port=config.MCP_SERVER_PORT)
    else:
        # Other transports
        mcp.run(
            transport=transport,
            host=config.MCP_SERVER_HOST,
            port=config.MCP_SERVER_PORT
        )


if __name__ == "__main__":
    run_server()
