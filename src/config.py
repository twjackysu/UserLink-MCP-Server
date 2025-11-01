"""Configuration management for UserLink MCP Server."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Server Configuration
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MCP_TRANSPORT: str = os.getenv("MCP_TRANSPORT", "streamable-http")

    # API Base URLs (optional overrides)
    ATLASSIAN_API_BASE_URL: str = os.getenv(
        "ATLASSIAN_API_BASE_URL", "https://api.atlassian.com"
    )
    MICROSOFT_GRAPH_API_BASE_URL: str = os.getenv(
        "MICROSOFT_GRAPH_API_BASE_URL", "https://graph.microsoft.com"
    )


config = Config()
