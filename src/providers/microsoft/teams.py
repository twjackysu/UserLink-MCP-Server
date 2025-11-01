"""Teams service implementation."""

from typing import Any, Optional
from datetime import datetime, timedelta
from .base import MicrosoftGraphClient


class TeamsService:
    """Service for Microsoft Teams operations."""

    def __init__(self, client: MicrosoftGraphClient) -> None:
        """
        Initialize Teams service.

        Args:
            client: Microsoft Graph API client instance
        """
        self.client = client

    async def get_joined_teams(self) -> dict[str, Any]:
        """
        Get user's joined teams.

        Returns:
            List of teams the user has joined
        """
        endpoint = "/v1.0/me/joinedTeams"
        return await self.client.get(endpoint)

    async def get_team_channels(self, team_id: str) -> dict[str, Any]:
        """
        Get channels in a specific team.

        Args:
            team_id: Team ID

        Returns:
            List of channels in the team
        """
        endpoint = f"/v1.0/teams/{team_id}/channels"
        return await self.client.get(endpoint)

    async def get_channel_messages(
        self,
        team_id: str,
        channel_id: str,
        top: int = 50
    ) -> dict[str, Any]:
        """
        Get messages from a specific channel.

        Args:
            team_id: Team ID
            channel_id: Channel ID
            top: Maximum number of messages to return (default: 50)

        Returns:
            List of messages from the channel
        """
        endpoint = f"/v1.0/teams/{team_id}/channels/{channel_id}/messages"
        params = {"$top": top}
        return await self.client.get(endpoint, params=params)

    async def search_teams_messages(
        self,
        keyword: Optional[str] = None,
        from_user: Optional[str] = None,
        days_back: int = 7,
        max_results: int = 50
    ) -> dict[str, Any]:
        """
        Search Teams messages with various filters.

        Args:
            keyword: Search keyword in message content
            from_user: Filter messages from specific user (email or display name)
            days_back: Number of days to search back (default: 7)
            max_results: Maximum number of results (default: 50)

        Returns:
            Search results containing matching messages
        """
        # Calculate date filter
        start_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build search query
        search_parts = []
        if keyword:
            search_parts.append(f'"{keyword}"')

        search_query = " ".join(search_parts) if search_parts else "*"

        # Build request body for search
        request_body = {
            "requests": [
                {
                    "entityTypes": ["chatMessage"],
                    "query": {
                        "queryString": search_query
                    },
                    "from": 0,
                    "size": max_results,
                    "fields": [
                        "id",
                        "subject",
                        "body",
                        "from",
                        "createdDateTime",
                        "webUrl"
                    ]
                }
            ]
        }

        # Add date filter
        if days_back:
            request_body["requests"][0]["query"]["query_string"] = {
                "query": search_query
            }
            request_body["requests"][0]["filters"] = {
                "createdDateTime": {
                    "start": start_date
                }
            }

        # Add from_user filter if provided
        if from_user:
            if "filters" not in request_body["requests"][0]:
                request_body["requests"][0]["filters"] = {}
            request_body["requests"][0]["filters"]["from"] = from_user

        endpoint = "/v1.0/search/query"
        return await self.client.post(endpoint, json=request_body)
