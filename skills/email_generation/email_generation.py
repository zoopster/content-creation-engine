"""
Email Generation Skill - Generates email content using LLM.

Supports multiple email types:
- Newsletter: Long-form content digest
- Outreach: Cold/warm outreach to prospects
- Nurture: Lead nurture sequence emails
- Announcement: Product/feature announcements
- Summary: Content summary emails
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agents.base.agent import Skill
from agents.base.models import ContentBrief, DraftContent, ContentType, ToneType
from core.models import (
    AgentModelConfig, GenerationConfig, Message, ModelRegistry, get_registry
)


@dataclass
class EmailContent:
    """Structured email content."""
    subject: str
    preview_text: str
    body: str
    email_type: str
    word_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.word_count = len(self.body.split())

    def to_full_text(self) -> str:
        """Return complete email as plain text."""
        return f"Subject: {self.subject}\nPreview: {self.preview_text}\n\n{self.body}"


# Email type system prompts
_EMAIL_SYSTEM_PROMPTS = {
    "newsletter": """You are an email newsletter writer who creates engaging content digests.
Your newsletters:
- Have a compelling subject line (6-10 words)
- Open with a brief personal note or teaser
- Present 3-5 key insights or stories with clear headers
- Use short paragraphs (2-3 sentences max)
- End with a single clear call to action
- Feel like a message from a trusted expert, not a marketer

Format your response as:
SUBJECT: [subject line]
PREVIEW: [one-line preview text, 90 chars max]
BODY:
[email body in plain text with light markdown]""",

    "outreach": """You are a sales and business development email specialist.
Your outreach emails:
- Are concise (under 150 words for the body)
- Lead with value for the recipient, not about the sender
- Reference something specific and relevant to the recipient
- Have one clear, low-commitment ask
- Feel human and non-templated
- Never start with "I hope this email finds you well"

Format your response as:
SUBJECT: [subject line]
PREVIEW: [one-line preview text, 90 chars max]
BODY:
[email body]""",

    "nurture": """You are an email marketing specialist who creates lead nurture sequences.
Your nurture emails:
- Build on a clear value proposition
- Educate rather than sell
- Include one key insight or case study
- Move the reader one step forward in their journey
- Have a conversational, helpful tone

Format your response as:
SUBJECT: [subject line]
PREVIEW: [one-line preview text, 90 chars max]
BODY:
[email body]""",

    "announcement": """You are a marketing communications specialist who writes product announcements.
Your announcement emails:
- Lead with the key benefit, not the feature
- Explain the "why this matters" clearly
- Use a logical structure: hook → context → announcement → benefit → CTA
- Are enthusiastic but not hyperbolic
- Include a clear, singular call to action

Format your response as:
SUBJECT: [subject line]
PREVIEW: [one-line preview text, 90 chars max]
BODY:
[email body]""",

    "summary": """You are a content curator who creates email summaries of articles and research.
Your summary emails:
- Capture the 3-5 most important points
- Preserve the key data or insights
- Add brief context for why each point matters
- Link to further reading if relevant
- Are scannable with clear structure

