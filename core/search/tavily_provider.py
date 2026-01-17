"""
Tavily Search Provider - AI-optimized web search.

Tavily provides high-quality search results specifically designed
for AI applications, with built-in content extraction and relevance scoring.

Features:
- AI-optimized search results
- Automatic content extraction
- Relevance scoring
- Domain filtering
- Time-based filtering

Requirements:
    pip install tavily-python

Usage:
    from core.search import TavilySearchProvider

    provider = TavilySearchProvider(api_key="your-tavily-api-key")
    results = await provider.search("AI in healthcare", max_results=10)
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .base import SearchProvider, SearchResult, SearchConfig

logger = logging.getLogger(__name__)


class TavilySearchProvider(SearchProvider):
    """
    Tavily search provider implementation.

    Tavily is an AI-native search engine that provides high-quality,
    relevant results with automatic content extraction.

    API Documentation: https://docs.tavily.com/
    """

    @property
    def name(self) -> str:
        return "tavily"

    def __init__(
        self,
        api_key: str,
        default_search_depth: str = "basic",
        include_raw_content: bool = False,
        **kwargs,
    ):
        """
        Initialize Tavily provider.

        Args:
            api_key: Tavily API key
            default_search_depth: Default search depth (basic or advanced)
            include_raw_content: Whether to include raw page content by default
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.default_search_depth = default_search_depth
        self.include_raw_content = include_raw_content

        # Initialize Tavily client
        try:
            from tavily import TavilyClient, AsyncTavilyClient

            self._client = TavilyClient(api_key=api_key)
            self._async_client = AsyncTavilyClient(api_key=api_key)
            logger.info("Tavily search provider initialized")
        except ImportError:
            raise ImportError(
                "tavily-python package is required. Install with: pip install tavily-python"
            )

    async def search(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Execute a search query using Tavily.

        Args:
            query: The search query string
            config: Optional search configuration

        Returns:
            List of SearchResult objects
        """
        config = config or SearchConfig()

        # Build Tavily search parameters
        search_params = {
            "query": query,
            "max_results": config.max_results,
            "search_depth": config.search_depth or self.default_search_depth,
            "include_raw_content": config.include_raw_content or self.include_raw_content,
            "include_images": config.include_images,
        }

        # Add domain filters
        if config.include_domains:
            search_params["include_domains"] = config.include_domains
        if config.exclude_domains:
            search_params["exclude_domains"] = config.exclude_domains

        # Add time filter if specified
        if config.time_range:
            search_params["days"] = self._time_range_to_days(config.time_range)

        logger.debug(f"Tavily search params: {search_params}")

        try:
            # Execute async search
            response = await self._async_client.search(**search_params)
            logger.info(f"Tavily returned {len(response.get('results', []))} results for: {query}")

            # Parse results
            return self._parse_results(response)

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            raise

    def _time_range_to_days(self, time_range: str) -> int:
        """Convert time range string to days."""
        time_map = {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365,
        }
        return time_map.get(time_range.lower(), 30)

    def _parse_results(self, response: Dict[str, Any]) -> List[SearchResult]:
        """
        Parse Tavily API response into SearchResult objects.

        Args:
            response: Raw Tavily API response

        Returns:
            List of SearchResult objects
        """
        results = []

        for item in response.get("results", []):
            # Extract domain from URL
            url = item.get("url", "")
            try:
                source = urlparse(url).netloc
                if source.startswith("www."):
                    source = source[4:]
            except Exception:
                source = None

            # Parse published date if available
            published_date = item.get("published_date")
            if published_date and isinstance(published_date, str):
                # Normalize date format
                try:
                    # Try parsing various formats
                    for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%B %d, %Y"]:
                        try:
                            dt = datetime.strptime(published_date[:10], fmt[:10])
                            published_date = dt.strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass  # Keep original string

            result = SearchResult(
                url=url,
                title=item.get("title", ""),
                content=item.get("content", ""),
                published_date=published_date,
                author=item.get("author"),  # Tavily may not always provide this
                source=source,
                score=item.get("score", 0.0),
                raw_data=item,
            )
            results.append(result)

        # Sort by score (Tavily provides relevance scores)
        results.sort(key=lambda x: x.score, reverse=True)

        return results

    async def get_content(self, url: str) -> Optional[str]:
        """
        Fetch full content from a URL using Tavily's extract feature.

        Args:
            url: The URL to fetch content from

        Returns:
            Full text content or None if unavailable
        """
        try:
            # Use Tavily's extract API for content extraction
            response = await self._async_client.extract(urls=[url])

            if response and "results" in response and response["results"]:
                return response["results"][0].get("raw_content", "")

            return None

        except Exception as e:
            logger.warning(f"Failed to extract content from {url}: {e}")
            return None

    def search_sync(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Synchronous search using Tavily's sync client.

        Args:
            query: The search query string
            config: Optional search configuration

        Returns:
            List of SearchResult objects
        """
        config = config or SearchConfig()

        search_params = {
            "query": query,
            "max_results": config.max_results,
            "search_depth": config.search_depth or self.default_search_depth,
            "include_raw_content": config.include_raw_content or self.include_raw_content,
            "include_images": config.include_images,
        }

        if config.include_domains:
            search_params["include_domains"] = config.include_domains
        if config.exclude_domains:
            search_params["exclude_domains"] = config.exclude_domains
        if config.time_range:
            search_params["days"] = self._time_range_to_days(config.time_range)

        try:
            response = self._client.search(**search_params)
            logger.info(f"Tavily (sync) returned {len(response.get('results', []))} results")
            return self._parse_results(response)

        except Exception as e:
            logger.error(f"Tavily sync search failed: {e}")
            raise

    async def search_with_context(
        self,
        query: str,
        context: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Execute a contextual search using Tavily's QNA mode.

        This is useful when you want search results tailored to
        answer a specific question in context.

        Args:
            query: The search query/question
            context: Additional context to guide the search
            config: Optional search configuration

        Returns:
            List of SearchResult objects
        """
        # Combine query with context for better results
        enhanced_query = f"{query} {context}"

        config = config or SearchConfig()
        config.search_depth = "advanced"  # Use advanced for contextual search

        return await self.search(enhanced_query, config)

    def is_available(self) -> bool:
        """Check if Tavily is properly configured."""
        if not self.api_key:
            return False

        try:
            # Verify client is initialized
            return self._client is not None and self._async_client is not None
        except Exception:
            return False
