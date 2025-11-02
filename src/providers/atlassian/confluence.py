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
        endpoint = f"/ex/confluence/{self.client.cloud_id}/rest/api/content/search"
        params = {
            "cql": cql,
            "limit": limit,
            "expand": "metadata,body.view"
        }
        return await self.client.get(endpoint, params=params)

    async def get_space(self, space_key: str) -> dict[str, Any]:
        """
        Get information about a specific Confluence space.

        Args:
            space_key: Space key (e.g., 'PROJ', 'TEAM')

        Returns:
            Space information including name, description, and metadata
        """
        endpoint = f"/ex/confluence/{self.client.cloud_id}/wiki/api/v2/spaces"
        params = {
            "keys": space_key,
            "limit": 1
        }
        response = await self.client.get(endpoint, params=params)
        
        # Extract the first result from the results array
        results = response.get("results", [])
        if not results:
            return {"error": f"Space with key '{space_key}' not found"}
        
        return results[0]

    async def get_page(self, page_id: str) -> dict[str, Any]:
        """
        Get a specific Confluence page with full content.

        Args:
            page_id: Page ID

        Returns:
            Page details including title, body content, and metadata
        """
        endpoint = f"/ex/confluence/{self.client.cloud_id}/wiki/api/v2/pages/{page_id}"
        params = {
            "body-format": "storage"  # Get full HTML content
        }
        return await self.client.get(endpoint, params=params)

    async def get_space_pages(
        self,
        space_id: str,
        limit: int = 25
    ) -> dict[str, Any]:
        """
        Get all pages in a specific Confluence space.

        Args:
            space_id: Space ID (numeric ID, not the space key)
            limit: Maximum number of pages to return (default: 25)

        Returns:
            List of pages in the space
        """
        endpoint = f"/ex/confluence/{self.client.cloud_id}/wiki/api/v2/spaces/{space_id}/pages"
        params = {
            "limit": limit
        }
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
            limit: Maximum number of child pages to return (default: 25)

        Returns:
            List of child pages
        """
        endpoint = f"/ex/confluence/{self.client.cloud_id}/wiki/api/v2/pages/{page_id}/children"
        params = {
            "limit": limit
        }
        return await self.client.get(endpoint, params=params)
