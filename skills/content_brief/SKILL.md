# Content Brief Skill

## Purpose

Structure research findings into actionable creation briefs that guide content writers.

## Function

Transforms `ResearchBrief` into `ContentBrief` with:
- Target audience definition
- Key messages hierarchy
- Tone and style parameters
- Required sections/structure
- SEO keywords (if applicable)

## Key Outputs

A `ContentBrief` includes:

1. **Target Audience**: Who the content is for
2. **Key Messages**: Ranked list of main points to communicate
3. **Tone**: Writing style (professional, conversational, technical, etc.)
4. **Structure Requirements**: Expected sections and organization
5. **Word Count Range**: Minimum and maximum word count
6. **SEO Keywords**: Relevant keywords for optimization
7. **Brand Guidelines**: Applicable brand voice rules

## Usage

```python
from skills.content_brief.content_brief import ContentBriefSkill
from agents.base.models import ResearchBrief, ContentType, Source

# Create skill instance
skill = ContentBriefSkill()

# Prepare research input
research = ResearchBrief(
    topic="AI in Healthcare",
    sources=[
        Source(
            url="https://example.com/ai-healthcare",
            title="AI Transforming Healthcare",
            credibility_score=0.8,
            key_facts=["AI reduces diagnosis time by 40%"]
        )
    ],
    key_findings=[
        "AI improves diagnostic accuracy",
        "Reduces healthcare costs",
        "Enables personalized treatment"
    ],
    data_points={"market_size": "$150B by 2026"}
)

# Generate brief
brief = skill.execute(
    research_brief=research,
    content_type=ContentType.ARTICLE,
    target_audience="Healthcare professionals",
    additional_requirements={
        "tone": ToneType.PROFESSIONAL,
        "word_count_range": (1000, 1500)
    }
)

# Access brief details
print(brief.key_messages)
print(brief.structure_requirements)
```

## Content Type Templates

### Article
- **Structure**: Hook → Problem → Main Content (3-5 sections) → Examples → Conclusion
- **Word Count**: 800-1500
- **Tone**: Educational

### Blog Post
- **Structure**: Catchy Intro → Main Points (2-4 sections) → Tips → CTA
- **Word Count**: 600-1200
- **Tone**: Conversational

### Social Post
- **Structure**: Hook → Message → CTA/Question
- **Word Count**: 50-300
- **Tone**: Conversational

### Whitepaper
- **Structure**: Executive Summary → Problem → Solution → Case Studies → Implementation → Conclusion
- **Word Count**: 2000-5000
- **Tone**: Professional

### Email
- **Structure**: Subject → Preview → Problem→Solution→Action → CTA
- **Word Count**: 100-400
- **Tone**: Conversational

### Presentation
- **Structure**: Title → Agenda → Key Points (1/slide) → Data → Summary
- **Word Count**: 500-1000
- **Tone**: Professional

## Quality Gate: Brief Alignment

The brief must pass validation before content creation:

✅ **Required**:
- Target audience defined
- At least 1 key message
- Structure requirements specified
- Valid word count range

❌ **Validation Fails If**:
- Target audience is empty
- No key messages
- No structure requirements
- Invalid word count (min > max or <= 0)

## Customization

### Override Default Templates

```python
config = {
    "custom_templates": {
        "article": {
            "default_structure": ["Custom structure"],
            "word_count_range": (500, 1000),
            "tone": ToneType.TECHNICAL
        }
    }
}

skill = ContentBriefSkill(config=config)
```

### Audience Inference

The skill can infer target audience from research topic:
- Technical keywords → "Technical professionals"
- Business keywords → "Business leaders"
- Beginner keywords → "General audience"

## Integration with Workflow

**Input**: `ResearchBrief` from Research Agent
**Output**: `ContentBrief` for Creation Agent
**Quality Gate**: Brief Alignment validation

## Future Enhancements

- NLP-based key message extraction and ranking
- Automatic tone detection from source material
- Competitive content analysis
- SEO optimization suggestions
- A/B testing variant generation
