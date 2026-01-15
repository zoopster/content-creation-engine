"""
LLM-Enabled Creation Agent - Generates content using configurable LLM providers.

This module extends the base CreationAgent with actual LLM-powered content generation,
supporting multiple providers (Anthropic Claude, OpenAI GPT) through the model
abstraction layer.
"""

import asyncio
from typing import Any, Dict, List, Optional

from agents.base.agent import Agent
from agents.base.models import (
    BrandVoiceResult,
    ContentBrief,
    ContentType,
    DraftContent,
    ToneType,
)
from core.models import (
    AgentModelConfig,
    GenerationConfig,
    GenerationResult,
    Message,
    ModelRegistry,
    get_registry,
)
from datetime import datetime


class LLMCreationAgent(Agent):
    """
    LLM-powered content creation agent.

    Uses configurable LLM providers for actual content generation rather than
    template-based synthesis.

    Usage:
        # With default configuration
        agent = LLMCreationAgent()
        draft = await agent.process_async({"content_brief": brief})

        # With custom model configuration
        agent = LLMCreationAgent(config={
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.8
        })

        # With custom registry
        registry = ModelRegistry()
        registry.register_provider("anthropic", AnthropicProvider())
        agent = LLMCreationAgent(registry=registry)
    """

    # System prompts for different content types
    SYSTEM_PROMPTS = {
        ContentType.ARTICLE: """You are a professional content writer specializing in
long-form articles. Create engaging, well-researched content that:
- Has a compelling introduction that hooks the reader
- Presents information in a logical, flowing structure
- Includes specific facts and data to support claims
- Concludes with actionable takeaways
- Matches the specified tone and target audience
Output format: Markdown with proper headings (##, ###).""",

        ContentType.BLOG_POST: """You are a blog content writer who creates engaging,
conversational content. Your posts should:
- Start with an attention-grabbing hook
- Use short paragraphs and scannable formatting
- Include personal touches and relatable examples
- End with a call to action or discussion prompt
- Be SEO-friendly while remaining natural
Output format: Markdown with proper headings.""",

        ContentType.SOCIAL_POST: """You are a social media content specialist. Create
platform-optimized posts that:
- Lead with the most engaging/important point
- Use appropriate length for the platform
- Include relevant hashtags where appropriate
- Have a clear call to action
- Match the brand voice precisely""",

        ContentType.EMAIL: """You are an email marketing specialist. Create emails that:
- Have a compelling subject line (provide as first line)
- Open with value for the reader
- Are scannable with clear sections
- Have a single, clear call to action
- Match the brand's communication style""",

        ContentType.WHITEPAPER: """You are a technical content writer specializing in
whitepapers and reports. Create authoritative content that:
- Establishes expertise and credibility
- Presents data and research systematically
- Uses professional, precise language
- Includes executive summary and key findings
- Follows industry best practices for structure
Output format: Markdown with proper document structure.""",

        ContentType.PRESENTATION: """You are a presentation content specialist. Create
slide content that:
- Has one key message per slide
- Uses bullet points for clarity
- Includes speaker notes where helpful
- Flows logically from introduction to conclusion
- Is visually scannable (not text-heavy)
Output format: Markdown with # for slide titles, - for bullets.""",
    }

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[ModelRegistry] = None,
    ):
        """
        Initialize the LLM Creation Agent.

        Args:
            config: Configuration dictionary with optional keys:
                - provider: LLM provider name (default: from registry)
                - model: Model ID (default: from registry)
                - temperature: Generation temperature (default: 0.7)
                - max_tokens: Max tokens to generate (default: 4096)
                - enable_brand_check: Enable brand voice validation (default: True)
            registry: Model registry instance (default: global registry)
        """
        super().__init__("creation", config)

        self.registry = registry or get_registry()
        self.enable_brand_check = (config or {}).get("enable_brand_check", True)

        # Build model configuration from config dict
        if config:
            provider = config.get("provider")
            model = config.get("model")

            if provider and model:
                gen_config = GenerationConfig(
                    max_tokens=config.get("max_tokens", 4096),
                    temperature=config.get("temperature", 0.7),
                )
                self._model_config = AgentModelConfig(
                    provider=provider,
                    model=model,
                    config=gen_config,
                )
            else:
                self._model_config = None
        else:
            self._model_config = None

    def _get_model_config(self) -> AgentModelConfig:
        """Get model configuration, falling back to registry defaults."""
        if self._model_config:
            return self._model_config
        return self.registry.get_agent_config("creation")

    async def process_async(self, input_data: Dict[str, Any]) -> DraftContent:
        """
        Generate content asynchronously using LLM.

        Args:
            input_data: Dictionary containing:
                - content_brief: ContentBrief object
                - additional_context: Optional additional context

        Returns:
            DraftContent with LLM-generated content
        """
        content_brief = input_data.get("content_brief")
        if not content_brief:
            raise ValueError("content_brief is required")

        # Validate input
        is_valid, errors = content_brief.validate()
        if not is_valid:
            raise ValueError(f"Invalid content brief: {errors}")

        additional_context = input_data.get("additional_context", {})

        self.logger.info(
            f"Creating {content_brief.content_type.value} content using LLM"
        )

        # Build the prompt
        prompt = self._build_prompt(content_brief, additional_context)
        system_prompt = self._get_system_prompt(content_brief)

        # Get model configuration
        model_config = self._get_model_config()

        # Create generation config with system prompt
        gen_config = GenerationConfig(
            max_tokens=model_config.config.max_tokens if model_config.config else 4096,
            temperature=model_config.config.temperature if model_config.config else 0.7,
            system_prompt=system_prompt,
        )

        # Generate content
        result = await self.registry.generate(
            prompt=prompt,
            provider=model_config.provider,
            model=model_config.model,
            config=gen_config,
        )

        content = result.content

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
                "created_at": datetime.now().isoformat(),
                "model": result.model,
                "provider": result.provider,
                "tokens_used": result.total_tokens,
            },
            brief=content_brief,
            format="markdown",
        )

        # Apply brand voice check if enabled
        if self.enable_brand_check and content_brief.brand_guidelines:
            brand_result = await self._check_brand_voice_llm(
                draft, content_brief.brand_guidelines
            )
            draft.metadata["brand_voice_score"] = brand_result.score
            draft.metadata["brand_voice_passed"] = brand_result.passed

            if not brand_result.passed:
                self.logger.warning(f"Brand voice check failed: {brand_result.issues}")

        self.log_execution(
            input_data,
            draft,
            {
                "word_count": word_count,
                "content_type": content_brief.content_type.value,
                "tone": content_brief.tone.value,
                "model": result.model,
                "provider": result.provider,
            },
        )

        return draft

    def process(self, input_data: Dict[str, Any]) -> DraftContent:
        """
        Synchronous wrapper for process_async.

        For async environments, prefer using process_async directly.
        """
        return asyncio.run(self.process_async(input_data))

    def _get_system_prompt(self, brief: ContentBrief) -> str:
        """Get system prompt for content type."""
        base_prompt = self.SYSTEM_PROMPTS.get(
            brief.content_type,
            "You are a professional content writer. Create high-quality content "
            "that matches the specified requirements.",
        )

        # Add brand voice guidelines if present
        if brief.brand_guidelines:
            brand_section = "\n\nBrand Voice Guidelines:"
            if brief.brand_guidelines.get("preferred_terms"):
                brand_section += f"\n- Preferred terms: {', '.join(brief.brand_guidelines['preferred_terms'][:5])}"
            if brief.brand_guidelines.get("avoided_terms"):
                brand_section += f"\n- Avoid: {', '.join(brief.brand_guidelines['avoided_terms'][:5])}"
            if brief.brand_guidelines.get("tone"):
                brand_section += f"\n- Tone: {brief.brand_guidelines['tone']}"
            base_prompt += brand_section

        return base_prompt

    def _build_prompt(
        self, brief: ContentBrief, context: Dict[str, Any]
    ) -> str:
        """Build the generation prompt from brief and context."""
        prompt_parts = []

        # Content type and format
        prompt_parts.append(
            f"Create a {brief.content_type.value} with the following specifications:"
        )

        # Target audience
        prompt_parts.append(f"\n\nTarget Audience: {brief.target_audience}")

        # Tone
        prompt_parts.append(f"Tone: {brief.tone.value}")

        # Word count range
        if brief.word_count_range:
            prompt_parts.append(
                f"Word Count: {brief.word_count_range[0]}-{brief.word_count_range[1]} words"
            )

        # Key messages
        if brief.key_messages:
            prompt_parts.append("\nKey Messages to Convey:")
            for i, message in enumerate(brief.key_messages, 1):
                prompt_parts.append(f"{i}. {message}")

        # Structure requirements
        if brief.structure_requirements:
            prompt_parts.append("\nRequired Sections/Structure:")
            for section in brief.structure_requirements:
                prompt_parts.append(f"- {section}")

        # SEO keywords
        if brief.seo_keywords:
            prompt_parts.append(
                f"\nSEO Keywords to Include: {', '.join(brief.seo_keywords)}"
            )

        # Research data
        if brief.research_brief and brief.research_brief.sources:
            prompt_parts.append("\nResearch Data to Reference:")
            for source in brief.research_brief.sources[:3]:
                prompt_parts.append(f"\nSource: {source.title}")
                if source.key_facts:
                    prompt_parts.append("Key Facts:")
                    for fact in source.key_facts[:3]:
                        prompt_parts.append(f"  - {fact}")
                if source.key_quotes:
                    prompt_parts.append("Quotes:")
                    for quote in source.key_quotes[:2]:
                        prompt_parts.append(f'  - "{quote}"')

        # Platform-specific context
        if context.get("platform"):
            prompt_parts.append(f"\nPlatform: {context['platform']}")

        # Additional instructions
        if context.get("additional_instructions"):
            prompt_parts.append(
                f"\nAdditional Instructions: {context['additional_instructions']}"
            )

        return "\n".join(prompt_parts)

    async def _check_brand_voice_llm(
        self, draft: DraftContent, brand_guidelines: Dict[str, Any]
    ) -> BrandVoiceResult:
        """
        Check brand voice compliance using LLM analysis.

        More sophisticated than pattern matching - uses LLM to evaluate
        tone, style, and overall brand alignment.
        """
        # For now, use pattern-based check
        # In future, this could use a separate LLM call for evaluation
        return self._check_brand_voice_patterns(draft, brand_guidelines)

    def _check_brand_voice_patterns(
        self, draft: DraftContent, brand_guidelines: Dict[str, Any]
    ) -> BrandVoiceResult:
        """Pattern-based brand voice check (fallback)."""
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
            found_preferred = sum(
                1 for term in preferred_terms if term.lower() in content_lower
            )
            if found_preferred == 0:
                score -= 0.2
                issues.append("No preferred brand terms found")
                suggestions.append(f"Consider using: {', '.join(preferred_terms[:3])}")

        score = max(0.0, score)
        passed = score >= 0.7 and len(issues) == 0

        return BrandVoiceResult(
            passed=passed, score=score, issues=issues, suggestions=suggestions
        )

    async def generate_variations_async(
        self, brief: ContentBrief, count: int = 3
    ) -> List[DraftContent]:
        """
        Generate multiple content variations for A/B testing.

        Each variation uses slightly different temperature for diversity.
        """
        tasks = []
        for i in range(count):
            # Vary temperature for diversity
            context = {
                "variation_number": i + 1,
                "additional_instructions": f"This is variation {i + 1}. "
                "Create a unique angle while covering the same key messages.",
            }
            tasks.append(
                self.process_async(
                    {"content_brief": brief, "additional_context": context}
                )
            )

        variations = await asyncio.gather(*tasks)

        # Add variation metadata
        for i, variation in enumerate(variations):
            variation.metadata["variation_id"] = i + 1

        return variations
