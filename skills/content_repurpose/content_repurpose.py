"""
Content Repurpose Skill - Transforms content between formats using LLM.

This skill orchestrates LLM-powered content transformation following the
content transformation matrix:

Article → Social: Extract key points, adapt for platform
Article → Presentation: Restructure content into slides
Article → Email: Condense to newsletter/outreach format
Research → Article: Expand into full long-form piece
Research → Email: Summarize findings for email
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import asyncio
from typing import Any, Dict, List, Optional

from agents.base.agent import Skill
from agents.base.models import (
    DraftContent, ContentBrief, ContentType, ToneType,
    ResearchBrief
)
from core.models import (
    AgentModelConfig, GenerationConfig, Message, ModelRegistry, get_registry
)


# System prompts for each transformation type
_SYSTEM_PROMPTS = {
    "article_to_social": """You are a social media content specialist who transforms
long-form articles into engaging platform-specific posts. Your posts:
- Lead with the most important insight
- Are appropriately concise for the platform
- Include a clear call to action
- Use relevant hashtags
- Match the original content's key message""",

    "article_to_presentation": """You are a presentation designer who converts
articles into structured slide decks. For each slide:
- Use # for slide titles
- Use bullet points (- ) for key points (max 4-5 per slide)
- Keep each point to one line
- Preserve the logical flow of the original article
- Add [SPEAKER NOTE: ...] for elaboration points""",

    "article_to_email": """You are an email marketing specialist who transforms
articles into compelling newsletter emails. Create:
- A clear subject line (prefix with 'Subject: ')
- A personal, engaging opening
- Key insights formatted as scannable bullets
- A single, compelling call to action
- A professional sign-off""",

    "research_to_article": """You are a professional content writer who transforms
research briefs into full-length articles. Your articles:
- Have a compelling introduction that hooks the reader
- Present information in a logical, flowing structure
- Include specific facts and data from the research
- Conclude with actionable takeaways
Output format: Markdown with proper headings (##, ###).""",

    "research_to_email": """You are an email marketing specialist who transforms
research findings into insightful newsletter emails. Create:
- A subject line that highlights the key finding
- An executive summary of the most important insight
- 3-5 key findings formatted as scannable bullets
- A call to action (read more, discuss, apply)
- Professional closing""",
}

# Platform-specific guidance for social content
_PLATFORM_GUIDANCE = {
    "linkedin": "LinkedIn post (max 3000 chars). Professional tone. 3-5 hashtags. Line breaks for readability.",
    "twitter": "Tweet or thread (280 chars per tweet). Punchy and direct. 1-2 hashtags. Use 🧵 for threads.",
    "instagram": "Instagram caption (max 2200 chars). Visual and emotional language. 5-10 hashtags at end.",
    "facebook": "Facebook post (max 63,206 chars but keep it concise). Conversational. 2-3 hashtags.",
}


