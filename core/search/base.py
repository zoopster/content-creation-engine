"""
Base classes for search provider abstraction.

Defines the interface that all search providers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SearchResult:
    """
    Standardized search result from any provider.

    Attributes:
        url: The URL of the search result
        title: The title of the page/article
        content: Content snippet or full text (provider-dependent)
        published_date: Publication date if available
        author: Author name if available
        source: Source/domain name
        score: Relevance score from provider (0.0-1.0)
        raw_data: Original raw data from provider for debugging
    """

    url: str
    title: str
    content: str = ""
    published_date: Optional[str] = None
    author: Optional[str] = None
    source: Optional[str] = None
    score: float = 0.0
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "published_date": self.published_date,
            "author": self.author,
            "source": self.source,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create from dictionary."""
        return cls(
            url=data.get("url", ""),
            title=data.get("title", ""),
            content=data.get("content", ""),
            published_date=data.get("published_date"),
            author=data.get("author"),
            source=data.get("source"),
            score=data.get("score", 0.0),
            raw_data=data.get("raw_data", {}),
        )


@dataclass
class SearchConfig:
    """
    Configuration for search requests.

    Attributes:
        max_results: Maximum number of results to return
        search_depth: Search depth (basic or advanced for Tavily)
        include_domains: List of domains to include
        exclude_domains: List of domains to exclude
        time_range: Time filter (day, week, month, year)
        include_raw_content: Whether to fetch full page content
        include_images: Whether to include image results
    """

    max_results: int = 10
    search_depth: str = "basic"  # basic or advanced
    include_domains: List[str] = field(default_factory=list)
    exclude_domains: List[str] = field(default_factory=list)
    time_range: Optional[str] = None  # day, week, month, year
    include_raw_content: bool = False
    include_images: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_results": self.max_results,
            "search_depth": self.search_depth,
            "include_domains": self.include_domains,
            "exclude_domains": self.exclude_domains,
            "time_range": self.time_range,
            "include_raw_content": self.include_raw_content,
            "include_images": self.include_images,
        }


class SearchProvider(ABC):
    """
    Abstract base class for search providers.

    All search providers must implement this interface to ensure
    consistent behavior across different backends.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the search provider.

        Args:
            api_key: API key for the search service
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self._validate_api_key()

    def _validate_api_key(self) -> None:
        """Validate that API key is provided."""
        if not self.api_key:
            raise ValueError(f"{self.__class__.__name__} requires an API key")

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Execute a search query.

        Args:
            query: The search query string
            config: Optional search configuration

        Returns:
            List of SearchResult objects
        """
        pass

    def search_sync(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Synchronous wrapper for search.

        Args:
            query: The search query string
            config: Optional search configuration

        Returns:
            List of SearchResult objects
        """
        import asyncio

        return asyncio.run(self.search(query, config))

    @abstractmethod
    async def get_content(self, url: str) -> Optional[str]:
        """
        Fetch full content from a URL.

        Args:
            url: The URL to fetch content from

        Returns:
            Full text content or None if unavailable
        """
        pass

    def is_available(self) -> bool:
        """
        Check if the provider is properly configured and available.

        Returns:
            True if the provider can be used
        """
        return bool(self.api_key)


class MockSearchProvider(SearchProvider):
    """
    Mock search provider for testing and development.

    Returns realistic mock results without making API calls.
    """

    @property
    def name(self) -> str:
        return "mock"

    def __init__(self, api_key: str = "mock-key", **kwargs):
        """Initialize mock provider (doesn't require real API key)."""
        self.api_key = api_key or "mock-key"

    def _validate_api_key(self) -> None:
        """Mock provider doesn't require API key validation."""
        pass

    async def search(
        self,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """Return mock search results."""
        config = config or SearchConfig()
        words = query.split()
        key_term = words[0] if words else "topic"

        mock_results = [
            SearchResult(
                url=f"https://research.edu/{key_term.lower()}-study",
                title=f"Comprehensive Study on {query.title()}",
                content=f"This peer-reviewed study examines {query.lower()} across multiple industries. "
                f"Key findings indicate 42% improvement in operational efficiency and 28% cost reduction.",
                published_date="2025-11-15",
                author="Dr. Sarah Chen, PhD",
                source="research.edu",
                score=0.95,
            ),
            SearchResult(
                url=f"https://techcrunch.com/{key_term.lower()}-trends-2026",
                title=f"Industry Report: {query.title()} Trends 2026",
                content=f"The {query.lower()} landscape is evolving rapidly. According to Gartner, "
                f"73% of organizations plan to increase investments this year.",
                published_date="2026-01-08",
                author="Maria Rodriguez",
                source="techcrunch.com",
                score=0.88,
            ),
            SearchResult(
                url=f"https://hbr.org/{key_term.lower()}-implementation",
                title=f"Strategic Implementation of {query.title()}: A Framework",
                content=f"Successful {query.lower()} implementation requires strategic alignment. "
                f"Our research across 200 Fortune 500 companies identifies five critical success factors.",
                published_date="2025-10-22",
                author="Prof. Michael Chang",
                source="hbr.org",
                score=0.85,
            ),
            SearchResult(
                url=f"https://nature.com/articles/{key_term.lower()}-review",
                title=f"Scientific Review: {query.title()} - Current State",
                content=f"This systematic review analyzes 156 peer-reviewed studies on {query.lower()}. "
                f"Meta-analysis findings show effect size (Cohen's d) of 0.72.",
                published_date="2025-09-30",
                author="Dr. Emily Watson et al.",
                source="nature.com",
                score=0.92,
            ),
            SearchResult(
                url=f"https://forbes.com/{key_term.lower()}-roi",
                title=f"The ROI Reality: What {query.title()} Actually Delivers",
                content=f"We analyzed financial data from 500 implementations. Average ROI: 287% over 3 years. "
                f"Median payback period: 16 months.",
                published_date="2025-12-01",
                author="David Kim",
                source="forbes.com",
                score=0.80,
            ),
        ]

        return mock_results[: config.max_results]

    async def get_content(self, url: str) -> Optional[str]:
        """Return mock content."""
        return f"Mock full content for {url}. This is placeholder text for testing purposes."
