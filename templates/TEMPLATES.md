# Brand Template System

The Content Creation Engine includes a comprehensive brand template system that ensures consistent visual identity across all produced content.

## Overview

Templates define:
- **Colors**: Primary, secondary, accent, text, and background colors
- **Typography**: Fonts, sizes, and line heights
- **Spacing**: Margins, padding, and layout
- **Branding**: Company name, tagline, logo, website

## Predefined Templates

### Professional Template
**Best for**: Corporate communications, business documents
- Primary Color: #2C3E50 (Dark blue-gray)
- Secondary Color: #34495E (Medium blue-gray)
- Accent Color: #3498DB (Bright blue)
- Fonts: Calibri
- Style: Clean, professional, trustworthy

### Modern Template
**Best for**: Tech startups, contemporary businesses
- Primary Color: #1A1A1A (Almost black)
- Secondary Color: #4A4A4A (Dark gray)
- Accent Color: #FF6B6B (Coral red)
- Fonts: Arial
- Style: Sleek, minimalist, bold accents

### Tech Template
**Best for**: Technology companies, developer content
- Primary Color: #0A192F (Navy)
- Secondary Color: #172A45 (Dark blue)
- Accent Color: #64FFDA (Teal)
- Fonts: Arial with Consolas monospace
- Style: Modern tech, high contrast

### Creative Template
**Best for**: Design agencies, creative industries
- Primary Color: #6C5CE7 (Purple)
- Secondary Color: #A29BFE (Light purple)
- Accent Color: #FD79A8 (Pink)
- Fonts: Georgia
- Style: Artistic, colorful, expressive

### Minimal Template
**Best for**: Minimalist brands, simple aesthetics
- Primary Color: #000000 (Black)
- Secondary Color: #333333 (Dark gray)
- Accent Color: #000000 (Black)
- Fonts: Helvetica
- Style: Ultra-clean, maximum white space

## Using Templates

### In Python Code

```python
from templates.brand.brand_config import get_brand_template

# Get a predefined template
template = get_brand_template("professional")

# Access template properties
print(template.colors.primary)  # #2C3E50
print(template.typography.heading_font)  # Calibri
print(template.company_name)  # Professional Corp
```

### In Production Agent

```python
from agents.production.production_v2 import ProductionAgentV2

# Initialize with a template
agent = ProductionAgentV2(config={
    "brand_template": "modern",
    "output_dir": "output"
})

# Or override at generation time
output = agent.process({
    "draft_content": draft,
    "output_format": "html",
    "template_override": "tech"
})
```

## Creating Custom Templates

### Method 1: Use the Helper Function

```python
from templates.brand.brand_config import create_custom_template

template = create_custom_template(
    name="My Brand",
    primary_color="#1E40AF",
    secondary_color="#3B82F6",
    accent_color="#F59E0B",
    heading_font="Montserrat",
    body_font="Open Sans",
    company_name="My Company Inc."
)
```

### Method 2: Define Fully Custom Template

```python
from templates.brand.brand_config import (
    BrandTemplate, BrandColors, BrandTypography,
    BrandSpacing, ColorScheme
)

custom_template = BrandTemplate(
    name="Custom Brand",
    colors=BrandColors(
        primary="#1E40AF",
        secondary="#3B82F6",
        accent="#F59E0B",
        text="#1F2937",
        text_light="#6B7280",
        background="#FFFFFF",
        background_alt="#F3F4F6"
    ),
    typography=BrandTypography(
        heading_font="Montserrat",
        body_font="Open Sans",
        h1_size=28,
        h2_size=22,
        h3_size=18,
        body_size=12
    ),
    spacing=BrandSpacing(
        page_margin_top=1.5,
        page_margin_bottom=1.5,
        paragraph_spacing=14
    ),
    company_name="My Company Inc.",
    company_tagline="Innovation Through Excellence",
    website="https://mycompany.com",
    color_scheme=ColorScheme.MODERN
)
```

## Template Components

### Colors

