# Creation Agent

## Purpose

The Creation Agent generates written content across formats using research inputs and brand guidelines. It transforms structured content briefs into polished draft content tailored to specific audiences, platforms, and content types.

## Responsibilities

- **Content Generation**: Create written content matching format specifications
- **Brand Voice Application**: Apply consistent brand voice and style guidelines
- **Audience Targeting**: Structure content for specific target audiences
- **Multi-Format Support**: Generate articles, social posts, emails, scripts, presentations
- **Quality Validation**: Ensure content meets word count and quality requirements
- **A/B Testing**: Generate content variations for testing

## Architecture

```
Creation Agent
├── Input: ContentBrief + additional context
├── Process:
│   ├── 1. Route to appropriate writing skill
│   ├── 2. Generate content (skill-specific)
│   ├── 3. Apply brand voice guidelines
│   ├── 4. Validate word count and quality
│   └── 5. Package as DraftContent
└── Output: DraftContent (markdown)
```

## Skills Used

### Primary Skills

| Skill | Function | Content Types | Status |
|-------|----------|---------------|--------|
| `long-form-writing` | Articles, blogs, whitepapers | ARTICLE, BLOG_POST, WHITEPAPER, CASE_STUDY | ✅ Implemented |
| `social-content` | Platform-optimized social posts | SOCIAL_POST | ✅ Implemented |
| `email-writing` | Newsletters, campaigns | EMAIL, NEWSLETTER | ✅ Integrated |
| `script-writing` | Video scripts, podcast outlines | VIDEO_SCRIPT | ✅ Integrated |

### Future Skills

| Skill | Function | Status |
|-------|----------|--------|
| `short-form` | Headlines, summaries, descriptions | 🔲 Planned (Phase 3) |
| `copy-writing` | Marketing copy, landing pages | 🔲 Planned (Phase 4) |

## Configuration

```python
config = {
    "model": "claude-sonnet-4",        # AI model to use
    "enable_brand_check": True         # Enable brand voice validation
}

agent = CreationAgent(config)
```

## Usage

### Basic Usage

```python
from agents.creation.creation import CreationAgent
from agents.base.models import ContentBrief, ContentType, ToneType

# Initialize agent
agent = CreationAgent()

# Create content brief (usually from content-brief skill)
brief = ContentBrief(
    content_type=ContentType.ARTICLE,
    target_audience="Technical professionals and developers",
    key_messages=[
        "AI agents are transforming content creation",
        "Multi-agent systems improve efficiency by 45%",
        "Specialized agents handle different workflow stages"
    ],
    tone=ToneType.TECHNICAL,
    structure_requirements=[
        "Engaging hook/intro",
        "Problem statement",
        "Main content (3 sections)",
        "Conclusion with takeaways"
    ],
    word_count_range=(800, 1500),
    seo_keywords=["AI agents", "content automation", "workflow"]
)

# Generate content
input_data = {"content_brief": brief}
draft = agent.process(input_data)

# Access results
print(f"Content generated: {draft.word_count} words")
print(f"Content type: {draft.content_type.value}")
print(f"Format: {draft.format}")
print(draft.content)
```

### Complete Workflow (Research → Brief → Creation)

```python
from agents.research.research import ResearchAgent
from skills.content_brief.content_brief import ContentBriefSkill
from agents.creation.creation import CreationAgent
from agents.base.models import ContentType

# Step 1: Research
research_agent = ResearchAgent()
research_brief = research_agent.process({
    "topic": "AI-powered content automation",
    "requirements": {"recent_only": True}
})

# Step 2: Create content brief
brief_skill = ContentBriefSkill()
content_brief = brief_skill.execute(
    research_brief=research_brief,
    content_type=ContentType.ARTICLE,
    target_audience="Marketing professionals"
)

# Step 3: Generate content
creation_agent = CreationAgent()
draft = creation_agent.process({"content_brief": content_brief})

print(f"✓ Generated {draft.word_count}-word article")
print(f"  Brand voice score: {draft.metadata.get('brand_voice_score', 'N/A')}")
```

### Social Media Content

```python
from agents.creation.creation import CreationAgent

agent = CreationAgent()

# Prepare brief for social content
input_data = {
    "content_brief": social_brief,  # ContentBrief with SOCIAL_POST type
    "additional_context": {
        "platform": "linkedin"  # or "twitter", "instagram", "facebook"
    }
}

# Generate platform-optimized post
draft = agent.process(input_data)

print(f"LinkedIn post ({len(draft.content)} chars):")
print(draft.content)
```

### Generate Multiple Variations

```python
agent = CreationAgent()

# Generate 3 variations for A/B testing
variations = agent.generate_variations(content_brief, count=3)

for i, variation in enumerate(variations, 1):
    print(f"\nVariation {i}:")
    print(f"  Word count: {variation.word_count}")
    print(f"  First 100 chars: {variation.content[:100]}...")
```

## Content Types

