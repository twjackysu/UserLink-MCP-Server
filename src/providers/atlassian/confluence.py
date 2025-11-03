"""Confluence service implementation."""

import logging
from typing import Any

from .base import AtlassianClient
from .preprocessing.confluence import ConfluencePreprocessor
from .utils.cql_utils import quote_cql_identifier_if_needed
from src.models.confluence import (
    ConfluencePage,
    ConfluenceSearchResult,
)

logger = logging.getLogger(__name__)


class ConfluenceService:
    """Service for Confluence operations."""

    def __init__(self, client: AtlassianClient) -> None:
        """
        Initialize Confluence service.

        Args:
            client: Atlassian API client instance
        """
        self.client = client
        self.confluence = client.confluence
        self.confluence_url = client.confluence_url
        
        # Initialize preprocessor
        self.preprocessor = ConfluencePreprocessor(base_url=client.confluence_url)

    def search(
        self,
        cql: str,
        limit: int = 10,
        spaces_filter: str | None = None
    ) -> list[ConfluencePage]:
        """
        Search content using Confluence Query Language (CQL).

        Args:
            cql: Confluence Query Language string
            limit: Maximum number of results to return
            spaces_filter: Optional comma-separated list of space keys to filter by

        Returns:
            List of ConfluencePage models containing search results
        """
        # Apply spaces filter if present
        if spaces_filter:
            # Split spaces filter by commas and handle possible whitespace
            spaces = [s.strip() for s in spaces_filter.split(",")]

            # Build the space filter query part using proper quoting for each space key
            space_query = " OR ".join(
                [f"space = {quote_cql_identifier_if_needed(space)}" for space in spaces]
            )

            # Add the space filter to existing query with parentheses
            if cql and space_query:
                if "space = " not in cql:  # Only add if not already filtering by space
                    cql = f"({cql}) AND ({space_query})"
            else:
                cql = space_query

            logger.info(f"Applied spaces filter to query: {cql}")

        # Execute the CQL search query
        logger.info(f"Executing CQL query: {cql} with limit: {limit}")
        results = self.confluence.cql(cql=cql, limit=limit)
        logger.info(f"CQL search returned {len(results.get('results', []))} results")

        # Convert the response to a search result model
        search_result = ConfluenceSearchResult.from_api_response(
            results,
            base_url=self.confluence_url,
            cql_query=cql,
            is_cloud=True,
        )

        # Process result excerpts as content
        processed_pages = []
        for page in search_result.results:
            # Get the excerpt from the original search results
            for result_item in results.get("results", []):
                if result_item.get("content", {}).get("id") == page.id:
                    excerpt = result_item.get("excerpt", "")
                    if excerpt:
                        # Process the excerpt as HTML content
                        space_key = page.space.key if page.space else ""
                        _, processed_markdown = self.preprocessor.process_html_content(
                            excerpt,
                            space_key=space_key,
                            confluence_client=self.confluence,
                        )
                        # Create a new page with processed content
                        page.content = processed_markdown
                    break

            processed_pages.append(page)

        # Return the list of result pages with processed content
        return processed_pages



