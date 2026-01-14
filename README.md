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

## Current Status: Phase 2 Complete ✅

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

**Coming Next** (Phase 3):
- Production Agent with document generation
- DOCX, PDF, PPTX output
- Template system
- Content repurposing capabilities

## Installation

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

# Run MVP test
python3 mvp_test.py
```

## Quick Start

### End-to-End Workflow (Phase 2)

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

## Examples

### Phase 2: End-to-End Workflows

```bash
python3 examples/phase2_endtoend.py
```

This demonstrates:
1. ✅ Complete article production workflow
2. ✅ Multi-platform campaign (article + social + email)
3. ✅ Social media content generation
4. ✅ Quality gate enforcement

### Phase 1: Core Components

```bash
python3 examples/phase1_example.py
```

This demonstrates:
1. Workflow planning with the Orchestrator
2. Content brief creation from research
3. Brand voice validation
4. Multi-platform campaign planning

## Project Structure

```
content-creation-engine/
├── agents/
│   ├── base/              # Base classes and data models
│   └── orchestrator/      # Orchestrator agent implementation
├── skills/
│   ├── content-brief/     # Content brief creation skill
│   └── brand-voice/       # Brand voice validation skill
├── workflows/             # Workflow definitions (future)
├── templates/             # Content templates
├── examples/              # Usage examples
└── CLAUDE.md             # Guide for Claude Code
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

Each agent and skill accepts configuration:

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

- **Phase 1** ✅: Orchestrator, content-brief, brand-voice
- **Phase 2** (Next): Research Agent, Creation Agent, basic workflows
- **Phase 3**: Production Agent, template system
- **Phase 4**: Content repurposing, parallel processing
- **Phase 5**: Quality automation, optimization

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
