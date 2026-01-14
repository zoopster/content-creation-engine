"""
Content Brief Skill - Structures research findings into actionable creation briefs.

Transforms ResearchBrief into ContentBrief with target audience, key messages,
tone, structure, and SEO requirements.
"""

from typing import Dict, List, Any, Optional
from agents.base.agent import Skill
from agents.base.models import (
    ResearchBrief, ContentBrief, ContentType, ToneType
)


class ContentBriefSkill(Skill):
    """
    Creates structured content briefs from research findings.

    Takes ResearchBrief and requirements, outputs ContentBrief with:
    - Target audience definition
    - Key messages hierarchy
    - Tone and style parameters
    - Required sections/structure
    - SEO keywords (if applicable)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("content-brief", config)
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[ContentType, Dict[str, Any]]:
        """Load content brief templates for different content types."""
        return {
            ContentType.ARTICLE: {
                "default_structure": [
                    "Engaging hook/intro",
                    "Problem statement",
                    "Main content (3-5 sections)",
                    "Examples/case studies",
                    "Conclusion with key takeaways"
                ],
                "word_count_range": (800, 1500),
                "tone": ToneType.EDUCATIONAL
            },
            ContentType.BLOG_POST: {
                "default_structure": [
                    "Catchy title and intro",
                    "Main points (2-4 sections)",
                    "Practical tips or examples",
                    "Call to action"
                ],
                "word_count_range": (600, 1200),
                "tone": ToneType.CONVERSATIONAL
            },
            ContentType.SOCIAL_POST: {
                "default_structure": [
                    "Hook (first line)",
                    "Main message",
                    "Call to action or question"
                ],
                "word_count_range": (50, 300),
                "tone": ToneType.CONVERSATIONAL
            },
            ContentType.WHITEPAPER: {
                "default_structure": [
                    "Executive summary",
                    "Problem analysis",
                    "Solution framework",
                    "Case studies/data",
                    "Implementation guidance",
                    "Conclusion"
                ],
                "word_count_range": (2000, 5000),
                "tone": ToneType.PROFESSIONAL
            },
            ContentType.EMAIL: {
                "default_structure": [
                    "Subject line",
                    "Preview text",
                    "Body (problem → solution → action)",
                    "Clear CTA"
                ],
                "word_count_range": (100, 400),
                "tone": ToneType.CONVERSATIONAL
            },
            ContentType.PRESENTATION: {
                "default_structure": [
                    "Title slide",
                    "Agenda/overview",
                    "Key points (1 per slide)",
                    "Supporting data/visuals",
                    "Summary/next steps"
                ],
                "word_count_range": (500, 1000),
                "tone": ToneType.PROFESSIONAL
            }
        }

    def execute(
        self,
        research_brief: ResearchBrief,
        content_type: ContentType,
        target_audience: Optional[str] = None,
        additional_requirements: Optional[Dict[str, Any]] = None
    ) -> ContentBrief:
        """
        Create a content brief from research findings.

        Args:
            research_brief: Research output to base content on
            content_type: Type of content to create
            target_audience: Target audience description
            additional_requirements: Optional requirements (tone, word count, etc.)

        Returns:
            ContentBrief ready for content creation
        """
        self.logger.info(f"Creating content brief for {content_type.value}")

        # Validate research brief
        is_valid, errors = research_brief.validate()
        if not is_valid:
            raise ValueError(f"Invalid research brief: {errors}")

        # Get template for content type
        template = self.templates.get(content_type, self.templates[ContentType.ARTICLE])

        # Extract additional requirements
        reqs = additional_requirements or {}

        # Create content brief
        brief = ContentBrief(
            content_type=content_type,
            target_audience=target_audience or self._infer_audience(research_brief),
            key_messages=self._extract_key_messages(research_brief),
            tone=reqs.get("tone", template["tone"]),
            structure_requirements=reqs.get("structure", template["default_structure"]),
            word_count_range=reqs.get("word_count_range", template["word_count_range"]),
            seo_keywords=self._extract_seo_keywords(research_brief),
            brand_guidelines=reqs.get("brand_guidelines", {}),
            research_brief=research_brief
        )

        # Validate brief
        is_valid, errors = brief.validate()
        if not is_valid:
            self.logger.warning(f"Content brief validation issues: {errors}")

        self.logger.info(f"Content brief created with {len(brief.key_messages)} key messages")
        return brief

    def _infer_audience(self, research_brief: ResearchBrief) -> str:
        """
        Infer target audience from research findings.

        Args:
            research_brief: Research to analyze

        Returns:
            Inferred audience description
        """
        # Simple inference - in production, this would use more sophisticated analysis
        topic_lower = research_brief.topic.lower()

        if any(word in topic_lower for word in ["technical", "engineering", "development"]):
            return "Technical professionals and engineers"
        elif any(word in topic_lower for word in ["business", "strategy", "executive"]):
            return "Business leaders and decision-makers"
        elif any(word in topic_lower for word in ["beginner", "introduction", "basics"]):
            return "Beginners and general audience"
        else:
            return "General professional audience"

    def _extract_key_messages(self, research_brief: ResearchBrief) -> List[str]:
        """
        Extract key messages from research findings.

        Args:
            research_brief: Research to analyze

        Returns:
            List of key messages prioritized by importance
        """
        # Use key findings as messages
        # In production, this would rank and refine them
        messages = research_brief.key_findings[:5]  # Top 5 findings

        if not messages:
            # Fallback: extract from sources
            messages = []
            for source in research_brief.sources[:3]:
                if source.key_facts:
                    messages.append(source.key_facts[0])

        return messages or ["No key messages extracted - requires manual input"]

    def _extract_seo_keywords(self, research_brief: ResearchBrief) -> List[str]:
        """
        Extract SEO keywords from research.

        Args:
            research_brief: Research to analyze

        Returns:
            List of relevant keywords
        """
        keywords = []

        # Extract from topic
        topic_words = research_brief.topic.split()
        keywords.extend([word.lower() for word in topic_words if len(word) > 3])

        # Extract from key findings
        for finding in research_brief.key_findings:
            words = finding.split()
            # Get important words (simple heuristic: longer words)
            keywords.extend([word.lower() for word in words if len(word) > 5])

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:10]  # Top 10 keywords

    def get_template(self, content_type: ContentType) -> Dict[str, Any]:
        """
        Get content brief template for a content type.

        Args:
            content_type: Type of content

        Returns:
            Template configuration
        """
        return self.templates.get(content_type, self.templates[ContentType.ARTICLE])
