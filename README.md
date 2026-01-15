# Content Creation Engine

[![CI/CD Pipeline](https://github.com/zoopster/content-creation-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/zoopster/content-creation-engine/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modular, multi-agent system for orchestrating content production across formats (articles, social posts, presentations, videos, newsletters).

## Overview

The Content Creation Engine uses specialized agents and skills to automate and enhance content creation workflows:

- **Orchestrator Agent**: Routes requests and manages workflows
- **Research Agent**: Gathers and validates source material *(Phase 2)*
- **Creation Agent**: Generates written content *(Phase 2)*
- **Production Agent**: Formats and exports final deliverables *(Phase 3)*

## Architecture

```
┌─────────────────────────────────────────┐
│        ORCHESTRATOR AGENT               │
│  (Routes, coordinates, manages state)   │
└─────────────────────────────────────────┘
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Research│ │Creation│ │Production│
└────────┘ └────────┘ └────────┘
```

## Current Status: Phase 3 Complete ✅

**Phase 1 - Foundation** (Complete):
- ✅ Orchestrator Agent with routing logic
- ✅ Content Brief skill
- ✅ Brand Voice skill
- ✅ Agent handoff protocol
- ✅ Base classes and data models
- ✅ Quality gate validation

**Phase 2 - End-to-End Workflows** (Complete):
- ✅ Research Agent with mock data generation
- ✅ Creation Agent with multi-format support
- ✅ Long-Form Writing skill
- ✅ Social Content skill
- ✅ Workflow Executor for full automation
- ✅ Multi-platform campaign workflows
- ✅ Quality gate enforcement
- ✅ Comprehensive examples

**Phase 3 - Production & LLM Integration** (Complete):
- ✅ Production Agent with document generation
- ✅ DOCX, PDF, PPTX output support
- ✅ Template system for documents and presentations
- ✅ Multi-model LLM support (Anthropic Claude & OpenAI GPT)
- ✅ Model registry and provider abstraction
- ✅ Real LLM-powered Research and Creation agents
- ✅ FastAPI backend with workflow execution
- ✅ React frontend wizard interface

**Coming Next** (Phase 4):
- Content repurposing capabilities
- Parallel workflow processing
- Real web search integration
- External platform integrations (CMS, social media)

## Installation

### Prerequisites

- Python 3.12+ (3.8+ supported but 3.12 recommended)
- Node.js 18+ and npm (for frontend)
- API keys from at least one LLM provider:
  - [Anthropic Claude](https://console.anthropic.com/) (recommended)
  - [OpenAI GPT](https://platform.openai.com/api-keys) (optional)

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/zoopster/content-creation-engine.git
cd content-creation-engine

# Run automated setup script
# On macOS/Linux:
./setup_and_test.sh

# On Windows:
setup_and_test.bat
```

The setup script will:
- Check prerequisites (Python 3.8+)
- Create and activate virtual environment
- Install all dependencies
- Run comprehensive MVP tests
- Validate the installation

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/zoopster/content-creation-engine.git
cd content-creation-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# Run MVP test (uses mock data, no API keys needed)
python3 mvp_test.py
```

### Environment Configuration

Create a `.env` file from the example template:

```bash
cp .env.example .env
```

**Required Configuration:**
```bash
# Add at least one API key
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Choose default provider
DEFAULT_PROVIDER=anthropic  # or openai
DEFAULT_MODEL=claude-sonnet-4-20250514  # or gpt-4o
```

See [.env.example](.env.example) for complete configuration options.

## Quick Start

### Running the Application

#### Option 1: Full Stack (API + Frontend)

```bash
# Terminal 1: Start the FastAPI backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn api.main:app --reload --port 8000

# Terminal 2: Start the React frontend
cd frontend
npm install  # First time only
npm run dev
```

Then open http://localhost:5173 in your browser to use the wizard interface.

#### Option 2: API Only

```bash
# Start the API server
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

Access the API documentation at http://localhost:8000/docs

#### Option 3: Python Scripts

Use the workflow executor directly in Python:

```python
from agents.workflow_executor import WorkflowExecutor
from agents.base.models import WorkflowRequest, ContentType

# Create workflow executor
executor = WorkflowExecutor()

# Create content request
request = WorkflowRequest(
    request_text="Write an article about AI in healthcare",
    content_types=[ContentType.ARTICLE],
    additional_context={
        "target_audience": "Healthcare professionals"
    }
)

# Execute complete workflow
result = executor.execute(request)

# Access outputs
if result.success:
    draft = result.outputs.get("draft_content")
    print(f"Generated {draft.word_count} words")
    print(f"Content: {draft.content[:200]}...")
```

### Using Real LLM Integration

The system now supports real LLM-powered content generation:

```python
from core.models import ModelRegistry, load_config_from_env
from agents.research import LLMResearchAgent
from agents.creation import LLMCreationAgent

# Load configuration from environment
config_manager = load_config_from_env()
registry = config_manager.configure_registry()

# Create LLM-powered agents
research_agent = LLMResearchAgent(registry=registry)
creation_agent = LLMCreationAgent(registry=registry)

# Generate real content
research_result = research_agent.research(
    request_text="AI in healthcare",
    research_depth="standard"
)

creation_result = creation_agent.create(
    content_brief=research_result.research_brief,
    content_type="article"
)
```

## Examples

Run the example scripts to see different capabilities:

### Phase 3: Multi-Model LLM Integration

```bash
python3 examples/multi_model_example.py
```

Demonstrates:
- Switching between Anthropic Claude and OpenAI GPT models
- Model-specific configurations
- Provider abstraction layer

### Phase 3: Document Production

```bash
python3 examples/phase3_production.py
```

Demonstrates:
- DOCX document generation
- PDF report creation
- PPTX presentation generation
- Template-based formatting

### Phase 2: End-to-End Workflows

```bash
python3 examples/phase2_endtoend.py
```

Demonstrates:
- Complete article production workflow
- Multi-platform campaign (article + social + email)
- Social media content generation
- Quality gate enforcement

### Phase 1: Core Components

```bash
python3 examples/phase1_example.py
```

Demonstrates:
- Workflow planning with the Orchestrator
- Content brief creation from research
- Brand voice validation
- Multi-platform campaign planning

## Project Structure

```
content-creation-engine/
├── agents/
│   ├── base/              # Base classes and data models
│   ├── orchestrator/      # Orchestrator agent
│   ├── research/          # Research agents (mock + LLM)
│   ├── creation/          # Creation agents (mock + LLM)
│   ├── production/        # Production agent (DOCX/PDF/PPTX)
│   └── workflow_executor.py
├── core/
│   └── models/            # Multi-model LLM abstraction
│       ├── base.py        # Base interfaces
│       ├── registry.py    # Model registry
│       ├── config.py      # Configuration management
│       ├── anthropic_provider.py
│       └── openai_provider.py
├── skills/
│   ├── content-brief/     # Content brief creation
│   ├── brand-voice/       # Brand voice validation
│   ├── long_form_writing/ # Article generation
│   ├── social_content/    # Social media content
│   ├── docx_generation/   # Word documents
│   ├── pdf_generation/    # PDF reports
│   └── pptx_generation/   # PowerPoint presentations
├── api/
│   ├── main.py           # FastAPI application
│   ├── routers/          # API endpoints
│   └── services/         # Business logic
├── frontend/
│   └── src/              # React TypeScript app
│       ├── components/   # UI components
│       └── api/          # API client
├── templates/            # Document templates
│   ├── brand/           # Brand configurations
│   ├── documents/       # DOCX templates
│   └── presentations/   # PPTX templates
├── examples/            # Usage examples
├── .env.example         # Environment configuration template
└── CLAUDE.md           # Guide for Claude Code
```

## Workflows

### Article Production (Implemented: Planning)
Research → Content Brief → Creation → Brand Voice → Production

### Multi-Platform Campaign (Implemented: Planning)
Research → Content Brief → Creation (parallel) → Brand Voice → Production

### Presentation (Implemented: Planning)
Research → Content Brief → Creation → Production

## Skills

### Content Brief (`skills/content-brief/`)
Transforms research into structured briefs with:
- Target audience definition
- Key messages hierarchy
- Tone and style parameters
- Structure requirements
- SEO keywords

### Brand Voice (`skills/brand-voice/`)
Validates content for:
- Vocabulary compliance
- Sentence length and structure
- Tone alignment
- Readability scoring
- Passive voice detection

## Quality Gates

1. **Research Completeness** - Validates research quality
2. **Brief Alignment** - Ensures brief meets requirements
3. **Brand Consistency** - Validates brand voice compliance
4. **Format Compliance** - Checks output formatting
5. **Final Review** - Pre-delivery validation

## Configuration

### Environment Variables

Configure the system via `.env` file:

```bash
# LLM Provider Keys (required)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...

# Provider Selection
DEFAULT_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4-20250514

# API Server
API_HOST=127.0.0.1
API_PORT=8000
API_DEBUG=true

# Quality Gates
ENABLE_QUALITY_GATES=true
QUALITY_THRESHOLD=0.7

# Output Configuration
OUTPUT_DIR=./output
MAX_OUTPUT_FILE_SIZE=50
```

See [.env.example](.env.example) for all options.

### Model Configuration

Customize model settings for each agent:

```python
from core.models import ModelConfigManager, ModelRegistry

# Create custom configuration
config = {
    "agents": {
        "research": {
            "provider": "anthropic",
            "model": "claude-3-5-haiku-20241022",
            "config": {
                "max_tokens": 4096,
                "temperature": 0.3
            }
        },
        "creation": {
            "provider": "openai",
            "model": "gpt-4o",
            "config": {
                "max_tokens": 8192,
                "temperature": 0.7
            }
        }
    }
}

manager = ModelConfigManager(config=config)
registry = manager.configure_registry()
```

### Agent Configuration

Each agent accepts runtime configuration:

```python
config = {
    "max_retries": 3,
    "quality_threshold": 0.7
}

orchestrator = OrchestratorAgent(config=config)
```

## Development

### Running Tests
```bash
pytest tests/  # (tests to be added)
```

### Adding New Skills
1. Create directory: `skills/<skill-name>/`
2. Implement skill class inheriting from `Skill`
3. Add `SKILL.md` documentation
4. Create reference materials in `references/`

### Adding New Workflows
1. Define workflow in Orchestrator's `_initialize_workflows()`
2. Implement routing logic in `_determine_workflow_type()`
3. Create YAML definition in `workflows/`

## Documentation

- See [CLAUDE.md](./CLAUDE.md) for architecture overview
- Each agent has an `AGENT.md` file
- Each skill has a `SKILL.md` file
- Original plan: [content-creation-engine-plan.md](./content-creation-engine-plan.md)

## Implementation Phases

- **Phase 1** ✅: Orchestrator, content-brief, brand-voice, base architecture
- **Phase 2** ✅: Research Agent, Creation Agent, workflow executor, end-to-end workflows
- **Phase 3** ✅: Production Agent, document generation (DOCX/PDF/PPTX), multi-model LLM support, API + frontend
- **Phase 4** (Next): Content repurposing, parallel processing, real web search
- **Phase 5**: External integrations (CMS, social platforms), quality automation, optimization

## API Documentation

When running the API server, access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/workflow/execute` - Execute a content creation workflow
- `GET /api/workflow/status/{job_id}` - Check workflow status
- `GET /api/workflow/result/{job_id}` - Get workflow results
- `GET /api/content-types` - List available content types
- `GET /api/platforms` - List supported platforms
- `GET /api/templates` - List available templates

## Testing

```bash
# Run MVP test (no API keys needed)
python3 mvp_test.py

# Run Phase 3 tests (requires API keys)
python3 tests/test_phase3_quick.py

# Run full test suite (when available)
pytest tests/
```

## Contributing

Contributions welcome! Please:
1. Follow existing code structure
2. Add tests for new features
3. Update documentation
4. Follow brand voice guidelines

## License

[License details to be added]

## Contact

[Contact information to be added]
