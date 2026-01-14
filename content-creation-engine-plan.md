# Content Creation Engine: Agent & Skill Architecture Plan

## Executive Summary

This plan outlines a modular content creation engine built on a multi-agent architecture with specialized skills. The system orchestrates content production across formats (articles, social posts, presentations, videos, newsletters) through coordinated agents that handle research, writing, editing, formatting, and distribution.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                          │
│        (Routes requests, manages workflow, coordinates output)   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   RESEARCH    │     │   CREATION    │     │   PRODUCTION  │
│    AGENT      │     │    AGENT      │     │    AGENT      │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ • web-search  │     │ • long-form   │     │ • docx        │
│ • source-eval │     │ • short-form  │     │ • pptx        │
│ • fact-check  │     │ • social      │     │ • pdf         │
│ • data-pull   │     │ • script      │     │ • image-gen   │
│               │     │ • email       │     │ • video-gen   │
└───────────────┘     └───────────────┘     └───────────────┘
```

---

## Agent Definitions

### 1. Orchestrator Agent

**Purpose**: Central coordinator that interprets user requests, routes work to specialized agents, manages handoffs, and assembles final deliverables.

**Responsibilities**:
- Parse content requests into discrete tasks
- Select appropriate agent sequence
- Manage state between agent handoffs
- Aggregate outputs into cohesive deliverables
- Handle retries and quality gates

**Triggers**:
- Any content creation request
- Multi-format content campaigns
- Content requiring multiple production stages

---

### 2. Research Agent

**Purpose**: Gather, validate, and structure source material for content creation.

**Responsibilities**:
- Execute web searches with query optimization
- Evaluate source credibility and recency
- Extract key facts, quotes, and data points
- Synthesize findings into structured briefs
- Identify gaps requiring additional research

**Skills Required**:
| Skill | Function |
|-------|----------|
| `web-search` | Query formulation, result parsing |
| `source-eval` | Credibility scoring, bias detection |
| `fact-check` | Cross-reference verification |
| `data-pull` | API integrations for market data, stats |

---

### 3. Creation Agent

**Purpose**: Generate written content across formats using research inputs and style guidelines.

**Responsibilities**:
- Draft content matching format specifications
- Apply brand voice and style guidelines
- Structure content for target audience
- Generate variations for A/B testing
- Incorporate SEO requirements where applicable

**Skills Required**:
| Skill | Function |
|-------|----------|
| `long-form` | Articles, reports, whitepapers |
| `short-form` | Headlines, summaries, descriptions |
| `social` | Platform-specific posts (LinkedIn, X, Instagram) |
| `script` | Video scripts, podcast outlines |
| `email` | Newsletters, campaigns, sequences |

---

### 4. Production Agent

**Purpose**: Transform written content into final deliverable formats with proper styling and assets.

**Responsibilities**:
- Format documents with brand templates
- Generate supporting visual assets
- Compile multi-section documents
- Produce presentation decks
- Export to required file formats

**Skills Required**:
| Skill | Function |
|-------|----------|
| `docx` | Word document creation/editing |
| `pptx` | Presentation generation |
| `pdf` | PDF compilation and forms |
| `image-gen` | Graphics, diagrams, social cards |
| `video-gen` | Short-form video assembly |

---

## Skill Specifications

### Core Skills to Develop

#### 1. `content-brief` Skill
**Purpose**: Structure research findings into actionable creation briefs.

```
content-brief/
├── SKILL.md
├── references/
│   └── brief-templates.md
└── assets/
    └── brief-template.json
```

**Key Outputs**:
- Target audience definition
- Key messages hierarchy
- Tone and style parameters
- Required sections/structure
- SEO keywords (if applicable)

---

#### 2. `brand-voice` Skill
**Purpose**: Apply consistent voice and style across all content.

```
brand-voice/
├── SKILL.md
├── references/
│   ├── voice-guidelines.md
│   ├── word-choices.md
│   └── examples/
│       ├── before-after.md
│       └── tone-spectrum.md
└── scripts/
    └── style-check.py
```

**Key Functions**:
- Vocabulary alignment (preferred/avoided terms)
- Sentence structure patterns
- Tone calibration per content type
- Consistency validation

---

#### 3. `long-form-writing` Skill
**Purpose**: Generate articles, reports, and extended written content.

```
long-form-writing/
├── SKILL.md
├── references/
│   ├── article-structures.md
│   ├── hook-patterns.md
│   └── transition-techniques.md
└── assets/
    └── outline-templates/
```

**Key Workflow**:
1. Receive brief from `content-brief`
2. Generate outline with hooks
3. Draft section by section
4. Apply `brand-voice` guidelines
5. Self-review against brief requirements

---

#### 4. `social-content` Skill
**Purpose**: Create platform-optimized social media content.

```
social-content/
├── SKILL.md
├── references/
│   ├── platform-specs.md     # Character limits, formats
│   ├── engagement-patterns.md
│   └── hashtag-strategy.md
└── assets/
    └── post-templates/
        ├── linkedin.md
        ├── twitter.md
        └── instagram.md
```

**Platform Specifications**:
| Platform | Max Length | Media | Hashtag Strategy |
|----------|------------|-------|-----------------|
| LinkedIn | 3,000 chars | Image, PDF, Video | 3-5 professional |
| X/Twitter | 280 chars | Image, Video, GIF | 1-2 relevant |
| Instagram | 2,200 chars | Image required | 5-15 mixed |

---

#### 5. `content-repurpose` Skill
**Purpose**: Transform source content into multiple derivative formats.

```
content-repurpose/
├── SKILL.md
├── references/
│   └── transformation-matrix.md
└── scripts/
    └── extract-highlights.py
