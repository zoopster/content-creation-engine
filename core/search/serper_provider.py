"""
Serper Search Provider - Google Search API access.

Serper provides fast, reliable access to Google Search results
via a simple REST API.

Features:
- Google Search results
- News search
- Image search
- Place search
- Shopping search

Requirements:
    pip install aiohttp

Usage:
    from core.search import SerperSearchProvider

    provider = SerperSearchProvider(api_key="your-serper-api-key")
    results = await provider.search("AI in healthcare", max_results=10)

API Documentation: https://serper.dev/docs
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp

from .base import SearchProvider, SearchResult, SearchConfig

logger = logging.getLogger(__name__)


class SerperSearchProvider(SearchProvider):
    """
    Serper search provider implementation.

    Serper provides Google Search API access with support for
    various search types (web, news, images, etc.).
    """

    SERPER_API_URL = "https://google.serper.dev/search"
    SERPER_NEWS_URL = "https://google.serper.dev/news"

    @property
    def name(self) -> str:
        return "serper"

    def __init__(
        self,
        api_key: str,
        country: str = "us",
        language: str = "en",
        **kwargs,
    ):
        """
        Initialize Serper provider.

        Args:
            api_key: Serper API key
            country: Country code for localized results (default: us)
            language: Language code for results (default: en)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.country = country
        self.language = language
        logger.info("Serper search provider initialized")

    async def search(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Execute a search query using Serper.

        Args:
            query: The search query string
            config: Optional search configuration

        Returns:
            List of SearchResult objects
        """
        config = config or SearchConfig()

        # Build Serper request payload
        payload = {
            "q": query,
            "gl": self.country,
            "hl": self.language,
            "num": config.max_results,
        }

        # Add time filter if specified
        if config.time_range:
            payload["tbs"] = self._time_range_to_tbs(config.time_range)

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        logger.debug(f"Serper search payload: {payload}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.SERPER_API_URL,
                    json=payload,
                    headers=headers,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            logger.info(f"Serper returned results for: {query}")

            # Parse results
            results = self._parse_results(data, config)

            # Apply domain filtering (Serper doesn't support this natively)
            if config.include_domains or config.exclude_domains:
                results = self._filter_by_domain(
                    results,
                    config.include_domains,
                    config.exclude_domains,
                )

            return results[:config.max_results]

        except aiohttp.ClientError as e:
            logger.error(f"Serper API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            raise

    def _time_range_to_tbs(self, time_range: str) -> str:
        """Convert time range to Google's tbs parameter."""
        time_map = {
            "day": "qdr:d",
            "week": "qdr:w",
            "month": "qdr:m",
            "year": "qdr:y",
        }
        return time_map.get(time_range.lower(), "")

    def _parse_results(
        self,
        response: Dict[str, Any],
        config: SearchConfig,
    ) -> List[SearchResult]:
        """
        Parse Serper API response into SearchResult objects.

        Args:
            response: Raw Serper API response
            config: Search configuration

        Returns:
            List of SearchResult objects
        """
        results = []

        # Parse organic results
        for i, item in enumerate(response.get("organic", [])):
            url = item.get("link", "")

            # Extract domain
            try:
                source = urlparse(url).netloc
                if source.startswith("www."):
                    source = source[4:]
            except Exception:
                source = None

            # Calculate relevance score based on position
            # First result = 1.0, decreasing by 0.05 per position
            score = max(0.5, 1.0 - (i * 0.05))

            result = SearchResult(
                url=url,
                title=item.get("title", ""),
                content=item.get("snippet", ""),
                published_date=item.get("date"),
                author=None,  # Serper doesn't provide author info
                source=source,
                score=score,
                raw_data=item,
            )
            results.append(result)

        # Optionally include knowledge graph info
        if "knowledgeGraph" in response:
            kg = response["knowledgeGraph"]
            if kg.get("description"):
                results.insert(
                    0,
                    SearchResult(
                        url=kg.get("website", ""),
                        title=kg.get("title", "Knowledge Graph"),
                        content=kg.get("description", ""),
                        source="knowledge_graph",
                        score=1.0,
                        raw_data=kg,
                    ),
                )

        return results

    def _filter_by_domain(
        self,
        results: List[SearchResult],
        include_domains: List[str],
        exclude_domains: List[str],
    ) -> List[SearchResult]:
        """Filter results by domain."""
        filtered = []

        for result in results:
            domain = result.source or ""

            # Check exclusions first
            if exclude_domains:
                if any(excl.lower() in domain.lower() for excl in exclude_domains):
                    continue

            # Check inclusions
            if include_domains:
                if not any(incl.lower() in domain.lower() for incl in include_domains):
                    continue

            filtered.append(result)

        return filtered

    async def search_news(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Search news articles using Serper News API.

        Args:
            query: The search query string
            config: Optional search configuration

        Returns:
            List of SearchResult objects
        """
        config = config or SearchConfig()

        payload = {
            "q": query,
            "gl": self.country,
            "hl": self.language,
            "num": config.max_results,
        }

        if config.time_range:
            payload["tbs"] = self._time_range_to_tbs(config.time_range)

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.SERPER_NEWS_URL,
                    json=payload,
                    headers=headers,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            return self._parse_news_results(data)

        except Exception as e:
            logger.error(f"Serper news search failed: {e}")
            raise

    def _parse_news_results(self, response: Dict[str, Any]) -> List[SearchResult]:
        """Parse Serper news API response."""
        results = []

        for i, item in enumerate(response.get("news", [])):
            url = item.get("link", "")

            try:
                source = urlparse(url).netloc
                if source.startswith("www."):
                    source = source[4:]
            except Exception:
                source = item.get("source")

            score = max(0.5, 1.0 - (i * 0.05))

            result = SearchResult(
                url=url,
                title=item.get("title", ""),
                content=item.get("snippet", ""),
                published_date=item.get("date"),
                author=None,
                source=source,
                score=score,
                raw_data=item,
            )
            results.append(result)

        return results

    async def get_content(self, url: str) -> Optional[str]:
        """
        Fetch content from a URL.

        Note: Serper doesn't provide content extraction,
        so this uses a basic HTTP fetch.

        Args:
            url: The URL to fetch content from

        Returns:
            Full text content or None if unavailable
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Basic text extraction (strip HTML tags)
                        # For production, use BeautifulSoup or similar
                        import re

                        text = re.sub(r"<[^>]+>", " ", html)
                        text = re.sub(r"\s+", " ", text)
                        return text[:5000]  # Limit content length
                    return None

        except Exception as e:
            logger.warning(f"Failed to fetch content from {url}: {e}")
            return None

    def search_sync(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """Synchronous search wrapper."""
        return asyncio.run(self.search(query, config))

    def is_available(self) -> bool:
        """Check if Serper is properly configured."""
        return bool(self.api_key)
