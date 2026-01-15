"""
Model configuration management.

Provides utilities for loading and managing model configurations
from files, environment variables, and runtime settings.
"""

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from .base import GenerationConfig
from .registry import AgentModelConfig, ModelRegistry, ProviderConfig


# Default configuration for the Content Creation Engine
DEFAULT_MODEL_CONFIG = {
    "providers": {
        "anthropic": {
            "enabled": True,
            "default_model": "claude-sonnet-4-20250514",
            "timeout": 60,
            "max_retries": 2,
        },
        "openai": {
            "enabled": True,
            "default_model": "gpt-4o",
            "timeout": 60,
            "max_retries": 2,
        },
    },
    "agents": {
        "research": {
            "provider": "anthropic",
            "model": "claude-3-5-haiku-20241022",
            "config": {
                "max_tokens": 4096,
                "temperature": 0.3,
                "system_prompt": (
                    "You are a research assistant. Gather accurate, well-sourced "
                    "information. Cite sources and distinguish facts from opinions."
                ),
            },
        },
        "creation": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "config": {
                "max_tokens": 8192,
                "temperature": 0.7,
                "system_prompt": (
                    "You are a professional content writer. Create engaging, "
                    "well-structured content that matches the specified tone and "
                    "audience. Follow brand voice guidelines precisely."
                ),
            },
        },
        "social": {
            "provider": "anthropic",
            "model": "claude-3-5-haiku-20241022",
            "config": {
                "max_tokens": 1024,
                "temperature": 0.8,
                "system_prompt": (
                    "You are a social media content specialist. Create engaging, "
                    "platform-appropriate content that drives engagement. "
                    "Use appropriate hashtags and calls-to-action."
                ),
            },
        },
        "editing": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "config": {
                "max_tokens": 4096,
                "temperature": 0.3,
                "system_prompt": (
                    "You are a professional editor. Review content for clarity, "
                    "grammar, style consistency, and brand voice alignment. "
                    "Provide specific, actionable suggestions."
                ),
            },
        },
    },
    "defaults": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "max_tokens": 4096,
    },
}


class ModelConfigManager:
    """
    Manages model configurations for the Content Creation Engine.

    Loads configuration from:
    1. Default settings
    2. Configuration file (if exists)
    3. Environment variables (override)

    Usage:
        manager = ModelConfigManager()
        manager.load_config("config/models.json")  # Optional

        # Apply to registry
        registry = manager.configure_registry()

        # Get agent-specific config
        creation_config = manager.get_agent_config("creation")
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize with optional configuration.

        Args:
            config: Configuration dictionary. Defaults to DEFAULT_MODEL_CONFIG.
        """
        self._config = config or DEFAULT_MODEL_CONFIG.copy()

    def load_config(self, path: str | Path) -> None:
        """
        Load configuration from a JSON file.

        Args:
            path: Path to configuration file.
        """
        path = Path(path)
        if path.exists():
            with open(path) as f:
                file_config = json.load(f)
            self._merge_config(file_config)

    def _merge_config(self, override: dict) -> None:
        """Deep merge override configuration into current config."""
        self._config = self._deep_merge(self._config, override)

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Recursively merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get_provider_config(self, provider: str) -> ProviderConfig:
        """Get configuration for a specific provider."""
        provider_conf = self._config.get("providers", {}).get(provider, {})

        # Check for API key in environment
        env_key_name = f"{provider.upper()}_API_KEY"
        api_key = os.environ.get(env_key_name) or provider_conf.get("api_key")

        return ProviderConfig(
            enabled=provider_conf.get("enabled", True),
            api_key=api_key,
            base_url=provider_conf.get("base_url"),
            timeout=provider_conf.get("timeout", 60),
            max_retries=provider_conf.get("max_retries", 2),
            extra=provider_conf.get("extra", {}),
        )

    def get_agent_config(self, agent_name: str) -> AgentModelConfig:
        """Get model configuration for a specific agent."""
        agent_conf = self._config.get("agents", {}).get(agent_name)

        if not agent_conf:
            # Fall back to defaults
            defaults = self._config.get("defaults", {})
            return AgentModelConfig(
                provider=defaults.get("provider", "anthropic"),
                model=defaults.get("model", "claude-sonnet-4-20250514"),
                config=GenerationConfig(
                    max_tokens=defaults.get("max_tokens", 4096),
                    temperature=defaults.get("temperature", 0.7),
                ),
            )

        gen_config = None
        if "config" in agent_conf:
            gen_config = GenerationConfig(**agent_conf["config"])

        return AgentModelConfig(
            provider=agent_conf["provider"],
            model=agent_conf["model"],
            config=gen_config,
        )

    def configure_registry(self, registry: Optional[ModelRegistry] = None) -> ModelRegistry:
        """
        Configure a registry with settings from this manager.

        Args:
            registry: Existing registry to configure. Creates new if None.

        Returns:
            Configured ModelRegistry instance.
        """
        from .anthropic_provider import AnthropicProvider
        from .openai_provider import OpenAIProvider

        if registry is None:
            registry = ModelRegistry()

        # Register providers
        providers_config = self._config.get("providers", {})

        if providers_config.get("anthropic", {}).get("enabled", True):
            anthropic_conf = self.get_provider_config("anthropic")
            if anthropic_conf.api_key:
                registry.register_provider(
                    "anthropic",
                    AnthropicProvider(
                        api_key=anthropic_conf.api_key,
                        base_url=anthropic_conf.base_url,
                        timeout=anthropic_conf.timeout,
                        max_retries=anthropic_conf.max_retries,
                    ),
                    anthropic_conf,
                )

        if providers_config.get("openai", {}).get("enabled", True):
            openai_conf = self.get_provider_config("openai")
            if openai_conf.api_key:
                registry.register_provider(
                    "openai",
                    OpenAIProvider(
                        api_key=openai_conf.api_key,
                        base_url=openai_conf.base_url,
                        timeout=openai_conf.timeout,
                        max_retries=openai_conf.max_retries,
                    ),
                    openai_conf,
                )

        # Set agent configurations
        for agent_name in self._config.get("agents", {}).keys():
            registry.set_agent_config(agent_name, self.get_agent_config(agent_name))

        return registry

    def save_config(self, path: str | Path) -> None:
        """Save current configuration to a JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self._config, f, indent=2)

    def to_dict(self) -> dict[str, Any]:
        """Return configuration as a dictionary."""
        return self._config.copy()


def load_config_from_env() -> ModelConfigManager:
    """
    Create a config manager loading settings from environment.

    Environment variables:
    - MODEL_CONFIG_PATH: Path to config file
    - ANTHROPIC_API_KEY: Anthropic API key
    - OPENAI_API_KEY: OpenAI API key
    - DEFAULT_PROVIDER: Default provider name
    - DEFAULT_MODEL: Default model ID
    """
    manager = ModelConfigManager()

    # Load config file if specified
    config_path = os.environ.get("MODEL_CONFIG_PATH")
    if config_path:
        manager.load_config(config_path)

    # Override defaults from environment
    default_provider = os.environ.get("DEFAULT_PROVIDER")
    default_model = os.environ.get("DEFAULT_MODEL")

    if default_provider or default_model:
        overrides = {"defaults": {}}
        if default_provider:
            overrides["defaults"]["provider"] = default_provider
        if default_model:
            overrides["defaults"]["model"] = default_model
        manager._merge_config(overrides)

    return manager
