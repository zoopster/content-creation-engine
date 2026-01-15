"""
Model Registry for managing multiple LLM providers.

The registry provides a unified interface for accessing different model providers,
handles provider initialization, and routes requests to the appropriate provider.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Optional

from .base import (
    GenerationConfig,
    GenerationResult,
    Message,
    ModelInfo,
    ModelProvider,
    ProviderError,
)


@dataclass
class ProviderConfig:
    """Configuration for a model provider."""
    enabled: bool = True
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    max_retries: int = 2
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentModelConfig:
    """Model configuration for a specific agent or skill."""
    provider: str
    model: str
    config: Optional[GenerationConfig] = None

    @classmethod
    def from_dict(cls, data: dict) -> "AgentModelConfig":
        config = None
        if "config" in data:
            config = GenerationConfig(**data["config"])
        return cls(
            provider=data["provider"],
            model=data["model"],
            config=config,
        )


class ModelRegistry:
    """
    Central registry for model providers.

    Manages provider instances, handles routing, and provides a unified
    interface for text generation across different providers.

    Usage:
        # Initialize with default providers
        registry = ModelRegistry()
        registry.register_provider("anthropic", AnthropicProvider())
        registry.register_provider("openai", OpenAIProvider())

        # Generate text
        result = await registry.generate(
            prompt="Write a poem",
            provider="anthropic",
            model="claude-sonnet-4"
        )

        # Or use agent-specific configuration
        registry.set_agent_config("creation", AgentModelConfig(
            provider="anthropic",
            model="claude-sonnet-4"
        ))
        result = await registry.generate_for_agent("creation", "Write a poem")
    """

    # Default model configurations for different use cases
    DEFAULT_CONFIGS = {
        "research": AgentModelConfig(
            provider="anthropic",
            model="claude-3-5-haiku-20241022",  # Fast, cost-effective for research
            config=GenerationConfig(
                max_tokens=4096,
                temperature=0.3,  # Lower temperature for factual research
            ),
        ),
        "creation": AgentModelConfig(
            provider="anthropic",
            model="claude-sonnet-4-20250514",  # Balanced for creative writing
            config=GenerationConfig(
                max_tokens=8192,
                temperature=0.7,  # Higher temperature for creativity
            ),
        ),
        "editing": AgentModelConfig(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            config=GenerationConfig(
                max_tokens=4096,
                temperature=0.3,  # Lower for precise editing
            ),
        ),
        "social": AgentModelConfig(
            provider="anthropic",
            model="claude-3-5-haiku-20241022",  # Fast for short-form content
            config=GenerationConfig(
                max_tokens=1024,
                temperature=0.8,  # Creative for engagement
            ),
        ),
    }

    def __init__(self):
        self._providers: dict[str, ModelProvider] = {}
        self._agent_configs: dict[str, AgentModelConfig] = {}
        self._provider_configs: dict[str, ProviderConfig] = {}

    def register_provider(
        self,
        name: str,
        provider: ModelProvider,
        config: Optional[ProviderConfig] = None,
    ) -> None:
        """
        Register a model provider.

        Args:
            name: Unique identifier for the provider (e.g., "anthropic", "openai")
            provider: Provider instance
            config: Optional provider configuration
        """
        self._providers[name] = provider
        if config:
            self._provider_configs[name] = config

    def get_provider(self, name: str) -> ModelProvider:
        """Get a registered provider by name."""
        if name not in self._providers:
            raise ProviderError(
                f"Provider '{name}' not registered. "
                f"Available: {list(self._providers.keys())}",
                provider=name,
            )
        return self._providers[name]

    def list_providers(self) -> list[str]:
        """List all registered provider names."""
        return list(self._providers.keys())

    def list_all_models(self) -> list[ModelInfo]:
        """List all available models across all providers."""
        models = []
        for provider in self._providers.values():
            models.extend(provider.list_models())
        return models

    def set_agent_config(self, agent_name: str, config: AgentModelConfig) -> None:
        """
        Set model configuration for a specific agent.

        Args:
            agent_name: Name of the agent (e.g., "research", "creation")
            config: Model configuration for this agent
        """
        self._agent_configs[agent_name] = config

    def get_agent_config(self, agent_name: str) -> AgentModelConfig:
        """
        Get model configuration for an agent.

        Falls back to default configuration if not explicitly set.
        """
        if agent_name in self._agent_configs:
            return self._agent_configs[agent_name]
        if agent_name in self.DEFAULT_CONFIGS:
            return self.DEFAULT_CONFIGS[agent_name]
        # Ultimate fallback
        return AgentModelConfig(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
        )

    async def generate(
        self,
        prompt: str,
        provider: str,
        model: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate text using a specific provider and model.

        Args:
            prompt: The input prompt
            provider: Provider name
            model: Model ID
            config: Generation configuration

        Returns:
            GenerationResult with the generated text
        """
        prov = self.get_provider(provider)
        return await prov.generate(prompt, model, config)

    async def generate_chat(
        self,
        messages: list[Message],
        provider: str,
        model: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate text from a conversation.

        Args:
            messages: Conversation messages
            provider: Provider name
            model: Model ID
            config: Generation configuration

        Returns:
            GenerationResult with the generated text
        """
        prov = self.get_provider(provider)
        return await prov.generate_chat(messages, model, config)

    async def generate_for_agent(
        self,
        agent_name: str,
        prompt: str,
        config_override: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate text using the configured model for an agent.

        Args:
            agent_name: Name of the agent
            prompt: The input prompt
            config_override: Optional config to override agent defaults

        Returns:
            GenerationResult with the generated text
        """
        agent_config = self.get_agent_config(agent_name)
        config = config_override or agent_config.config

        return await self.generate(
            prompt=prompt,
            provider=agent_config.provider,
            model=agent_config.model,
            config=config,
        )

    async def generate_chat_for_agent(
        self,
        agent_name: str,
        messages: list[Message],
        config_override: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate text from a conversation using the configured model for an agent.

        Args:
            agent_name: Name of the agent
            messages: Conversation messages
            config_override: Optional config to override agent defaults

        Returns:
            GenerationResult with the generated text
        """
        agent_config = self.get_agent_config(agent_name)
        config = config_override or agent_config.config

        return await self.generate_chat(
            messages=messages,
            provider=agent_config.provider,
            model=agent_config.model,
            config=config,
        )


def create_default_registry() -> ModelRegistry:
    """
    Create a registry with default providers configured from environment.

    Reads API keys from environment variables:
    - ANTHROPIC_API_KEY
    - OPENAI_API_KEY
    """
    from .anthropic_provider import AnthropicProvider
    from .openai_provider import OpenAIProvider

    registry = ModelRegistry()

    # Register Anthropic if API key available
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        registry.register_provider(
            "anthropic",
            AnthropicProvider(api_key=anthropic_key),
            ProviderConfig(api_key=anthropic_key),
        )

    # Register OpenAI if API key available
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        registry.register_provider(
            "openai",
            OpenAIProvider(api_key=openai_key),
            ProviderConfig(api_key=openai_key),
        )

    return registry


# Global registry instance (lazy-loaded)
_global_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    """Get the global model registry, creating it if necessary."""
    global _global_registry
    if _global_registry is None:
        _global_registry = create_default_registry()
    return _global_registry


def set_registry(registry: ModelRegistry) -> None:
    """Set the global model registry."""
    global _global_registry
    _global_registry = registry
