"""Authentication utilities for extracting and validating access tokens."""

from typing import Optional


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class ProviderTokenHeader:
    """Header names for different provider tokens."""

    MICROSOFT = "x-microsoft-graph-token"
    ATLASSIAN = "x-atlassian-token"
    ATLASSIAN_CLOUD_ID = "x-atlassian-cloud-id"


def extract_microsoft_token(headers: dict[str, str]) -> Optional[str]:
    """
    Extract Microsoft Graph access token from request headers.

    Args:
        headers: Request headers dictionary

    Returns:
        Access token if found, None otherwise
    """
    # Check both lowercase and original case (headers can be case-insensitive)
    token = headers.get(ProviderTokenHeader.MICROSOFT) or headers.get(ProviderTokenHeader.MICROSOFT.upper())
    return token


def extract_atlassian_token(headers: dict[str, str]) -> Optional[str]:
    """
    Extract Atlassian access token from request headers.

    Args:
        headers: Request headers dictionary

    Returns:
        Access token if found, None otherwise
    """
    # Check both lowercase and original case (headers can be case-insensitive)
    token = headers.get(ProviderTokenHeader.ATLASSIAN) or headers.get(ProviderTokenHeader.ATLASSIAN.upper())
    return token


def extract_atlassian_cloud_id(headers: dict[str, str]) -> Optional[str]:
    """
    Extract Atlassian Cloud ID from request headers.

    Args:
        headers: Request headers dictionary

    Returns:
        Cloud ID if found, None otherwise
    """
    # Check both lowercase and original case (headers can be case-insensitive)
    cloud_id = headers.get(ProviderTokenHeader.ATLASSIAN_CLOUD_ID) or headers.get(ProviderTokenHeader.ATLASSIAN_CLOUD_ID.upper())
    return cloud_id


def validate_token(token: Optional[str]) -> bool:
    """
    Validate access token format.

    Args:
        token: Access token to validate

    Returns:
        True if token is valid, False otherwise
    """
    # Basic validation - token should exist and have reasonable length
    if not token:
        return False

    # Trim whitespace
    token = token.strip()

    # Token should be at least 20 characters (typical OAuth tokens are much longer)
    return len(token) >= 20


def validate_cloud_id(cloud_id: Optional[str]) -> bool:
    """
    Validate Atlassian Cloud ID format.

    Args:
        cloud_id: Cloud ID to validate

    Returns:
        True if cloud ID is valid, False otherwise
    """
    if not cloud_id:
        return False

    # Trim whitespace
    cloud_id = cloud_id.strip()

    # Cloud ID should be a non-empty string (typically a UUID-like format)
    return len(cloud_id) > 0
