"""API configuration settings."""

from typing import List
import os


class Settings:
    """Application settings."""

    # API Settings
    API_TITLE: str = "Content Creation Engine API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Multi-agent content creation system API"

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Output Settings
    OUTPUT_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "output",
        "api"
    )

    # Job Settings
    JOB_EXPIRY_HOURS: int = 24


settings = Settings()
