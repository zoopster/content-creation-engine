"""
Model Provider Abstraction Layer.

This module provides a unified interface for interacting with multiple LLM providers,
allowing the Content Creation Engine to use different models interchangeably.

Usage:
    from core.models import get_registry, GenerationConfig

    # Get the global registry (auto-configures from environment)
    registry = get_registry()

    # Generate text with a specific provider/model
    result = await registry.generate(
        prompt="Write an article about AI",
        provider="anthropic",
        model="claude-sonnet-4"
    )

    # Or use agent-specific configuration
    result = await registry.generate_for_agent("creation", "Write an article about AI")

Providers:
    - AnthropicProvider: Claude models (claude-sonnet-4, claude-opus-4, etc.)
    - OpenAIProvider: GPT models (gpt-4o, gpt-4-turbo, etc.)

Configuration:
    Set API keys via environment variables:
    - ANTHROPIC_API_KEY
    - OPENAI_API_KEY
"""

from .base import (
    GenerationConfig,
    GenerationResult,
    Message,
    ModelCapability,
    ModelInfo,
    ModelProvider,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    GenerationError,
)

from .registry import (
    AgentModelConfig,
    ModelRegistry,
    ProviderConfig,
    create_default_registry,
    get_registry,
    set_registry,
)

from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider
from .config import (
    ModelConfigManager,
    load_config_from_env,
    DEFAULT_MODEL_CONFIG,
)

__all__ = [
    # Base classes
    "GenerationConfig",
    "GenerationResult",
    "Message",
    "ModelCapability",
    "ModelInfo",
    "ModelProvider",
    # Exceptions
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    "ModelNotFoundError",
    "GenerationError",
    # Registry
    "AgentModelConfig",
    "ModelRegistry",
    "ProviderConfig",
    "create_default_registry",
    "get_registry",
    "set_registry",
    # Providers
    "AnthropicProvider",
    "OpenAIProvider",
    # Config
    "ModelConfigManager",
    "load_config_from_env",
    "DEFAULT_MODEL_CONFIG",
]
