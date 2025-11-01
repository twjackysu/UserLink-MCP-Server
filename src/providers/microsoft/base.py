"""Base client for Microsoft Graph API interactions."""

import httpx
from typing import Any, Optional
from src.config import config


class MicrosoftGraphClient:
    """Base client for Microsoft Graph API requests."""

    def __init__(self, access_token: str) -> None:
        """
        Initialize Microsoft Graph client with access token.

        Args:
            access_token: OAuth access token from request header
        """
        self.access_token = access_token
        self.base_url = config.MICROSOFT_GRAPH_API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Make HTTP request to Microsoft Graph API.

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
