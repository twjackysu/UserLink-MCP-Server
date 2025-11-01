"""Headers capture middleware for UserLink MCP Server."""

from typing import Dict
from contextvars import ContextVar
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
import logging

logger = logging.getLogger(__name__)

# Context variable for storing request headers
current_request_headers: ContextVar[Dict[str, str]] = ContextVar('current_request_headers', default={})


class HeadersCaptureMiddleware(Middleware):
    """Middleware to capture and store request headers in ContextVar."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Process tool call and capture headers."""
        try:
            # Get headers from FastMCP
            headers = get_http_headers()

            # Normalize headers for easier access
            normalized_headers = {}
            for key, value in headers.items():
                normalized_headers[key] = value
                # Convert header names to lowercase for case-insensitive access
                normalized_headers[key.lower()] = value

            # Log headers for debugging (excluding sensitive tokens)
            safe_headers = {k: v for k, v in normalized_headers.items()
                           if not any(x in k.lower() for x in ['token', 'authorization', 'cookie', 'key', 'secret'])}
            logger.info(f"🔍 Middleware captured headers: {safe_headers}")
            logger.info(f"🔍 Header count: {len(normalized_headers)}")

            # Set headers in ContextVar for this request
            current_request_headers.set(normalized_headers)
            logger.info(f"✅ Headers set in ContextVar")

            # Allow the tool to proceed
            return await call_next(context)

        except Exception as e:
            logger.error(f"❌ Error in headers middleware: {e}", exc_info=True)
            # Continue processing even if header capture fails
            return await call_next(context)
