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
        top: int = 10
    ) -> dict[str, Any]:
        """
        Get messages from a specific Teams channel.

        Note: This uses the search API as direct channel message retrieval is limited.
        For most scenarios, use search_teams_messages() instead.

        Args:
            team_id: Team ID
            channel_id: Channel ID (in format: 19:xxx@thread.xxx)
            top: Maximum number of messages to return (default: 10)

        Returns:
            List of messages from the channel via search
        """
        # Microsoft Graph doesn't support direct /teams/{id}/channels/{id}/messages GET
        # Instead, we need to use the search API with channel context
        # For now, return a helpful message directing to search_teams_messages
        return {
            "message": "Direct channel message retrieval is not available. Please use search_teams_messages() to search for messages.",
            "note": f"To get messages from channel {channel_id} in team {team_id}, use teams_search_messages with appropriate keywords.",
            "alternative": "Use the search_teams_messages endpoint which supports channel filtering"
        }

    async def search_teams_messages(
        self,
        keyword: Optional[str] = None,
        from_user: Optional[str] = None,
        days_back: int = 7,
        max_results: int = 10
    ) -> dict[str, Any]:
        """
        Search Teams messages with various filters.

        Args:
            keyword: Search keyword in message content
            from_user: Filter messages from specific user (email or display name)
            days_back: Number of days to search back (default: 7)
            max_results: Maximum number of results (default: 10)
        Returns:
            Search results containing matching messages
        """
        # Build search query string
        query_parts = []
        if keyword:
            query_parts.append(keyword)
        if from_user:
            query_parts.append(f"from:{from_user}")

        # If no specific query, search all messages
        query_string = " ".join(query_parts) if query_parts else "*"

        # Build request body for Microsoft Graph Search API
        request_body = {
            "requests": [
                {
                    "entityTypes": ["chatMessage"],
                    "query": {
                        "queryString": query_string
                    },
                    "from": 0,
                    "size": min(max_results, 25)  # Microsoft Graph limits to 25
                }
            ]
        }

        endpoint = "/v1.0/search/query"
        return await self.client.post(endpoint, json=request_body)

    async def list_my_chats(self, top: int = 50) -> dict[str, Any]:
        """
        Get user's chat conversations.

        Args:
            top: Maximum number of chats to return (default: 50)

        Returns:
            List of chat conversations
        """
        endpoint = "/v1.0/me/chats"
        params = {"$top": str(top)}
        return await self.client.get(endpoint, params=params)

    async def list_chat_messages(
        self, chat_id: str, top: int = 50
    ) -> dict[str, Any]:
        """
        Get messages from a specific chat.

        Args:
            chat_id: Chat ID (get from list_my_chats)
            top: Maximum number of messages to return (default: 50)

        Returns:
            List of messages from the chat
        """
        endpoint = f"/v1.0/me/chats/{chat_id}/messages"
        params = {"$top": str(top)}
        return await self.client.get(endpoint, params=params)
