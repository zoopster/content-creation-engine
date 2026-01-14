"""
PDF Generation Skill - Creates PDF documents from draft content.

This skill transforms markdown content into formatted PDF files with:
- Professional styling and formatting
- Brand template support
- Headers, footers, and page numbers
- Custom typography and colors
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, Any, Optional, List
from agents.base.agent import Skill
from agents.base.models import DraftContent
from datetime import datetime
import re


class PdfGenerationSkill(Skill):
    """
    Generates PDF documents from draft content using reportlab.

    Features:
    - Markdown to PDF conversion
    - Brand template application
    - Professional typography and layout
    - Headers, footers, and page numbers
    - Automatic page breaks
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("pdf-generation", config)
        self.output_dir = config.get("output_dir", "./output") if config else "./output"

        # Ensure directories exist
        os.makedirs(self.output_dir, exist_ok=True)

    def execute(self, input_data: DraftContent, **kwargs) -> Dict[str, Any]:
        """
        Generate PDF document from draft content.

        Args:
            input_data: DraftContent object with markdown content
            **kwargs:
                - brand_template: BrandTemplate for styling
                - include_toc: Include table of contents (default: False)
                - page_numbers: Add page numbers (default: True)

        Returns:
            Dictionary with:
                - file_path: Path to generated PDF file
                - success: Boolean indicating success
                - metadata: Additional information
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.platypus import ListFlowable, ListItem
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
            from reportlab.lib import colors
            from reportlab.pdfgen import canvas
        except ImportError:
            self.logger.error("reportlab not installed. Install with: pip install reportlab")
            return self._generate_mock_pdf(input_data, **kwargs)

        brand_template = kwargs.get("brand_template")
        include_toc = kwargs.get("include_toc", False)
        page_numbers = kwargs.get("page_numbers", True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{input_data.content_type.value}_{timestamp}.pdf"
        file_path = os.path.join(self.output_dir, filename)

        # Determine page size
        page_size = letter
        if brand_template and hasattr(brand_template, 'document_layout'):
            if brand_template.document_layout.page_size == "a4":
                page_size = A4

        # Create PDF document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Apply margins from brand template if available
        if brand_template and hasattr(brand_template, 'document_layout'):
            layout = brand_template.document_layout
            doc.rightMargin = layout.margin_right * inch
            doc.leftMargin = layout.margin_left * inch
            doc.topMargin = layout.margin_top * inch
            doc.bottomMargin = layout.margin_bottom * inch

        # Create styles
        styles = self._create_styles(brand_template)

        # Build content
        story = []

        # Add brand header
        if brand_template:
            story.append(Paragraph(brand_template.company_name, styles['BrandHeader']))
            if brand_template.company_tagline:
                story.append(Paragraph(brand_template.company_tagline, styles['BrandTagline']))
            story.append(Spacer(1, 0.3 * inch))

        # Parse markdown and add to story
        elements = self._parse_markdown_to_elements(input_data.content, styles, brand_template)
        story.extend(elements)

        # Add brand footer content
        if brand_template:
            story.append(Spacer(1, 0.5 * inch))
            footer_text = f"© {datetime.now().year} {brand_template.company_name}"
            if brand_template.website:
                footer_text += f" | {brand_template.website}"
            footer_text += f" | Generated {datetime.now().strftime('%B %d, %Y')}"
            story.append(Paragraph(footer_text, styles['FooterText']))

        # Build PDF with page numbers
        if page_numbers and brand_template:
            doc.build(story, onFirstPage=lambda c, d: self._add_page_decorations(c, d, brand_template),
                     onLaterPages=lambda c, d: self._add_page_decorations(c, d, brand_template))
        else:
            doc.build(story)

        self.logger.info(f"Generated PDF: {file_path}")

        return {
            "file_path": file_path,
            "success": True,
            "metadata": {
                "word_count": input_data.word_count,
                "page_size": brand_template.document_layout.page_size if brand_template else "letter",
                "brand_template": brand_template.name if brand_template else None,
                "created_at": datetime.now().isoformat()
            }
        }

    def _create_styles(self, brand_template: Any = None) -> Dict[str, Any]:
        """Create reportlab styles from brand template."""
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
        from reportlab.lib.units import inch
        from reportlab.lib import colors

        styles_dict = {}
        base_styles = getSampleStyleSheet()

        # Helper to convert hex to reportlab color
        def hex_to_color(hex_string: str):
            """Convert hex color to reportlab color."""
            hex_string = hex_string.lstrip('#')
            r, g, b = tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))
            return colors.Color(r/255.0, g/255.0, b/255.0)

        if brand_template:
            # Brand-specific styles
            styles_dict['BrandHeader'] = ParagraphStyle(
                'BrandHeader',
                parent=base_styles['Heading1'],
                fontSize=brand_template.typography.h1_size + 4,
                textColor=hex_to_color(brand_template.colors.primary),
                alignment=TA_CENTER,
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )

            styles_dict['BrandTagline'] = ParagraphStyle(
                'BrandTagline',
                parent=base_styles['Normal'],
                fontSize=brand_template.typography.small_size,
                textColor=hex_to_color(brand_template.colors.text_light),
                alignment=TA_CENTER,
                fontStyle='italic',
                spaceAfter=12
            )

            styles_dict['Heading1'] = ParagraphStyle(
                'CustomHeading1',
                parent=base_styles['Heading1'],
                fontSize=brand_template.typography.h1_size,
                textColor=hex_to_color(brand_template.colors.primary),
                spaceAfter=12,
                spaceBefore=20,
                fontName='Helvetica-Bold'
            )

            styles_dict['Heading2'] = ParagraphStyle(
                'CustomHeading2',
                parent=base_styles['Heading2'],
                fontSize=brand_template.typography.h2_size,
                textColor=hex_to_color(brand_template.colors.secondary),
                spaceAfter=10,
                spaceBefore=16,
                fontName='Helvetica-Bold'
            )

            styles_dict['Heading3'] = ParagraphStyle(
                'CustomHeading3',
                parent=base_styles['Heading3'],
                fontSize=brand_template.typography.h3_size,
                textColor=hex_to_color(brand_template.colors.secondary),
                spaceAfter=8,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )

            styles_dict['BodyText'] = ParagraphStyle(
                'CustomBody',
                parent=base_styles['BodyText'],
                fontSize=brand_template.typography.body_size,
                textColor=hex_to_color(brand_template.colors.text),
                alignment=TA_JUSTIFY,
                spaceAfter=brand_template.document_layout.paragraph_spacing_after,
                fontName='Helvetica'
            )

            styles_dict['FooterText'] = ParagraphStyle(
                'FooterText',
                parent=base_styles['Normal'],
                fontSize=brand_template.typography.small_size,
                textColor=hex_to_color(brand_template.colors.text_light),
                alignment=TA_CENTER
            )

        else:
            # Default styles without brand template
            styles_dict['Heading1'] = base_styles['Heading1']
            styles_dict['Heading2'] = base_styles['Heading2']
            styles_dict['Heading3'] = base_styles['Heading3']
            styles_dict['BodyText'] = base_styles['BodyText']

        # Bullet style
        styles_dict['Bullet'] = ParagraphStyle(
            'Bullet',
            parent=styles_dict.get('BodyText', base_styles['BodyText']),
            leftIndent=20,
            spaceAfter=6
        )

        return styles_dict

    def _parse_markdown_to_elements(self, content: str, styles: Dict, brand_template: Any = None) -> List:
        """Convert markdown content to reportlab elements."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch

        elements = []
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                elements.append(Spacer(1, 0.1 * inch))
                i += 1
                continue

            # Heading 1
            if line.startswith('# '):
                text = line[2:].strip()
                elements.append(Spacer(1, 0.2 * inch))
                elements.append(Paragraph(text, styles.get('Heading1')))

            # Heading 2
            elif line.startswith('## '):
                text = line[3:].strip()
                elements.append(Spacer(1, 0.15 * inch))
                elements.append(Paragraph(text, styles.get('Heading2')))

            # Heading 3
            elif line.startswith('### '):
                text = line[4:].strip()
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(Paragraph(text, styles.get('Heading3')))

            # Heading 4
            elif line.startswith('#### '):
                text = line[5:].strip()
                elements.append(Paragraph(text, styles.get('Heading3')))

            # Unordered list
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip()
                bullet_text = f"• {text}"
                elements.append(Paragraph(bullet_text, styles.get('Bullet')))

            # Ordered list
            elif re.match(r'^\d+\.\s', line):
                text = line[line.index('.') + 1:].strip()
                number = line[:line.index('.')]
                numbered_text = f"{number}. {text}"
                elements.append(Paragraph(numbered_text, styles.get('Bullet')))

            # Blockquote
            elif line.startswith('> '):
                text = line[2:].strip()
                quote_text = f"<i>{text}</i>"
                elements.append(Paragraph(quote_text, styles.get('BodyText')))

            # Horizontal rule
            elif line.strip() == '---':
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(Paragraph('_' * 80, styles.get('BodyText')))
                elements.append(Spacer(1, 0.1 * inch))

            # Regular paragraph
            else:
                # Handle inline formatting (bold, italic)
                text = self._process_inline_formatting(line)
                elements.append(Paragraph(text, styles.get('BodyText')))

            i += 1

        return elements

    def _process_inline_formatting(self, text: str) -> str:
        """Process inline markdown formatting for reportlab."""
        # Bold: **text** -> <b>text</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

        # Italic: *text* -> <i>text</i>
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)

        # Inline code: `text` -> <font name="Courier">text</font>
        text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)

        return text

    def _add_page_decorations(self, canvas: Any, doc: Any, brand_template: Any):
        """Add headers, footers, and page numbers."""
        from reportlab.lib.units import inch

        canvas.saveState()

        # Page number
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(doc.width + doc.leftMargin - 0.5*inch,
                              0.5*inch, text)

        canvas.restoreState()

    def _generate_mock_pdf(self, draft: DraftContent, **kwargs) -> Dict[str, Any]:
        """
        Generate a mock PDF file when reportlab is not available.
        Creates a simple text file with .pdf extension for development.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{draft.content_type.value}_{timestamp}.pdf"
        file_path = os.path.join(self.output_dir, filename)

        brand_template = kwargs.get("brand_template")

        # Create a simple text representation
        content = f"""PDF Document (Mock)
{'=' * 50}

Content Type: {draft.content_type.value}
Word Count: {draft.word_count}
Created: {datetime.now().isoformat()}
"""

        if brand_template:
            content += f"""Brand Template: {brand_template.name}
Company: {brand_template.company_name}
"""

        content += f"""
{'=' * 50}

{draft.content}

{'=' * 50}
Note: This is a mock PDF file. Install reportlab for real PDF generation.
pip install reportlab Pillow
"""

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        self.logger.info(f"Generated mock PDF: {file_path}")

        return {
            "file_path": file_path,
            "success": True,
            "metadata": {
                "word_count": draft.word_count,
                "mock": True,
                "created_at": datetime.now().isoformat()
            }
        }

    def validate_requirements(self) -> tuple[bool, list[str]]:
        """Validate that required dependencies are available."""
        missing = []

        try:
            import reportlab
        except ImportError:
            missing.append("reportlab")

        try:
            import PIL
        except ImportError:
            missing.append("Pillow")

        return len(missing) == 0, missing
