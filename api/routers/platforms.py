"""Platforms API router."""

from fastapi import APIRouter

from api.schemas.platforms import PlatformSpec, PlatformListResponse

router = APIRouter()

# Platform specifications
PLATFORM_SPECS = [
    PlatformSpec(
        id="linkedin",
        name="linkedin",
        display_name="LinkedIn",
        max_length=3000,
        optimal_length=(150, 300),
        hashtag_count=(3, 5),
        supports_threads=False,
        supports_carousel=True,
        emoji_recommendation="moderate",
        icon="linkedin",
    ),
    PlatformSpec(
        id="twitter",
        name="twitter",
        display_name="X (Twitter)",
        max_length=280,
        optimal_length=(150, 250),
        hashtag_count=(1, 2),
        supports_threads=True,
        supports_carousel=False,
        emoji_recommendation="moderate",
        icon="twitter",
    ),
    PlatformSpec(
        id="instagram",
        name="instagram",
        display_name="Instagram",
        max_length=2200,
        optimal_length=(100, 500),
        hashtag_count=(5, 15),
        supports_threads=False,
        supports_carousel=True,
        emoji_recommendation="high",
        icon="instagram",
    ),
    PlatformSpec(
        id="facebook",
        name="facebook",
        display_name="Facebook",
        max_length=63206,
        optimal_length=(40, 250),
        hashtag_count=(1, 3),
        supports_threads=False,
        supports_carousel=True,
        emoji_recommendation="moderate",
        icon="facebook",
    ),
]


@router.get("", response_model=PlatformListResponse)
async def list_platforms():
    """List all social platforms with specifications."""
    return PlatformListResponse(platforms=PLATFORM_SPECS)
