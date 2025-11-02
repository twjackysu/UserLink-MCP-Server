"""Outlook service implementation."""

from typing import Any, Optional
from datetime import datetime, timedelta
from .base import MicrosoftGraphClient


class OutlookService:
    """Service for Outlook operations."""

    def __init__(self, client: MicrosoftGraphClient) -> None:
        """
        Initialize Outlook service.

        Args:
            client: Microsoft Graph API client instance
        """
        self.client = client

    async def get_emails(
        self,
        top: int = 10,
        folder: Optional[str] = None,
        from_address: Optional[str] = None,
        subject_contains: Optional[str] = None,
        days_back: Optional[int] = None,
        is_read: Optional[bool] = None
    ) -> dict[str, Any]:
        """
        Get user's email messages with advanced filtering.

        Note: Microsoft Graph messages API has limited filter support.
        For complex queries (e.g., filtering by sender or subject),
        use outlook_search_emails() instead.

        Args:
            top: Number of messages to return (default: 10)
            folder: Folder name to search in (e.g., 'inbox', 'sent')
            from_address: Filter emails from specific sender (Note: Not supported, use outlook_search_emails)
            subject_contains: Filter emails with subject containing text (Note: Not supported, use outlook_search_emails)
            days_back: Number of days to search back
            is_read: Filter by read status (True/False)

        Returns:
            List of email messages matching the filters
        """
        # Build endpoint - use standard folders or inbox as default
        if folder:
            # Map common folder names to their well-known folder IDs
            folder_mapping = {
                "inbox": "inbox",
                "sent": "sentitems", 
                "drafts": "drafts",
                "deleted": "deleteditems",
                "junk": "junkemail"
            }
            folder_name = folder_mapping.get(folder.lower(), folder)
            endpoint = f"/v1.0/me/mailFolders/{folder_name}/messages"
        else:
            endpoint = "/v1.0/me/messages"

        # Build filter query with limited supported OData syntax
        # Note: Microsoft Graph messages API has very limited filter support
        filters = []

        # Note: from_address filtering is not supported by Microsoft Graph messages API
        # This would need to be implemented client-side after retrieving messages

        # Note: subject_contains filtering is not supported by Microsoft Graph messages API  
        # This would need to be implemented client-side after retrieving messages

        if days_back:
            start_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            filters.append(f"receivedDateTime ge {start_date}")

        if is_read is not None:
            filters.append(f"isRead eq {str(is_read).lower()}")

        # Build params
        params = {
            "$top": top,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,isRead,hasAttachments,bodyPreview"
        }

        if filters:
            params["$filter"] = " and ".join(filters)

        return await self.client.get(endpoint, params=params)

    async def get_message(self, message_id: str) -> dict[str, Any]:
        """
        Get a specific email message.

        Args:
            message_id: Message ID

        Returns:
            Message details
        """
        endpoint = f"/v1.0/me/messages/{message_id}"
        return await self.client.get(endpoint)

    async def get_calendar_events(
        self,
        days_ahead: int = 7,
        top: int = 10
    ) -> dict[str, Any]:
        """
        Get upcoming calendar events.

        Args:
            days_ahead: Number of days ahead to fetch events (default: 7)
            top: Maximum number of events to return (default: 10)

        Returns:
            List of calendar events
        """
        # Calculate date range
        start_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date = (datetime.utcnow() + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%SZ")

        endpoint = "/v1.0/me/calendar/calendarView"
        params = {
            "startDateTime": start_date,
            "endDateTime": end_date,
            "$top": top,
            "$orderby": "start/dateTime"
        }

        return await self.client.get(endpoint, params=params)

    async def search_emails(
        self,
        query: str,
        top: int = 10
    ) -> dict[str, Any]:
        """
        Search emails using Microsoft Graph Search API with KQL (Keyword Query Language).

        This method supports complex queries including sender, subject, and full-text search.

        Args:
            query: Search query using KQL syntax
                   Examples:
                   - "from:john@example.com" - emails from specific sender
                   - "subject:urgent" - emails with "urgent" in subject
                   - "from:john@example.com subject:meeting" - combined filters
                   - "project update" - full-text search
            top: Maximum number of results (default: 10, max: 25)

        Returns:
            Search results containing matching emails
        """
        endpoint = "/v1.0/me/messages"
        params = {
            "$search": f'"{query}"',
            "$top": min(top, 25),  # Graph API limits to 25
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,isRead,hasAttachments,bodyPreview"
        }
        return await self.client.get(endpoint, params=params)
