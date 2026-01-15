"""
Anthropic Claude provider implementation.

Supports Claude 3.5/3 family models with full feature support including
streaming, vision, and extended context windows.
"""

import os
from typing import AsyncIterator, Optional

from .base import (
    AuthenticationError,
    GenerationConfig,
    GenerationError,
    GenerationResult,
    Message,
    ModelCapability,
    ModelInfo,
    ModelNotFoundError,
    ModelProvider,
    RateLimitError,
)


# Available Claude models with their specifications
ANTHROPIC_MODELS = [
    ModelInfo(
        id="claude-sonnet-4-20250514",
        provider="anthropic",
        display_name="Claude Sonnet 4",
        max_tokens=8192,
        context_window=200000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
    ModelInfo(
        id="claude-opus-4-20250514",
        provider="anthropic",
        display_name="Claude Opus 4",
        max_tokens=8192,
        context_window=200000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
    ),
    ModelInfo(
        id="claude-3-5-sonnet-20241022",
        provider="anthropic",
        display_name="Claude 3.5 Sonnet",
        max_tokens=8192,
        context_window=200000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
    ModelInfo(
        id="claude-3-5-haiku-20241022",
        provider="anthropic",
        display_name="Claude 3.5 Haiku",
        max_tokens=8192,
        context_window=200000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.0008,
        cost_per_1k_output=0.004,
    ),
    ModelInfo(
        id="claude-3-opus-20240229",
        provider="anthropic",
        display_name="Claude 3 Opus",
        max_tokens=4096,
        context_window=200000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
    ),
    ModelInfo(
        id="claude-3-haiku-20240307",
        provider="anthropic",
        display_name="Claude 3 Haiku",
        max_tokens=4096,
        context_window=200000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.00125,
    ),
]

# Model aliases for convenience
MODEL_ALIASES = {
    "claude-sonnet": "claude-sonnet-4-20250514",
    "claude-sonnet-4": "claude-sonnet-4-20250514",
    "claude-opus": "claude-opus-4-20250514",
    "claude-opus-4": "claude-opus-4-20250514",
    "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
    "claude-3.5-haiku": "claude-3-5-haiku-20241022",
    "claude-3-opus": "claude-3-opus-20240229",
    "claude-3-haiku": "claude-3-haiku-20240307",
    "claude-haiku": "claude-3-5-haiku-20241022",
}


class AnthropicProvider(ModelProvider):
    """
    Anthropic Claude API provider.

    Usage:
        provider = AnthropicProvider(api_key="sk-ant-...")
        result = await provider.generate(
            prompt="Write a haiku about coding",
            model="claude-sonnet-4"
        )
        print(result.content)
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
            **kwargs: Additional options:
                - base_url: Override API base URL
                - timeout: Request timeout in seconds (default: 60)
                - max_retries: Number of retries on failure (default: 2)
        """
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        super().__init__(api_key=api_key, **kwargs)

        self.base_url = kwargs.get("base_url", "https://api.anthropic.com")
        self.timeout = kwargs.get("timeout", 60)
        self.max_retries = kwargs.get("max_retries", 2)
        self._client = None

    @property
    def name(self) -> str:
        return "anthropic"

    def _resolve_model(self, model: str) -> str:
        """Resolve model alias to full model ID."""
        return MODEL_ALIASES.get(model, model)

    def list_models(self) -> list[ModelInfo]:
        return ANTHROPIC_MODELS.copy()

    def _get_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. "
                    "Run: pip install anthropic"
                )

            if not self.api_key:
                raise AuthenticationError(
                    "API key not provided. Set ANTHROPIC_API_KEY environment variable "
                    "or pass api_key to AnthropicProvider.",
                    provider=self.name,
                )

            self._client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
        return self._client

    async def generate(
        self,
        prompt: str,
        model: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """Generate text from a single prompt."""
        messages = [Message(role="user", content=prompt)]
        return await self.generate_chat(messages, model, config)

    async def generate_chat(
        self,
        messages: list[Message],
        model: str,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """Generate text from a conversation."""
        config = config or GenerationConfig()
        model_id = self._resolve_model(model)

        # Validate model
        if not self.validate_model(model_id):
            # Check if it was an alias that didn't resolve
            if model != model_id:
                raise ModelNotFoundError(
                    f"Model '{model}' (resolved to '{model_id}') not found",
                    provider=self.name,
                    model=model,
                )
            raise ModelNotFoundError(
                f"Model '{model}' not found",
                provider=self.name,
                model=model,
            )

        client = self._get_client()

        # Convert messages to Anthropic format
        anthropic_messages = []
        for msg in messages:
            if msg.role == "system":
                # System messages handled separately in Anthropic API
                continue
            anthropic_messages.append({
                "role": msg.role,
                "content": msg.content,
            })

        # Extract system prompt
        system_prompt = config.system_prompt
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
                break

        try:
            import anthropic as anthropic_module

            kwargs = {
                "model": model_id,
                "messages": anthropic_messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            if config.stop_sequences:
                kwargs["stop_sequences"] = config.stop_sequences

            response = await client.messages.create(**kwargs)

            return GenerationResult(
                content=response.content[0].text,
                model=model_id,
                provider=self.name,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                finish_reason=response.stop_reason or "stop",
                raw_response=response,
            )

        except anthropic_module.AuthenticationError as e:
            raise AuthenticationError(str(e), provider=self.name)
        except anthropic_module.RateLimitError as e:
            raise RateLimitError(str(e), provider=self.name)
        except anthropic_module.APIError as e:
            raise GenerationError(str(e), provider=self.name, model=model_id)

    async def generate_stream(
        self,
        prompt: str,
        model: str,
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        """Stream generated text."""
        config = config or GenerationConfig()
        model_id = self._resolve_model(model)
        client = self._get_client()

        try:
            import anthropic as anthropic_module

            kwargs = {
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "stream": True,
            }

            if config.system_prompt:
                kwargs["system"] = config.system_prompt

            async with client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text

        except anthropic_module.APIError as e:
            raise GenerationError(str(e), provider=self.name, model=model_id)
