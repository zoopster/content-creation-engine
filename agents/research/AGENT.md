# Research Agent

## Purpose

The Research Agent gathers, validates, and structures source material for content creation. It executes web searches, evaluates source credibility, extracts key information, and synthesizes findings into structured `ResearchBrief` objects.

## Responsibilities

- **Web Search Execution**: Formulate and execute optimized search queries
- **Source Evaluation**: Assess credibility and quality of sources
- **Information Extraction**: Extract key facts, quotes, and data points
- **Synthesis**: Combine findings from multiple sources into coherent insights
- **Gap Identification**: Identify areas requiring additional research

## Architecture

```
ResearchAgent
├── Input: topic + requirements
├── Process:
│   ├── 1. Web Search (web-search skill)
│   ├── 2. Source Evaluation (credibility scoring)
│   ├── 3. Fact Extraction (quotes, facts, data)
│   ├── 4. Synthesis (key findings)
│   └── 5. Gap Analysis
└── Output: ResearchBrief
```

## Skills Used

### Primary Skills

| Skill | Function | Status |
|-------|----------|--------|
| `web-search` | Query formulation and execution | ✅ Implemented |
| `source-eval` | Credibility scoring and filtering | ✅ Integrated |
| `fact-extraction` | Extract quotes, facts, statistics | ✅ Integrated |

### Future Skills

| Skill | Function | Status |
|-------|----------|--------|
| `fact-check` | Cross-reference verification | 🔲 Planned (Phase 2) |
| `data-pull` | API integrations for market data | 🔲 Planned (Phase 2) |

## Configuration

```python
config = {
    "min_sources": 3,          # Minimum sources required
    "max_sources": 10,         # Maximum sources to include
    "min_credibility": 0.5     # Minimum credibility threshold
}

agent = ResearchAgent(config)
```

## Usage

### Basic Usage

```python
from agents.research.research import ResearchAgent

# Initialize agent
agent = ResearchAgent()

# Prepare input
input_data = {
    "topic": "Multi-agent systems for content creation",
    "requirements": {
        "recent_only": True,
        "focus_areas": ["AI agents", "workflow automation"],
        "content_type": "technical"
    }
}

# Execute research
research_brief = agent.process(input_data)

# Access results
print(f"Found {len(research_brief.sources)} sources")
print(f"Key findings: {research_brief.key_findings}")
print(f"Research gaps: {research_brief.research_gaps}")
```

### With Web Search Integration

```python
from agents.research.research import ResearchAgent
from skills.web_search.web_search import WebSearchSkill

# Initialize components
agent = ResearchAgent()
search_skill = WebSearchSkill()

# Prepare input
input_data = {
    "topic": "AI-powered content creation",
    "requirements": {"recent_only": True}
}

# Execute search using the skill
query = search_skill.optimize_query(
    input_data["topic"],
    input_data.get("requirements", {})
)

# Note: Actual web search would be performed here using WebSearch tool
# search_results = [call WebSearch tool with query]

# Process with agent (agent expects search results in input_data)
research_brief = agent.process(input_data)
```

## Input Format

```python
{
    "topic": str,                    # Required: Research topic
    "requirements": {                # Optional: Additional requirements
        "recent_only": bool,         # Only include recent sources
        "focus_areas": List[str],    # Specific areas to focus on
        "content_type": str,         # "technical", "business", etc.
        "year": int,                 # Specific year to search
        "domains": List[str],        # Specific domains to include
        "must_include": List[str],   # Required terms
        "exclude": List[str]         # Terms to exclude
    }
}
```

## Output Format

Returns a `ResearchBrief` object:

```python
@dataclass
class ResearchBrief:
    topic: str                       # Research topic
    sources: List[Source]            # Evaluated sources
    key_findings: List[str]          # Synthesized findings
    data_points: Dict[str, Any]      # Structured data
    research_gaps: List[str]         # Identified gaps
    timestamp: str                   # ISO timestamp
```

### Source Object

```python
@dataclass
class Source:
    url: str                         # Source URL
    title: str                       # Article/page title
    author: Optional[str]            # Author name
    publication_date: Optional[str]  # Publication date
    credibility_score: float         # 0.0 to 1.0
    key_quotes: List[str]            # Extracted quotes
    key_facts: List[str]             # Extracted facts
```

## Credibility Scoring

The agent evaluates source credibility using multiple factors:

