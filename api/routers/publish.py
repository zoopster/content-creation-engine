"""
WordPress Publish API router.

Endpoints:
    GET  /api/publish/wordpress/verify      Test credentials & connection
    GET  /api/publish/wordpress/categories  List available categories
    GET  /api/publish/wordpress/tags        List available tags
    POST /api/publish/wordpress             Publish content to WordPress
"""

import os
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from skills.wordpress_publish import WordPressPublishSkill

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class WordPressCredentials(BaseModel):
    """WordPress connection credentials (optional — falls back to env vars)."""
    wp_url: Optional[str] = Field(default=None, description="WordPress site URL")
    username: Optional[str] = Field(default=None, description="WordPress username")
    app_password: Optional[str] = Field(
        default=None,
        description="Application password (spaces stripped automatically)"
    )


class WordPressPublishRequest(BaseModel):
    """Request body for publishing content to WordPress."""

    # Content
    title: str = Field(..., min_length=1, max_length=500, description="Post title")
    content: str = Field(..., min_length=1, description="Post body (HTML or Markdown)")
    content_format: str = Field(
        default="html",
        pattern="^(html|markdown)$",
        description="Content format: 'html' or 'markdown'"
    )
    excerpt: Optional[str] = Field(default=None, description="Short excerpt / summary")

    # WordPress settings
    status: str = Field(
        default="draft",
        pattern="^(draft|publish|pending|private)$",
        description="Post status"
    )
    category_names: List[str] = Field(
        default_factory=list,
        description="Category names (created automatically if they don't exist)"
    )
    tag_names: List[str] = Field(
        default_factory=list,
        description="Tag names (created automatically if they don't exist)"
    )
    slug: Optional[str] = Field(default=None, description="URL slug (auto-generated if omitted)")
    featured_media: Optional[int] = Field(
        default=None,
        description="Attachment ID of the featured image"
    )

    # Optional credential override (falls back to env vars if not provided)
    credentials: Optional[WordPressCredentials] = Field(
        default=None,
        description="WordPress credentials. Omit to use server-side env vars."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "AI in Healthcare: A 2026 Overview",
                "content": "<h2>Introduction</h2><p>AI is transforming healthcare...</p>",
                "content_format": "html",
                "status": "draft",
                "category_names": ["Technology", "Healthcare"],
                "tag_names": ["AI", "healthcare", "2026"],
            }
        }
    }


class WordPressVerifyRequest(BaseModel):
    """Optional credential override for connection verification."""
    credentials: Optional[WordPressCredentials] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_skill(credentials: Optional[WordPressCredentials]) -> WordPressPublishSkill:
    """
    Build a WordPressPublishSkill from request credentials or env vars.

    Priority: request credentials → environment variables.

    Raises:
        HTTPException 422 if required credentials are missing.
    """
    wp_url = (credentials and credentials.wp_url) or os.environ.get("WORDPRESS_URL", "")
    username = (credentials and credentials.username) or os.environ.get("WORDPRESS_USERNAME", "")
    app_password = (
        (credentials and credentials.app_password)
        or os.environ.get("WORDPRESS_APP_PASSWORD", "")
    )

    missing = [k for k, v in [("wp_url", wp_url), ("username", username), ("app_password", app_password)] if not v]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Missing WordPress credentials: {', '.join(missing)}. "
                "Set WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD env vars "
                "or include 'credentials' in the request body."
            ),
        )

    return WordPressPublishSkill(
        wp_url=wp_url,
        username=username,
        app_password=app_password,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/verify")
async def verify_wordpress_connection(
    wp_url: Optional[str] = None,
    username: Optional[str] = None,
    app_password: Optional[str] = None,
):
    """
    Verify WordPress credentials and REST API connectivity.

    Query params override env vars for quick ad-hoc testing.
    """
    creds = WordPressCredentials(
        wp_url=wp_url, username=username, app_password=app_password
    ) if any([wp_url, username, app_password]) else None

    skill = _build_skill(creds)
    info = await skill.verify_connection()

    if not info.connected:
        raise HTTPException(status_code=502, detail=info.error)

    return {
        "connected": True,
        "site_url": info.site_url,
        "site_name": info.site_name,
        "user_id": info.user_id,
        "username": info.username,
    }


@router.get("/categories")
async def list_categories(
    wp_url: Optional[str] = None,
    username: Optional[str] = None,
    app_password: Optional[str] = None,
):
    """List all categories on the WordPress site."""
    creds = WordPressCredentials(
        wp_url=wp_url, username=username, app_password=app_password
    ) if any([wp_url, username, app_password]) else None

    skill = _build_skill(creds)
    categories = await skill.get_categories()
    return {
        "count": len(categories),
        "categories": [
            {"id": c["id"], "name": c["name"], "slug": c["slug"]}
            for c in categories
        ],
    }


@router.get("/tags")
async def list_tags(
    wp_url: Optional[str] = None,
    username: Optional[str] = None,
    app_password: Optional[str] = None,
):
    """List all tags on the WordPress site."""
    creds = WordPressCredentials(
        wp_url=wp_url, username=username, app_password=app_password
    ) if any([wp_url, username, app_password]) else None

    skill = _build_skill(creds)
    tags = await skill.get_tags()
    return {
        "count": len(tags),
        "tags": [
            {"id": t["id"], "name": t["name"], "slug": t["slug"]}
            for t in tags
        ],
    }


@router.post("")
async def publish_to_wordpress(request: WordPressPublishRequest):
    """
    Publish content to WordPress.

    - Converts Markdown to HTML if `content_format` is `'markdown'`
    - Resolves category/tag names to IDs (creates them if missing)
    - Returns post ID, URL, and edit link on success
    """
    skill = _build_skill(request.credentials)

    # Convert markdown if needed
    content = request.content
    if request.content_format == "markdown":
        content = WordPressPublishSkill.markdown_to_html(content)
        logger.debug("Converted markdown content to HTML")

    # Resolve category and tag names to IDs
    category_ids = await skill.resolve_category_names(request.category_names)
    tag_ids = await skill.resolve_tag_names(request.tag_names)

    # Publish
    result = await skill.publish(
        title=request.title,
        content=content,
        status=request.status,
        excerpt=request.excerpt,
        category_ids=category_ids,
        tag_ids=tag_ids,
        slug=request.slug,
        featured_media=request.featured_media,
    )

    if not result.success:
        raise HTTPException(status_code=502, detail=result.error)

    return {
        "success": True,
        "post_id": result.post_id,
        "post_url": result.post_url,
        "edit_url": result.edit_url,
        "status": result.status,
        "categories_resolved": category_ids,
        "tags_resolved": tag_ids,
    }