Format your response as:
SUBJECT: [subject line]
PREVIEW: [one-line preview text, 90 chars max]
BODY:
[email body]""",
}


class EmailGenerationSkill(Skill):
    """
    LLM-powered email generation skill.

    Generates structured, high-quality email content across multiple
    email types (newsletter, outreach, nurture, announcement, summary).

    Usage:
        skill = EmailGenerationSkill()

        # From a content brief
        email = await skill.execute_async(
            content_brief=brief,
            email_type="newsletter"
        )

        # From a topic directly
        email = await skill.execute_async(
            topic="The impact of AI on content marketing",
            email_type="outreach",
            recipient_context="marketing directors at SaaS companies"
        )
    """

    EMAIL_TYPES = list(_EMAIL_SYSTEM_PROMPTS.keys())

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[ModelRegistry] = None,
    ):
        super().__init__("email-generation", config)
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

    def execute(
        self,
        content_brief: Optional[ContentBrief] = None,
        topic: Optional[str] = None,
        email_type: str = "newsletter",
        **kwargs,
    ) -> EmailContent:
        """
        Generate email content synchronously.

        Args:
            content_brief: ContentBrief to base the email on (optional)
            topic: Direct topic string (used if no content_brief)
            email_type: One of newsletter, outreach, nurture, announcement, summary
            **kwargs:
                - recipient_context: Description of target recipient
                - tone: ToneType override
                - key_points: List of points to include
                - sender_name: Sender name for sign-off
                - company_name: Company name

        Returns:
            EmailContent with subject, preview, and body
        """
        return asyncio.run(self.execute_async(content_brief, topic, email_type, **kwargs))

    async def execute_async(
        self,
        content_brief: Optional[ContentBrief] = None,
        topic: Optional[str] = None,
        email_type: str = "newsletter",
        **kwargs,
    ) -> EmailContent:
        """Async version of execute."""
        if email_type not in self.EMAIL_TYPES:
            raise ValueError(f"email_type must be one of {self.EMAIL_TYPES}, got '{email_type}'")

        if not content_brief and not topic:
            raise ValueError("Either content_brief or topic is required")

        self.logger.info(f"Generating {email_type} email")

        prompt = self._build_prompt(content_brief, topic, email_type, **kwargs)
        system_prompt = _EMAIL_SYSTEM_PROMPTS[email_type]

        model_config = self._get_model_config()
        gen_config = GenerationConfig(
            max_tokens=model_config.config.max_tokens if (model_config and model_config.config) else 2048,
            temperature=model_config.config.temperature if (model_config and model_config.config) else 0.7,
            system_prompt=system_prompt,
        )

        messages = [Message(role="user", content=prompt)]

        try:
            result = await self.registry.generate_chat(
                messages=messages,
                provider=model_config.provider,
                model=model_config.model,
                config=gen_config,
            )
            return self._parse_llm_output(result.content, email_type)
        except Exception as e:
            self.logger.warning(f"LLM generation failed, using fallback: {e}")
            return self._fallback_email(content_brief, topic, email_type, **kwargs)

    def _build_prompt(
        self,
        content_brief: Optional[ContentBrief],
        topic: Optional[str],
        email_type: str,
        **kwargs,
    ) -> str:
        """Build LLM prompt for email generation."""
        parts = [f"Generate a {email_type} email"]

        recipient_context = kwargs.get("recipient_context")
        if recipient_context:
            parts.append(f"for: {recipient_context}")

        parts.append("\n")

        if content_brief:
            parts.append(f"TOPIC: {getattr(content_brief, 'topic', 'Content')}")
            parts.append(f"TARGET AUDIENCE: {content_brief.target_audience}")
            parts.append(f"TONE: {content_brief.tone.value if hasattr(content_brief.tone, 'value') else content_brief.tone}")

            if content_brief.key_messages:
                parts.append("\nKEY MESSAGES TO INCLUDE:")
                for msg in content_brief.key_messages[:5]:
                    parts.append(f"- {msg}")

            if content_brief.seo_keywords:
                parts.append(f"\nRELEVANT TERMS: {', '.join(content_brief.seo_keywords[:5])}")
        else:
            parts.append(f"TOPIC: {topic}")

        key_points = kwargs.get("key_points", [])
        if key_points:
            parts.append("\nMUST INCLUDE THESE POINTS:")
            for point in key_points:
                parts.append(f"- {point}")

        sender_name = kwargs.get("sender_name", "")
        company_name = kwargs.get("company_name", "")
        if sender_name or company_name:
            sign_off = f"{sender_name}" + (f", {company_name}" if company_name else "")
            parts.append(f"\nSIGN OFF AS: {sign_off}")

        return '\n'.join(parts)

    def _parse_llm_output(self, raw: str, email_type: str) -> EmailContent:
        """Parse structured LLM output into EmailContent."""
        subject = ""
        preview = ""
        body_lines = []
        in_body = False

        for line in raw.strip().split('\n'):
            if line.upper().startswith("SUBJECT:"):
                subject = line[8:].strip().lstrip(':').strip()
            elif line.upper().startswith("PREVIEW:"):
                preview = line[8:].strip().lstrip(':').strip()
            elif line.strip().upper() == "BODY:":
                in_body = True
            elif in_body:
                body_lines.append(line)

        # Fallback: if parsing failed, treat whole response as body
        if not subject:
            subject = f"Your {email_type.title()} Update"
        if not preview:
            preview = raw[:90].replace('\n', ' ')
        if not body_lines:
            body_lines = raw.split('\n')

        body = '\n'.join(body_lines).strip()

        return EmailContent(
            subject=subject,
            preview_text=preview[:90],
            body=body,
            email_type=email_type,
            metadata={"generated_by": "llm"},
        )

    def _fallback_email(
        self,
        content_brief: Optional[ContentBrief],
        topic: Optional[str],
        email_type: str,
        **kwargs,
    ) -> EmailContent:
        """Simple fallback when LLM is unavailable."""
        title = topic or (getattr(content_brief, 'topic', None)) or "Update"
        subject = f"[{email_type.title()}] {title[:50]}"
        preview = f"Key insights on {title}"

        audience = "there"
        if content_brief:
            audience = content_brief.target_audience or "there"

        body = f"Hi {audience},\n\nI wanted to share some thoughts on {title}.\n\n"

        if content_brief and content_brief.key_messages:
            body += "Key points:\n"
            for msg in content_brief.key_messages[:3]:
                body += f"• {msg}\n"

        body += "\nBest regards"

        return EmailContent(
            subject=subject,
            preview_text=preview[:90],
            body=body,
            email_type=email_type,
            metadata={"generated_by": "fallback"},
        )

    def _get_model_config(self) -> Optional[AgentModelConfig]:
        if self._model_config:
            return self._model_config
        try:
            return self.registry.get_agent_config("creation")
        except Exception:
            return None

    def validate_requirements(self) -> tuple[bool, list[str]]:
        return True, []