### Scoring Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Domain Reputation | High (±0.3) | Educational, government, academic domains |
| Content Quality | Medium (±0.1) | Length, depth, structure |
| Attribution | Low (±0.1) | Author and publication date presence |
| Title Quality | Negative (-0.2) | Penalize clickbait patterns |

### Domain Tiers

**High Reputation (+0.3):**
- `.edu`, `.gov`
- `ieee.org`, `acm.org`, `nature.com`, `science.org`
- `arxiv.org`, `scholar.google.com`
- `techcrunch.com`, `wired.com`, `arstechnica.com`

**Medium Reputation (+0.2):**
- `forbes.com`, `bloomberg.com`, `reuters.com`
- `wsj.com`, `nytimes.com`, `theguardian.com`

**Low Quality (-0.1):**
- Personal blogs, WordPress sites, Medium posts

## Quality Gate Integration

The Research Agent outputs are validated through **Quality Gate 1: Research Completeness**.

### Validation Checks

```python
def validate(self) -> tuple[bool, List[str]]:
    """
    Validation requirements:
    - Topic must be present
    - At least 2 sources required
    - At least 1 key finding required
    - At least 1 source with credibility >= 0.7
    """
```

### Handling Validation Failures

```python
research_brief = agent.process(input_data)

is_valid, errors = research_brief.validate()
if not is_valid:
    print(f"Validation errors: {errors}")
    # Handle: retry search, adjust requirements, or continue with warning
```

## Integration with Workflow

### Workflow Position

```
User Request
     ↓
Orchestrator → RESEARCH AGENT → Creation Agent → Production Agent
               └─────────────────────────┘
                  ResearchBrief (JSON)
```

### Handoff to Creation Agent

The `ResearchBrief` output is passed to:
1. **content-brief skill** - Structures findings into creation brief
2. **Creation Agent** - Generates content based on research

```python
# Complete workflow example
from agents.orchestrator.orchestrator import OrchestratorAgent
from agents.research.research import ResearchAgent

orchestrator = OrchestratorAgent()
research_agent = ResearchAgent()

# User request
request = WorkflowRequest(
    request_text="Create an article about AI agents",
    content_types=[ContentType.ARTICLE]
)

# Orchestrator routes to research
execution_plan = orchestrator.process(request)

# Research agent executes
research_brief = research_agent.process({
    "topic": "AI agents for automation"
})

# Brief is passed to content-brief skill and then creation agent
# (This will be implemented in Phase 2)
```

## Error Handling

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Insufficient sources | Topic too specific or misspelled | Broaden query, check spelling |
| Low credibility scores | Limited high-quality sources available | Accept lower threshold or expand search |
| Research gaps | Missing focus areas | Add additional targeted searches |
| Empty key findings | Poor source content | Manual extraction or retry |

### Example Error Handling

```python
try:
    research_brief = agent.process(input_data)

    is_valid, errors = research_brief.validate()
    if not is_valid:
        # Handle specific errors
        if "At least 2 sources required" in errors:
            # Retry with broader query
            input_data["topic"] += " introduction"
            research_brief = agent.process(input_data)
        elif "high-quality source" in errors:
            # Lower threshold
            agent.min_credibility = 0.4
            research_brief = agent.process(input_data)

except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Research failed: {e}")
```

## Logging and Monitoring

The agent logs execution details for debugging:

```python
# View execution history
summary = agent.get_execution_summary()
print(f"Total executions: {summary['total_executions']}")

# Access execution log
for record in agent.execution_history:
    print(f"{record['timestamp']}: {record['metadata']}")
```

### Log Output Example

```
INFO - Starting research on topic: AI agents for automation
INFO - Found 12 initial search results
INFO - Evaluated 12 sources
INFO - Selected 8 quality sources
INFO - Execution logged: {'total_sources': 12, 'quality_sources': 8, 'key_findings_count': 5}
```

## Performance Considerations

- **Search Results**: Limiting to 10 sources balances quality and performance
- **Content Extraction**: Regex-based extraction is fast but may miss complex patterns
- **Credibility Calculation**: O(n) complexity, scales linearly with source count

## Future Enhancements (Phase 2+)

- [ ] Integration with actual WebSearch tool/API
- [ ] Fact-checking across multiple sources
- [ ] API integrations for market data, statistics
- [ ] Machine learning-based credibility scoring
- [ ] Entity extraction and relationship mapping
- [ ] Automatic query refinement based on results
- [ ] Research caching for common topics
- [ ] Multi-language support

## Testing

See `examples/research_example.py` for complete usage examples.

```bash
# Run research agent example
python examples/research_example.py
```
