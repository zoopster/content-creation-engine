"""
Long-Form Writing Skill - Generates articles, reports, and extended content.

Handles:
- Articles (800-1500 words)
- Blog posts (600-1200 words)
- Whitepapers (2000-5000 words)
- Case studies (1000-2000 words)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, List, Any, Optional
from agents.base.agent import Skill
from agents.base.models import ContentBrief, ContentType, ToneType


class LongFormWritingSkill(Skill):
    """
    Generates long-form written content from content briefs.

    Features:
    - Multiple article structures (problem-solution, how-to, listicle, narrative)
    - Tone-aware writing (professional, conversational, technical)
    - SEO optimization
    - Research integration
    - Proper markdown formatting
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("long-form-writing", config)
        self.structures = self._initialize_structures()
        self.hooks = self._initialize_hooks()

    def _initialize_structures(self) -> Dict[str, List[str]]:
        """Define content structure templates."""
        return {
            "problem_solution": [
                "Introduction: Present the problem",
                "Problem Analysis: Deep dive into the issue",
                "Solution Framework: Proposed approach",
                "Implementation: How to apply the solution",
                "Results: Expected outcomes",
                "Conclusion: Summary and next steps"
            ],
            "how_to": [
                "Introduction: What you'll learn",
                "Prerequisites: What you need",
                "Step-by-step guide",
                "Common pitfalls to avoid",
                "Advanced tips",
                "Conclusion: Review and next steps"
            ],
            "listicle": [
                "Introduction: Why this list matters",
                "Item 1 with details",
                "Item 2 with details",
                "Item 3 with details",
                "Additional items",
                "Conclusion: Final thoughts"
            ],
            "narrative": [
                "Hook: Engaging opening story",
                "Background: Context and setup",
                "Rising action: Building the narrative",
                "Climax: Key insight or turning point",
                "Resolution: Takeaways",
                "Conclusion: Call to action"
            ],
            "analysis": [
                "Executive summary",
                "Background and context",
                "Data analysis",
                "Key findings",
                "Implications",
                "Recommendations",
                "Conclusion"
            ]
        }

    def _initialize_hooks(self) -> Dict[str, List[str]]:
        """Define opening hook templates."""
        return {
            "statistic": "Did you know that {statistic}?",
            "question": "Have you ever wondered {question}?",
            "story": "Imagine this: {scenario}",
            "bold_claim": "{claim}",
            "problem": "Here's a problem: {problem}"
        }

    def execute(
        self,
        content_brief: ContentBrief,
        structure_type: str = "problem_solution",
        **kwargs
    ) -> str:
        """
        Generate long-form content from a brief.

        Args:
            content_brief: Content brief with requirements
            structure_type: Type of structure to use
            **kwargs: Additional parameters

        Returns:
            Generated content as markdown string
        """
        self.logger.info(f"Generating {content_brief.content_type.value} with {structure_type} structure")

        # Validate brief
        is_valid, errors = content_brief.validate()
        if not is_valid:
            self.logger.warning(f"Content brief validation issues: {errors}")

        # Select structure
        if structure_type not in self.structures:
            structure_type = self._infer_structure(content_brief)

        structure = self.structures[structure_type]

        # Generate content
        sections = []

        # Title
        title = self._generate_title(content_brief)
        sections.append(f"# {title}\n")

        # Meta description (for SEO)
        if content_brief.seo_keywords:
            meta = self._generate_meta_description(content_brief)
            sections.append(f"*{meta}*\n")

        # Generate each section
        for i, section_template in enumerate(structure):
            section_content = self._generate_section(
                content_brief,
                section_template,
                i,
                structure_type
            )
            sections.append(section_content)

        # Join sections
        full_content = "\n\n".join(sections)

        # Validate word count
        word_count = len(full_content.split())
        min_words, max_words = content_brief.word_count_range

        if word_count < min_words:
            self.logger.warning(f"Content below minimum: {word_count} < {min_words}")
        elif word_count > max_words:
            self.logger.warning(f"Content exceeds maximum: {word_count} > {max_words}")
        else:
            self.logger.info(f"Content word count: {word_count} (target: {min_words}-{max_words})")

        return full_content

    def _infer_structure(self, brief: ContentBrief) -> str:
        """Infer best structure type from content brief."""
        # Check content type
        if brief.content_type == ContentType.WHITEPAPER:
            return "analysis"
        elif brief.content_type == ContentType.CASE_STUDY:
            return "narrative"

        # Check structure requirements for hints
        structure_text = " ".join(brief.structure_requirements).lower()

        if "step" in structure_text or "how to" in structure_text:
            return "how_to"
        elif "list" in structure_text or any(char.isdigit() for char in structure_text):
            return "listicle"
        elif "story" in structure_text or "narrative" in structure_text:
            return "narrative"
        elif "analysis" in structure_text or "findings" in structure_text:
            return "analysis"
        else:
            return "problem_solution"  # Default

    def _generate_title(self, brief: ContentBrief) -> str:
        """Generate an engaging, SEO-friendly title."""
        if not brief.key_messages:
            return "Untitled Article"

        base_message = brief.key_messages[0]

        # Apply tone-specific formatting
        if brief.tone == ToneType.CONVERSATIONAL:
            # Make it engaging and question-based
            if "?" not in base_message:
                if "how" in base_message.lower():
                    return base_message
                else:
                    return f"How to {base_message}"
            return base_message

        elif brief.tone == ToneType.PROFESSIONAL:
            # Make it authoritative
            if ":" not in base_message:
                return f"{base_message}: A Comprehensive Guide"
            return base_message

        elif brief.tone == ToneType.TECHNICAL:
            # Add technical framing
            return f"Technical Deep Dive: {base_message}"

        elif brief.tone == ToneType.PERSUASIVE:
            # Make it compelling
            return f"Why {base_message}"

        elif brief.tone == ToneType.EDUCATIONAL:
            # Make it learning-focused
            return f"Understanding {base_message}"

        return base_message

    def _generate_meta_description(self, brief: ContentBrief) -> str:
        """Generate SEO meta description."""
        # Combine key message with keywords
        desc_parts = []

        if brief.key_messages:
            # Use first message as base
            desc_parts.append(brief.key_messages[0])

        # Add target audience context
        desc_parts.append(f"For {brief.target_audience}.")

        # Add top keywords
        if brief.seo_keywords:
            keywords = ", ".join(brief.seo_keywords[:3])
            desc_parts.append(f"Topics: {keywords}")

        meta = " ".join(desc_parts)

        # Limit to 155 characters for SEO
        if len(meta) > 155:
            meta = meta[:152] + "..."

        return meta

    def _generate_section(
        self,
        brief: ContentBrief,
        section_template: str,
        section_index: int,
        structure_type: str
    ) -> str:
        """Generate a single content section."""
        parts = []

        # Section heading
        heading_level = "##" if section_index > 0 else "#"
        parts.append(f"{heading_level} {section_template}\n")

        # Generate content based on section type and available research
        if section_index == 0:
            # Introduction section
            content = self._generate_introduction(brief, structure_type)
        elif "conclusion" in section_template.lower():
            # Conclusion section
            content = self._generate_conclusion(brief)
        else:
            # Main content section
            content = self._generate_main_section(brief, section_template, section_index)

        parts.append(content)

        return "\n".join(parts)

    def _generate_introduction(self, brief: ContentBrief, structure_type: str) -> str:
        """Generate introduction section."""
        intro_parts = []

        # Hook - choose based on available research data
        hook = self._generate_hook(brief)
        intro_parts.append(hook)

        # Context/Problem statement
        if brief.key_messages:
            intro_parts.append(f"\n\n{brief.key_messages[0]}")

        # Preview what's covered
        if len(brief.key_messages) > 1:
            intro_parts.append(f"\n\nIn this article, we'll explore:")
            for message in brief.key_messages[1:4]:
                intro_parts.append(f"\n- {message}")

        # Target audience relevance
        intro_parts.append(f"\n\nWhether you're {brief.target_audience.lower()}, this guide will help you understand the key concepts and practical applications.")

        return "".join(intro_parts)

    def _generate_hook(self, brief: ContentBrief) -> str:
        """Generate an engaging opening hook."""
        # Try to use research data
        if brief.research_brief and brief.research_brief.sources:
            # Look for statistics first
            for source in brief.research_brief.sources:
                if source.key_facts:
                    for fact in source.key_facts:
                        # Check if it contains a statistic
                        if any(char in fact for char in ['%', 'million', 'billion', 'thousand']):
                            return fact

            # Fall back to first compelling fact
            if brief.research_brief.sources[0].key_facts:
                return brief.research_brief.sources[0].key_facts[0]

            # Use a quote
            if brief.research_brief.sources[0].key_quotes:
                return f'"{brief.research_brief.sources[0].key_quotes[0]}"'

        # Fallback: use key message as a question
        if brief.key_messages:
            message = brief.key_messages[0]
            if "?" not in message:
                return f"Have you ever wondered about {message.lower()}?"
            return message

        return "Let's dive into an important topic."

    def _generate_main_section(self, brief: ContentBrief, section_template: str, index: int) -> str:
        """Generate main content section."""
        section_parts = []

        # Use corresponding key message if available
        if index <= len(brief.key_messages):
            key_point = brief.key_messages[index - 1]
            section_parts.append(f"{key_point}\n")

        # Add research-based content
        if brief.research_brief and brief.research_brief.sources:
            # Distribute facts across sections
            source_index = (index - 1) % len(brief.research_brief.sources)
            source = brief.research_brief.sources[source_index]

            if source.key_facts:
                fact_index = (index - 1) % len(source.key_facts)
                section_parts.append(f"\n{source.key_facts[fact_index]}\n")

            # Add supporting details
            section_parts.append(f"\nFor {brief.target_audience}, this means:\n")
            section_parts.append(f"- Practical application in daily workflows\n")
            section_parts.append(f"- Improved efficiency and outcomes\n")
            section_parts.append(f"- Better understanding of key concepts\n")

            # Occasionally add a quote for credibility
            if index == 2 and source.key_quotes:
                section_parts.append(f'\n> "{source.key_quotes[0]}"')
                if source.author:
                    section_parts.append(f"\n> — {source.author}")
                section_parts.append("\n")

        else:
            # Generate placeholder content
            section_parts.append(f"\nThis section covers {section_template.lower()} in detail, providing actionable insights for {brief.target_audience}.\n")

        # Add SEO keywords naturally if applicable
        if brief.seo_keywords and index == 1:
            # Incorporate keywords in first main section
            keywords_used = brief.seo_keywords[:2]
            section_parts.append(f"\nKey concepts like {' and '.join(keywords_used)} play a crucial role here.\n")

        return "".join(section_parts)

    def _generate_conclusion(self, brief: ContentBrief) -> str:
        """Generate conclusion section."""
        conclusion_parts = []

        # Summarize main points
        conclusion_parts.append("We've covered several important aspects:\n")

        if brief.key_messages:
            for i, message in enumerate(brief.key_messages[:3], 1):
                conclusion_parts.append(f"\n{i}. {message}")

        # Key takeaway
        conclusion_parts.append("\n\nThe key takeaway is that ")
        if brief.key_messages:
            conclusion_parts.append(brief.key_messages[0].lower())
        else:
            conclusion_parts.append("understanding these concepts is crucial for success.")

        # Call to action based on content type
        if brief.content_type == ContentType.BLOG_POST:
            conclusion_parts.append("\n\n**What's your experience with this topic? Share your thoughts in the comments below!**")
        elif brief.content_type == ContentType.ARTICLE:
            conclusion_parts.append("\n\nFor further reading, explore the sources and research cited throughout this article.")
        elif brief.content_type == ContentType.WHITEPAPER:
            conclusion_parts.append("\n\n## Next Steps\n\nTo implement these recommendations:\n1. Review your current approach\n2. Identify areas for improvement\n3. Develop an action plan\n4. Monitor results and iterate")

        # Add relevant resources if research is available
        if brief.research_brief and brief.research_brief.sources:
            conclusion_parts.append("\n\n## References\n")
            for i, source in enumerate(brief.research_brief.sources[:5], 1):
                conclusion_parts.append(f"\n{i}. [{source.title}]({source.url})")

        return "".join(conclusion_parts)

    def get_word_count_estimate(self, brief: ContentBrief, structure_type: str = "problem_solution") -> int:
        """
        Estimate word count for given brief and structure.

        Args:
            brief: Content brief
            structure_type: Structure type

        Returns:
            Estimated word count
        """
        structure = self.structures.get(structure_type, self.structures["problem_solution"])

        # Rough estimate: 150-250 words per section
        num_sections = len(structure)
        avg_words_per_section = 200

        return num_sections * avg_words_per_section
