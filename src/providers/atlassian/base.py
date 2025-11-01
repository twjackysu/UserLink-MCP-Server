"""Base client for Atlassian API interactions."""

import httpx
from typing import Any, Optional
from src.config import config


class AtlassianClient:
    """Base client for Atlassian API requests."""

    def __init__(self, access_token: str, cloud_id: str) -> None:
        """
        Initialize Atlassian client with access token and cloud ID.

        Args:
            access_token: OAuth access token from request header
            cloud_id: Atlassian cloud ID from request header
        """
        self.access_token = access_token
        self.cloud_id = cloud_id
        self.base_url = config.ATLASSIAN_API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Make HTTP request to Atlassian API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            JSON response data
        """
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method, url=url, headers=self.headers, **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make GET request."""
        return await self._request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make POST request."""
        return await self._request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make PUT request."""
        return await self._request("PUT", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make DELETE request."""
        return await self._request("DELETE", endpoint, **kwargs)
