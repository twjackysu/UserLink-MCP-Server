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
