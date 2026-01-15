"""Templates API router."""

from fastapi import APIRouter, HTTPException

from api.schemas.templates import (
    BrandTemplatePreview,
    BrandTemplateListResponse,
    ColorPalette,
    Typography,
)
from templates.brand.brand_config import BRAND_TEMPLATES

router = APIRouter()

# Template descriptions
TEMPLATE_DESCRIPTIONS = {
    "professional": "Clean, corporate look with blue-gray tones. Ideal for business documents and formal communications.",
    "modern": "Bold and contemporary with coral accents. Great for startups, tech companies, and modern brands.",
    "tech": "Navy and teal palette with tech-forward feel. Perfect for technical content and software documentation.",
    "creative": "Vibrant purple and pink scheme. Excellent for creative agencies, design portfolios, and artistic content.",
    "minimal": "Black and white simplicity. Best for elegant, understated content that lets the message shine.",
}


@router.get("", response_model=BrandTemplateListResponse)
async def list_templates():
    """List all available brand templates with preview info."""
    templates = []

    for name, template in BRAND_TEMPLATES.items():
        templates.append(
            BrandTemplatePreview(
                name=name,
                display_name=template.name,
                description=TEMPLATE_DESCRIPTIONS.get(name, ""),
                colors=ColorPalette(
                    primary=template.colors.primary,
                    secondary=template.colors.secondary,
                    accent=template.colors.accent,
                    text=template.colors.text,
                    background=template.colors.background,
                ),
                typography=Typography(
                    heading_font=template.typography.heading_font,
                    body_font=template.typography.body_font,
                    h1_size=template.typography.h1_size,
                    body_size=template.typography.body_size,
                ),
                company_name=template.company_name,
            )
        )

    return BrandTemplateListResponse(templates=templates)


@router.get("/{name}", response_model=BrandTemplatePreview)
async def get_template(name: str):
    """Get a specific brand template by name."""
    if name not in BRAND_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{name}' not found. Available: {', '.join(BRAND_TEMPLATES.keys())}",
        )

    template = BRAND_TEMPLATES[name]

    return BrandTemplatePreview(
        name=name,
        display_name=template.name,
        description=TEMPLATE_DESCRIPTIONS.get(name, ""),
        colors=ColorPalette(
            primary=template.colors.primary,
            secondary=template.colors.secondary,
            accent=template.colors.accent,
            text=template.colors.text,
            background=template.colors.background,
        ),
        typography=Typography(
            heading_font=template.typography.heading_font,
            body_font=template.typography.body_font,
            h1_size=template.typography.h1_size,
            body_size=template.typography.body_size,
        ),
        company_name=template.company_name,
    )
