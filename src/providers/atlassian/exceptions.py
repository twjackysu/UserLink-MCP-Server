"""Custom exceptions for Atlassian integration."""

import logging

logger = logging.getLogger(__name__)


class AtlassianAuthenticationError(Exception):
    """Exception raised for authentication-related errors with Atlassian services."""

    pass
