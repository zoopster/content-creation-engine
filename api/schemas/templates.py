"""Brand template API schemas."""

from pydantic import BaseModel
from typing import List, Optional


class ColorPalette(BaseModel):
    """Brand color palette for preview."""
    primary: str
    secondary: str
    accent: str
    text: str
    background: str


class Typography(BaseModel):
    """Typography settings."""
    heading_font: str
    body_font: str
    h1_size: int
    body_size: int


class BrandTemplatePreview(BaseModel):
    """Brand template with preview information."""
    name: str
    display_name: str
    description: str
    colors: ColorPalette
    typography: Typography
    company_name: str
    preview_image_url: Optional[str] = None


class BrandTemplateListResponse(BaseModel):
    """List of available brand templates."""
    templates: List[BrandTemplatePreview]