### Supported Content Types

| Type | Description | Word Count Range | Structure |
|------|-------------|------------------|-----------|
| ARTICLE | Long-form articles | 800-1500 | Problem-solution, How-to, Analysis |
| BLOG_POST | Blog posts | 600-1200 | Conversational, Listicle |
| WHITEPAPER | Technical whitepapers | 2000-5000 | Executive summary, Analysis, Recommendations |
| CASE_STUDY | Customer case studies | 1000-2000 | Narrative, Results-focused |
| SOCIAL_POST | Social media posts | 50-3000* | Platform-specific |
| EMAIL | Email content | 100-400 | Subject, Body, CTA |
| NEWSLETTER | Newsletter content | 300-800 | Multi-section, Links |
| VIDEO_SCRIPT | Video scripts | 500-1000 | Scene-based, Dialogue |
| PRESENTATION | Presentation content | 500-1000 | Slide-based |

*Social post length varies by platform

## Input Format

```python
{
    "content_brief": ContentBrief,           # Required: Content brief object
    "additional_context": {                  # Optional: Additional context
        "platform": str,                     # For social: platform name
        "variation_number": int,             # For variations
        "custom_instructions": str           # Any special instructions
    },
    "variations": int                        # Number of variations (default: 1)
}
```

## Output Format

Returns a `DraftContent` object:

```python
@dataclass
class DraftContent:
    content: str                             # Generated content (markdown)
    content_type: ContentType                # Type of content
    word_count: int                          # Word count
    metadata: Dict[str, Any]                 # Additional metadata
    brief: Optional[ContentBrief]            # Source brief
    format: str                              # Content format (default: "markdown")
```

### Metadata Fields

```python
{
    "tone": str,                             # Content tone
    "target_audience": str,                  # Target audience
    "key_messages": List[str],               # Key messages covered
    "seo_keywords": List[str],               # SEO keywords used
    "created_at": str,                       # ISO timestamp
    "brand_voice_score": float,              # Brand voice compliance (0-1)
    "brand_voice_passed": bool,              # Brand check result
    "variation_id": int                      # Variation number (if applicable)
}
```

## Writing Skills

### Long-Form Writing

Generates articles, blog posts, whitepapers, and case studies.

**Structures Available:**
- `problem_solution`: Problem analysis → solution framework
- `how_to`: Step-by-step guide with tips
- `listicle`: Numbered list format
- `narrative`: Storytelling approach
- `analysis`: Data-driven analysis with recommendations

**Features:**
- SEO-optimized titles and meta descriptions
- Tone-aware writing (professional, conversational, technical)
- Research integration (facts, quotes, statistics)
- Proper markdown formatting
- Reference citations

**Example:**
```python
from skills.long_form_writing.long_form_writing import LongFormWritingSkill

skill = LongFormWritingSkill()

content = skill.execute(
    content_brief=brief,
    structure_type="how_to"  # or "problem_solution", "listicle", etc.
)
```

### Social Content

Generates platform-optimized social media content.

**Platforms Supported:**
- **LinkedIn** (3,000 chars max, professional tone, 3-5 hashtags)
- **Twitter/X** (280 chars max, conversational, 1-2 hashtags, thread support)
- **Instagram** (2,200 chars max, casual, 5-15 hashtags, carousel support)
- **Facebook** (variable, conversational, 1-3 hashtags)

**Features:**
- Platform-specific constraints and formatting
- Engagement-optimized hooks
- Hashtag strategies
- Call-to-action optimization
- Thread/carousel support

**Example:**
```python
from skills.social_content.social_content import SocialContentSkill

skill = SocialContentSkill()

# Single post
post = skill.execute(
    content_brief=brief,
    platform="linkedin",
    format_type="single"
)

# Twitter thread
thread = skill.execute(
    content_brief=brief,
    platform="twitter",
    format_type="thread"
)

# Instagram carousel
carousel = skill.execute(
    content_brief=brief,
    platform="instagram",
    format_type="carousel"
)
```

## Brand Voice Integration

The Creation Agent integrates with the brand-voice skill to ensure content consistency.

### Brand Voice Checking

```python
# Enable brand voice checking (default: True)
agent = CreationAgent(config={"enable_brand_check": True})

# Provide brand guidelines in content brief
brand_guidelines = {
    "preferred_terms": ["AI agents", "automation", "workflow"],
    "avoided_terms": ["artificial intelligence robots", "bots"],
    "tone": "professional"
}

content_brief.brand_guidelines = brand_guidelines

# Generate content with brand checking
draft = agent.process({"content_brief": content_brief})

# Check results
print(f"Brand voice score: {draft.metadata['brand_voice_score']}")
print(f"Passed: {draft.metadata['brand_voice_passed']}")
```

### Brand Voice Scoring

