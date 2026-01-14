# Source Evaluation Skill

## Purpose

Evaluates the credibility and quality of information sources for content research. Provides objective scoring based on domain reputation, content quality, recency, and other factors.

## Function

- Domain credibility scoring
- Content quality assessment
- Recency scoring
- Fact and quote extraction
- Source categorization

## Usage

```python
from skills.source_eval.source_eval import SourceEvalSkill

# Initialize skill
eval_skill = SourceEvalSkill()

# Evaluate a source
source = eval_skill.execute(
    url="https://arxiv.org/abs/2024.12345",
    title="Multi-Agent Systems: A Survey",
    snippet="Comprehensive review of agent architectures...",
    author="Jane Smith",
    publication_date="2025-01-10",
    full_content="[Full article text...]"
)

# Check credibility
print(f"Credibility: {source.credibility_score:.2f}")
print(f"Key facts: {source.key_facts}")
print(f"Key quotes: {source.key_quotes}")

# Categorize source
category = eval_skill.categorize_source(source.url)
print(f"Category: {category}")  # e.g., "academic"
```

## Credibility Scoring

### Scoring Factors

The credibility score (0.0 to 1.0) is calculated using weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Domain Reputation | 0.4 | Based on trusted domain list |
| Recency | 0.2 | How recent the content is |
| Author Presence | 0.1 | Whether author is attributed |
| Content Quality | 0.3 | Length, structure, citations |

### Domain Reputation Tiers

**High Credibility (0.85-0.95):**
- Academic: `.edu`, `arxiv.org`, `scholar.google.com`, `ieee.org`, `nature.com`, `science.org`
- Government: `.gov` domains
- Research: `ncbi.nlm.nih.gov`, `sciencedirect.com`

**Medium Credibility (0.65-0.8):**
- Established Media: `reuters.com`, `apnews.com`, `bbc.com`, `nytimes.com`
- Tech Publications: `techcrunch.com`, `wired.com`, `arstechnica.com`
- Business: `hbr.org`, `forbes.com`, `wsj.com`, `economist.com`

**Neutral (0.5-0.7):**
- Community: `stackoverflow.com`, `github.com`
- Variable Quality: `medium.com`

**Low Credibility (<0.5):**
- Invalid URLs
- Unknown domains with quality issues

### Recency Scoring

Content age affects the score:

| Age | Score | Notes |
|-----|-------|-------|
| 0-30 days | 1.0 | Very recent |
| 30-180 days | 0.9 | Recent |
| 180-365 days | 0.8 | Current year |
| 1-2 years | 0.7 | Fairly recent |
| 2-3 years | 0.6 | Somewhat dated |
| 3+ years | 0.5 | May be outdated |

### Content Quality Indicators

**Positive Indicators (+0.1 each):**
- Substantial length (>1000 chars)
- Very long content (>2000 chars)
- Contains citations/references
- Includes data or statistics

**Negative Indicators (-0.2):**
- Clickbait phrases ("you won't believe", "shocking", etc.)

## Source Categorization

Sources are categorized by domain:

| Category | Domains |
|----------|---------|
| `academic` | arxiv.org, scholar.google.com, ncbi.nlm.nih.gov, ieee.org |
| `government` | .gov domains |
| `news` | reuters.com, apnews.com, bbc.com, nytimes.com |
| `industry` | techcrunch.com, wired.com, arstechnica.com |
| `business` | hbr.org, forbes.com, wsj.com, economist.com |
| `community` | stackoverflow.com, github.com, medium.com |
| `general` | Other recognized domains |
| `unknown` | Unrecognized domains |

## Information Extraction

### Key Facts

Extracted from content using pattern matching:
- Sentences with statistics (numbers, percentages)
- Sentences with large numbers (millions, billions)
- Definitive statements (is, are, has, will)
- Length: 30-200 characters
- Limit: Top 5 facts per source

### Key Quotes

Extracted quotable statements:
- Text within quotation marks (50-200 chars)
- Sentences with authority indicators ("research shows", "study found", "according to")
- Length: 50-300 characters
- Limit: Top 3 quotes per source

