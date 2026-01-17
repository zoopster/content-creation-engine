"""
Search provider registry and configuration.

Manages search provider instances and provides factory methods
for getting configured providers.
"""

import os
import logging
from typing import Dict, Optional, Type

from .base import SearchProvider, SearchConfig, SearchResult, MockSearchProvider

logger = logging.getLogger(__name__)

# Global registry instance
_global_registry: Optional["SearchRegistry"] = None


class SearchRegistry:
    """
    Registry for managing search provider instances.

    Handles provider registration, configuration, and retrieval.

    Usage:
        registry = SearchRegistry()
        registry.register_provider("tavily", TavilyProvider, api_key="...")

        provider = registry.get_provider("tavily")
        results = await provider.search("AI healthcare")
    """

    def __init__(self):
        """Initialize empty registry."""
        self._providers: Dict[str, SearchProvider] = {}
        self._provider_classes: Dict[str, Type[SearchProvider]] = {}
        self._default_provider: Optional[str] = None

    def register_provider(
        self,
        name: str,
        provider: SearchProvider,
        set_default: bool = False,
    ) -> None:
        """
        Register a search provider instance.

        Args:
            name: Unique name for the provider
            provider: SearchProvider instance
            set_default: If True, set as default provider
        """
        self._providers[name] = provider
        logger.info(f"Registered search provider: {name}")

        if set_default or self._default_provider is None:
            self._default_provider = name
            logger.info(f"Set default search provider: {name}")

    def register_provider_class(
        self,
        name: str,
        provider_class: Type[SearchProvider],
    ) -> None:
        """
        Register a provider class for lazy initialization.

        Args:
            name: Unique name for the provider
            provider_class: SearchProvider class (not instance)
        """
        self._provider_classes[name] = provider_class

    def get_provider(self, name: Optional[str] = None) -> Optional[SearchProvider]:
        """
        Get a search provider by name.

        Args:
            name: Provider name. If None, returns default provider.

        Returns:
            SearchProvider instance or None if not found
        """
        if name is None:
            name = self._default_provider

        if name is None:
            return None

        return self._providers.get(name)

    def get_default_provider(self) -> Optional[SearchProvider]:
        """Get the default search provider."""
        return self.get_provider(self._default_provider)

    def set_default(self, name: str) -> None:
        """Set the default provider by name."""
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not registered")
        self._default_provider = name

    def list_providers(self) -> list[str]:
        """List all registered provider names."""
        return list(self._providers.keys())

    def is_available(self, name: Optional[str] = None) -> bool:
        """Check if a provider is available."""
        provider = self.get_provider(name)
        return provider is not None and provider.is_available()


def get_global_registry() -> SearchRegistry:
    """Get or create the global search registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = SearchRegistry()
    return _global_registry


def configure_search(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    use_mock: bool = False,
) -> SearchRegistry:
    """
    Configure search providers from environment and parameters.

    Checks for API keys in this order:
    1. Explicit api_key parameter
    2. Environment variables (FIRECRAWL_API_KEY, SERPER_API_KEY, TAVILY_API_KEY)

    Args:
        provider: Preferred provider name (firecrawl, serper, tavily)
        api_key: Explicit API key (overrides environment)
        use_mock: If True, use mock provider (for testing)

    Returns:
        Configured SearchRegistry instance
    """
    registry = get_global_registry()

    # If mock requested, register and return
    if use_mock or os.environ.get("USE_MOCK_SEARCH", "").lower() == "true":
        mock_provider = MockSearchProvider()
        registry.register_provider("mock", mock_provider, set_default=True)
        logger.info("Using mock search provider")
        return registry

    # Try to configure real providers
    providers_configured = 0

    # Firecrawl (recommended - AI-optimized search with content extraction)
    firecrawl_key = api_key if provider == "firecrawl" else None
    firecrawl_key = firecrawl_key or os.environ.get("FIRECRAWL_API_KEY")
    if firecrawl_key:
        try:
            from .firecrawl_provider import FirecrawlSearchProvider

            firecrawl = FirecrawlSearchProvider(api_key=firecrawl_key)
            registry.register_provider(
                "firecrawl", firecrawl, set_default=(provider == "firecrawl" or providers_configured == 0)
            )
            providers_configured += 1
            logger.info("Firecrawl search provider configured")
        except ImportError:
            logger.warning("Firecrawl provider not available (missing firecrawl-py package)")
        except Exception as e:
            logger.warning(f"Failed to configure Firecrawl provider: {e}")

    # Serper (Google Search API)
    serper_key = api_key if provider == "serper" else None
    serper_key = serper_key or os.environ.get("SERPER_API_KEY")
    if serper_key:
        try:
            from .serper_provider import SerperSearchProvider

            serper = SerperSearchProvider(api_key=serper_key)
            registry.register_provider(
                "serper", serper, set_default=(provider == "serper" and providers_configured == 0)
            )
            providers_configured += 1
        except ImportError:
            logger.warning("Serper provider not available")
        except Exception as e:
            logger.warning(f"Failed to configure Serper provider: {e}")

    # Tavily (legacy support)
    tavily_key = api_key if provider == "tavily" else None
    tavily_key = tavily_key or os.environ.get("TAVILY_API_KEY")
    if tavily_key:
        try:
            from .tavily_provider import TavilySearchProvider

            tavily = TavilySearchProvider(api_key=tavily_key)
            registry.register_provider(
                "tavily", tavily, set_default=(provider == "tavily" and providers_configured == 0)
            )
            providers_configured += 1
        except ImportError:
            logger.warning("Tavily provider not available (missing tavily-python package)")
        except Exception as e:
            logger.warning(f"Failed to configure Tavily provider: {e}")

    # If no providers configured, fall back to mock
    if providers_configured == 0:
        logger.warning("No search providers configured, falling back to mock provider")
        mock_provider = MockSearchProvider()
        registry.register_provider("mock", mock_provider, set_default=True)

    return registry


def get_search_provider(name: Optional[str] = None) -> Optional[SearchProvider]:
    """
    Get a configured search provider.

    If the registry hasn't been configured, attempts auto-configuration
    from environment variables.

    Args:
        name: Provider name. If None, returns default provider.

    Returns:
        SearchProvider instance or None if not available
    """
    registry = get_global_registry()

    # Auto-configure if no providers registered
    if not registry.list_providers():
        configure_search()

    return registry.get_provider(name)