class ContentRepurposeSkill(Skill):
    """
    Repurpose content between formats using LLM-powered transformation.

    Supported Transformations:
    - Article/Blog/Whitepaper → Social posts (platform-aware)
    - Article/Blog/Whitepaper → Presentation (slide structure)
    - Article/Blog/Whitepaper → Email (newsletter/outreach)
    - Research → Article (full draft)
    - Research → Email (summary + key findings)
    """

    TRANSFORMATION_MAP = {
        (ContentType.ARTICLE, ContentType.SOCIAL_POST): "article_to_social",
        (ContentType.ARTICLE, ContentType.PRESENTATION): "article_to_presentation",
        (ContentType.ARTICLE, ContentType.EMAIL): "article_to_email",
        (ContentType.BLOG_POST, ContentType.SOCIAL_POST): "article_to_social",
        (ContentType.BLOG_POST, ContentType.PRESENTATION): "article_to_presentation",
        (ContentType.BLOG_POST, ContentType.EMAIL): "article_to_email",
        (ContentType.WHITEPAPER, ContentType.PRESENTATION): "article_to_presentation",
        (ContentType.WHITEPAPER, ContentType.EMAIL): "article_to_email",
        (ContentType.WHITEPAPER, ContentType.SOCIAL_POST): "article_to_social",
    }

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[ModelRegistry] = None,
    ):
        super().__init__("content-repurpose", config)
        self.registry = registry or get_registry()
        self._model_config: Optional[AgentModelConfig] = None
        if config:
            provider = config.get("provider")
            model = config.get("model")
            if provider and model:
                self._model_config = AgentModelConfig(
                    provider=provider,
                    model=model,
                    config=GenerationConfig(
                        max_tokens=config.get("max_tokens", 2048),
                        temperature=config.get("temperature", 0.7),
                    ),
                )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def execute(
        self,
        source_content: Any,
        target_format: ContentType,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Repurpose content synchronously.

        Args:
            source_content: DraftContent or ResearchBrief
            target_format: Target ContentType
            **kwargs:
                - platform: Target social platform (linkedin, twitter, etc.)
                - tone: Override tone
                - additional_context: Extra instructions for the LLM

        Returns:
            {"content": str, "success": bool, "metadata": dict}
        """
        return asyncio.run(self.execute_async(source_content, target_format, **kwargs))

    async def execute_async(
        self,
        source_content: Any,
        target_format: ContentType,
        **kwargs,
    ) -> Dict[str, Any]:
        """Async version of execute."""
        source_type = self._detect_source_type(source_content)
        self.logger.info(f"Repurposing {source_type.value} → {target_format.value}")

        # Determine transformation key
        transform_key = (source_type, target_format)
        transform_name = self.TRANSFORMATION_MAP.get(transform_key)

        if not transform_name:
            # Try research-based fallbacks
            if isinstance(source_content, ResearchBrief):
                if target_format == ContentType.ARTICLE:
                    transform_name = "research_to_article"
                elif target_format == ContentType.EMAIL:
                    transform_name = "research_to_email"

        if not transform_name:
            supported = [f"{s.value}→{t.value}" for s, t in self.TRANSFORMATION_MAP.keys()]
            raise ValueError(
                f"Transformation {source_type.value}→{target_format.value} not supported. "
                f"Supported: {', '.join(supported)}"
            )

        # Build source text
        source_text = self._extract_source_text(source_content)

        # Try LLM transformation, fall back to rule-based
        try:
            result_text = await self._llm_transform(
                transform_name, source_text, source_type, target_format, **kwargs
            )
        except Exception as e:
            self.logger.warning(f"LLM transformation failed, using fallback: {e}")
            result_text = self._fallback_transform(
                transform_name, source_content, source_text, **kwargs
            )

        return {
            "content": result_text,
            "success": True,
            "metadata": {
                "source_type": source_type.value,
                "target_type": target_format.value,
                "transformation": transform_name,
                "platform": kwargs.get("platform"),
            },
        }

    # ------------------------------------------------------------------
    # LLM transformation
    # ------------------------------------------------------------------

    async def _llm_transform(
        self,
        transform_name: str,
        source_text: str,
        source_type: ContentType,
        target_format: ContentType,
        **kwargs,
    ) -> str:
        """Run LLM-powered transformation."""
        model_config = self._get_model_config()
        system_prompt = _SYSTEM_PROMPTS.get(transform_name, "You are a content transformation specialist.")

        platform = kwargs.get("platform", "linkedin")
        platform_guide = _PLATFORM_GUIDANCE.get(platform, "")
        additional_context = kwargs.get("additional_context", "")

        user_prompt = self._build_user_prompt(
            transform_name, source_text, target_format, platform, platform_guide, additional_context
        )

        gen_config = GenerationConfig(
            max_tokens=model_config.config.max_tokens if model_config.config else 2048,
            temperature=model_config.config.temperature if model_config.config else 0.7,
            system_prompt=system_prompt,
        )

        messages = [Message(role="user", content=user_prompt)]
        result = await self.registry.generate_chat(
            messages=messages,
            provider=model_config.provider,
            model=model_config.model,
            config=gen_config,
        )

        return result.content.strip()

    def _build_user_prompt(
        self,
        transform_name: str,
        source_text: str,
        target_format: ContentType,
        platform: str,
        platform_guide: str,
        additional_context: str,
    ) -> str:
        """Build LLM prompt for the given transformation."""
        base_instructions = {
            "article_to_social": (
                f"Transform this article into a {platform} post.\n"
                f"Platform requirements: {platform_guide}\n"
            ),
            "article_to_presentation": (
                "Transform this article into a slide deck structure.\n"
                "Create 8-12 slides. Use # for titles, - for bullets.\n"
                "Add [SPEAKER NOTE: ...] below each slide for presenter guidance.\n"
            ),
            "article_to_email": (
                "Transform this article into a compelling email.\n"
                "Start with 'Subject: [subject line]' on its own line.\n"
                "Then write the email body.\n"
            ),
            "research_to_article": (
                "Transform this research brief into a complete, well-structured article.\n"
                "Write at least 800 words in Markdown format.\n"
            ),
            "research_to_email": (
                "Transform this research into a concise email newsletter.\n"
                "Start with 'Subject: [subject line]' on its own line.\n"
            ),
        }

        instruction = base_instructions.get(transform_name, "Transform this content:\n")
        if additional_context:
            instruction += f"\nAdditional instructions: {additional_context}\n"

        return f"{instruction}\n---\nSOURCE CONTENT:\n{source_text}"

    def _get_model_config(self) -> Optional[AgentModelConfig]:
        """Get model config, falling back to registry defaults."""
        if self._model_config:
            return self._model_config
        try:
            return self.registry.get_agent_config("creation")
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Rule-based fallbacks
    # ------------------------------------------------------------------

    def _fallback_transform(
        self,
        transform_name: str,
        source_content: Any,
        source_text: str,
        **kwargs,
    ) -> str:
        """Simple rule-based fallback when LLM is unavailable."""
        if transform_name == "article_to_social":
            return self._simple_social_extract(source_content, source_text, **kwargs)
        elif transform_name == "article_to_presentation":
            return self._simple_presentation(source_text)
        elif transform_name in ("article_to_email", "research_to_email"):
            return self._simple_email(source_text)
        elif transform_name == "research_to_article":
            return source_text  # Research text is close enough
        return source_text

    def _simple_social_extract(self, source_content: Any, source_text: str, **kwargs) -> str:
        platform = kwargs.get("platform", "linkedin")
        title = self._extract_title(source_text)
        key_points = self._extract_key_points(source_text, max_points=3)
        parts = [title, ""]
        parts.extend([f"• {point}" for point in key_points])
        parts.append("")
        if platform == "twitter":
            parts.append("#content #insights")
        else:
            parts.append("#content #insights #leadership")
        return '\n'.join(parts)

    def _simple_presentation(self, source_text: str) -> str:
        lines = source_text.split('\n')
        result = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('# ') or stripped.startswith('## '):
                result.append(stripped)
            elif stripped and not stripped.startswith('#'):
                sentences = stripped.split('. ')
                if sentences:
                    result.append(f"- {sentences[0]}")
        return '\n'.join(result)

    def _simple_email(self, source_text: str) -> str:
        title = self._extract_title(source_text)
        key_points = self._extract_key_points(source_text, max_points=5)
        parts = [f"Subject: {title}", "", "Hi there,", "",
                 "I wanted to share some key insights:", ""]
        parts.extend([f"• {point}" for point in key_points])
        parts += ["", "Let me know if you'd like to discuss further!", "", "Best regards"]
        return '\n'.join(parts)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _detect_source_type(self, content: Any) -> ContentType:
        if isinstance(content, DraftContent):
            return content.content_type
        elif isinstance(content, ResearchBrief):
            return ContentType.ARTICLE  # Research → treat as article source
        elif hasattr(content, 'content_type'):
            return content.content_type
        return ContentType.ARTICLE

    def _extract_source_text(self, content: Any) -> str:
        if isinstance(content, DraftContent):
            return content.content
        elif isinstance(content, ResearchBrief):
            parts = []
            if hasattr(content, 'topic'):
                parts.append(f"# {content.topic}")
            if hasattr(content, 'summary') and content.summary:
                parts.append(content.summary)
            if hasattr(content, 'key_findings') and content.key_findings:
                parts.append("\n## Key Findings")
                for finding in content.key_findings:
                    parts.append(f"- {finding}")
            return '\n\n'.join(parts)
        elif hasattr(content, 'content'):
            return content.content
        return str(content)

    def _extract_key_points(self, content: str, max_points: int = 3) -> List[str]:
        points = []
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            if stripped and len(stripped) > 50:
                sentences = stripped.split('. ')
                if sentences[0]:
                    points.append(sentences[0])
            if len(points) >= max_points:
                break
        return points[:max_points]

    def _extract_title(self, content: str) -> str:
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('# '):
                return stripped[2:].strip()
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                return stripped[:60] + ('...' if len(stripped) > 60 else '')
        return "Content Summary"

    def validate_requirements(self) -> tuple[bool, list[str]]:
        return True, []
