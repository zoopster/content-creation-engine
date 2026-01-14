# Quick Start Guide

Get started with the Content Creation Engine in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- No external dependencies required for Phase 1

## Running the Examples

```bash
# Navigate to the project directory
cd /Users/johnpugh/Documents/source/content-creation-engine

# Run the Phase 1 examples
python3 examples/phase1_example.py
```

You should see output demonstrating:
1. ✅ Workflow planning
2. ✅ Content brief creation
3. ✅ Brand voice validation (good vs. bad examples)
4. ✅ Multi-platform campaign planning

## Basic Usage

### 1. Plan a Content Workflow

```python
import sys
sys.path.append('/Users/johnpugh/Documents/source/content-creation-engine')

from agents.orchestrator import OrchestratorAgent
from agents.base.models import WorkflowRequest, ContentType

# Create orchestrator
orchestrator = OrchestratorAgent()

# Create a request
request = WorkflowRequest(
    request_text="Write an article about sustainable agriculture",
    content_types=[ContentType.ARTICLE],
    priority="normal"
)

# Get execution plan
result = orchestrator.process(request)

# View the plan
print(f"Workflow: {result['workflow_type']}")
for step in result['execution_plan']:
    print(f"- {step.get('agent') or step.get('skill')}")
```

### 2. Create a Content Brief

```python
from skills import ContentBriefSkill
from agents.base.models import ResearchBrief, Source, ContentType, ToneType

# Create skill
skill = ContentBriefSkill()

# Mock research data
research = ResearchBrief(
    topic="Sustainable Agriculture",
    sources=[
        Source(
            url="https://example.com/agriculture",
            title="Modern Farming Techniques",
            credibility_score=0.85,
            key_facts=["Sustainable farming reduces water usage by 40%"]
        )
    ],
    key_findings=[
        "Sustainable practices improve soil health",
        "Reduced environmental impact"
    ],
    data_points={"water_savings": "40%"}
)

# Generate brief
brief = skill.execute(
    research_brief=research,
    content_type=ContentType.ARTICLE,
    target_audience="Farmers and agricultural professionals"
)

print(f"Key Messages: {brief.key_messages}")
print(f"Structure: {brief.structure_requirements}")
```

### 3. Validate Brand Voice

```python
from skills import BrandVoiceSkill
from agents.base.models import DraftContent, ContentType, ToneType

# Create skill
skill = BrandVoiceSkill()

# Your content
draft = DraftContent(
    content="""
    Sustainable agriculture improves soil health while reducing environmental impact.
    Modern farming techniques achieve 40% water savings through efficient irrigation
    systems. These practices benefit both farmers and ecosystems.
    """,
    content_type=ContentType.ARTICLE,
    word_count=30
)

# Validate
result = skill.execute(draft, target_tone=ToneType.PROFESSIONAL)

if result.passed:
    print(f"✅ Passed! Score: {result.score:.2f}")
else:
    print(f"❌ Failed. Score: {result.score:.2f}")
    print(f"Issues: {result.issues}")
    print(f"Suggestions: {result.suggestions}")
```

## Available Content Types

- `ContentType.ARTICLE` - Long-form articles (800-1500 words)
- `ContentType.BLOG_POST` - Blog posts (600-1200 words)
- `ContentType.SOCIAL_POST` - Social media (50-300 words)
- `ContentType.WHITEPAPER` - Whitepapers (2000-5000 words)
- `ContentType.EMAIL` - Email content (100-400 words)
- `ContentType.NEWSLETTER` - Newsletters
- `ContentType.PRESENTATION` - Presentations (500-1000 words)
- `ContentType.VIDEO_SCRIPT` - Video scripts
- `ContentType.CASE_STUDY` - Case studies

## Available Tone Types

- `ToneType.PROFESSIONAL` - Business and professional content
- `ToneType.CONVERSATIONAL` - Friendly, approachable content
- `ToneType.TECHNICAL` - Technical documentation
- `ToneType.EDUCATIONAL` - Teaching and learning content
- `ToneType.PERSUASIVE` - Marketing and sales content
- `ToneType.INSPIRATIONAL` - Motivational content

## Supported Workflows

### Single Content Type
```python
# Article workflow
request = WorkflowRequest(
    request_text="Your topic here",
    content_types=[ContentType.ARTICLE]
)
```

### Multi-Platform Campaign
```python
# Multiple content types
request = WorkflowRequest(
    request_text="Your topic here",
    content_types=[
        ContentType.ARTICLE,
        ContentType.SOCIAL_POST,
        ContentType.EMAIL
    ]
)
```

## Quality Gates

All content passes through validation checkpoints:

1. **Research Completeness** - Validates research quality
   - Minimum 2 sources
   - At least 1 high-quality source (credibility >= 0.7)
   - Key findings present

2. **Brief Alignment** - Validates content brief
   - Target audience defined
   - At least 1 key message
   - Structure requirements specified
   - Valid word count range

3. **Brand Consistency** - Validates brand voice
   - Score >= 0.7
   - No avoided terms
   - Acceptable readability (Flesch >= 60)
   - Passive voice < 15%

4. **Format Compliance** - Validates output format
5. **Final Review** - Pre-delivery check

## File Structure

```
content-creation-engine/
├── agents/              # Agent implementations
│   ├── base/           # Base classes
│   └── orchestrator/   # Workflow orchestration
├── skills/             # Skill implementations
│   ├── content-brief/  # Brief creation
│   └── brand-voice/    # Voice validation
└── examples/           # Usage examples
```

## Next Steps

- Explore `examples/phase1_example.py` for detailed examples
- Read `CLAUDE.md` for architecture overview
- Check `README.md` for full documentation
- Review `PHASE1_COMPLETE.md` for implementation details

## Need Help?

- See full documentation in `README.md`
- Review architecture in `CLAUDE.md`
- Check agent docs in `agents/*/AGENT.md`
- Check skill docs in `skills/*/SKILL.md`

## Phase 2 Preview

Coming next:
- Research Agent with web search
- Creation Agent for content generation
- End-to-end workflow execution
- Automated testing framework
