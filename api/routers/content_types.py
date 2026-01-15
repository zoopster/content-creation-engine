"""Content types API router."""

from fastapi import APIRouter

from api.schemas.content_types import ContentTypeMetadata, ContentTypeListResponse
from api.schemas.workflow import ToneTypeEnum, OutputFormatEnum

router = APIRouter()

# Content type metadata with defaults
CONTENT_TYPE_METADATA = [
    ContentTypeMetadata(
        id="article",
        name="article",
        display_name="Article",
        description="Long-form editorial content for publications and websites",
        default_word_count_range=(800, 1500),
        default_tone=ToneTypeEnum.PROFESSIONAL,
        supports_social_settings=False,
        available_output_formats=[
            OutputFormatEnum.HTML,
            OutputFormatEnum.MARKDOWN,
            OutputFormatEnum.DOCX,
            OutputFormatEnum.PDF,
        ],
        icon="article",
    ),
    ContentTypeMetadata(
        id="blog_post",
        name="blog_post",
        display_name="Blog Post",
        description="Informal web content for blogs and personal sites",
        default_word_count_range=(600, 1200),
        default_tone=ToneTypeEnum.CONVERSATIONAL,
        supports_social_settings=False,
        available_output_formats=[
            OutputFormatEnum.HTML,
            OutputFormatEnum.MARKDOWN,
        ],
        icon="edit_note",
    ),
    ContentTypeMetadata(
        id="social_post",
        name="social_post",
        display_name="Social Post",
        description="Platform-optimized social media content",
        default_word_count_range=(50, 300),
        default_tone=ToneTypeEnum.CONVERSATIONAL,
        supports_social_settings=True,
        available_output_formats=[
            OutputFormatEnum.HTML,
            OutputFormatEnum.MARKDOWN,
        ],
        icon="share",
    ),
    ContentTypeMetadata(
        id="presentation",
        name="presentation",
        display_name="Presentation",
        description="Slide deck content for meetings and conferences",
        default_word_count_range=(500, 1000),
        default_tone=ToneTypeEnum.PROFESSIONAL,
        supports_social_settings=False,
        available_output_formats=[
            OutputFormatEnum.PPTX,
            OutputFormatEnum.PDF,
        ],
        icon="slideshow",
    ),
    ContentTypeMetadata(
        id="email",
        name="email",
        display_name="Email",
        description="Professional email communication",
        default_word_count_range=(100, 400),
        default_tone=ToneTypeEnum.PROFESSIONAL,
        supports_social_settings=False,
        available_output_formats=[
            OutputFormatEnum.HTML,
            OutputFormatEnum.MARKDOWN,
        ],
        icon="email",
    ),
    ContentTypeMetadata(
        id="newsletter",
        name="newsletter",
        display_name="Newsletter",
        description="Email newsletter for subscribers",
        default_word_count_range=(400, 800),
        default_tone=ToneTypeEnum.CONVERSATIONAL,
        supports_social_settings=False,
        available_output_formats=[
            OutputFormatEnum.HTML,
            OutputFormatEnum.MARKDOWN,
        ],
        icon="newspaper",
    ),
    ContentTypeMetadata(
        id="video_script",
        name="video_script",
        display_name="Video Script",
        description="Script for video narration and presentations",
        default_word_count_range=(300, 1000),
        default_tone=ToneTypeEnum.CONVERSATIONAL,
        supports_social_settings=False,
        available_output_formats=[
            OutputFormatEnum.DOCX,
            OutputFormatEnum.MARKDOWN,
        ],
        icon="videocam",
    ),
    ContentTypeMetadata(
        id="whitepaper",
        name="whitepaper",
        display_name="Whitepaper",
        description="In-depth technical document or research report",
        default_word_count_range=(2000, 5000),
        default_tone=ToneTypeEnum.TECHNICAL,
        supports_social_settings=False,
        available_output_formats=[
            OutputFormatEnum.PDF,
            OutputFormatEnum.DOCX,
        ],
        icon="description",
    ),
    ContentTypeMetadata(
        id="case_study",
        name="case_study",
        display_name="Case Study",
        description="Customer success story or project analysis",
        default_word_count_range=(800, 1500),
        default_tone=ToneTypeEnum.PROFESSIONAL,
        supports_social_settings=False,
        available_output_formats=[
            OutputFormatEnum.PDF,
            OutputFormatEnum.DOCX,
            OutputFormatEnum.HTML,
        ],
        icon="cases",
    ),
]


@router.get("", response_model=ContentTypeListResponse)
async def list_content_types():
    """List all content types with metadata and defaults."""
    return ContentTypeListResponse(content_types=CONTENT_TYPE_METADATA)
