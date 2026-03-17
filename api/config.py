"""API configuration settings."""

import os
from typing import List


def _parse_cors_origins(raw: str) -> List[str]:
    """Parse a comma-separated CORS origins string into a list."""
    return [o.strip() for o in raw.split(",") if o.strip()]


class Settings:
    """Application settings — values sourced from environment variables with sensible defaults."""

    # API metadata
    API_TITLE: str = "Content Creation Engine API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Multi-agent content creation system API"

    # Server
    API_HOST: str = os.environ.get("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.environ.get("API_PORT", "8000"))
    API_DEBUG: bool = os.environ.get("API_DEBUG", "false").lower() == "true"

    # CORS — read from env or fall back to local dev defaults
    CORS_ORIGINS: List[str] = _parse_cors_origins(
        os.environ.get(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,"
            "http://127.0.0.1:5173,http://127.0.0.1:3000",
        )
    )

    # Output
    OUTPUT_DIR: str = os.environ.get(
        "OUTPUT_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "api"),
    )

    # Job settings
    JOB_EXPIRY_HOURS: int = int(os.environ.get("JOB_EXPIRY_HOURS", "24"))


settings = Settings()
