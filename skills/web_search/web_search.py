"""
Web Search Skill - Executes optimized web searches and returns structured results.

Uses configurable search providers (Tavily, Serper, etc.) to find relevant sources.
Includes query optimization, result filtering, and deduplication.

Usage:
    from skills.web_search import WebSearchSkill

    # With auto-configured provider (from environment)
    skill = WebSearchSkill()
    results = await skill.execute_async("AI in healthcare", max_results=10)

    # With specific provider
    skill = WebSearchSkill(config={"provider": "tavily"})

    # Synchronous usage
    results = skill.execute("AI in healthcare")
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from agents.base.agent import Skill

logger = logging.getLogger(__name__)


class WebSearchSkill(Skill):
    """
    Executes web searches with query optimization.

    Features:
    - Multiple search provider support (Tavily, Serper, mock)
    - Query optimization for better results
    - Result parsing and structuring
    - Deduplication
    - Relevance filtering
    - Domain filtering

    Configuration:
        config = {
            "provider": "tavily",           # Search provider (tavily, serper, mock)
            "max_results": 10,              # Default max results
            "enable_filtering": True,       # Enable relevance filtering
            "search_depth": "basic",        # basic or advanced
            "include_raw_content": False,   # Include full page content
        }
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("web-search", config)
        config = config or {}

        self.max_results = config.get("max_results", 10)
        self.enable_filtering = config.get("enable_filtering", True)
        self.provider_name = config.get("provider")
        self.search_depth = config.get("search_depth", "basic")
        self.include_raw_content = config.get("include_raw_content", False)

        # Search provider will be initialized lazily
        self._search_provider = None

    def _get_search_provider(self):
        """Get or initialize the search provider."""
        if self._search_provider is None:
            try:
                from core.search import get_search_provider, configure_search

                # Configure search from environment if not already done
                configure_search(provider=self.provider_name)
                self._search_provider = get_search_provider(self.provider_name)

                if self._search_provider:
                    self.logger.info(
                        f"Using search provider: {self._search_provider.name}"
                    )
                else:
                    self.logger.warning("No search provider available, using mock")
                    from core.search.base import MockSearchProvider

                    self._search_provider = MockSearchProvider()

            except ImportError as e:
                self.logger.warning(f"Search providers not available: {e}")
                from core.search.base import MockSearchProvider

                self._search_provider = MockSearchProvider()

        return self._search_provider

    async def execute_async(
        self,
        query: str,
        max_results: Optional[int] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Execute a web search asynchronously.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            **kwargs: Additional search parameters
                - include_domains: List of domains to include
                - exclude_domains: List of domains to exclude
                - time_range: Time filter (day, week, month, year)
                - search_depth: basic or advanced

        Returns:
            List of search result dictionaries
        """
        max_results = max_results or self.max_results
        provider = self._get_search_provider()

        self.logger.info(f"Executing web search: {query}")

        # Build search configuration
        from core.search.base import SearchConfig

        search_config = SearchConfig(
            max_results=max_results,
            search_depth=kwargs.get("search_depth", self.search_depth),
            include_domains=kwargs.get("include_domains", []),
            exclude_domains=kwargs.get("exclude_domains", []),
            time_range=kwargs.get("time_range"),
            include_raw_content=kwargs.get("include_raw_content", self.include_raw_content),
        )

        # Execute search
        try:
            search_results = await provider.search(query, search_config)

            # Convert to dictionaries
            results = [result.to_dict() for result in search_results]

            self.logger.info(f"Search returned {len(results)} results")

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            results = []

        # Apply additional filtering if enabled
        if self.enable_filtering and results:
            results = self._filter_results(results, query)

        # Deduplicate
        results = self._deduplicate_results(results)

        self.logger.info(f"Returning {len(results)} filtered results")

        return results[:max_results]

    def execute(
        self,
        query: str,
        max_results: Optional[int] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Execute a web search synchronously.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of search result dictionaries
        """
        return asyncio.run(self.execute_async(query, max_results, **kwargs))

    def _filter_results(
        self, results: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Filter search results for relevance and quality.

        Args:
            results: Raw search results
            query: Original query

        Returns:
            Filtered results
        """
        filtered = []
        query_terms = set(query.lower().split())

        for result in results:
            title = result.get("title", "").lower()
            content = result.get("content", "").lower()

            # Count query term matches
            title_matches = sum(1 for term in query_terms if term in title)
            content_matches = sum(1 for term in query_terms if term in content)

            # Require at least some matches (or high provider score)
            provider_score = result.get("score", 0)
            if title_matches > 0 or content_matches > 1 or provider_score > 0.7:
                result["_relevance_score"] = (
                    title_matches * 2 + content_matches + provider_score * 5
                )
                filtered.append(result)

        # Sort by relevance
        filtered.sort(key=lambda x: x.get("_relevance_score", 0), reverse=True)

        return filtered

    def _deduplicate_results(
        self, results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate results based on URL and title similarity.

        Args:
            results: Search results

        Returns:
            Deduplicated results
        """
        seen_urls = set()
        seen_titles = set()
        deduplicated = []

        for result in results:
            url = result.get("url", "")
            title = result.get("title", "").lower()

            # Skip if we've seen this URL
            if url in seen_urls:
                continue

            # Skip if we've seen a very similar title
            if title in seen_titles:
                continue

            seen_urls.add(url)
            seen_titles.add(title)
            deduplicated.append(result)

        return deduplicated

    def optimize_query(self, base_query: str, requirements: Dict[str, Any]) -> str:
        """
        Optimize a search query based on requirements.

        Args:
            base_query: Base search query
            requirements: Search requirements

        Returns:
            Optimized query string
        """
        query = base_query

        # Add time constraints
        if requirements.get("recent_only"):
            current_year = datetime.now().year
            query += f" {current_year}"
        elif requirements.get("year"):
            query += f" {requirements['year']}"

        # Add domain restrictions (for query, not API filter)
        if requirements.get("site"):
            query += f" site:{requirements['site']}"

        # Add content type hints
        content_type = requirements.get("content_type")
        if content_type:
            type_hints = {
                "technical": "technical guide implementation",
                "business": "business strategy ROI",
                "academic": "research study peer-reviewed",
                "news": "news latest update",
            }
            query += " " + type_hints.get(content_type, content_type)

        # Add must-include terms
        if requirements.get("must_include"):
            must_terms = requirements["must_include"]
            if isinstance(must_terms, list):
                query += " " + " ".join(f'"{term}"' for term in must_terms)

        # Add exclusions
        if requirements.get("exclude"):
            exclude_terms = requirements["exclude"]
            if isinstance(exclude_terms, list):
                query += " " + " ".join(f'-"{term}"' for term in exclude_terms)

        return query.strip()

    def parse_search_result(self, raw_result: Any) -> Dict[str, Any]:
        """
        Parse a raw search result into standard format.

        Args:
            raw_result: Raw result from search API

        Returns:
            Standardized result dictionary
        """
        if isinstance(raw_result, dict):
            # Extract domain from URL
            url = raw_result.get("url", raw_result.get("link", ""))
            try:
                source = urlparse(url).netloc
                if source.startswith("www."):
                    source = source[4:]
            except Exception:
                source = raw_result.get("source", raw_result.get("domain"))

            return {
                "title": raw_result.get("title", ""),
                "url": url,
                "content": raw_result.get(
                    "content", raw_result.get("snippet", raw_result.get("description", ""))
                ),
                "published_date": raw_result.get(
                    "published_date", raw_result.get("date")
                ),
                "author": raw_result.get("author"),
                "source": source,
                "score": raw_result.get("score", 0.0),
            }

        return {}

    async def search_multiple_queries(
        self,
        queries: List[str],
        max_results_per_query: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple search queries and combine results.

        Args:
            queries: List of search queries
            max_results_per_query: Max results per query

        Returns:
            Combined, deduplicated results
        """
        all_results = []

        # Execute searches concurrently
        tasks = [
            self.execute_async(query, max_results=max_results_per_query)
            for query in queries
        ]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)

        for results in results_lists:
            if isinstance(results, list):
                all_results.extend(results)
            elif isinstance(results, Exception):
                self.logger.warning(f"Search query failed: {results}")

        # Deduplicate combined results
        return self._deduplicate_results(all_results)

    async def get_full_content(self, url: str) -> Optional[str]:
        """
        Fetch full content from a URL.

        Args:
            url: URL to fetch content from

        Returns:
            Full text content or None
        """
        provider = self._get_search_provider()

        try:
            return await provider.get_content(url)
        except Exception as e:
            self.logger.warning(f"Failed to fetch content from {url}: {e}")
            return None
