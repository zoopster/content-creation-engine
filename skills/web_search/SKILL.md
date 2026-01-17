# Web Search Skill

## Purpose

Execute real web searches and return structured results for the Research Agent. Supports multiple search providers (Firecrawl, Serper) with automatic fallback to mock data for testing.

## Skill Type

**Research Skill** - Used by the Research Agent to gather source material from the web.

## Key Features

- **Multiple Search Providers**: Firecrawl (AI-optimized, recommended), Serper (Google Search API)
- **Query Optimization**: Automatic query enhancement for better results
- **Result Filtering**: Relevance scoring and deduplication
- **Async Support**: Non-blocking search execution
- **Content Extraction**: Firecrawl provides automatic markdown extraction
- **Mock Mode**: Testing without API keys

## Configuration

### Environment Variables

```bash
# Enable real web search
ENABLE_WEB_SEARCH=true

# Search provider API keys (at least one required for real search)
FIRECRAWL_API_KEY=fc-...   # Recommended: https://firecrawl.dev/
SERPER_API_KEY=...         # Alternative: https://serper.dev/

# Optional: Default provider
DEFAULT_SEARCH_PROVIDER=firecrawl
```

### Skill Configuration

```python
from skills.web_search import WebSearchSkill

config = {
    "provider": "firecrawl",        # Search provider (firecrawl, serper, mock)
    "max_results": 10,              # Maximum results to return
    "enable_filtering": True,       # Enable relevance filtering
    "search_depth": "basic",        # basic or advanced
    "include_raw_content": False,   # Include full page content
}

skill = WebSearchSkill(config)
```

## Usage

### Basic Search

```python
from skills.web_search import WebSearchSkill

skill = WebSearchSkill()

# Synchronous search
results = skill.execute("AI content generation", max_results=10)

# Asynchronous search
results = await skill.execute_async("AI content generation", max_results=10)

for result in results:
    print(f"{result['title']}: {result['url']}")
```

### With Domain Filtering

```python
results = await skill.execute_async(
    "machine learning tutorials",
    max_results=10,
    include_domains=["arxiv.org", "ieee.org"],
    exclude_domains=["medium.com"],
    time_range="month",  # day, week, month, year
)
```

### Query Optimization

```python
skill = WebSearchSkill()

requirements = {
    "recent_only": True,
    "content_type": "technical",
    "must_include": ["machine learning"],
    "exclude": ["marketing"],
}

optimized = skill.optimize_query("AI agents", requirements)
# Result: "AI agents 2026 technical guide implementation "machine learning" -"marketing""
```

### Multiple Query Search

```python
queries = [
    "AI content generation tools",
    "multi-agent systems architecture",
    "automated content workflow",
]

# Execute all queries in parallel
results = await skill.search_multiple_queries(queries, max_results_per_query=5)
```

## Search Providers

### Firecrawl (Recommended)

AI-optimized search with built-in content extraction and markdown conversion.

```python
from core.search import FirecrawlSearchProvider

provider = FirecrawlSearchProvider(api_key="fc-your-key")
results = await provider.search("AI healthcare", SearchConfig(max_results=10))
```

Features:
- High-quality, AI-relevant results
- Automatic markdown content extraction
- URL scraping capabilities
- Deep research mode
- Relevance scoring

### Serper (Google Search)

Access to Google Search results via simple API.

```python
from core.search import SerperSearchProvider

provider = SerperSearchProvider(api_key="your-key")
results = await provider.search("AI healthcare", SearchConfig(max_results=10))
```

Features:
- Google Search results
- News search support
- Knowledge graph integration
- Position-based ranking

### Mock Provider

For testing without API keys.

```python
from core.search.base import MockSearchProvider

provider = MockSearchProvider()
results = await provider.search("test query")  # Returns realistic mock data
```

## Result Format

```python
{
    "url": str,                # Source URL
    "title": str,              # Page/article title
    "content": str,            # Content snippet or full text (markdown with Firecrawl)
    "published_date": str,     # Publication date (ISO format)
    "author": str,             # Author name (if available)
    "source": str,             # Domain name
    "score": float,            # Relevance score (0.0-1.0)
}
```

## Integration with Research Agent

```python
from agents.research import LLMResearchAgent

# Research agent with Firecrawl web search
agent = LLMResearchAgent(config={
    "enable_web_search": True,
    "search_provider": "firecrawl",
})

# Execute research with live search
brief = await agent.process_async({
    "topic": "AI in healthcare",
    "requirements": {
        "recent_only": True,
        "content_type": "technical",
    }
})

print(f"Found {len(brief.sources)} sources")
for source in brief.sources:
    print(f"  - {source.title} (credibility: {source.credibility_score:.2f})")
```

## Firecrawl Advanced Features

### URL Scraping

```python
from core.search import FirecrawlSearchProvider

provider = FirecrawlSearchProvider(api_key="fc-your-key")

# Scrape a single URL
content = await provider.get_content("https://example.com/article")
print(content)  # Returns markdown content
```

### Deep Research

```python
# Comprehensive research on a topic
research = await provider.deep_research(
    "AI in healthcare trends 2025",
    max_depth=3,
    max_urls=50,
    time_limit=120,
)
```

## Filtering Logic

### Relevance Filtering

When `enable_filtering=True`, results are scored based on:

1. **Title Matches**: 2x weight per query term
2. **Content Matches**: 1x weight per query term
3. **Provider Score**: 5x weight (if available)

Results with score < threshold are filtered out.

### Deduplication

Removes duplicate results based on:
- Exact URL matches
- Identical titles (case-insensitive)

## Error Handling

```python
try:
    results = await skill.execute_async(query)

    if not results:
        print("No results found - try broader query")

except Exception as e:
    print(f"Search failed: {e}")
    # Skill automatically falls back to mock data
```

## Performance Tips

1. **Use Basic Search Depth**: Advanced depth uses more API credits
2. **Limit Results Per Query**: 5-10 per query is usually sufficient
3. **Enable Filtering**: Reduces noise from irrelevant results
4. **Leverage Content Extraction**: Firecrawl extracts markdown automatically
5. **Use Domain Filters**: Narrow searches to authoritative sources

## Related Components

- **LLMResearchAgent**: Uses this skill for research
- **SourceEvalSkill**: Evaluates source credibility
- **SearchConfig**: Configuration options
- **SearchResult**: Result data structure

## Dependencies

```
firecrawl-py>=1.0.0     # Firecrawl search provider (recommended)
aiohttp>=3.9.0          # Async HTTP for Serper
```

## Testing

```bash
# Run with mock search (no API key needed)
python examples/web_search_example.py

# Run with Firecrawl
ENABLE_WEB_SEARCH=true FIRECRAWL_API_KEY=fc-your-key python examples/web_search_example.py
```
