# CLAUDE.md - Content Creation Engine

## Project Overview

**Name:** Content Creation Engine (CCE)
**Type:** Multi-agent content production system with REST API and React frontend
**Status:** Active Development (Phases 1-4 Complete)

A modular system that orchestrates AI agents to research, write, and produce content across multiple formats (articles, social posts, presentations, documents).

## Tech Stack

### Backend (Python)
- **Framework:** FastAPI with Uvicorn
- **Python:** 3.8+ (venv in `./venv`)
- **LLM Providers:** Anthropic Claude, OpenAI GPT
- **Document Generation:** python-docx, python-pptx, reportlab
- **Web Search:** Firecrawl, aiohttp (for Serper API)

### Frontend (TypeScript)
- **Framework:** React 18 with Vite
- **State:** Zustand
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios

## Common Commands

```bash
# Backend - activate venv first
source venv/bin/activate        # macOS/Linux
.\venv\Scripts\activate         # Windows

# Run API server (from project root)
uvicorn api.main:app --reload --port 8000

# Run tests
pytest tests/
python mvp_test.py              # Integration test

# Frontend (from frontend/ directory)
cd frontend
npm run dev                     # Dev server on :5173
npm run build                   # Production build
npm run lint                    # ESLint check
```

## Project Structure

```
content-creation-engine/
├── agents/                     # AI Agent implementations
│   ├── orchestrator/           # Routes requests, manages workflow
│   ├── research/               # Gathers and validates sources
│   ├── creation/               # Generates written content
│   ├── production/             # Produces final documents
│   └── workflow_executor.py    # Runs multi-agent workflows
├── skills/                     # Modular agent capabilities
│   ├── content_brief/          # Brief generation
│   ├── brand_voice/            # Voice/tone consistency
│   ├── long_form_writing/      # Articles, blog posts
│   ├── social_content/         # Social media posts
│   ├── docx_generation/        # Word documents
│   ├── pptx_generation/        # PowerPoint slides
│   ├── pdf_generation/         # PDF output
│   ├── content_repurpose/      # Format transformations
│   ├── email_generation/       # Email content generation
│   └── wordpress_publish/      # WordPress REST API publishing
├── api/                        # FastAPI REST API
│   ├── main.py                 # App entry point
│   ├── config.py               # Settings
│   ├── job_store.py            # SQLite-backed persistent job store
│   ├── routers/                # API endpoints
│   ├── schemas/                # Pydantic models
│   └── services/               # Business logic
├── frontend/                   # React SPA
│   └── src/
│       ├── components/         # UI components
│       ├── api/                # API client
│       ├── store/              # Zustand state
│       └── hooks/              # Custom hooks
├── templates/                  # Document templates
│   └── brand/                  # Brand configuration
├── output/                     # Generated content (gitignored)
├── examples/                   # Usage examples
└── tests/                      # Test suite
```

## Architecture

### Agent Pipeline
```
Orchestrator → Research Agent → Creation Agent → Production Agent
     ↓              ↓                ↓                ↓
  Routing      Web Search       Long-form         DOCX/PPTX/PDF
              Source Eval      Social Content    Template System
```

### Agent Handoffs
- **Research → Creation:** JSON Research Brief
- **Creation → Production:** Markdown content
- **Production → Output:** Final documents (DOCX, PPTX, PDF)

### Quality Gates (5 Checkpoints)
1. Research Completeness
2. Brief Alignment
3. Brand Consistency
4. Format Compliance
5. Final Review

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/output-formats` | List supported formats |
| POST | `/api/workflow/execute` | Run content workflow |
| GET | `/api/workflow/status/{id}` | Poll job status |
| GET | `/api/workflow/result/{id}` | Fetch completed result |
| GET | `/api/workflow/download/{id}/{file}` | Download output file |
| GET | `/api/templates` | List templates |
| GET | `/api/content-types` | List content types |
| GET | `/api/platforms` | List platforms |
| GET | `/api/repurpose/formats` | List repurpose transformations |
| POST | `/api/repurpose` | Repurpose existing content |
| POST | `/api/repurpose/email` | Generate email from topic |
| GET | `/api/publish/wordpress/verify` | Verify WP credentials |
| GET | `/api/publish/wordpress/categories` | List WP categories |
| GET | `/api/publish/wordpress/tags` | List WP tags |
| POST | `/api/publish/wordpress` | Publish content to WordPress |
| GET | `/api/repurpose/formats` | List repurpose transformations |
| POST | `/api/repurpose` | Repurpose content to new format |
| POST | `/api/repurpose/email` | Generate email from topic |
| GET | `/api/publish/wordpress/verify` | Verify WordPress connection |
| POST | `/api/publish/wordpress` | Publish content to WordPress |

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
ANTHROPIC_API_KEY=sk-ant-...     # Required for Claude
OPENAI_API_KEY=sk-...            # Optional for GPT
FIRECRAWL_API_KEY=fc-...         # For web search
SERPER_API_KEY=...               # Alternative search
WORDPRESS_URL=https://yoursite.com     # WordPress publishing
WORDPRESS_USERNAME=your-username       # WordPress username
WORDPRESS_APP_PASSWORD=xxxx xxxx ...   # WP application password
JOB_DB_PATH=/path/to/jobs.db          # SQLite job store (default: ./jobs.db)
```

## Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | Complete | Orchestrator, content-brief, brand-voice, handoff protocol |
| Phase 2 | Complete | long-form-writing, social-content, Research Agent |
| Phase 3 | Complete | Production Agent, DOCX/PPTX/PDF skills, template system |
| Phase 4 | Complete | LLM content-repurpose, email-generation, parallel workflows, repurpose API, WordPress publish, SQLite job store, frontend publish UI |
| Phase 5 | Pending | Quality gate automation, performance optimization |

## Coding Standards

- Use **4 spaces** for indentation (Python & TypeScript)
- Python: Follow PEP 8, type hints required
- TypeScript: Strict mode, prefer `interface` over `type`
- All agents/skills must have `__init__.py` exports
- Document public functions with docstrings

## Things to Avoid

- Don't modify files in `venv/` or `node_modules/`
- Don't commit `.env` files (use `.env.example`)
- Don't hardcode API keys
- Don't put generated content in git (use `output/`)
- Avoid synchronous API calls in agents (use async)

## Testing

```bash
# Quick integration test
python mvp_test.py

# Full test suite
pytest tests/ -v

# Phase 3 specific tests
pytest tests/test_phase3_quick.py
```

## Key Files to Read First

1. `api/main.py` - API entry point and routes
2. `agents/orchestrator/orchestrator.py` - Workflow coordination
3. `agents/workflow_executor.py` - Multi-agent execution
4. `skills/long_form_writing/long_form_writing.py` - Content generation pattern

## Recent Work / Current Focus

- Phases 1-4 complete
- Phase 4 delivered: LLM content repurposing, email generation, parallel multi-platform workflows, repurpose API (`/api/repurpose`), WordPress publish API + frontend UI, SQLite-backed persistent job store (`api/job_store.py`)
- Job state survives server restarts; `JOB_DB_PATH` env var controls SQLite file location
- Frontend `WorkflowResult` now includes a collapsible "Publish to WordPress" panel
- Next: Phase 5 quality gate automation and performance optimization

## Platform Specs Reference

| Platform | Max Length | Media | Hashtags |
|----------|-----------|-------|----------|
| LinkedIn | 3,000 chars | Image, PDF, Video | 3-5 |
| X/Twitter | 280 chars | Image, Video, GIF | 1-2 |
| Instagram | 2,200 chars | Image required | 5-15 |
