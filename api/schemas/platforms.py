"""Platform API schemas."""

from pydantic import BaseModel
from typing import List, Tuple


class PlatformSpec(BaseModel):
    """Platform-specific specifications."""
    id: str
    name: str
    display_name: str
    max_length: int
    optimal_length: Tuple[int, int]
    hashtag_count: Tuple[int, int]
    supports_threads: bool
    supports_carousel: bool
    emoji_recommendation: str
    icon: str


class PlatformListResponse(BaseModel):
    """List of social platforms."""
    platforms: List[PlatformSpec]
