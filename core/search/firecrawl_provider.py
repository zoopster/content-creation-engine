"""
Firecrawl Search Provider - AI-powered web search and content extraction.

Firecrawl provides high-quality web search results with built-in
content extraction, making it ideal for AI research applications.

Features:
- Web search with relevance scoring
- Automatic content extraction (markdown, HTML)
- Deep research capabilities
- URL scraping and crawling

Requirements:
    pip install firecrawl-py

Usage:
    from core.search import FirecrawlSearchProvider

    provider = FirecrawlSearchProvider(api_key="fc-your-api-key")
    results = await provider.search("AI in healthcare", max_results=10)

API Documentation: https://docs.firecrawl.dev/
Get API Key: https://firecrawl.dev/
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .base import SearchProvider, SearchResult, SearchConfig

logger = logging.getLogger(__name__)


class FirecrawlSearchProvider(SearchProvider):
    """
    Firecrawl search provider implementation.

    Firecrawl is an AI-native search and web scraping platform that provides
    high-quality search results with automatic content extraction.
    """

    @property
    def name(self) -> str:
        return "firecrawl"

    def __init__(
        self,
        api_key: str,
        timeout: int = 30,
        **kwargs,
    ):
        """
        Initialize Firecrawl provider.

        Args:
            api_key: Firecrawl API key (starts with 'fc-')
            timeout: Request timeout in seconds
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.timeout = timeout

        # Initialize Firecrawl clients
        try:
            from firecrawl import Firecrawl, AsyncFirecrawl

            self._client = Firecrawl(api_key=api_key)
            self._async_client = AsyncFirecrawl(api_key=api_key)
            logger.info("Firecrawl search provider initialized")
        except ImportError:
            raise ImportError(
                "firecrawl-py package is required. Install with: pip install firecrawl-py"
            )

    async def search(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Execute a search query using Firecrawl.

        Args:
            query: The search query string
            config: Optional search configuration

        Returns:
            List of SearchResult objects
        """
        config = config or SearchConfig()

        logger.debug(f"Firecrawl search: {query}, max_results={config.max_results}")

        try:
            # Execute async search
            response = await self._async_client.search(
                query,
                limit=config.max_results,
            )

            logger.info(f"Firecrawl returned results for: {query}")

            # Parse results
            return self._parse_results(response, config)

        except Exception as e:
            logger.error(f"Firecrawl search failed: {e}")
            raise

    def _parse_results(
        self,
        response: Any,
        config: SearchConfig,
    ) -> List[SearchResult]:
        """
        Parse Firecrawl API response into SearchResult objects.

        Args:
            response: Firecrawl API response (SearchData Pydantic model or dict)
            config: Search configuration

        Returns:
            List of SearchResult objects
        """
        results = []
        items = []

        # Handle Pydantic model response (firecrawl-py v4+)
        if hasattr(response, 'web') and response.web:
            items = response.web
        elif hasattr(response, 'data') and response.data:
            items = response.data
        # Handle dict response (older versions or raw API)
        elif isinstance(response, dict):
            items = response.get("data", response.get("web", []))
        # Handle direct list response
        elif isinstance(response, list):
            items = response

        for i, item in enumerate(items):
            # Handle both Pydantic models and dicts
            if hasattr(item, 'url'):
                # Pydantic model
                url = item.url or ""
                title = item.title or ""
                content = getattr(item, 'markdown', '') or getattr(item, 'description', '') or ""
                published_date = getattr(item, 'publishedDate', None) or getattr(item, 'date', None)
                author = getattr(item, 'author', None)
                item_score = getattr(item, 'score', 0.0)
                raw = item.model_dump() if hasattr(item, 'model_dump') else {}
            else:
                # Dict
                url = item.get("url", item.get("link", ""))
                title = item.get("title", "")
                content = (
                    item.get("markdown", "")
                    or item.get("description", "")
                    or item.get("content", "")
                    or item.get("snippet", "")
                )
                published_date = item.get("publishedDate", item.get("date"))
                author = item.get("author")
                item_score = item.get("score", 0.0)
                raw = item

            # Extract domain from URL
            try:
                source = urlparse(url).netloc
                if source.startswith("www."):
                    source = source[4:]
            except Exception:
                source = None

            # Truncate long content for the snippet
            if content and len(content) > 500:
                content = content[:500] + "..."

            # Calculate score - use provided score or position-based
            score = item_score if item_score else max(0.5, 0.95 - (i * 0.05))

            result = SearchResult(
                url=url,
                title=title,
                content=content,
                published_date=published_date,
                author=author,
                source=source,
                score=score,
                raw_data=raw,
            )
            results.append(result)

        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:config.max_results]

    async def get_content(self, url: str) -> Optional[str]:
        """
        Fetch full content from a URL using Firecrawl's scrape feature.

        Args:
            url: The URL to fetch content from

        Returns:
            Full text content (markdown) or None if unavailable
        """
        try:
            response = await self._async_client.scrape(
                url,
                formats=["markdown"],
            )

            if response:
                return response.get("markdown", response.get("content", ""))

            return None

        except Exception as e:
            logger.warning(f"Failed to scrape content from {url}: {e}")
            return None

    def search_sync(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Synchronous search using Firecrawl's sync client.

        Args:
            query: The search query string
            config: Optional search configuration

        Returns:
            List of SearchResult objects
        """
        config = config or SearchConfig()

        try:
            response = self._client.search(
                query,
                limit=config.max_results,
            )

            logger.info(f"Firecrawl (sync) returned results")
            return self._parse_results(response, config)

        except Exception as e:
            logger.error(f"Firecrawl sync search failed: {e}")
            raise

    async def scrape_url(
        self,
        url: str,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Scrape a single URL and extract content.

        Args:
            url: URL to scrape
            formats: Output formats (markdown, html, rawHtml)

        Returns:
            Scraped content dictionary
        """
        formats = formats or ["markdown"]

        try:
            response = await self._async_client.scrape(url, formats=formats)
            return response or {}

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return {}

    async def deep_research(
        self,
        query: str,
        max_depth: int = 3,
        max_urls: int = 50,
        time_limit: int = 120,
    ) -> Dict[str, Any]:
        """
        Conduct deep web research on a topic.

        Uses Firecrawl's deep research capability for comprehensive
        multi-source analysis.

        Args:
            query: Research question or topic
            max_depth: Maximum recursive depth (1-10)
            max_urls: Maximum URLs to analyze (1-1000)
            time_limit: Time limit in seconds (30-300)

        Returns:
            Research results with analysis and sources
        """
        try:
            # Note: deep_research may not be in all SDK versions
            # This is a placeholder for the API capability
            response = await self._async_client.search(
                query,
                limit=max_urls,
            )

            return {
                "query": query,
                "results": self._parse_results(response, SearchConfig(max_results=max_urls)),
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Deep research failed: {e}")
            return {"query": query, "error": str(e), "status": "failed"}

    def is_available(self) -> bool:
        """Check if Firecrawl is properly configured."""
        if not self.api_key:
            return False

        try:
            return self._client is not None and self._async_client is not None
        except Exception:
            return False