```

**Transformation Matrix**:
| Source | → Article | → Social | → Presentation | → Email |
|--------|-----------|----------|----------------|---------|
| Research Brief | Full draft | Key stats | Slide deck | Summary |
| Long Article | — | Thread | Key points | Teaser |
| Webinar | Recap | Quotes | — | Follow-up |
| Case Study | Blog post | Results | Sales deck | Nurture |

---

## Workflow Definitions

### Workflow 1: Article Production

```
User Request
     │
     ▼
┌─────────────────┐
│  ORCHESTRATOR   │ Parse request, identify article type
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    RESEARCH     │ Execute: web-search → source-eval → fact-check
│     AGENT       │ Output: Research Brief (JSON)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   CREATION      │ Execute: content-brief → long-form-writing → brand-voice
│     AGENT       │ Output: Draft Article (Markdown)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PRODUCTION     │ Execute: docx OR pdf
│     AGENT       │ Output: Final Document
└────────┬────────┘
         │
         ▼
    Final Delivery
```

---

### Workflow 2: Multi-Platform Campaign

```
User Request: "Create content about [topic] for blog + LinkedIn + email"
     │
     ▼
┌─────────────────┐
│  ORCHESTRATOR   │ Decompose into parallel tracks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    RESEARCH     │ Single research pass, shared brief
│     AGENT       │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐
│ Blog  │ │Social │ │ Email │   CREATION AGENT runs in parallel
│ Track │ │ Track │ │ Track │
└───┬───┘ └───┬───┘ └───┬───┘
    │         │         │
    └────┬────┴────┬────┘
         │         │
         ▼         ▼
┌─────────────────────────┐
│    PRODUCTION AGENT     │ Format each deliverable
└─────────────────────────┘
         │
         ▼
    Campaign Package
    ├── blog-post.docx
    ├── linkedin-posts.md
    └── email-sequence.html
```

---

### Workflow 3: Presentation from Research

```
User Request: "Create a presentation on [topic]"
     │
     ▼
┌─────────────────────────────────────────────┐
│ ORCHESTRATOR determines:                     │
│  • Audience (executive, technical, sales)   │
│  • Slide count target                       │
│  • Visual style requirements                │
└────────────────────┬────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│    RESEARCH     │     │   PRODUCTION    │
│  (if needed)    │     │  Load template  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌─────────────────┐
         │    CREATION     │ Generate slide content per template
         │     AGENT       │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   PRODUCTION    │ Execute: pptx skill
         │     AGENT       │
         └────────┬────────┘
                  │
                  ▼
            presentation.pptx
```

---

## Quality Gates

Each workflow includes validation checkpoints:

| Gate | Location | Validation |
|------|----------|------------|
| Research Completeness | After Research Agent | Required facts present, sources cited |
| Brief Alignment | After content-brief | Audience, messages, structure defined |
| Brand Consistency | After Creation Agent | Voice check passes, terms aligned |
| Format Compliance | After Production Agent | File opens correctly, styling applied |
| Final Review | Before delivery | All requirements met, no errors |

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Build Orchestrator Agent routing logic
- [ ] Implement `content-brief` skill
- [ ] Implement `brand-voice` skill
- [ ] Create agent handoff protocol

### Phase 2: Core Creation (Weeks 3-4)
- [ ] Implement `long-form-writing` skill
- [ ] Implement `social-content` skill
- [ ] Build Research Agent with web search integration
- [ ] Test single-format workflows

### Phase 3: Production Pipeline (Weeks 5-6)
- [ ] Integrate `docx`, `pptx`, `pdf` skills
- [ ] Build Production Agent formatting logic
- [ ] Implement template system
- [ ] Test end-to-end article workflow

### Phase 4: Multi-Format (Weeks 7-8)
- [ ] Implement `content-repurpose` skill
- [ ] Build parallel processing for campaigns
- [ ] Add email sequence generation
- [ ] Test multi-platform workflow

### Phase 5: Polish & Scale (Weeks 9-10)
- [ ] Add quality gate automation
- [ ] Performance optimization
- [ ] Error handling and retry logic
- [ ] Documentation and examples

---

## File Structure: Complete Engine

```
content-creation-engine/
├── agents/
│   ├── orchestrator/
│   │   ├── AGENT.md
│   │   └── scripts/
│   │       ├── route_request.py
│   │       └── manage_workflow.py
│   ├── research/
│   │   ├── AGENT.md
│   │   └── scripts/
│   │       └── compile_brief.py
│   ├── creation/
│   │   ├── AGENT.md
│   │   └── scripts/
│   │       └── validate_output.py
│   └── production/
│       ├── AGENT.md
│       └── scripts/
│           └── format_deliverable.py
│
├── skills/
│   ├── content-brief/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── assets/
│   ├── brand-voice/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/
│   ├── long-form-writing/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── assets/
│   ├── social-content/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── assets/
│   ├── content-repurpose/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/
│   └── ... (integrate existing docx, pptx, pdf)
│
├── workflows/
│   ├── article-production.yaml
│   ├── multi-platform-campaign.yaml
│   └── presentation-from-research.yaml
│
└── templates/
    ├── briefs/
    ├── documents/
    └── presentations/
```

---

## Next Steps

1. **Define your brand voice parameters** – Required before implementing `brand-voice` skill
2. **Specify priority content types** – Which formats matter most for your use case?
3. **Provide template examples** – Existing documents/presentations to use as references
4. **Identify integration points** – CMS, social platforms, email tools to connect

Would you like me to begin implementing any specific skill or agent from this plan?
