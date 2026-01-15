"""Content type API schemas."""

from pydantic import BaseModel
from typing import List, Tuple

from .workflow import ToneTypeEnum, OutputFormatEnum


class ContentTypeMetadata(BaseModel):
    """Metadata for a content type."""
    id: str
    name: str
    display_name: str
    description: str
    default_word_count_range: Tuple[int, int]
    default_tone: ToneTypeEnum
    supports_social_settings: bool
    available_output_formats: List[OutputFormatEnum]
    icon: str


class ContentTypeListResponse(BaseModel):
    """List of content types with metadata."""
    content_types: List[ContentTypeMetadata]
