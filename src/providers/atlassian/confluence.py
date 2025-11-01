"""Confluence service implementation."""

from typing import Any, Optional
from .base import AtlassianClient


class ConfluenceService:
    """Service for Confluence operations."""

    def __init__(self, client: AtlassianClient) -> None:
        """
        Initialize Confluence service.

        Args:
            client: Atlassian API client instance
        """
        self.client = client

    async def search_content(
        self,
        cql: str,
        limit: int = 25
    ) -> dict[str, Any]:
        """
        Search Confluence content using CQL (Confluence Query Language).

        Args:
            cql: CQL query string
            limit: Maximum number of results (default: 25)

        Returns:
            Search results containing matching content
        """
        endpoint = f"/ex/confluence/{self.client.cloud_id}/rest/api/search"
        params = {
            "cql": cql,
            "limit": limit,
            "expand": "content.metadata,content.body.view"
        }
        return await self.client.get(endpoint, params=params)

    async def get_page(
        self,
        page_id: str,
        expand: str = "body.storage,version,space"
    ) -> dict[str, Any]:
        """
        Get details of a specific Confluence page.

        Args:
            page_id: Page ID
            expand: Fields to expand (default: body.storage,version,space)

        Returns:
            Page details with expanded fields
        """
        endpoint = f"/ex/confluence/{self.client.cloud_id}/rest/api/content/{page_id}"
        params = {"expand": expand}
        return await self.client.get(endpoint, params=params)

    async def get_page_children(
        self,
        page_id: str,
        limit: int = 25
    ) -> dict[str, Any]:
        """
        Get child pages of a specific Confluence page.

        Args:
            page_id: Parent page ID
            limit: Maximum number of child pages (default: 25)

        Returns:
            List of child pages
        """
        endpoint = f"/ex/confluence/{self.client.cloud_id}/rest/api/content/{page_id}/child/page"
        params = {
            "limit": limit,
            "expand": "body.view,version,space"
        }
        return await self.client.get(endpoint, params=params)

    async def get_page_comments(
        self,
        page_id: str,
        limit: int = 50
    ) -> dict[str, Any]:
        """
        Get comments on a specific Confluence page.

        Args:
            page_id: Page ID
            limit: Maximum number of comments (default: 50)

        Returns:
            List of comments on the page
        """
        endpoint = f"/ex/confluence/{self.client.cloud_id}/rest/api/content/{page_id}/child/comment"
        params = {
            "limit": limit,
            "expand": "body.view,version"
        }
        return await self.client.get(endpoint, params=params)

    async def get_spaces(self, limit: int = 25) -> dict[str, Any]:
        """
        Get Confluence spaces.

        Args:
            limit: Maximum number of spaces to return (default: 25)

        Returns:
            List of spaces
        """
        endpoint = f"/ex/confluence/{self.client.cloud_id}/rest/api/space"
        params = {"limit": limit}
        return await self.client.get(endpoint, params=params)
