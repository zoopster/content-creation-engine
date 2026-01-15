"""
Base classes for model provider abstraction layer.

This module provides a unified interface for interacting with multiple LLM providers
(Anthropic, OpenAI, etc.) allowing agents to use different models interchangeably.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Optional


class ModelCapability(Enum):
    """Capabilities that a model may support."""
    TEXT_GENERATION = "text_generation"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    LONG_CONTEXT = "long_context"  # >32k tokens


@dataclass
class ModelInfo:
    """Information about a specific model."""
    id: str
    provider: str
    display_name: str
    max_tokens: int
    context_window: int
    capabilities: list[ModelCapability] = field(default_factory=list)
    cost_per_1k_input: float = 0.0  # USD
    cost_per_1k_output: float = 0.0  # USD

    @property
    def supports_vision(self) -> bool:
        return ModelCapability.VISION in self.capabilities

    @property
    def supports_streaming(self) -> bool:
        return ModelCapability.STREAMING in self.capabilities


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    stop_sequences: list[str] = field(default_factory=list)
    system_prompt: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stop_sequences": self.stop_sequences,
            "system_prompt": self.system_prompt,
        }


@dataclass
class Message:
    """A message in a conversation."""
    role: str  # "user", "assistant", "system"
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class GenerationResult:
    """Result from a generation request."""
    content: str
    model: str
    provider: str
    usage: dict[str, int] = field(default_factory=dict)  # input_tokens, output_tokens
    finish_reason: str = "stop"
    raw_response: Optional[Any] = None

    @property
    def total_tokens(self) -> int:
        return self.usage.get("input_tokens", 0) + self.usage.get("output_tokens", 0)

    @property
    def estimated_cost(self) -> float:
        """Estimate cost based on token usage (requires model info)."""
        # This would need model pricing info to calculate
        return 0.0


class ModelProvider(ABC):
    """
    Abstract base class for LLM providers.

    Implementations should handle:
    - API authentication
    - Request formatting for specific provider APIs
    - Response parsing
    - Error handling and retries
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the provider.

        Args:
            api_key: API key for authentication. If None, will attempt to read
                    from environment variable.
            **kwargs: Provider-specific configuration options.
        """
        self.api_key = api_key
        self.config = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'anthropic', 'openai')."""
        pass

    @abstractmethod
    def list_models(self) -> list[ModelInfo]:
        """Return list of available models for this provider."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate text from a prompt.

        Args:
            prompt: The input prompt/message.
            model: Model ID to use.
            config: Generation configuration options.

        Returns:
            GenerationResult with the generated text and metadata.
        """
        pass

    @abstractmethod
    async def generate_chat(
        self,
        messages: list[Message],
        model: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """
        Generate text from a conversation.

        Args:
            messages: List of conversation messages.
            model: Model ID to use.
            config: Generation configuration options.

        Returns:
            GenerationResult with the generated text and metadata.
        """
        pass

    async def generate_stream(
        self,
        prompt: str,
        model: str,
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        """
        Stream generated text from a prompt.

        Default implementation falls back to non-streaming.
        Override for providers that support streaming.
        """
        result = await self.generate(prompt, model, config)
        yield result.content

    def validate_model(self, model: str) -> bool:
        """Check if a model ID is valid for this provider."""
        return any(m.id == model for m in self.list_models())

    def get_model_info(self, model: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        for m in self.list_models():
            if m.id == model:
                return m
        return None


class ProviderError(Exception):
    """Base exception for provider errors."""

    def __init__(self, message: str, provider: str, model: Optional[str] = None):
        self.provider = provider
        self.model = model
        super().__init__(f"[{provider}] {message}")


class AuthenticationError(ProviderError):
    """API key is invalid or missing."""
    pass


class RateLimitError(ProviderError):
    """Rate limit exceeded."""

    def __init__(self, message: str, provider: str, retry_after: Optional[float] = None):
        self.retry_after = retry_after
        super().__init__(message, provider)


class ModelNotFoundError(ProviderError):
    """Requested model does not exist."""
    pass


class GenerationError(ProviderError):
    """Error during text generation."""
    pass
