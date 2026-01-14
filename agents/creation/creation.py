"""
Creation Agent - Generates written content across formats.

Responsibilities:
- Draft content matching format specifications
- Apply brand voice and style guidelines
- Structure content for target audience
- Generate variations for A/B testing
- Incorporate SEO requirements where applicable
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, List, Any, Optional
from agents.base.agent import Agent
from agents.base.models import (
    ContentBrief, DraftContent, ContentType, ToneType, BrandVoiceResult
)
from datetime import datetime


class CreationAgent(Agent):
    """
    Generates written content across formats using research and briefs.

    Uses specialized writing skills to create content tailored to:
    - Content type (article, social, email, etc.)
    - Target audience
    - Brand voice guidelines
    - SEO requirements
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("creation", config)
        self.default_model = config.get("model", "claude-sonnet-4") if config else "claude-sonnet-4"
        self.enable_brand_check = config.get("enable_brand_check", True) if config else True

    def process(self, input_data: Dict[str, Any]) -> DraftContent:
        """
        Generate content from a content brief.

        Args:
            input_data: Dictionary containing:
                - content_brief: ContentBrief object
                - additional_context: Optional additional context
                - variations: Number of variations to generate (default: 1)

        Returns:
            DraftContent with generated content
        """
        content_brief = input_data.get("content_brief")
        if not content_brief:
            raise ValueError("content_brief is required")

        # Validate input
        is_valid, errors = content_brief.validate()
        if not is_valid:
            raise ValueError(f"Invalid content brief: {errors}")

        additional_context = input_data.get("additional_context", {})
        variations = input_data.get("variations", 1)

        self.logger.info(f"Creating {content_brief.content_type.value} content")

        # Route to appropriate writing skill based on content type
        if content_brief.content_type in [ContentType.ARTICLE, ContentType.BLOG_POST,
                                          ContentType.WHITEPAPER, ContentType.CASE_STUDY]:
            content = self._create_long_form(content_brief, additional_context)
        elif content_brief.content_type == ContentType.SOCIAL_POST:
            content = self._create_social(content_brief, additional_context)
        elif content_brief.content_type in [ContentType.EMAIL, ContentType.NEWSLETTER]:
            content = self._create_email(content_brief, additional_context)
        elif content_brief.content_type == ContentType.VIDEO_SCRIPT:
            content = self._create_script(content_brief, additional_context)
        elif content_brief.content_type == ContentType.PRESENTATION:
            content = self._create_presentation_content(content_brief, additional_context)
        else:
            raise ValueError(f"Unsupported content type: {content_brief.content_type}")

        # Calculate word count
        word_count = len(content.split())

        # Create draft content object
        draft = DraftContent(
            content=content,
            content_type=content_brief.content_type,
            word_count=word_count,
            metadata={
                "tone": content_brief.tone.value,
                "target_audience": content_brief.target_audience,
                "key_messages": content_brief.key_messages,
                "seo_keywords": content_brief.seo_keywords,
                "created_at": datetime.now().isoformat()
            },
            brief=content_brief,
            format="markdown"
        )

        # Validate output
        is_valid, errors = draft.validate()
        if not is_valid:
            self.logger.warning(f"Draft validation issues: {errors}")

        # Apply brand voice check if enabled
        if self.enable_brand_check and content_brief.brand_guidelines:
            brand_result = self._check_brand_voice(draft, content_brief.brand_guidelines)
            draft.metadata["brand_voice_score"] = brand_result.score
            draft.metadata["brand_voice_passed"] = brand_result.passed

            if not brand_result.passed:
                self.logger.warning(f"Brand voice check failed: {brand_result.issues}")

        self.log_execution(input_data, draft, {
            "word_count": word_count,
            "content_type": content_brief.content_type.value,
            "tone": content_brief.tone.value
        })

        return draft

    def _create_long_form(self, brief: ContentBrief, context: Dict[str, Any]) -> str:
        """
        Create long-form content (articles, blog posts, whitepapers).

        Args:
            brief: Content brief
            context: Additional context

        Returns:
            Generated content as markdown string
        """
        self.logger.info("Generating long-form content")

        # Build content sections based on structure requirements
        sections = []

        # Title
        title = self._generate_title(brief)
        sections.append(f"# {title}\n")

        # Introduction
        intro = self._generate_introduction(brief)
        sections.append(intro)

        # Main content sections
        for i, structure_item in enumerate(brief.structure_requirements[1:-1], 1):
            # Generate content for each section
            section_content = self._generate_section(brief, structure_item, i)
            sections.append(section_content)

        # Conclusion
        conclusion = self._generate_conclusion(brief)
        sections.append(conclusion)

        return "\n\n".join(sections)

    def _generate_title(self, brief: ContentBrief) -> str:
        """Generate an engaging title."""
        # Use the first key message as basis for title
        if brief.key_messages:
            base_message = brief.key_messages[0]

            # Adjust title based on tone
            if brief.tone == ToneType.CONVERSATIONAL:
                return self._conversational_title(base_message, brief)
            elif brief.tone == ToneType.PROFESSIONAL:
                return self._professional_title(base_message, brief)
            elif brief.tone == ToneType.TECHNICAL:
                return self._technical_title(base_message, brief)
            else:
                return base_message

        # Fallback: use topic from research brief
        if brief.research_brief:
            return brief.research_brief.topic.title()

        return "Untitled Content"

    def _conversational_title(self, base: str, brief: ContentBrief) -> str:
        """Generate conversational-style title."""
        # Make it more engaging and question-based if appropriate
        if "?" not in base and len(base) < 60:
            return f"How {base}"
        return base

    def _professional_title(self, base: str, brief: ContentBrief) -> str:
        """Generate professional-style title."""
        # Keep it authoritative and clear
        if ":" not in base and len(base.split()) < 8:
            return f"{base}: A Comprehensive Guide"
        return base

    def _technical_title(self, base: str, brief: ContentBrief) -> str:
        """Generate technical-style title."""
        # Add technical framing
        if not any(word in base.lower() for word in ["technical", "guide", "implementation"]):
            return f"Technical Guide: {base}"
        return base

    def _generate_introduction(self, brief: ContentBrief) -> str:
        """Generate introduction section."""
        intro_parts = []

        # Hook - attention-grabbing opening
        if brief.research_brief and brief.research_brief.sources:
            # Use a fact or statistic if available
            first_source = brief.research_brief.sources[0]
            if first_source.key_facts:
                intro_parts.append(first_source.key_facts[0])

        # Problem statement / context
        if brief.key_messages:
            intro_parts.append(f"\n\n{brief.key_messages[0]}")

        # What the reader will learn
        if len(brief.key_messages) > 1:
            intro_parts.append(
                f"\n\nIn this {brief.content_type.value}, we'll explore:"
            )
            for i, message in enumerate(brief.key_messages[1:4], 1):
                intro_parts.append(f"\n- {message}")

        return "".join(intro_parts)

    def _generate_section(self, brief: ContentBrief, structure_item: str, section_num: int) -> str:
        """Generate a main content section."""
        section = []

        # Section heading
        section.append(f"## {section_num}. {structure_item}\n")

        # Section content based on research
        if brief.research_brief and brief.research_brief.sources:
            # Use facts from sources
            relevant_facts = []
            for source in brief.research_brief.sources[:3]:
                if source.key_facts:
                    relevant_facts.extend(source.key_facts[:2])

            if relevant_facts and section_num <= len(relevant_facts):
                section.append(f"{relevant_facts[section_num - 1]}\n")

            # Add supporting details
            section.append(
                f"\nThis is particularly important for {brief.target_audience}. "
            )

            # Include a quote if available
            for source in brief.research_brief.sources:
                if source.key_quotes:
                    section.append(f'\n\n> "{source.key_quotes[0]}"\n')
                    break

        else:
            # Generate placeholder content
            section.append(
                f"Content for {structure_item} targeting {brief.target_audience}.\n"
            )

        return "".join(section)

    def _generate_conclusion(self, brief: ContentBrief) -> str:
        """Generate conclusion section."""
        conclusion = ["## Conclusion\n"]

        # Summarize key points
        if brief.key_messages:
            conclusion.append(
                f"We've explored {brief.key_messages[0].lower()}. "
            )

        # Key takeaways
        if len(brief.key_messages) > 1:
            conclusion.append("\n\nKey takeaways:\n")
            for message in brief.key_messages[:3]:
                conclusion.append(f"- {message}\n")

        # Call to action based on content type
        if brief.content_type == ContentType.BLOG_POST:
            conclusion.append("\n\nWhat are your thoughts? Share in the comments below.")
        elif brief.content_type == ContentType.ARTICLE:
            conclusion.append("\n\nFor more information, explore the sources referenced throughout this article.")

        return "".join(conclusion)

    def _create_social(self, brief: ContentBrief, context: Dict[str, Any]) -> str:
        """
        Create social media content.

        Args:
            brief: Content brief
            context: Additional context (should include 'platform')

        Returns:
            Social post content
        """
        self.logger.info("Generating social content")

        platform = context.get("platform", "linkedin")  # Default to LinkedIn

        # Get platform-specific constraints
        if platform.lower() == "twitter":
            max_length = 280
        elif platform.lower() == "linkedin":
            max_length = 3000
        elif platform.lower() == "instagram":
            max_length = 2200
        else:
            max_length = 500

        # Build social post
        post_parts = []

        # Hook (first line is critical)
        if brief.key_messages:
            hook = brief.key_messages[0]
            # Make it punchy
            if len(hook) > 80:
                hook = hook[:77] + "..."
            post_parts.append(hook)

        # Main content
        if brief.research_brief and brief.research_brief.sources:
            # Use a key fact or statistic
            for source in brief.research_brief.sources:
                if source.key_facts:
                    post_parts.append(f"\n\n{source.key_facts[0]}")
                    break

        # Additional key points (if space allows)
        if len(brief.key_messages) > 1:
            for message in brief.key_messages[1:3]:
                if len("\n\n".join(post_parts + [message])) < max_length - 100:
                    post_parts.append(f"\n\n{message}")

        # Call to action
        if platform.lower() == "linkedin":
            post_parts.append("\n\nWhat's your experience with this? Share your thoughts below. 💭")
        elif platform.lower() == "twitter":
            post_parts.append("\n\nThoughts?")

        # Hashtags
        if brief.seo_keywords:
            hashtags = [f"#{kw.replace(' ', '').title()}" for kw in brief.seo_keywords[:3]]
            hashtag_line = "\n\n" + " ".join(hashtags)

            # Only add if we have room
            full_post = "".join(post_parts) + hashtag_line
            if len(full_post) <= max_length:
                post_parts.append(hashtag_line)

        return "".join(post_parts)

    def _create_email(self, brief: ContentBrief, context: Dict[str, Any]) -> str:
        """Create email/newsletter content."""
        self.logger.info("Generating email content")

        email_parts = []

        # Subject line
        if brief.key_messages:
            subject = brief.key_messages[0]
            if len(subject) > 60:
                subject = subject[:57] + "..."
            email_parts.append(f"Subject: {subject}\n\n---\n\n")

        # Greeting
        email_parts.append("Hi there,\n\n")

        # Opening
        if brief.research_brief and brief.research_brief.sources:
            if brief.research_brief.sources[0].key_facts:
                email_parts.append(f"{brief.research_brief.sources[0].key_facts[0]}\n\n")

        # Main content
        if brief.key_messages:
            for message in brief.key_messages[:3]:
                email_parts.append(f"{message}\n\n")

        # CTA
        email_parts.append("Ready to learn more? [Read the full article here]\n\n")

        # Signature
        email_parts.append("Best regards,\nThe Team")

        return "".join(email_parts)

    def _create_script(self, brief: ContentBrief, context: Dict[str, Any]) -> str:
        """Create video script content."""
        self.logger.info("Generating script content")

        script_parts = []

        # Title card
        if brief.key_messages:
            script_parts.append(f"[TITLE CARD]\n{brief.key_messages[0]}\n\n")

        # Opening hook
        script_parts.append("[OPENING]\n")
        script_parts.append("Hey everyone! Today we're talking about something really important.\n\n")

        # Main sections
        for i, message in enumerate(brief.key_messages[:3], 1):
            script_parts.append(f"[SECTION {i}]\n")
            script_parts.append(f"{message}\n\n")

        # Closing
        script_parts.append("[CLOSING]\n")
        script_parts.append("Thanks for watching! Don't forget to like and subscribe.\n")

        return "".join(script_parts)

    def _create_presentation_content(self, brief: ContentBrief, context: Dict[str, Any]) -> str:
        """Create presentation slide content."""
        self.logger.info("Generating presentation content")

        slides = []

        # Title slide
        if brief.key_messages:
            slides.append(f"# Slide 1: Title\n{brief.key_messages[0]}\n")

        # Content slides
        for i, message in enumerate(brief.key_messages[1:], 2):
            slides.append(f"\n# Slide {i}: {message}\n")
            # Add supporting points
            if brief.research_brief and brief.research_brief.sources:
                for source in brief.research_brief.sources[:2]:
                    if source.key_facts:
                        slides.append(f"- {source.key_facts[0]}\n")
                        break

        # Summary slide
        slides.append(f"\n# Slide {len(brief.key_messages) + 1}: Summary\n")
        slides.append("Key Takeaways:\n")
        for message in brief.key_messages[:3]:
            slides.append(f"- {message}\n")

        return "\n".join(slides)

    def _check_brand_voice(self, draft: DraftContent, brand_guidelines: Dict[str, Any]) -> BrandVoiceResult:
        """
        Check content against brand voice guidelines.

        Args:
            draft: Draft content to check
            brand_guidelines: Brand guidelines dictionary

        Returns:
            BrandVoiceResult with validation results
        """
        self.logger.info("Checking brand voice compliance")

        score = 1.0
        issues = []
        suggestions = []

        content_lower = draft.content.lower()

        # Check for avoided terms
        avoided_terms = brand_guidelines.get("avoided_terms", [])
        for term in avoided_terms:
            if term.lower() in content_lower:
                score -= 0.1
                issues.append(f"Contains avoided term: '{term}'")
                suggestions.append(f"Replace '{term}' with approved alternative")

        # Check for preferred terms presence
        preferred_terms = brand_guidelines.get("preferred_terms", [])
        if preferred_terms:
            found_preferred = sum(1 for term in preferred_terms if term.lower() in content_lower)
            if found_preferred == 0:
                score -= 0.2
                issues.append("No preferred brand terms found")
                suggestions.append(f"Consider using: {', '.join(preferred_terms[:3])}")

        # Check tone consistency
        required_tone = brand_guidelines.get("tone")
        if required_tone and draft.brief:
            if required_tone != draft.brief.tone.value:
                score -= 0.15
                issues.append(f"Tone mismatch: expected {required_tone}, got {draft.brief.tone.value}")

        # Ensure score doesn't go negative
        score = max(0.0, score)

        passed = score >= 0.7 and len(issues) == 0

        return BrandVoiceResult(
            passed=passed,
            score=score,
            issues=issues,
            suggestions=suggestions
        )

    def generate_variations(self, brief: ContentBrief, count: int = 3) -> List[DraftContent]:
        """
        Generate multiple variations of content for A/B testing.

        Args:
            brief: Content brief
            count: Number of variations to generate

        Returns:
            List of DraftContent variations
        """
        variations = []

        for i in range(count):
            # Add variation context
            input_data = {
                "content_brief": brief,
                "additional_context": {"variation_number": i + 1}
            }

            variation = self.process(input_data)
            variation.metadata["variation_id"] = i + 1
            variations.append(variation)

        return variations
