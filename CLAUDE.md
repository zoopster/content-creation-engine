# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Content Creation Engine is a multi-agent system designed to orchestrate content production across formats (articles, social posts, presentations, videos, newsletters). The system uses specialized agents that handle research, writing, editing, formatting, and distribution.

## Architecture

### Agent System

The system follows a four-agent architecture:

1. **Orchestrator Agent** (`agents/orchestrator/`): Central coordinator that routes requests, manages workflow state, and assembles final deliverables
2. **Research Agent** (`agents/research/`): Gathers and validates source material, produces structured research briefs
3. **Creation Agent** (`agents/creation/`): Generates written content using research inputs and brand guidelines
4. **Production Agent** (`agents/production/`): Transforms content into final formats (DOCX, PPTX, PDF) with templates

### Skill System

Skills are modular capabilities invoked by agents:

- **Research Skills**: `web-search`, `source-eval`, `fact-check`, `data-pull`
- **Creation Skills**: `long-form`, `short-form`, `social`, `script`, `email`
- **Production Skills**: `docx`, `pptx`, `pdf`, `image-gen`, `video-gen`
- **Cross-cutting Skills**: `content-brief`, `brand-voice`, `content-repurpose`

Each skill lives in `skills/<skill-name>/` with structure:
```
<skill-name>/
├── SKILL.md              # Documentation and usage
├── references/           # Guidelines and examples
├── assets/              # Templates and resources
└── scripts/             # Implementation code
```

### Workflow System

Workflows define agent coordination patterns:
- **Article Production**: Research → Creation → Production (sequential)
- **Multi-Platform Campaign**: Research → parallel Creation tracks → Production
- **Presentation from Research**: Research + Production (template) → Creation → Production

Workflows are defined in `workflows/*.yaml` files.

## Key Design Principles

### Agent Handoffs

Agents communicate through structured data formats:
- Research Agent outputs: Research Brief (JSON)
- Creation Agent outputs: Draft content (Markdown)
- Production Agent outputs: Final documents (format-specific)

Each handoff includes validation checkpoints (Quality Gates).

### Quality Gates

Validation happens at five checkpoints:
1. Research Completeness (after Research Agent)
2. Brief Alignment (after content-brief skill)
3. Brand Consistency (after Creation Agent)
4. Format Compliance (after Production Agent)
5. Final Review (before delivery)

### Brand Voice System

The `brand-voice` skill ensures consistency through:
- Vocabulary alignment (preferred/avoided terms)
- Sentence structure patterns
- Tone calibration per content type
- Style validation scripts

## Implementation Status

This is a greenfield project. The architecture is defined in `content-creation-engine-plan.md` but no code has been implemented yet.

### Implementation Order (from plan)

1. **Phase 1**: Orchestrator routing, `content-brief` and `brand-voice` skills, agent handoff protocol
2. **Phase 2**: `long-form-writing` and `social-content` skills, Research Agent with web search
3. **Phase 3**: Production Agent with `docx`/`pptx`/`pdf` skills, template system
4. **Phase 4**: `content-repurpose` skill, parallel processing, email generation
5. **Phase 5**: Quality gate automation, performance optimization, error handling

## File Structure

```
content-creation-engine/
├── agents/
│   ├── orchestrator/
│   ├── research/
│   ├── creation/
│   └── production/
├── skills/
│   ├── content-brief/
│   ├── brand-voice/
│   ├── long-form-writing/
│   ├── social-content/
│   ├── content-repurpose/
│   └── (docx, pptx, pdf, etc.)
├── workflows/
│   ├── article-production.yaml
│   ├── multi-platform-campaign.yaml
│   └── presentation-from-research.yaml
└── templates/
    ├── briefs/
    ├── documents/
    └── presentations/
```

## Content Transformation Matrix

When implementing `content-repurpose` skill, follow these transformations:

| Source Format | Target: Article | Target: Social | Target: Presentation | Target: Email |
|--------------|-----------------|----------------|---------------------|---------------|
| Research Brief | Full draft | Key stats | Slide deck | Summary |
| Long Article | N/A | Thread | Key points | Teaser |
| Webinar | Recap | Quotes | N/A | Follow-up |
| Case Study | Blog post | Results | Sales deck | Nurture |

## Platform-Specific Requirements

### Social Content Specifications

| Platform | Max Length | Media Support | Hashtag Strategy |
|----------|-----------|---------------|------------------|
| LinkedIn | 3,000 chars | Image, PDF, Video | 3-5 professional |
| X/Twitter | 280 chars | Image, Video, GIF | 1-2 relevant |
| Instagram | 2,200 chars | Image required | 5-15 mixed |

Reference: `skills/social-content/references/platform-specs.md` (when created)

## Prerequisites for Implementation

Before beginning implementation:
1. Define brand voice parameters for `brand-voice` skill
2. Specify priority content types/formats
3. Provide template examples for documents and presentations
4. Identify third-party integration points (CMS, social platforms, email tools)