```python
colors = BrandColors(
    primary="#2C3E50",      # Main brand color (headers, accents)
    secondary="#34495E",    # Secondary brand color (subheaders)
    accent="#3498DB",       # Highlight color (links, CTAs)
    text="#333333",         # Body text color
    text_light="#666666",   # Light text (captions, footnotes)
    background="#FFFFFF",   # Page background
    background_alt="#F5F5F5" # Alternate background (sections)
)
```

### Typography

```python
typography = BrandTypography(
    heading_font="Calibri",
    body_font="Calibri",
    mono_font="Courier New",
    h1_size=24,             # points
    h2_size=20,
    h3_size=16,
    body_size=11,
    small_size=9,
    heading_line_height=1.2,
    body_line_height=1.5
)
```

### Spacing

```python
spacing = BrandSpacing(
    page_margin_top=1.0,      # inches
    page_margin_bottom=1.0,
    page_margin_left=1.0,
    page_margin_right=1.0,
    paragraph_spacing=12.0,   # points
    section_spacing=24.0,
    slide_padding=0.5         # for presentations
)
```

## Output Formats

### Markdown
- Adds brand header and footer
- Plain text with formatting
- Best for version control
- Universal compatibility

### HTML
- Fully styled with brand CSS
- Responsive design
- Print-optimized styles
- Viewable in any browser

### DOCX (requires python-docx)
- Microsoft Word format
- Editable documents
- Professional output
- Cross-platform

### PDF (requires reportlab)
- Fixed layout
- Print-ready
- Universal viewing
- Archival quality

### PPTX (requires python-pptx)
- PowerPoint presentations
- Slide-based content
- Speaker notes support
- Professional decks

## Workflow Integration

The template system integrates seamlessly with the workflow executor:

```python
from agents.workflow_executor import WorkflowExecutor

executor = WorkflowExecutor(config={
    "production": {
        "brand_template": "professional",
        "output_dir": "output"
    }
})

# Templates are automatically applied to production output
result = executor.execute(request)
```

## Best Practices

### Color Selection
- **Primary**: Most prominent brand color, use sparingly
- **Secondary**: Supporting color, use for hierarchy
- **Accent**: Draw attention, use for CTAs and links
- **Text**: High contrast with background (minimum 4.5:1 ratio)
- **Backgrounds**: Light for readability, consider alternates for sections

### Typography
- **Sans-serif** (Arial, Calibri, Helvetica): Modern, clean, professional
- **Serif** (Georgia, Times): Traditional, trustworthy, readable
- **Monospace** (Courier, Consolas): Technical, code, data
- Stick to 1-2 font families per template
- Maintain clear size hierarchy: H1 > H2 > H3 > Body

### Spacing
- Consistent margins create professional appearance
- More spacing = easier reading
- Group related content with consistent gaps
- Use section breaks to separate topics

### Brand Elements
- Always include company name
- Tagline adds context and personality
- Website provides credibility and contact
- Logo (when available) enhances recognition

## Template Files Structure

```
templates/
├── brand/
│   ├── brand_config.py          # Template definitions
│   └── __init__.py
├── documents/
│   └── (future: DOCX templates)
├── presentations/
│   └── (future: PPTX templates)
└── TEMPLATES.md                 # This documentation
```

## Examples

See `examples/phase3_templates.py` for complete examples of:
- Using all predefined templates
- Creating custom templates
- Generating output in multiple formats
- Comparing template styles

## Technical Reference

### BrandTemplate Class

```python
@dataclass
class BrandTemplate:
    name: str
    colors: BrandColors
    typography: BrandTypography
    spacing: BrandSpacing
    logo: Optional[BrandLogo]
    company_name: str
    company_tagline: str
    website: str
    color_scheme: ColorScheme
    use_header_footer: bool
    include_page_numbers: bool
```

### Methods

- `to_dict()`: Serialize template to dictionary
- `get_brand_template(name)`: Retrieve predefined template
- `create_custom_template(...)`: Quick custom template creation

## Future Enhancements

- Logo integration with positioning
- Custom header/footer templates
- Multi-page document layouts
- Presentation master slides
- Theme inheritance
- Template versioning
- Template marketplace/sharing
