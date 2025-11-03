"""Base client for Atlassian API interactions."""

from atlassian import Confluence, Jira
from requests import Session
from typing import Any
from src.config import config


class AtlassianClient:
    """Base client for Atlassian API requests using atlassian-python-api library."""

    def __init__(self, access_token: str, cloud_id: str) -> None:
        """
        Initialize Atlassian client with access token and cloud ID.

        Args:
            access_token: OAuth access token from request header
            cloud_id: Atlassian cloud ID from request header
        """
        self.access_token = access_token
        self.cloud_id = cloud_id
        
        # Create a session for OAuth authentication
        session = Session()
        session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        
        # Initialize Confluence client
        self.confluence_url = f"https://api.atlassian.com/ex/confluence/{cloud_id}"
        self.confluence = Confluence(
            url=self.confluence_url,
            session=session,
            cloud=True,
            verify_ssl=True,
        )
        
        # Initialize Jira client
        self.jira_url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
        self.jira = Jira(
            url=self.jira_url,
            session=session,
            cloud=True,
            verify_ssl=True,
        )


