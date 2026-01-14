# Web Search Skill

## Purpose

Execute optimized web searches and return structured results for the Research Agent. Handles query optimization, result parsing, deduplication, and relevance filtering.

## Skill Type

**Research Skill** - Used by the Research Agent to gather source material.

## Key Functions

- Query optimization based on requirements
- Web search execution (via WebSearch tool)
- Result parsing and normalization
- Relevance filtering
- Deduplication
- Result structuring

## Configuration

```python
config = {
    "max_results": 10,           # Maximum results to return
    "enable_filtering": True     # Enable relevance filtering
}

skill = WebSearchSkill(config)
```

## Usage

### Basic Search

```python
from skills.web_search.web_search import WebSearchSkill

skill = WebSearchSkill()

# Execute search
results = skill.execute(
    query="AI content generation",
    max_results=10
)

print(f"Found {len(results)} results")
```

### With Query Optimization

```python
skill = WebSearchSkill()

# Define requirements
requirements = {
    "recent_only": True,
    "content_type": "technical",
    "domains": ["arxiv.org", "ieee.org"],
    "must_include": ["machine learning"],
    "exclude": ["marketing"]
}

# Optimize query
base_query = "AI agents"
optimized_query = skill.optimize_query(base_query, requirements)
# Result: "AI agents 2024 (site:arxiv.org OR site:ieee.org) "machine learning" -"marketing""

# Execute with optimized query
results = skill.execute(optimized_query, max_results=15)
```

### Integration with Research Agent

```python
from agents.research.research import ResearchAgent
from skills.web_search.web_search import WebSearchSkill

agent = ResearchAgent()
search_skill = WebSearchSkill()

# Prepare search
topic = "Multi-agent content systems"
requirements = {"recent_only": True}

# Optimize query
query = search_skill.optimize_query(topic, requirements)

# Execute search (with WebSearch tool)
# search_results = WebSearch(query)  # Using Claude's WebSearch tool

# Parse and normalize results
# parsed = [search_skill.parse_search_result(r) for r in search_results]

# Process with Research Agent
# research_brief = agent.process({"topic": topic, "search_results": parsed})
```

## Query Optimization Rules

### Time Constraints

| Requirement | Query Modification | Example |
|-------------|-------------------|---------|
| `recent_only: true` | Adds current year | "AI agents 2024" |
| `year: 2023` | Adds specific year | "AI agents 2023" |

### Domain Restrictions

| Requirement | Query Modification | Example |
|-------------|-------------------|---------|
| `domains: ["edu", "org"]` | Adds site: operators | "(site:edu OR site:org)" |

### Term Requirements

| Requirement | Query Modification | Example |
|-------------|-------------------|---------|
| `must_include: ["ML"]` | Adds quoted terms | `"ML"` |
| `exclude: ["marketing"]` | Adds minus operator | `-"marketing"` |

### Content Type Hints

| Type | Added Terms |
|------|-------------|
| `technical` | "technical implementation" |
| `business` | "business impact" |

## Result Format

Returns list of standardized result dictionaries:

```python
{
    "title": str,              # Article/page title
    "url": str,                # Source URL
    "content": str,            # Content preview or full text
    "published_date": str,     # Publication date (ISO format)
    "author": str,             # Author name (optional)
    "source": str              # Source/domain name
}
```

## Filtering Logic

### Relevance Filtering

When `enable_filtering: True`, results are filtered based on:

1. **Query Term Matching**
   - Title matches: weight = 2x
   - Content matches: weight = 1x

2. **Relevance Scoring**
   - Calculates `_relevance_score` for each result
   - Filters out results with no matches
   - Sorts by relevance (highest first)

3. **Quality Indicators**
   - Content length > minimum threshold
   - Presence of author/date
   - Domain reputation

### Deduplication

Removes duplicate results based on:
- Exact URL matches
- Identical titles (case-insensitive)

## Methods

### `execute(query, max_results, **kwargs)`

Execute a web search.

**Parameters:**
- `query` (str): Search query string
- `max_results` (int, optional): Maximum results to return
- `**kwargs`: Additional search parameters

**Returns:** List of result dictionaries

### `optimize_query(base_query, requirements)`

Optimize a search query based on requirements.

**Parameters:**
- `base_query` (str): Base search query
- `requirements` (dict): Search requirements

**Returns:** Optimized query string

### `parse_search_result(raw_result)`

Parse a raw search result into standard format.

**Parameters:**
- `raw_result` (Any): Raw result from search API

**Returns:** Standardized result dictionary

## Integration Points

### Claude WebSearch Tool

To integrate with Claude's WebSearch tool:

```python
from skills.web_search.web_search import WebSearchSkill

skill = WebSearchSkill()

# Prepare query
query = skill.optimize_query("AI agents", {"recent_only": True})

# Execute search using WebSearch tool
# (This would be called in your agent implementation)
# results = WebSearch(query=query)

# Parse results
# parsed_results = [skill.parse_search_result(r) for r in results]
```

### Custom Search APIs

The skill can normalize results from different search APIs:

```python
# Google Custom Search
google_result = {
    "title": "Article Title",
    "link": "https://example.com",
    "snippet": "Preview text..."
}

# Bing Search
bing_result = {
    "name": "Article Title",
    "url": "https://example.com",
    "description": "Preview text..."
}

# Normalize both
parsed_google = skill.parse_search_result(google_result)
parsed_bing = skill.parse_search_result(bing_result)
# Both return the same standardized format
```

## Performance Considerations

- **Query Optimization**: O(1) - Simple string operations
- **Filtering**: O(n) where n = number of results
- **Deduplication**: O(n) with set lookups

**Recommended Limits:**
- Max results: 10-20 for balance of quality and speed
- Enable filtering for better quality results
- Use domain restrictions for focused searches

## Error Handling

```python
try:
    results = skill.execute(query)

    if not results:
        print("No results found - try broader query")

    if len(results) < expected_minimum:
        print("Fewer results than expected - check query")

except Exception as e:
    print(f"Search failed: {e}")
```

## Future Enhancements

- [ ] Machine learning-based relevance scoring
- [ ] Semantic search capabilities
- [ ] Result caching for common queries
- [ ] A/B testing of query optimizations
- [ ] Multi-language support
- [ ] Image and video search
- [ ] Real-time search result updates

## Dependencies

- Python 3.8+
- Base Agent/Skill classes
- Web search API access (WebSearch tool or custom API)

## Testing

See `examples/research_example.py` for complete usage examples.

```bash
python examples/research_example.py
```

## Related Skills

- **source-eval** (integrated in Research Agent) - Evaluates source credibility
- **fact-check** (planned) - Cross-references facts across sources
- **data-pull** (planned) - Fetches structured data from APIs
