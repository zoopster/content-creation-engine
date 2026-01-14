"""
Data models for agent handoffs in the Content Creation Engine.

These models define the structure of data passed between agents
and provide validation for quality gates.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ContentType(Enum):
    """Supported content types."""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    PRESENTATION = "presentation"
    EMAIL = "email"
    NEWSLETTER = "newsletter"
    VIDEO_SCRIPT = "video_script"
    WHITEPAPER = "whitepaper"
    CASE_STUDY = "case_study"


class ToneType(Enum):
    """Voice and tone options."""
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"
    EDUCATIONAL = "educational"
    INSPIRATIONAL = "inspirational"


class Platform(Enum):
    """Social media platforms."""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"


@dataclass
class Source:
    """A research source with credibility metadata."""
    url: str
    title: str
    author: Optional[str] = None
    publication_date: Optional[str] = None
    credibility_score: float = 0.0
    key_quotes: List[str] = field(default_factory=list)
    key_facts: List[str] = field(default_factory=list)


@dataclass
class ResearchBrief:
    """Output from Research Agent, input to Creation Agent."""
    topic: str
    sources: List[Source]
    key_findings: List[str]
    data_points: Dict[str, Any]
    research_gaps: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def validate(self) -> tuple[bool, List[str]]:
        """Validate research completeness (Quality Gate 1)."""
        errors = []

        if not self.topic:
            errors.append("Topic is required")

        if len(self.sources) < 2:
            errors.append("At least 2 sources required")

        if not self.key_findings:
            errors.append("Key findings cannot be empty")

        # Check source credibility
        high_quality_sources = [s for s in self.sources if s.credibility_score >= 0.7]
        if len(high_quality_sources) < 1:
            errors.append("At least 1 high-quality source (credibility >= 0.7) required")

        return len(errors) == 0, errors


@dataclass
class ContentBrief:
    """Output from content-brief skill, guides content creation."""
    content_type: ContentType
    target_audience: str
    key_messages: List[str]
    tone: ToneType
    structure_requirements: List[str]
    word_count_range: tuple[int, int]
    seo_keywords: List[str] = field(default_factory=list)
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    research_brief: Optional[ResearchBrief] = None

    def validate(self) -> tuple[bool, List[str]]:
        """Validate brief alignment (Quality Gate 2)."""
        errors = []

        if not self.target_audience:
            errors.append("Target audience must be defined")

        if len(self.key_messages) < 1:
            errors.append("At least 1 key message required")

        if not self.structure_requirements:
            errors.append("Structure requirements must be defined")

        min_words, max_words = self.word_count_range
        if min_words <= 0 or max_words < min_words:
            errors.append("Invalid word count range")

        return len(errors) == 0, errors


@dataclass
class DraftContent:
    """Output from Creation Agent, input to Production Agent."""
    content: str
    content_type: ContentType
    word_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    brief: Optional[ContentBrief] = None
    format: str = "markdown"

    def validate(self) -> tuple[bool, List[str]]:
        """Validate content completeness."""
        errors = []

        if not self.content or len(self.content.strip()) < 100:
            errors.append("Content is too short or empty")

        if self.word_count <= 0:
            errors.append("Invalid word count")

        if self.brief:
            min_words, max_words = self.brief.word_count_range
            if not (min_words <= self.word_count <= max_words):
                errors.append(f"Word count {self.word_count} outside target range {min_words}-{max_words}")

        return len(errors) == 0, errors


@dataclass
class BrandVoiceResult:
    """Output from brand-voice validation."""
    passed: bool
    score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def validate(self) -> tuple[bool, List[str]]:
        """Validate brand consistency (Quality Gate 3)."""
        errors = []

        if self.score < 0.7:
            errors.append(f"Brand voice score {self.score} below threshold 0.7")

        if not self.passed:
            errors.append("Brand voice validation failed")

        return len(errors) == 0, errors


@dataclass
class ProductionOutput:
    """Final output from Production Agent."""
    file_path: str
    file_format: str
    content_type: ContentType
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def validate(self) -> tuple[bool, List[str]]:
        """Validate format compliance (Quality Gate 4)."""
        errors = []

        if not self.file_path:
            errors.append("File path is required")

        if not self.file_format:
            errors.append("File format is required")

        return len(errors) == 0, errors


@dataclass
class WorkflowRequest:
    """User request to create content."""
    request_text: str
    content_types: List[ContentType]
    priority: str = "normal"
    deadline: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)