| Score Range | Interpretation | Action |
|-------------|----------------|--------|
| 0.9 - 1.0 | Excellent compliance | Accept as-is |
| 0.7 - 0.9 | Good compliance | Minor adjustments |
| 0.5 - 0.7 | Moderate issues | Review and revise |
| < 0.5 | Significant issues | Major revision needed |

## Quality Gates

### Quality Gate 3: Brand Consistency

Validates content against brand voice guidelines:

```python
def validate_brand_voice(draft: DraftContent) -> BrandVoiceResult:
    """
    Checks:
    - No avoided terms present
    - Preferred terms included
    - Tone matches requirements
    - Score >= 0.7 for passing
    """
```

### Content Validation

```python
draft = agent.process(input_data)

# Validate against brief requirements
is_valid, errors = draft.validate()

if not is_valid:
    print(f"Validation issues: {errors}")
    # Common issues:
    # - Word count outside target range
    # - Content too short (<100 chars)
    # - Invalid word count
```

## Integration with Workflow

### Workflow Position

```
User Request
     ↓
Orchestrator → Research Agent → content-brief skill
                                        ↓
                              → CREATION AGENT → Production Agent
                                        ↓
                                  DraftContent (Markdown)
```

### Handoff from Content Brief

```python
# Content brief skill output
content_brief = brief_skill.execute(
    research_brief=research_brief,
    content_type=ContentType.ARTICLE
)

# Pass to Creation Agent
draft = creation_agent.process({"content_brief": content_brief})

# Validate and pass to Production Agent
if draft.metadata.get("brand_voice_passed", True):
    # Continue to production
    production_input = {"draft_content": draft}
else:
    # Handle brand voice issues
    print("Brand voice check failed - review needed")
```

## Error Handling

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Invalid content brief | Missing required fields | Validate brief before processing |
| Word count outside range | Content too short/long | Adjust structure or regenerate |
| Brand voice failure | Avoided terms present | Review and replace terms |
| Unsupported content type | Type not implemented | Use supported type or implement handler |

### Example Error Handling

```python
try:
    draft = agent.process(input_data)

    # Check validation
    is_valid, errors = draft.validate()
    if not is_valid:
        if "word count" in str(errors):
            # Regenerate with adjusted target
            input_data["content_brief"].word_count_range = (
                draft.word_count - 100,
                draft.word_count + 100
            )
            draft = agent.process(input_data)

    # Check brand voice
    if not draft.metadata.get("brand_voice_passed", True):
        issues = draft.metadata.get("brand_voice_issues", [])
        print(f"Brand voice issues: {issues}")
        # Handle: manual review or regeneration

except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Content generation failed: {e}")
```

## Performance Considerations

- **Generation Time**: Varies by content type and length
  - Short social posts: ~2-5 seconds
  - Articles (800-1500 words): ~10-20 seconds
  - Whitepapers (2000-5000 words): ~30-60 seconds

- **Quality vs Speed**: Balance controlled by model selection
  - `claude-sonnet-4`: Best quality (default)
  - `claude-haiku-4`: Faster, good for drafts

- **Caching**: Research briefs can be reused for multiple content pieces

## Advanced Features

### A/B Testing Variations

```python
# Generate multiple variations
variations = agent.generate_variations(content_brief, count=3)

# Compare variations
for i, var in enumerate(variations, 1):
    print(f"\nVariation {i}:")
    print(f"  Word count: {var.word_count}")
    print(f"  Brand score: {var.metadata.get('brand_voice_score', 'N/A')}")
    print(f"  Preview: {var.content[:150]}...")
```

### Custom Instructions

```python
input_data = {
    "content_brief": brief,
    "additional_context": {
        "custom_instructions": "Focus on practical examples and case studies",
        "avoid_technical_jargon": True,
        "include_actionable_tips": True
    }
}

draft = agent.process(input_data)
```

## Logging and Monitoring

```python
# View execution history
summary = agent.get_execution_summary()
print(f"Total content pieces created: {summary['total_executions']}")

# Access execution log
for record in agent.execution_history:
    print(f"{record['timestamp']}: {record['metadata']['content_type']}")
    print(f"  Word count: {record['metadata']['word_count']}")
```

## Future Enhancements (Phase 3+)

- [ ] SEO optimization engine
- [ ] Readability scoring (Flesch-Kincaid, etc.)
- [ ] Plagiarism checking
- [ ] Multi-language support
- [ ] Custom writing style profiles
- [ ] Image/media suggestions
- [ ] Interactive content generation
- [ ] Real-time collaboration features
- [ ] Version control and revision history

## Testing

See `examples/creation_example.py` for complete usage examples.

```bash
# Run creation agent examples
python3 examples/creation_example.py
```

## Related Documentation

- [Long-Form Writing Skill](../../skills/long_form_writing/SKILL.md)
- [Social Content Skill](../../skills/social_content/SKILL.md)
- [Content Brief Skill](../../skills/content_brief/SKILL.md)
- [Brand Voice Skill](../../skills/brand_voice/SKILL.md)
