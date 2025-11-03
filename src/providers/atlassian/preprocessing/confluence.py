"""Confluence-specific text preprocessing module."""

import logging
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from typing import Tuple

logger = logging.getLogger(__name__)


class ConfluencePreprocessor:
    """Handles text preprocessing for Confluence content."""

    def __init__(self, base_url: str) -> None:
        """
        Initialize the Confluence text preprocessor.

        Args:
            base_url: Base URL for Confluence API
        """
        self.base_url = base_url

    def process_html_content(
        self,
        html_content: str,
        space_key: str = "",
        confluence_client=None,
    ) -> Tuple[str, str]:
        """
        Convert HTML content to Markdown.

        Args:
            html_content: HTML content to process
            space_key: Space key for the content
            confluence_client: Confluence client (unused in simple implementation)

        Returns:
            Tuple of (html_content, markdown_content)
        """
        try:
            # Clean HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            cleaned_html = str(soup)
            
            # Convert to markdown
            markdown_content = md(cleaned_html, heading_style="ATX")
            
            return cleaned_html, markdown_content
        except Exception as e:
            logger.error(f"Error processing HTML content: {e}")
            return html_content, html_content
