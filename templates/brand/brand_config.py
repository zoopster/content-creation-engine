"""
Brand Configuration - Central brand identity and style definitions.

This module defines the brand's visual identity, voice, and style guidelines
that are applied consistently across all produced content.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ColorScheme(Enum):
    """Standard color scheme options."""
    PROFESSIONAL = "professional"
    MODERN = "modern"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    TECH = "tech"


@dataclass
class BrandColors:
    """Brand color palette."""
    primary: str  # Hex color code
    secondary: str
    accent: str
    text: str = "#333333"
    text_light: str = "#666666"
    background: str = "#FFFFFF"
    background_alt: str = "#F5F5F5"

    # Additional colors
    success: str = "#28A745"
    warning: str = "#FFC107"
    error: str = "#DC3545"
    info: str = "#17A2B8"


@dataclass
class BrandTypography:
    """Brand typography settings."""
    heading_font: str
    body_font: str
    mono_font: str = "Courier New"

    # Font sizes (in points)
    h1_size: int = 24
    h2_size: int = 20
    h3_size: int = 16
    body_size: int = 11
    small_size: int = 9

    # Line heights
    heading_line_height: float = 1.2
    body_line_height: float = 1.5


@dataclass
class BrandSpacing:
    """Brand spacing and layout settings."""
    page_margin_top: float = 1.0  # inches
    page_margin_bottom: float = 1.0
    page_margin_left: float = 1.0
    page_margin_right: float = 1.0

    paragraph_spacing: float = 12.0  # points
    section_spacing: float = 24.0

    # Presentation spacing
    slide_padding: float = 0.5  # inches


@dataclass
class DocumentLayout:
    """Document-specific layout settings for DOCX and PDF output."""
    # Page dimensions
    page_size: str = "letter"  # letter, a4, legal
    page_width: float = 8.5  # inches (letter size)
    page_height: float = 11.0

    # Page margins
    margin_top: float = 1.0  # inches
    margin_bottom: float = 1.0
    margin_left: float = 1.0
    margin_right: float = 1.0

    # Header/footer spacing
    header_margin: float = 0.5  # inches
    footer_margin: float = 0.5

    # Text layout
    first_line_indent: float = 0.0  # inches
    paragraph_spacing_before: float = 6.0  # points
    paragraph_spacing_after: float = 6.0


@dataclass
class PresentationLayout:
    """Presentation-specific layout settings for PPTX output."""
    # Slide dimensions (16:9 aspect ratio standard)
    slide_width: float = 10.0  # inches
    slide_height: float = 7.5

    # Content areas
    title_height: float = 1.5  # inches from top
    content_top: float = 2.0
    content_left: float = 0.75
    content_right: float = 9.25
    content_bottom: float = 6.75

    # Title slide specifics
    title_slide_title_size: int = 44  # points
    title_slide_subtitle_size: int = 24

    # Content slide specifics
    slide_title_size: int = 32  # points
    bullet_size: int = 18
    bullet_indent: float = 0.5  # inches


@dataclass
class BrandLogo:
    """Brand logo information."""
    path: Optional[str] = None
    width: float = 2.0  # inches
    height: float = 0.5  # inches
    position: str = "header"  # header, footer, corner


@dataclass
class BrandTemplate:
    """
    Complete brand template configuration.

    This defines the visual identity and style guidelines
    for all produced content.
    """
    name: str
    colors: BrandColors
    typography: BrandTypography
    spacing: BrandSpacing = field(default_factory=BrandSpacing)
    document_layout: DocumentLayout = field(default_factory=DocumentLayout)
    presentation_layout: PresentationLayout = field(default_factory=PresentationLayout)
    logo: Optional[BrandLogo] = None

    # Document metadata
    company_name: str = "Company Name"
    company_tagline: str = ""
    website: str = ""

    # Style preferences
    color_scheme: ColorScheme = ColorScheme.PROFESSIONAL
    use_header_footer: bool = True
    include_page_numbers: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "colors": {
                "primary": self.colors.primary,
                "secondary": self.colors.secondary,
                "accent": self.colors.accent,
                "text": self.colors.text,
                "background": self.colors.background
            },
            "typography": {
                "heading_font": self.typography.heading_font,
                "body_font": self.typography.body_font,
                "h1_size": self.typography.h1_size,
                "body_size": self.typography.body_size
            },
            "company": {
                "name": self.company_name,
                "tagline": self.company_tagline,
                "website": self.website
            }
        }


# Predefined brand templates

PROFESSIONAL_TEMPLATE = BrandTemplate(
    name="Professional",
    colors=BrandColors(
        primary="#2C3E50",      # Dark blue-gray
        secondary="#34495E",    # Medium blue-gray
        accent="#3498DB",       # Bright blue
        text="#2C3E50",
        text_light="#7F8C8D",
        background="#FFFFFF",
        background_alt="#ECF0F1"
    ),
    typography=BrandTypography(
        heading_font="Calibri",
        body_font="Calibri",
        h1_size=24,
        h2_size=18,
        h3_size=14,
        body_size=11
    ),
    company_name="Professional Corp",
    color_scheme=ColorScheme.PROFESSIONAL
)

MODERN_TEMPLATE = BrandTemplate(
    name="Modern",
    colors=BrandColors(
        primary="#1A1A1A",      # Almost black
        secondary="#4A4A4A",    # Dark gray
        accent="#FF6B6B",       # Coral red
        text="#1A1A1A",
        text_light="#6C6C6C",
        background="#FFFFFF",
        background_alt="#F8F8F8"
    ),
    typography=BrandTypography(
        heading_font="Arial",
        body_font="Arial",
        h1_size=26,
        h2_size=20,
        h3_size=16,
        body_size=11
    ),
    company_name="Modern Tech",
    color_scheme=ColorScheme.MODERN
)

TECH_TEMPLATE = BrandTemplate(
    name="Tech",
    colors=BrandColors(
        primary="#0A192F",      # Navy
        secondary="#172A45",    # Dark blue
        accent="#64FFDA",       # Teal
        text="#0A192F",
        text_light="#8892B0",
        background="#FFFFFF",
        background_alt="#F7FAFC"
    ),
    typography=BrandTypography(
        heading_font="Arial",
        body_font="Arial",
        mono_font="Consolas",
        h1_size=24,
        h2_size=18,
        h3_size=14,
        body_size=11
    ),
    company_name="Tech Innovators",
    color_scheme=ColorScheme.TECH
)

CREATIVE_TEMPLATE = BrandTemplate(
    name="Creative",
    colors=BrandColors(
        primary="#6C5CE7",      # Purple
        secondary="#A29BFE",    # Light purple
        accent="#FD79A8",       # Pink
        text="#2D3436",
        text_light="#636E72",
        background="#FFFFFF",
        background_alt="#F8F9FA"
    ),
    typography=BrandTypography(
        heading_font="Georgia",
        body_font="Georgia",
        h1_size=26,
        h2_size=20,
        h3_size=16,
        body_size=11
    ),
    company_name="Creative Studio",
    color_scheme=ColorScheme.CREATIVE
)

MINIMAL_TEMPLATE = BrandTemplate(
    name="Minimal",
    colors=BrandColors(
        primary="#000000",      # Black
        secondary="#333333",    # Dark gray
        accent="#000000",       # Black (minimal accent)
        text="#000000",
        text_light="#666666",
        background="#FFFFFF",
        background_alt="#FAFAFA"
    ),
    typography=BrandTypography(
        heading_font="Helvetica",
        body_font="Helvetica",
        h1_size=24,
        h2_size=18,
        h3_size=14,
        body_size=11
    ),
    company_name="Minimal Co",
    color_scheme=ColorScheme.MINIMAL
)


# Template registry
BRAND_TEMPLATES = {
    "professional": PROFESSIONAL_TEMPLATE,
    "modern": MODERN_TEMPLATE,
    "tech": TECH_TEMPLATE,
    "creative": CREATIVE_TEMPLATE,
    "minimal": MINIMAL_TEMPLATE
}


def get_brand_template(name: str = "professional") -> BrandTemplate:
    """
    Get a brand template by name.

    Args:
        name: Template name (professional, modern, tech, creative, minimal)

    Returns:
        BrandTemplate instance
    """
    return BRAND_TEMPLATES.get(name.lower(), PROFESSIONAL_TEMPLATE)


def create_custom_template(
    name: str,
    primary_color: str,
    secondary_color: str,
    accent_color: str,
    heading_font: str = "Arial",
    body_font: str = "Arial",
    company_name: str = "Company Name"
) -> BrandTemplate:
    """
    Create a custom brand template.

    Args:
        name: Template name
        primary_color: Primary brand color (hex)
        secondary_color: Secondary brand color (hex)
        accent_color: Accent color (hex)
        heading_font: Font for headings
        body_font: Font for body text
        company_name: Company name

    Returns:
        Custom BrandTemplate
    """
    return BrandTemplate(
        name=name,
        colors=BrandColors(
            primary=primary_color,
            secondary=secondary_color,
            accent=accent_color
        ),
        typography=BrandTypography(
            heading_font=heading_font,
            body_font=body_font
        ),
        company_name=company_name
    )
