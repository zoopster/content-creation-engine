"""
Search provider abstraction for real web search integration.

Provides a unified interface for multiple search providers:
- Tavily (AI-optimized search)
- Serper (Google Search API)
- Brave Search (privacy-focused)

Usage:
    from core.search import get_search_provider, SearchResult

    # Get configured provider
    provider = get_search_provider()

    # Execute search
    results = await provider.search("AI in healthcare", max_results=10)

    # Process results
    for result in results:
        print(f"{result.title}: {result.url}")
"""

from .base import SearchProvider, SearchResult, SearchConfig, MockSearchProvider
from .registry import SearchRegistry, get_search_provider, configure_search

# Lazy imports for providers to avoid import errors if dependencies missing
def _get_firecrawl_provider():
    from .firecrawl_provider import FirecrawlSearchProvider
    return FirecrawlSearchProvider

def _get_serper_provider():
    from .serper_provider import SerperSearchProvider
    return SerperSearchProvider

def _get_tavily_provider():
    from .tavily_provider import TavilySearchProvider
    return TavilySearchProvider

__all__ = [
    "SearchProvider",
    "SearchResult",
    "SearchConfig",
    "MockSearchProvider",
    "SearchRegistry",
    "get_search_provider",
    "configure_search",
]

# Make providers accessible but lazy-loaded
def __getattr__(name):
    if name == "FirecrawlSearchProvider":
        return _get_firecrawl_provider()
    if name == "SerperSearchProvider":
        return _get_serper_provider()
    if name == "TavilySearchProvider":
        return _get_tavily_provider()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
