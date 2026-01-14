"""
Web Search Skill - Executes optimized web searches and returns structured results.

Uses search APIs to find relevant sources based on queries.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, List, Any, Optional
from agents.base.agent import Skill
from datetime import datetime


class WebSearchSkill(Skill):
    """
    Executes web searches with query optimization.

    Features:
    - Query optimization for better results
    - Result parsing and structuring
    - Deduplication
    - Relevance filtering
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("web-search", config)
        self.max_results = config.get("max_results", 10) if config else 10
        self.enable_filtering = config.get("enable_filtering", True) if config else True

    def execute(
        self,
        query: str,
        max_results: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Execute a web search.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            **kwargs: Additional search parameters (e.g., date_filter, domain_filter)

        Returns:
            List of search result dictionaries
        """
        max_results = max_results or self.max_results

        self.logger.info(f"Executing web search: {query}")

        # In a real implementation, this would call the WebSearch tool
        # For now, we'll return a structured format that can be populated
        # by the calling code

        results = self._execute_search(query, max_results, **kwargs)

        if self.enable_filtering:
            results = self._filter_results(results, query)

        results = self._deduplicate_results(results)

        self.logger.info(f"Returning {len(results)} search results")

        return results[:max_results]

    def _execute_search(
        self,
        query: str,
        max_results: int,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Execute the actual search.

        This method should be called by the Research Agent or orchestrator
        with the WebSearch tool integrated.

        Args:
            query: Search query
            max_results: Maximum results
            **kwargs: Additional parameters

        Returns:
            List of search results
        """
        # Placeholder for actual search implementation
        # In production, this would use the WebSearch tool

        # The expected format returned:
        # [
        #     {
        #         "title": "Article Title",
        #         "url": "https://example.com/article",
        #         "content": "Article content preview or full text",
        #         "published_date": "2024-01-15",
        #         "author": "Author Name",
        #         "source": "Source Name"
        #     },
        #     ...
        # ]

        return []

    def _filter_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
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
            # Basic relevance check
            title = result.get("title", "").lower()
            content = result.get("content", "").lower()

            # Count query term matches
            title_matches = sum(1 for term in query_terms if term in title)
            content_matches = sum(1 for term in query_terms if term in content)

            # Require at least some matches
            if title_matches > 0 or content_matches > 1:
                result["_relevance_score"] = title_matches * 2 + content_matches
                filtered.append(result)

        # Sort by relevance
        filtered.sort(key=lambda x: x.get("_relevance_score", 0), reverse=True)

        return filtered

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
            # (simple check: exact match after lowercasing)
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

        # Add domain restrictions
        if requirements.get("domains"):
            domains = requirements["domains"]
            if isinstance(domains, list):
                # Add site: operators for specific domains
                domain_queries = [f"site:{domain}" for domain in domains]
                query += " (" + " OR ".join(domain_queries) + ")"

        # Add content type hints
        content_type = requirements.get("content_type")
        if content_type:
            query += f" {content_type}"

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
        # This method can be used to normalize results from different search APIs
        # into a consistent format

        if isinstance(raw_result, dict):
            return {
                "title": raw_result.get("title", ""),
                "url": raw_result.get("url", raw_result.get("link", "")),
                "content": raw_result.get("content", raw_result.get("snippet", "")),
                "published_date": raw_result.get("published_date", raw_result.get("date")),
                "author": raw_result.get("author"),
                "source": raw_result.get("source", raw_result.get("domain"))
            }

        return {}
