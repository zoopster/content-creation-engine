# Production Agent

## Overview

The Production Agent is responsible for transforming draft content into final formatted deliverables. It takes markdown content from the Creation Agent and produces professional documents in various formats.

## Responsibilities

- **Document Generation**: Create DOCX, PDF, HTML, and Markdown files
- **Presentation Creation**: Generate PPTX presentations with slides
- **Template Application**: Apply branded templates and styling
- **Format Validation**: Ensure outputs meet quality standards (Quality Gate 4)
- **Batch Processing**: Handle multiple documents efficiently
- **Content Repurposing**: Convert between formats

## Input

The Production Agent accepts a dictionary containing:

```python
{
    "draft_content": DraftContent,      # Required: content to format
    "output_format": str,               # Required: docx, pdf, pptx, html, markdown
    "template_name": str,               # Optional: template to apply
    "additional_options": dict          # Optional: format-specific options
}
```

### DraftContent Structure

From `agents/base/models.py`:

```python
@dataclass
class DraftContent:
    content: str                    # Markdown formatted content
    content_type: ContentType       # Type of content
    word_count: int                 # Word count
    metadata: Dict[str, Any]        # Additional metadata
    brief: Optional[ContentBrief]   # Source brief
    format: str = "markdown"        # Source format
```

## Output

Returns a `ProductionOutput` object:

```python
@dataclass
class ProductionOutput:
    file_path: str                  # Path to generated file
    file_format: str                # Output format
    content_type: ContentType       # Type of content
    metadata: Dict[str, Any]        # Production metadata
    timestamp: str                  # ISO timestamp
```

## Supported Formats

### Document Formats
- **DOCX**: Microsoft Word documents with rich formatting
- **PDF**: Portable Document Format for universal viewing
- **HTML**: Web-ready HTML with embedded CSS
- **Markdown**: Plain markdown with metadata header

### Presentation Formats
- **PPTX**: Microsoft PowerPoint presentations

## Usage Examples

### Basic Document Production

```python
from agents.production.production import ProductionAgent
from agents.base.models import DraftContent, ContentType

# Create agent
producer = ProductionAgent(config={
    "output_dir": "./output",
    "template_dir": "./templates"
})

# Prepare draft content
draft = DraftContent(
    content="# My Article\n\nThis is great content.",
    content_type=ContentType.ARTICLE,
    word_count=100,
    format="markdown"
)

# Produce DOCX
output = producer.process({
    "draft_content": draft,
    "output_format": "docx",
    "template_name": "corporate"
})

print(f"Document created: {output.file_path}")
```

### Batch Production

```python
# Produce multiple formats at once
drafts = [draft1, draft2, draft3]

outputs = producer.batch_produce(
    drafts=drafts,
    output_format="pdf",
    template="report"
)

for output in outputs:
    print(f"Created: {output.file_path}")
```

### Content Repurposing

```python
# Convert existing output to other formats
new_outputs = producer.repurpose_content(
    source_output=original_output,
    target_formats=["pdf", "html", "pptx"]
)
```

## Production Skills

The Production Agent delegates format-specific work to specialized skills:

### DOCX Generation Skill
- Creates Microsoft Word documents
- Applies templates and styling
- Handles headers, footers, and page layout
- Supports tables, images, and formatting

### PDF Generation Skill
- Generates PDF documents
- Converts from HTML/markdown
- Applies branding and watermarks
- Ensures print-ready quality

### PPTX Generation Skill
- Creates PowerPoint presentations
- Parses content into slides
- Applies slide templates
- Handles title, content, and summary slides

### Content Repurpose Skill
- Converts between formats
- Adapts content for different mediums
- Maintains brand consistency
- Optimizes for each format

## Quality Gate 4: Format Compliance

The Production Agent enforces Quality Gate 4, which validates:

1. **File Existence**: Generated file exists at specified path
2. **Format Validity**: File is valid in specified format
3. **Completeness**: All content sections included
4. **Template Compliance**: Branding and styling applied correctly
5. **Metadata Accuracy**: Metadata matches content

## Configuration Options

```python
config = {
    "output_dir": "./output",           # Output directory
    "template_dir": "./templates",      # Template directory
    "enable_validation": True,          # Enable quality gates
    "default_template": "standard",     # Default template
    "compression": True,                # Enable file compression
    "watermark": False                  # Add watermarks
}

producer = ProductionAgent(config=config)
```

## Integration with Workflow

The Production Agent is the final step in content creation workflows:

```
Research Agent → Creation Agent → Production Agent
   ↓                  ↓                    ↓
ResearchBrief → DraftContent → ProductionOutput
```

## Error Handling

The agent handles common production errors:

- **Invalid Input**: Validates draft content before processing
- **Template Not Found**: Falls back to default template
- **Format Errors**: Logs issues and attempts recovery
- **File System Errors**: Creates directories as needed

## Performance Considerations

- **Batch Processing**: Process multiple documents efficiently
- **Template Caching**: Reuse loaded templates
- **Parallel Production**: Generate multiple formats concurrently
- **Resource Management**: Clean up temporary files

## Next Steps (Phase 4)

Future enhancements planned:
- Image generation integration
- Video production capabilities
- Advanced template designer
- Cloud storage integration
- Real-time collaboration features

## See Also

- [Content Repurpose Skill](../../skills/content_repurpose/SKILL.md)
- [DOCX Generation Skill](../../skills/docx_generation/SKILL.md)
- [PDF Generation Skill](../../skills/pdf_generation/SKILL.md)
- [PPTX Generation Skill](../../skills/pptx_generation/SKILL.md)
