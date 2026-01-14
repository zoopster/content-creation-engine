"""
Production Agent - Transforms content into final formatted deliverables.

Unified implementation combining native generation (Markdown, HTML) with
skill delegation (DOCX, PDF, PPTX) for flexible, brand-consistent output.

Responsibilities:
- Convert content to target formats (DOCX, PDF, PPTX, HTML, Markdown)
- Apply brand templates and styling
- Validate format compliance
- Support batch production and content repurposing
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import re

from agents.base.agent import Agent
from agents.base.models import (
    DraftContent, ProductionOutput, ContentType
)
from templates.brand.brand_config import BrandTemplate, get_brand_template


class ProductionAgent(Agent):
    """
    Transforms draft content into final formatted deliverables with brand consistency.

    Native Formats (no dependencies):
    - Markdown (with brand headers/footers)
    - HTML (fully styled with brand CSS)

    Delegated Formats (optional dependencies):
    - DOCX (requires python-docx)
    - PDF (requires reportlab)
    - PPTX (requires python-pptx)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("production", config)
        self.output_dir = Path(self.config.get("output_dir", "output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load brand template
        template_name = self.config.get("brand_template", "professional")
        self.brand_template = get_brand_template(template_name)

        # Check for optional dependencies
        self.has_docx = self._check_dependency("docx")
        self.has_pptx = self._check_dependency("pptx")
        self.has_reportlab = self._check_dependency("reportlab")

        if not self.has_docx:
            self.logger.info("python-docx not available - DOCX will fall back to HTML")
        if not self.has_reportlab:
            self.logger.info("reportlab not available - PDF will fall back to HTML")
        if not self.has_pptx:
            self.logger.info("python-pptx not available - PPTX will fall back to HTML")

    def _check_dependency(self, module_name: str) -> bool:
        """Check if optional dependency is available."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def process(self, input_data: Dict[str, Any]) -> ProductionOutput:
        """
        Transform draft content into final formatted output.

        Args:
            input_data: Dictionary containing:
                - draft_content: DraftContent object
                - output_format: Target format (markdown, html, docx, pdf, pptx)
                - template_override: Optional template name override
                - additional_options: Format-specific options

        Returns:
            ProductionOutput with file path and metadata
        """
        draft = input_data.get("draft_content")
        if not draft:
            raise ValueError("draft_content is required")

        output_format = input_data.get("output_format", "html").lower()
        template_override = input_data.get("template_override")

        if template_override:
            self.brand_template = get_brand_template(template_override)

        self.logger.info(f"Producing {output_format} output for {draft.content_type.value} using {self.brand_template.name} template")

        # Route to appropriate generator
        if output_format == "markdown":
            output = self._generate_markdown(draft)
        elif output_format == "html":
            output = self._generate_html(draft)
        elif output_format == "docx":
            output = self._generate_docx(draft)
        elif output_format == "pdf":
            output = self._generate_pdf(draft)
        elif output_format == "pptx":
            output = self._generate_pptx(draft)
        else:
            # Default to HTML
            self.logger.warning(f"Unknown format {output_format}, using HTML")
            output = self._generate_html(draft)

        # Validate output
        is_valid, errors = output.validate()
        if not is_valid:
            self.logger.warning(f"Production output validation issues: {errors}")

        self.log_execution(input_data, output, {
            "format": output_format,
            "brand_template": self.brand_template.name
        })

        self.logger.info(f"Produced {output_format} file: {output.file_path}")
        return output

    def _generate_markdown(self, draft: DraftContent) -> ProductionOutput:
        """
        Generate markdown with brand elements.

        Adds brand header and footer to maintain brand consistency
        even in plain markdown format.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{draft.content_type.value}_{timestamp}.md"
        file_path = self.output_dir / filename

        # Build content with brand elements
        parts = []

        # Brand header
        parts.append(f"**{self.brand_template.company_name}**\n")
        if self.brand_template.company_tagline:
            parts.append(f"*{self.brand_template.company_tagline}*\n")
        parts.append("\n---\n\n")

        # Main content
        parts.append(draft.content)

        # Brand footer
        parts.append("\n\n---\n\n")
        parts.append(f"*© {datetime.now().year} {self.brand_template.company_name}*\n")
        if self.brand_template.website:
            parts.append(f"*{self.brand_template.website}*\n")
        parts.append(f"*Generated {datetime.now().strftime('%B %d, %Y')}*")

        # Write file
        content = "".join(parts)
        file_path.write_text(content, encoding="utf-8")

        return ProductionOutput(
            file_path=str(file_path),
            file_format="markdown",
            content_type=draft.content_type,
            metadata={
                "word_count": draft.word_count,
                "brand_template": self.brand_template.name,
                "file_size": len(content)
            }
        )

    def _generate_html(self, draft: DraftContent) -> ProductionOutput:
        """
        Generate HTML with full brand styling.

        Creates a complete HTML document with:
        - Brand colors and typography
        - Brand header and footer
        - Print-optimized styles
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{draft.content_type.value}_{timestamp}.html"
        file_path = self.output_dir / filename

        # Convert markdown content to HTML
        html_content = self._markdown_to_html(draft.content)

        # Build complete HTML document
        html_doc = self._build_branded_html(html_content, draft)

        # Write file
        file_path.write_text(html_doc, encoding="utf-8")

        return ProductionOutput(
            file_path=str(file_path),
            file_format="html",
            content_type=draft.content_type,
            metadata={
                "word_count": draft.word_count,
                "brand_template": self.brand_template.name,
                "colors": self.brand_template.colors.primary,
                "file_size": len(html_doc)
            }
        )

    def _markdown_to_html(self, markdown: str) -> str:
        """
        Convert markdown to HTML.

        Simple implementation supporting:
        - Headings (# to ####)
        - Paragraphs
        - Lists (future enhancement)
        - Bold/italic (future enhancement)
        """
        lines = markdown.split("\n")
        processed = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("# "):
                processed.append(f"<h1>{stripped[2:]}</h1>")
            elif stripped.startswith("## "):
                processed.append(f"<h2>{stripped[3:]}</h2>")
            elif stripped.startswith("### "):
                processed.append(f"<h3>{stripped[4:]}</h3>")
            elif stripped.startswith("#### "):
                processed.append(f"<h4>{stripped[5:]}</h4>")
            elif stripped:
                # Paragraph
                processed.append(f"<p>{stripped}</p>")
            else:
                # Empty line
                processed.append("")

        return "\n".join(processed)

    def _build_branded_html(self, content: str, draft: DraftContent) -> str:
        """Build complete HTML document with brand styling."""
        colors = self.brand_template.colors
        typo = self.brand_template.typography

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{draft.content_type.value.title().replace('_', ' ')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: '{typo.body_font}', Arial, sans-serif;
            font-size: {typo.body_size}pt;
            line-height: {typo.body_line_height};
            color: {colors.text};
            background-color: {colors.background};
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 60px 40px;
        }}

        /* Brand Header */
        header.brand-header {{
            border-bottom: 4px solid {colors.primary};
            padding-bottom: 30px;
            margin-bottom: 50px;
        }}

        .company-name {{
            font-family: '{typo.heading_font}', Arial, sans-serif;
            font-size: {typo.h1_size}pt;
            font-weight: bold;
            color: {colors.primary};
            margin-bottom: 10px;
        }}

        .company-tagline {{
            font-size: {typo.small_size}pt;
            color: {colors.text_light};
            font-style: italic;
        }}

        /* Content Typography */
        h1 {{
            font-family: '{typo.heading_font}', Arial, sans-serif;
            font-size: {typo.h1_size}pt;
            font-weight: bold;
            color: {colors.primary};
            margin: 30px 0 20px 0;
            line-height: {typo.heading_line_height};
        }}

        h2 {{
            font-family: '{typo.heading_font}', Arial, sans-serif;
            font-size: {typo.h2_size}pt;
            font-weight: bold;
            color: {colors.secondary};
            margin: 25px 0 15px 0;
            line-height: {typo.heading_line_height};
        }}

        h3 {{
            font-family: '{typo.heading_font}', Arial, sans-serif;
            font-size: {typo.h3_size}pt;
            font-weight: bold;
            color: {colors.secondary};
            margin: 20px 0 10px 0;
            line-height: {typo.heading_line_height};
        }}

        h4 {{
            font-family: '{typo.heading_font}', Arial, sans-serif;
            font-size: {typo.body_size + 1}pt;
            font-weight: bold;
            color: {colors.text};
            margin: 15px 0 10px 0;
        }}

        p {{
            margin-bottom: 1.2em;
            text-align: justify;
        }}

        /* Links */
        a {{
            color: {colors.accent};
            text-decoration: none;
            border-bottom: 1px solid {colors.accent};
            transition: color 0.2s;
        }}

        a:hover {{
            color: {colors.primary};
            border-bottom-color: {colors.primary};
        }}

        /* Emphasis */
        strong {{
            color: {colors.primary};
            font-weight: bold;
        }}

        em {{
            font-style: italic;
            color: {colors.text_light};
        }}

        /* Lists */
        ul, ol {{
            margin: 1em 0 1em 2em;
        }}

        li {{
            margin-bottom: 0.5em;
        }}

        /* Blockquotes */
        blockquote {{
            border-left: 4px solid {colors.accent};
            padding-left: 20px;
            margin: 1.5em 0;
            font-style: italic;
            color: {colors.text_light};
        }}

        /* Content area */
        .content {{
            margin-bottom: 60px;
        }}

        /* Brand Footer */
        footer.brand-footer {{
            border-top: 2px solid {colors.text_light};
            padding-top: 30px;
            margin-top: 60px;
            text-align: center;
            color: {colors.text_light};
            font-size: {typo.small_size}pt;
        }}

        .footer-content {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            align-items: center;
        }}

        .footer-content p {{
            margin: 0;
        }}

        .generated-date {{
            font-style: italic;
            font-size: {typo.small_size - 1}pt;
        }}

        /* Print styles */
        @media print {{
            body {{
                background: white;
            }}

            .container {{
                padding: 0;
            }}

            a {{
                color: {colors.text};
                border-bottom: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="brand-header">
            <div class="company-name">{self.brand_template.company_name}</div>
            {f'<div class="company-tagline">{self.brand_template.company_tagline}</div>' if self.brand_template.company_tagline else ''}
        </header>

        <main class="content">
{content}
        </main>

        <footer class="brand-footer">
            <div class="footer-content">
                <p><strong>© {datetime.now().year} {self.brand_template.company_name}</strong></p>
                {f'<p><a href="{self.brand_template.website}">{self.brand_template.website}</a></p>' if self.brand_template.website else ''}
                <p class="generated-date">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
        </footer>
    </div>
</body>
</html>"""

    def _generate_docx(self, draft: DraftContent) -> ProductionOutput:
        """
        Generate DOCX document from draft content.

        Delegates to DocxGenerationSkill if python-docx is available,
        otherwise falls back to HTML output.
        """
        if not self.has_docx:
            self.logger.warning("python-docx not installed, falling back to HTML")
            return self._generate_html(draft)

        from skills.docx_generation.docx_generation import DocxGenerationSkill

        skill = DocxGenerationSkill(config={
            "output_dir": str(self.output_dir)
        })

        result = skill.execute(draft, brand_template=self.brand_template)

        return ProductionOutput(
            file_path=result["file_path"],
            file_format="docx",
            content_type=draft.content_type,
            metadata=result.get("metadata", {})
        )

    def _generate_pdf(self, draft: DraftContent) -> ProductionOutput:
        """
        Generate PDF document from draft content.

        Delegates to PdfGenerationSkill if reportlab is available,
        otherwise falls back to HTML output.
        """
        if not self.has_reportlab:
            self.logger.warning("reportlab not installed, falling back to HTML")
            return self._generate_html(draft)

        from skills.pdf_generation.pdf_generation import PdfGenerationSkill

        skill = PdfGenerationSkill(config={
            "output_dir": str(self.output_dir)
        })

        result = skill.execute(draft, brand_template=self.brand_template)

        return ProductionOutput(
            file_path=result["file_path"],
            file_format="pdf",
            content_type=draft.content_type,
            metadata=result.get("metadata", {})
        )

    def _generate_pptx(self, draft: DraftContent) -> ProductionOutput:
        """
        Generate PPTX presentation from draft content.

        Delegates to PptxGenerationSkill if python-pptx is available,
        otherwise falls back to HTML output.
        """
        if not self.has_pptx:
            self.logger.warning("python-pptx not installed, falling back to HTML")
            return self._generate_html(draft)

        from skills.pptx_generation.pptx_generation import PptxGenerationSkill

        skill = PptxGenerationSkill(config={
            "output_dir": str(self.output_dir)
        })

        result = skill.execute(draft, brand_template=self.brand_template)

        return ProductionOutput(
            file_path=result["file_path"],
            file_format="pptx",
            content_type=draft.content_type,
            metadata=result.get("metadata", {})
        )

    def batch_produce(self, drafts: List[DraftContent], output_formats: List[str],
                     template_override: Optional[str] = None) -> List[ProductionOutput]:
        """
        Produce multiple outputs in batch.

        Args:
            drafts: List of draft content to process
            output_formats: List of target formats to generate
            template_override: Optional template to use for all outputs

        Returns:
            List of ProductionOutput objects
        """
        outputs = []
        total = len(drafts) * len(output_formats)
        count = 0

        for draft in drafts:
            for output_format in output_formats:
                count += 1
                self.logger.info(f"Processing {count}/{total}: {draft.content_type.value} → {output_format}")

                input_data = {
                    "draft_content": draft,
                    "output_format": output_format,
                    "template_override": template_override
                }

                try:
                    output = self.process(input_data)
                    outputs.append(output)
                except Exception as e:
                    self.logger.error(f"Failed to produce {output_format}: {str(e)}")
                    # Continue with remaining items

        return outputs

    def repurpose_content(self, source_output: ProductionOutput,
                         target_formats: List[str]) -> List[ProductionOutput]:
        """
        Repurpose existing output into multiple formats.

        Note: This method will be fully implemented when ContentRepurposeSkill
        is available. Currently provides a basic implementation.

        Args:
            source_output: Source production output
            target_formats: List of target formats

        Returns:
            List of new ProductionOutput objects
        """
        self.logger.info(f"Repurposing {source_output.file_format} to {target_formats}")

        # Basic implementation: read source and regenerate
        # In Phase 3D, this will use ContentRepurposeSkill for smart transformation
        try:
            source_path = Path(source_output.file_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source file not found: {source_output.file_path}")

            # For now, return empty list with info message
            # This will be properly implemented in Phase 3D with ContentRepurposeSkill
            self.logger.info("Content repurposing requires ContentRepurposeSkill (Phase 3D)")
            return []

        except Exception as e:
            self.logger.error(f"Content repurposing failed: {str(e)}")
            return []
