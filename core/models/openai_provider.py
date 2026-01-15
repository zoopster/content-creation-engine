"""
OpenAI GPT provider implementation.

Supports GPT-4, GPT-4o, and GPT-3.5 family models with full feature support
including streaming, vision, and function calling.
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


# Available OpenAI models with their specifications
OPENAI_MODELS = [
    ModelInfo(
        id="gpt-4o",
        provider="openai",
        display_name="GPT-4o",
        max_tokens=16384,
        context_window=128000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.0025,
        cost_per_1k_output=0.01,
    ),
    ModelInfo(
        id="gpt-4o-mini",
        provider="openai",
        display_name="GPT-4o Mini",
        max_tokens=16384,
        context_window=128000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
    ),
    ModelInfo(
        id="gpt-4-turbo",
        provider="openai",
        display_name="GPT-4 Turbo",
        max_tokens=4096,
        context_window=128000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
    ),
    ModelInfo(
        id="gpt-4",
        provider="openai",
        display_name="GPT-4",
        max_tokens=8192,
        context_window=8192,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
        ],
        cost_per_1k_input=0.03,
        cost_per_1k_output=0.06,
    ),
    ModelInfo(
        id="gpt-3.5-turbo",
        provider="openai",
        display_name="GPT-3.5 Turbo",
        max_tokens=4096,
        context_window=16385,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
        ],
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.0015,
    ),
    ModelInfo(
        id="o1",
        provider="openai",
        display_name="o1",
        max_tokens=100000,
        context_window=200000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.06,
    ),
    ModelInfo(
        id="o1-mini",
        provider="openai",
        display_name="o1 Mini",
        max_tokens=65536,
        context_window=128000,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.LONG_CONTEXT,
        ],
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.012,
    ),
]

# Model aliases for convenience
MODEL_ALIASES = {
    "gpt4": "gpt-4",
    "gpt4o": "gpt-4o",
    "gpt-4-o": "gpt-4o",
    "gpt4-mini": "gpt-4o-mini",
    "gpt-4o-mini": "gpt-4o-mini",
    "gpt35": "gpt-3.5-turbo",
    "gpt-35": "gpt-3.5-turbo",
    "chatgpt": "gpt-4o",
}


class OpenAIProvider(ModelProvider):
    """
    OpenAI GPT API provider.

    Usage:
        provider = OpenAIProvider(api_key="sk-...")
        result = await provider.generate(
            prompt="Write a haiku about coding",
            model="gpt-4o"
        )
        print(result.content)
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key. Falls back to OPENAI_API_KEY env var.
            **kwargs: Additional options:
                - base_url: Override API base URL (for Azure OpenAI, etc.)
                - organization: OpenAI organization ID
                - timeout: Request timeout in seconds (default: 60)
                - max_retries: Number of retries on failure (default: 2)
        """
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        super().__init__(api_key=api_key, **kwargs)

        self.base_url = kwargs.get("base_url")
        self.organization = kwargs.get("organization")
        self.timeout = kwargs.get("timeout", 60)
        self.max_retries = kwargs.get("max_retries", 2)
        self._client = None

    @property
    def name(self) -> str:
        return "openai"

    def _resolve_model(self, model: str) -> str:
        """Resolve model alias to full model ID."""
        return MODEL_ALIASES.get(model, model)

    def list_models(self) -> list[ModelInfo]:
        return OPENAI_MODELS.copy()

    def _get_client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "openai package not installed. "
                    "Run: pip install openai"
                )

            if not self.api_key:
                raise AuthenticationError(
                    "API key not provided. Set OPENAI_API_KEY environment variable "
                    "or pass api_key to OpenAIProvider.",
                    provider=self.name,
                )

            kwargs = {
                "api_key": self.api_key,
                "timeout": self.timeout,
                "max_retries": self.max_retries,
            }

            if self.base_url:
                kwargs["base_url"] = self.base_url
            if self.organization:
                kwargs["organization"] = self.organization

            self._client = openai.AsyncOpenAI(**kwargs)
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

        # Convert messages to OpenAI format
        openai_messages = []

        # Add system prompt if provided
        if config.system_prompt:
            openai_messages.append({
                "role": "system",
                "content": config.system_prompt,
            })

        for msg in messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content,
            })

        try:
            import openai as openai_module

            kwargs = {
                "model": model_id,
                "messages": openai_messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
            }

            if config.stop_sequences:
                kwargs["stop"] = config.stop_sequences

            response = await client.chat.completions.create(**kwargs)

            choice = response.choices[0]
            return GenerationResult(
                content=choice.message.content or "",
                model=model_id,
                provider=self.name,
                usage={
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0,
                },
                finish_reason=choice.finish_reason or "stop",
                raw_response=response,
            )

        except openai_module.AuthenticationError as e:
            raise AuthenticationError(str(e), provider=self.name)
        except openai_module.RateLimitError as e:
            raise RateLimitError(str(e), provider=self.name)
        except openai_module.APIError as e:
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
            import openai as openai_module

            messages = [{"role": "user", "content": prompt}]
            if config.system_prompt:
                messages.insert(0, {"role": "system", "content": config.system_prompt})

            kwargs = {
                "model": model_id,
                "messages": messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "stream": True,
            }

            stream = await client.chat.completions.create(**kwargs)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except openai_module.APIError as e:
            raise GenerationError(str(e), provider=self.name, model=model_id)
