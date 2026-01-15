"""Workflow API schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ContentTypeEnum(str, Enum):
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


class ToneTypeEnum(str, Enum):
    """Voice and tone options."""
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"
    EDUCATIONAL = "educational"
    INSPIRATIONAL = "inspirational"


class PlatformEnum(str, Enum):
    """Social media platforms."""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"


class PriorityEnum(str, Enum):
    """Request priority levels."""
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class OutputFormatEnum(str, Enum):
    """Supported output formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    DOCX = "docx"
    PDF = "pdf"
    PPTX = "pptx"


class WorkflowJobStatus(str, Enum):
    """Workflow job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SocialSettings(BaseModel):
    """Settings specific to social content."""
    platform: PlatformEnum = PlatformEnum.LINKEDIN
    format_type: str = Field(
        default="single",
        pattern="^(single|thread|carousel)$",
        description="Post format type"
    )
    include_cta: bool = Field(default=True, description="Include call-to-action")
    emoji_density: str = Field(
        default="moderate",
        pattern="^(none|low|moderate|high)$",
        description="Emoji usage level"
    )


class WorkflowRequestSchema(BaseModel):
    """Complete workflow request from frontend wizard."""

    # Step 1: Basic Request
    request_text: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Natural language content request"
    )
    content_types: List[ContentTypeEnum] = Field(
        ...,
        min_length=1,
        description="Selected content types"
    )
    priority: PriorityEnum = Field(
        default=PriorityEnum.NORMAL,
        description="Request priority"
    )
    deadline: Optional[datetime] = Field(
        default=None,
        description="Optional deadline"
    )

    # Step 2: Audience & Tone
    target_audience: str = Field(
        default="General audience",
        description="Target audience description"
    )
    tone: ToneTypeEnum = Field(
        default=ToneTypeEnum.PROFESSIONAL,
        description="Content tone"
    )
    word_count_min: Optional[int] = Field(
        default=None,
        ge=50,
        le=10000,
        description="Minimum word count"
    )
    word_count_max: Optional[int] = Field(
        default=None,
        ge=100,
        le=20000,
        description="Maximum word count"
    )

    # Step 3: Social Settings (optional)
    social_settings: Optional[SocialSettings] = Field(
        default=None,
        description="Social media specific settings"
    )

    # Step 4: Brand Template
    brand_template: str = Field(
        default="professional",
        pattern="^(professional|modern|tech|creative|minimal)$",
        description="Brand template name"
    )

    # Step 5: Output Settings
    output_format: OutputFormatEnum = Field(
        default=OutputFormatEnum.HTML,
        description="Output file format"
    )
    include_metadata: bool = Field(
        default=True,
        description="Include metadata page"
    )
    page_numbers: bool = Field(
        default=True,
        description="Include page numbers"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "request_text": "Write a comprehensive article about cloud migration best practices",
                "content_types": ["article"],
                "priority": "normal",
                "target_audience": "IT executives and technical decision makers",
                "tone": "professional",
                "word_count_min": 800,
                "word_count_max": 1500,
                "brand_template": "tech",
                "output_format": "pdf"
            }
        }
    }


class WorkflowStepProgress(BaseModel):
    """Progress of a single workflow step."""
    step: str
    status: str
    timestamp: datetime
    message: Optional[str] = None


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status check."""
    job_id: str
    status: WorkflowJobStatus
    progress: float = Field(ge=0, le=100)
    current_step: Optional[str] = None
    steps_completed: List[WorkflowStepProgress] = Field(default_factory=list)
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None


class OutputFileInfo(BaseModel):
    """Information about a generated output file."""
    file_id: str
    filename: str
    format: str
    size_bytes: int
    download_url: str


class WorkflowResultResponse(BaseModel):
    """Complete workflow result."""
    job_id: str
    status: WorkflowJobStatus
    workflow_type: str
    success: bool
    outputs: List[OutputFileInfo] = Field(default_factory=list)
    content_preview: Optional[str] = Field(
        default=None,
        description="Preview of generated content (first 500 chars)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    start_time: datetime
    end_time: Optional[datetime] = None
    errors: List[str] = Field(default_factory=list)
