# Orchestrator Agent

## Purpose

Central coordinator that interprets user requests, routes work to specialized agents, manages handoffs, and assembles final deliverables.

## Responsibilities

- Parse content requests into discrete tasks
- Select appropriate agent sequence based on content type
- Manage state between agent handoffs
- Aggregate outputs into cohesive deliverables
- Handle retries and quality gates

## Supported Workflows

### 1. Article Production
**Content Types**: Article, Blog Post, Whitepaper, Case Study
**Sequence**: Research → Content Brief → Creation → Brand Voice → Production
**Parallel**: No

### 2. Multi-Platform Campaign
**Content Types**: Multiple (Article + Social + Email)
**Sequence**: Research → Content Brief → Creation (parallel tracks) → Brand Voice → Production
**Parallel**: Yes (creation phase)

### 3. Presentation
**Content Types**: Presentation
**Sequence**: Research → Content Brief → Creation → Production
**Parallel**: No

### 4. Social Only
**Content Types**: Social Post
**Sequence**: Research → Content Brief → Creation → Brand Voice
**Parallel**: No

### 5. Email Sequence
**Content Types**: Email, Newsletter
**Sequence**: Research → Content Brief → Creation → Brand Voice → Production
**Parallel**: No

## Usage

```python
from agents.orchestrator.orchestrator import OrchestratorAgent
from agents.base.models import WorkflowRequest, ContentType

# Create orchestrator
orchestrator = OrchestratorAgent()

# Create request
request = WorkflowRequest(
    request_text="Write an article about AI in healthcare",
    content_types=[ContentType.ARTICLE]
)

# Process request
result = orchestrator.process(request)

# Inspect execution plan
print(result["execution_plan"])
```

## Quality Gates

The orchestrator enforces quality gates at key handoff points:

1. **Research Completeness** - After Research Agent
2. **Brief Alignment** - After content-brief skill
3. **Brand Consistency** - After brand-voice skill
4. **Format Compliance** - After Production Agent
5. **Final Review** - Before delivery

## Configuration

The orchestrator can be configured with:

```python
config = {
    "max_retries": 3,
    "quality_threshold": 0.7,
    "enable_parallel": True
}

orchestrator = OrchestratorAgent(config=config)
```

## Workflow Selection Logic

The orchestrator automatically selects the appropriate workflow based on:

1. Number of content types requested (1 vs multiple)
2. Specific content type characteristics
3. Additional context from request

## Extension Points

To add new workflow types:

1. Add workflow definition to `_initialize_workflows()`
2. Define step sequence and configuration
3. Implement any custom routing logic in `_determine_workflow_type()`

## Implementation Status

**Phase 1**: Core routing logic, workflow definitions, execution planning
**Future Phases**: Agent execution, parallel processing, retry logic, quality gate enforcement
