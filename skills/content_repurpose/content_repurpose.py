"""
Content Repurpose Skill - Transforms content between formats.

This skill orchestrates other skills to convert content from one format
to another following the content transformation matrix:

Article → Social: Extract key points, use SocialContentSkill
Article → Presentation: Restructure for slides
Research → Article: Use LongFormWritingSkill
Research → Email: Extract summary
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, Any, Optional, List
from agents.base.agent import Skill
from agents.base.models import (
    DraftContent, ContentBrief, ContentType, ToneType,
    ResearchBrief
)


class ContentRepurposeSkill(Skill):
    """
    Repurpose content between formats using skill orchestration.

    Supported Transformations:
    - Article → Social posts (extract key points)
    - Article → Presentation (structure to slides)
    - Article → Email (condense to summary)
    - Research → Article (full draft)
    - Research → Email (summary + key findings)
    """

    # Transformation matrix: (source_type, target_type) → method_name
    TRANSFORMATION_MAP = {
        (ContentType.ARTICLE, ContentType.SOCIAL_POST): "_article_to_social",
        (ContentType.ARTICLE, ContentType.PRESENTATION): "_article_to_presentation",
        (ContentType.ARTICLE, ContentType.EMAIL): "_article_to_email",
        (ContentType.BLOG_POST, ContentType.SOCIAL_POST): "_article_to_social",
        (ContentType.BLOG_POST, ContentType.PRESENTATION): "_article_to_presentation",
        (ContentType.WHITEPAPER, ContentType.PRESENTATION): "_article_to_presentation",
        (ContentType.WHITEPAPER, ContentType.EMAIL): "_article_to_email",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("content-repurpose", config)

    def execute(self, source_content: Any, target_format: ContentType, **kwargs) -> Dict[str, Any]:
        """
        Execute content transformation.

        Args:
            source_content: Source content (DraftContent, ResearchBrief, or ProductionOutput)
            target_format: Target ContentType
            **kwargs:
                - platform: Target platform for social posts (linkedin, twitter, etc.)
                - length: Target length (short, medium, long)
                - tone: Target tone if different from source

        Returns:
            Dictionary with:
                - content: Transformed content (str or DraftContent)
                - success: Boolean indicating success
                - metadata: Transformation information
        """
        # Detect source type
        source_type = self._detect_source_type(source_content)

        self.logger.info(f"Repurposing {source_type.value} → {target_format.value}")

        # Find transformation method
        transform_key = (source_type, target_format)

        if transform_key not in self.TRANSFORMATION_MAP:
            supported = [f"{s.value}→{t.value}" for s, t in self.TRANSFORMATION_MAP.keys()]
            raise ValueError(
                f"Transformation {source_type.value}→{target_format.value} not supported. "
                f"Supported: {', '.join(supported)}"
            )

        method_name = self.TRANSFORMATION_MAP[transform_key]
        method = getattr(self, method_name)

        # Execute transformation
        result = method(source_content, **kwargs)

        return {
            "content": result,
            "success": True,
            "metadata": {
                "source_type": source_type.value,
                "target_type": target_format.value,
                "transformation": method_name
            }
        }

    def _detect_source_type(self, content: Any) -> ContentType:
        """Detect the type of source content."""
        if isinstance(content, DraftContent):
            return content.content_type
        elif isinstance(content, ResearchBrief):
            return ContentType.ARTICLE  # Research can become article
        elif hasattr(content, 'content_type'):
            return content.content_type
        else:
            # Default
            return ContentType.ARTICLE

    def _article_to_social(self, draft: DraftContent, **kwargs) -> str:
        """Transform article to social post."""
        platform = kwargs.get("platform", "linkedin")

        # Extract key points (first sentence of each section)
        key_points = self._extract_key_points(draft.content, max_points=3)

        # Create brief for social content
        brief = ContentBrief(
            content_type=ContentType.SOCIAL_POST,
            target_audience=draft.metadata.get("target_audience", "general"),
            key_messages=key_points,
            tone=draft.metadata.get("tone", ToneType.PROFESSIONAL),
            structure_requirements=["hook", "value", "cta"],
            word_count_range=(100, 300),
            seo_keywords=[],
            brand_guidelines={},
            research_brief=None
        )

        # Use SocialContentSkill
        try:
            from skills.social_content.social_content import SocialContentSkill

            skill = SocialContentSkill()
            return skill.execute(brief, platform=platform)
        except ImportError as e:
            self.logger.error(f"SocialContentSkill not available: {e}")
            # Fallback: simple extraction
            return self._simple_social_extract(draft.content, key_points)

    def _article_to_presentation(self, draft: DraftContent, **kwargs) -> str:
        """Transform article to presentation structure."""
        # Restructure content for slides
        # H1 → Section slides
        # H2 → Content slides
        # Paragraphs → Bullet points

        lines = draft.content.split('\n')
        presentation_content = []
        current_section = None

        for line in lines:
            stripped = line.strip()

            if stripped.startswith('# '):
                # Section slide
                presentation_content.append(stripped)
                current_section = stripped[2:].strip()

            elif stripped.startswith('## '):
                # Content slide
                presentation_content.append(stripped)

            elif stripped and not stripped.startswith('#'):
                # Convert paragraphs to bullets
                # Take first sentence or key phrase
                sentences = stripped.split('. ')
                if sentences:
                    presentation_content.append(f"- {sentences[0]}")

        return '\n'.join(presentation_content)

    def _article_to_email(self, draft: DraftContent, **kwargs) -> str:
        """Transform article to email summary."""
        # Extract key points
        key_points = self._extract_key_points(draft.content, max_points=5)

        # Build email format
        email_parts = []

        # Subject line (from first H1 or first sentence)
        title = self._extract_title(draft.content)
        email_parts.append(f"Subject: {title}")
        email_parts.append("")

        # Opening
        email_parts.append("Hi there,")
        email_parts.append("")

        # Brief introduction
        email_parts.append("I wanted to share some key insights:")
        email_parts.append("")

        # Key points as bullets
        for point in key_points:
            email_parts.append(f"• {point}")

        email_parts.append("")

        # Closing with CTA
        email_parts.append("Let me know if you'd like to discuss further!")
        email_parts.append("")
        email_parts.append("Best regards")

        return '\n'.join(email_parts)

    def _extract_key_points(self, content: str, max_points: int = 3) -> List[str]:
        """Extract key points from content."""
        points = []
        lines = content.split('\n')

        for line in lines:
            stripped = line.strip()

            # Skip headings
            if stripped.startswith('#'):
                continue

            # Get sentences from paragraphs
            if stripped and len(stripped) > 50:
                # Take first sentence
                sentences = stripped.split('. ')
                if sentences[0]:
                    points.append(sentences[0])

            # Stop when we have enough
            if len(points) >= max_points:
                break

        return points[:max_points]

    def _extract_title(self, content: str) -> str:
        """Extract title from content."""
        lines = content.split('\n')

        for line in lines:
            stripped = line.strip()

            # Find first H1
            if stripped.startswith('# '):
                return stripped[2:].strip()

        # Fallback: first non-empty line
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Take first 60 chars
                return stripped[:60] + ('...' if len(stripped) > 60 else '')

        return "Content Summary"

    def _simple_social_extract(self, content: str, key_points: List[str]) -> str:
        """Simple social post extraction (fallback)."""
        title = self._extract_title(content)

        parts = [title, ""]
        parts.extend([f"• {point}" for point in key_points])
        parts.append("")
        parts.append("#content #insights")

        return '\n'.join(parts)

    def validate_requirements(self) -> tuple[bool, list[str]]:
        """Validate that required skills are available."""
        missing = []

        try:
            from skills.social_content.social_content import SocialContentSkill
        except ImportError:
            missing.append("SocialContentSkill (recommended)")

        # Content repurpose can work with fallbacks, so return success
        return True, missing
