"""
Content Repurpose API router.

Endpoints:
    POST /api/repurpose          Repurpose existing content to a new format
    POST /api/repurpose/email    Generate a new email from a topic or brief
    GET  /api/repurpose/formats  List supported source→target transformations
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agents.base.models import ContentType, ToneType, DraftContent
from skills.content_repurpose.content_repurpose import ContentRepurposeSkill
from skills.email_generation.email_generation import EmailGenerationSkill

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RepurposeRequest(BaseModel):
    """Request body for content repurposing."""

    # Source content
    content: str = Field(..., min_length=1, description="Source content text")
    source_type: str = Field(
        default="article",
        description="Source content type: article, blog_post, whitepaper"
    )

    # Target
    target_format: str = Field(
        ...,
        description="Target format: social_post, presentation, email"
    )

    # Options
    platform: Optional[str] = Field(
        default="linkedin",
        description="Target platform for social posts: linkedin, twitter, instagram, facebook"
    )
    additional_context: Optional[str] = Field(
        default=None,
        description="Additional instructions for the transformation"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": "# AI in Healthcare\n\nArtificial intelligence is transforming...",
                "source_type": "article",
                "target_format": "social_post",
                "platform": "linkedin",
                "additional_context": "Focus on the ROI angle for healthcare executives",
            }
        }
    }


class RepurposeResponse(BaseModel):
    """Response from content repurposing."""
    success: bool
    content: str
    source_type: str
    target_format: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmailGenerateRequest(BaseModel):
    """Request body for email generation."""

    topic: str = Field(..., min_length=1, description="Topic or subject of the email")
    email_type: str = Field(
        default="newsletter",
        description="Email type: newsletter, outreach, nurture, announcement, summary"
    )
    recipient_context: Optional[str] = Field(
        default=None,
        description="Description of the target recipient (e.g. 'marketing directors at SaaS companies')"
    )
    key_points: Optional[List[str]] = Field(
        default=None,
        description="Specific points to include in the email"
    )
    sender_name: Optional[str] = Field(default=None, description="Sender name for sign-off")
    company_name: Optional[str] = Field(default=None, description="Company name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "topic": "The impact of AI on content marketing in 2026",
                "email_type": "outreach",
                "recipient_context": "marketing directors at B2B SaaS companies",
                "key_points": [
                    "AI reduces content production time by 60%",
                    "Quality remains high with human oversight",
                ],
                "sender_name": "Alex",
                "company_name": "ContentAI",
            }
        }
    }


class EmailGenerateResponse(BaseModel):
    """Response from email generation."""
    success: bool
    subject: str
    preview_text: str
    body: str
    email_type: str
    word_count: int
    full_text: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/formats")
async def list_repurpose_formats():
    """List all supported source → target content transformations."""
    return {
        "transformations": [
            {"source": "article", "target": "social_post", "platforms": ["linkedin", "twitter", "instagram", "facebook"]},
            {"source": "article", "target": "presentation", "platforms": None},
            {"source": "article", "target": "email", "platforms": None},
            {"source": "blog_post", "target": "social_post", "platforms": ["linkedin", "twitter", "instagram", "facebook"]},
            {"source": "blog_post", "target": "presentation", "platforms": None},
            {"source": "blog_post", "target": "email", "platforms": None},
            {"source": "whitepaper", "target": "social_post", "platforms": ["linkedin", "twitter"]},
            {"source": "whitepaper", "target": "presentation", "platforms": None},
            {"source": "whitepaper", "target": "email", "platforms": None},
        ],
        "email_types": ["newsletter", "outreach", "nurture", "announcement", "summary"],
    }


@router.post("", response_model=RepurposeResponse)
async def repurpose_content(request: RepurposeRequest):
    """
    Repurpose existing content from one format to another.

    Uses LLM to intelligently transform content while preserving the key message.
    Falls back to rule-based transformation if LLM is unavailable.
    """
    # Map string types to ContentType enum
    source_type_map = {
        "article": ContentType.ARTICLE,
        "blog_post": ContentType.BLOG_POST,
        "whitepaper": ContentType.WHITEPAPER,
    }
    target_type_map = {
        "social_post": ContentType.SOCIAL_POST,
        "presentation": ContentType.PRESENTATION,
        "email": ContentType.EMAIL,
    }

    source_type = source_type_map.get(request.source_type)
    if not source_type:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported source_type '{request.source_type}'. Must be one of: {list(source_type_map.keys())}"
        )

    target_format = target_type_map.get(request.target_format)
    if not target_format:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported target_format '{request.target_format}'. Must be one of: {list(target_type_map.keys())}"
        )

    # Build a DraftContent from the raw content string
    draft = DraftContent(
        content=request.content,
        content_type=source_type,
        word_count=len(request.content.split()),
        metadata={}
    )

    try:
        skill = ContentRepurposeSkill()
        result = await skill.execute_async(
            source_content=draft,
            target_format=target_format,
            platform=request.platform or "linkedin",
            additional_context=request.additional_context or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Repurpose failed: {e}")
        raise HTTPException(status_code=500, detail=f"Repurpose failed: {str(e)}")

    return RepurposeResponse(
        success=result["success"],
        content=result["content"],
        source_type=request.source_type,
        target_format=request.target_format,
        metadata=result.get("metadata", {}),
    )


@router.post("/email", response_model=EmailGenerateResponse)
async def generate_email(request: EmailGenerateRequest):
    """
    Generate a new email from a topic using LLM.

    Supports newsletter, outreach, nurture, announcement, and summary email types.
    """
    valid_types = ["newsletter", "outreach", "nurture", "announcement", "summary"]
    if request.email_type not in valid_types:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid email_type '{request.email_type}'. Must be one of: {valid_types}"
        )

    try:
        skill = EmailGenerationSkill()
        email = await skill.execute_async(
            topic=request.topic,
            email_type=request.email_type,
            recipient_context=request.recipient_context,
            key_points=request.key_points or [],
            sender_name=request.sender_name or "",
            company_name=request.company_name or "",
        )
    except Exception as e:
        logger.error(f"Email generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Email generation failed: {str(e)}")

    return EmailGenerateResponse(
        success=True,
        subject=email.subject,
        preview_text=email.preview_text,
        body=email.body,
        email_type=email.email_type,
        word_count=email.word_count,
        full_text=email.to_full_text(),
    )