## Output Format

Returns a `Source` object:

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

## Example: Complete Evaluation

```python
from skills.source_eval.source_eval import SourceEvalSkill

skill = SourceEvalSkill()

# Evaluate a high-quality academic source
source = skill.execute(
    url="https://arxiv.org/abs/2024.12345",
    title="Multi-Agent Systems for Content Creation: A Survey",
    snippet="This paper surveys recent advances in multi-agent systems...",
    author="Dr. Jane Smith, MIT",
    publication_date="2025-01-10",
    full_content="""
    This paper surveys recent advances in multi-agent systems for automated
    content creation. Research shows that multi-agent architectures can
    improve content quality by 40% compared to single-agent systems.

    The study analyzed over 1,000 implementations across various domains.
    According to the findings, "agent coordination is the primary factor
    in system performance." The research demonstrates that properly designed
    agent handoffs can reduce errors by 60%.

    References: [1] Smith et al. 2024, [2] Jones et al. 2023...
    """
)

# Results
print(f"Credibility Score: {source.credibility_score:.2f}")
# Output: 0.95 (academic domain + recent + has author + quality content)

print(f"Category: {skill.categorize_source(source.url)}")
# Output: "academic"

print(f"Key Facts: {source.key_facts}")
# Output: [
#   "multi-agent architectures can improve content quality by 40%",
#   "The study analyzed over 1,000 implementations",
#   "agent handoffs can reduce errors by 60%"
# ]

print(f"Key Quotes: {source.key_quotes}")
# Output: ["agent coordination is the primary factor in system performance"]
```

## Integration with Research Agent

The Research Agent uses this skill to evaluate all sources:

```python
from agents.research.research import ResearchAgent

# Agent automatically uses SourceEvalSkill
agent = ResearchAgent(config={
    "min_credibility": 0.6  # Only accept sources >= 0.6
})

research_brief = agent.process({
    "topic": "AI agent systems"
})

# All sources in research_brief have been evaluated
for source in research_brief.sources:
    print(f"{source.title}: {source.credibility_score:.2f}")
```

## Configuration

```python
config = {
    # Add custom trusted domains
    "custom_domains": {
        "mycompany.com": 0.8,
        "industry-blog.com": 0.6
    }
}

skill = SourceEvalSkill(config)
```

## Methods

### `execute(url, title, snippet, author, publication_date, full_content)`
Evaluates a source and returns a Source object with credibility score.

**Args:**
- `url` (str): Source URL
- `title` (str): Article/page title
- `snippet` (str, optional): Brief description
- `author` (str, optional): Author name
- `publication_date` (str, optional): Publication date (ISO format)
- `full_content` (str, optional): Full article text

**Returns:**
- `Source` object with credibility score and extracted information

### `categorize_source(url)`
Categorizes the source type based on domain.

**Args:**
- `url` (str): Source URL

**Returns:**
- Category string (academic, news, government, etc.)

## Best Practices

1. **Always provide full content when available** - Improves fact/quote extraction
2. **Include publication dates** - Enables recency scoring
3. **Set appropriate credibility thresholds** - Higher for critical content (0.7+), lower for exploratory research (0.5+)
4. **Review extracted facts** - Automated extraction may miss context
5. **Combine with fact-checking** - Credibility scores don't verify accuracy

## Limitations

- Regex-based extraction may miss complex patterns
- Domain reputation is based on general reputation, not topic-specific authority
- Cannot verify factual accuracy (only assesses source credibility)
- Date parsing requires standard formats (ISO 8601 preferred)

## Future Enhancements

- [ ] Machine learning-based credibility prediction
- [ ] Topic-specific domain authority
- [ ] Cross-source fact verification
- [ ] Advanced NLP for fact/quote extraction
- [ ] Citation network analysis
- [ ] Author reputation tracking
- [ ] Bias detection and political leaning analysis
- [ ] Paywall detection and access scoring
