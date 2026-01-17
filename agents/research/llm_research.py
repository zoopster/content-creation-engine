"""
LLM-Enabled Research Agent - Gathers and analyzes source material using LLM.

This module extends the base ResearchAgent with LLM-powered capabilities:
- Query optimization for better search results
- Intelligent source analysis and credibility assessment
- Deep extraction of facts, quotes, and insights
- Synthesis of findings across multiple sources
- Gap identification and research recommendations
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from agents.base.agent import Agent
from agents.base.models import ResearchBrief, Source
from core.models import (
    AgentModelConfig,
    GenerationConfig,
    GenerationResult,
    Message,
    ModelRegistry,
    get_registry,
)


class LLMResearchAgent(Agent):
    """
    LLM-powered research agent for intelligent source gathering and analysis.

    Uses configurable LLM providers for:
    - Optimizing search queries
    - Analyzing source content for relevance and credibility
    - Extracting structured facts, quotes, and insights
    - Synthesizing findings into coherent research briefs
    - Identifying gaps and recommending additional research

    Usage:
        # With default configuration (uses mock search)
        agent = LLMResearchAgent()
        brief = await agent.process_async({"topic": "AI in healthcare"})

        # With custom model configuration
        agent = LLMResearchAgent(config={
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.3
        })

        # With real web search (Tavily)
        agent = LLMResearchAgent(config={
            "search_provider": "tavily",
            "enable_web_search": True
        })

        # With Serper search
        agent = LLMResearchAgent(config={
            "search_provider": "serper",
            "enable_web_search": True
        })

    Environment variables for search:
        TAVILY_API_KEY - Tavily API key
        SERPER_API_KEY - Serper API key
        ENABLE_WEB_SEARCH - Enable real web search (true/false)
    """

    # System prompts for different research tasks
    SYSTEM_PROMPTS = {
        "query_optimization": """You are a search query optimization expert. Given a research
topic and requirements, generate optimized search queries that will find high-quality,
relevant sources. Consider:
- Adding specific terms to improve precision
- Including date filters for recency
- Adding domain-specific terminology
- Considering multiple angles on the topic

Output format: JSON array of 3-5 optimized search queries.""",

        "source_analysis": """You are a research analyst evaluating source credibility and
extracting key information. For each source, analyze:
1. Credibility indicators (author expertise, publication reputation, citations)
2. Content relevance to the research topic
3. Key facts with supporting evidence
4. Notable quotes from experts or studies
5. Data points and statistics

Be objective and thorough. Distinguish between facts and opinions.""",

        "fact_extraction": """You are a fact-checker and information extractor. Extract
verifiable facts from the provided content. For each fact:
- State the fact clearly and concisely
- Note any statistics or numbers mentioned
- Identify the source of the claim if mentioned
- Rate confidence level (high/medium/low)

Focus on concrete, verifiable information rather than opinions or speculation.""",

        "synthesis": """You are a research synthesizer who combines findings from multiple
sources into coherent insights. Your task:
1. Identify common themes across sources
2. Note areas of agreement and disagreement
3. Highlight the most important findings
4. Identify gaps in the research
5. Suggest areas for further investigation

Be balanced and evidence-based in your synthesis.""",

        "gap_analysis": """You are a research completeness analyst. Given the research
findings and original requirements, identify:
1. Topics or questions not adequately addressed
2. Missing perspectives or viewpoints
3. Areas needing more authoritative sources
4. Potential biases in the current research
5. Suggested additional research directions

Be specific and actionable in your recommendations.""",
    }

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[ModelRegistry] = None,
    ):
        """
        Initialize the LLM Research Agent.

        Args:
            config: Configuration dictionary with optional keys:
                - provider: LLM provider name (default: from registry)
                - model: Model ID (default: from registry)
                - temperature: Generation temperature (default: 0.3 for accuracy)
                - max_tokens: Max tokens to generate (default: 4096)
                - min_sources: Minimum sources to include (default: 3)
                - max_sources: Maximum sources to include (default: 10)
                - min_credibility: Minimum credibility score (default: 0.5)
                - search_provider: Web search provider (tavily, serper, mock)
                - enable_web_search: Enable real web search (default: from env)
            registry: Model registry instance (default: global registry)
        """
        super().__init__("research", config)

        self.registry = registry or get_registry()

        # Research settings
        config = config or {}
        self.min_sources = config.get("min_sources", 3)
        self.max_sources = config.get("max_sources", 10)
        self.min_credibility = config.get("min_credibility", 0.5)

        # Search settings
        self.search_provider_name = config.get("search_provider")
        self._search_provider = None

        # Check if web search is enabled (from config or environment)
        env_enable = os.environ.get("ENABLE_WEB_SEARCH", "").lower() == "true"
        self.enable_web_search = config.get("enable_web_search", env_enable)

        # Build model configuration
        provider = config.get("provider")
        model = config.get("model")

        if provider and model:
            gen_config = GenerationConfig(
                max_tokens=config.get("max_tokens", 4096),
                temperature=config.get("temperature", 0.3),  # Lower for accuracy
            )
            self._model_config = AgentModelConfig(
                provider=provider,
                model=model,
                config=gen_config,
            )
        else:
            self._model_config = None

    def _get_model_config(self) -> AgentModelConfig:
        """Get model configuration, falling back to registry defaults."""
        if self._model_config:
            return self._model_config
        return self.registry.get_agent_config("research")

    async def process_async(self, input_data: Dict[str, Any]) -> ResearchBrief:
        """
        Execute LLM-powered research workflow.

        Args:
            input_data: Dictionary with:
                - topic: Research topic (required)
                - requirements: Optional requirements dict with:
                    - focus_areas: List of specific areas to research
                    - recent_only: Boolean for recency filter
                    - content_type: "technical", "business", etc.
                    - depth: "quick", "standard", "comprehensive"

        Returns:
            ResearchBrief with LLM-analyzed sources and synthesized findings
        """
        topic = input_data.get("topic")
        if not topic:
            raise ValueError("Topic is required for research")

        requirements = input_data.get("requirements", {})

        self.logger.info(f"Starting LLM-powered research on topic: {topic}")

        # Step 1: Optimize search queries using LLM
        optimized_queries = await self._optimize_queries(topic, requirements)
        self.logger.info(f"Generated {len(optimized_queries)} optimized queries")

        # Step 2: Execute searches (mock for now, real integration later)
        search_results = await self._execute_search(topic, optimized_queries)
        self.logger.info(f"Found {len(search_results)} search results")

        # Step 3: Analyze sources using LLM
        analyzed_sources = await self._analyze_sources(search_results, topic)
        self.logger.info(f"Analyzed {len(analyzed_sources)} sources")

        # Filter by credibility
        quality_sources = [
            s for s in analyzed_sources
            if s.credibility_score >= self.min_credibility
        ][:self.max_sources]

        self.logger.info(f"Selected {len(quality_sources)} quality sources")

        # Step 4: Synthesize findings using LLM
        key_findings = await self._synthesize_findings(quality_sources, topic)

        # Step 5: Extract data points
        data_points = self._extract_data_points(quality_sources)

        # Step 6: Identify gaps using LLM
        research_gaps = await self._identify_gaps(
            quality_sources, key_findings, requirements, topic
        )

        # Create research brief
        research_brief = ResearchBrief(
            topic=topic,
            sources=quality_sources,
            key_findings=key_findings,
            data_points=data_points,
            research_gaps=research_gaps,
        )

        # Validate
        is_valid, errors = research_brief.validate()
        if not is_valid:
            self.logger.warning(f"Research brief validation issues: {errors}")

        self.log_execution(
            input_data,
            research_brief,
            {
                "total_sources": len(search_results),
                "quality_sources": len(quality_sources),
                "key_findings_count": len(key_findings),
                "model": self._get_model_config().model,
            },
        )

        return research_brief

    def process(self, input_data: Dict[str, Any]) -> ResearchBrief:
        """Synchronous wrapper for process_async."""
        return asyncio.run(self.process_async(input_data))

    async def _optimize_queries(
        self, topic: str, requirements: Dict[str, Any]
    ) -> List[str]:
        """
        Use LLM to generate optimized search queries.

        Args:
            topic: Research topic
            requirements: Research requirements

        Returns:
            List of optimized search queries
        """
        model_config = self._get_model_config()

        prompt = f"""Generate optimized search queries for researching the following topic:

Topic: {topic}

Requirements:
- Focus areas: {requirements.get('focus_areas', ['general overview'])}
- Recency preference: {'Recent content only' if requirements.get('recent_only') else 'Any time period'}
- Content type: {requirements.get('content_type', 'general')}
- Research depth: {requirements.get('depth', 'standard')}

Generate 3-5 search queries that will find high-quality, authoritative sources.
Each query should target different aspects or angles of the topic.

Output as a JSON array of strings, like: ["query 1", "query 2", "query 3"]"""

        try:
            result = await self.registry.generate(
                prompt=prompt,
                provider=model_config.provider,
                model=model_config.model,
                config=GenerationConfig(
                    max_tokens=500,
                    temperature=0.3,
                    system_prompt=self.SYSTEM_PROMPTS["query_optimization"],
                ),
            )

            # Parse JSON response
            queries = self._parse_json_array(result.content)
            if queries:
                return queries

        except Exception as e:
            self.logger.warning(f"LLM query optimization failed: {e}")

        # Fallback to basic query generation
        return self._generate_fallback_queries(topic, requirements)

    def _generate_fallback_queries(
        self, topic: str, requirements: Dict[str, Any]
    ) -> List[str]:
        """Generate basic search queries without LLM."""
        queries = [topic]

        if requirements.get("recent_only"):
            queries.append(f"{topic} {datetime.now().year}")

        focus_areas = requirements.get("focus_areas", [])
        for area in focus_areas[:2]:
            queries.append(f"{topic} {area}")

        content_type = requirements.get("content_type")
        if content_type == "technical":
            queries.append(f"{topic} technical implementation guide")
        elif content_type == "business":
            queries.append(f"{topic} business impact ROI")

        return queries[:5]

    def _get_search_provider(self):
        """Get or initialize the search provider."""
        if self._search_provider is None:
            try:
                from core.search import configure_search, get_search_provider

                # Configure search based on settings
                use_mock = not self.enable_web_search
                configure_search(
                    provider=self.search_provider_name,
                    use_mock=use_mock,
                )
                self._search_provider = get_search_provider(self.search_provider_name)

                if self._search_provider:
                    self.logger.info(
                        f"Research agent using search provider: {self._search_provider.name}"
                    )

            except ImportError as e:
                self.logger.warning(f"Search providers not available: {e}")
                self._search_provider = None

        return self._search_provider

    async def _execute_search(
        self, topic: str, queries: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Execute web searches using configured provider.

        Uses real search providers (Tavily, Serper) when enabled,
        otherwise falls back to mock data for testing.

        Args:
            topic: Research topic
            queries: Optimized search queries

        Returns:
            List of search results
        """
        provider = self._get_search_provider()

        # If provider is available and not mock, use real search
        if provider and provider.name != "mock":
            return await self._execute_real_search(queries, provider)

        # Fall back to mock results
        self.logger.info("Using mock search results (set ENABLE_WEB_SEARCH=true for real search)")
        return self._generate_mock_results(topic, queries)

    async def _execute_real_search(
        self, queries: List[str], provider
    ) -> List[Dict[str, Any]]:
        """
        Execute real web searches using the configured provider.

        Args:
            queries: Search queries to execute
            provider: Search provider instance

        Returns:
            List of search results
        """
        from core.search.base import SearchConfig

        all_results = []
        seen_urls = set()

        # Execute each query
        for query in queries:
            try:
                config = SearchConfig(
                    max_results=5,  # Limit per query to avoid too many results
                    search_depth="basic",
                )

                results = await provider.search(query, config)

                for result in results:
                    # Deduplicate by URL
                    if result.url not in seen_urls:
                        seen_urls.add(result.url)
                        all_results.append({
                            "url": result.url,
                            "title": result.title,
                            "content": result.content,
                            "published_date": result.published_date,
                            "author": result.author,
                            "source": result.source,
                        })

                self.logger.debug(f"Query '{query}' returned {len(results)} results")

            except Exception as e:
                self.logger.warning(f"Search query failed: {query} - {e}")
                continue

        self.logger.info(f"Real search returned {len(all_results)} unique results")
        return all_results

    def _generate_mock_results(
        self, topic: str, queries: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate realistic mock search results."""
        words = topic.split()
        key_term = words[0] if words else "topic"

        results = [
            {
                "url": f"https://research.edu/{key_term.lower()}-comprehensive-study",
                "title": f"Comprehensive Study on {topic.title()}: Evidence and Outcomes",
                "author": "Dr. Sarah Chen, PhD",
                "published_date": "2025-11-15",
                "content": f"""This peer-reviewed study examines the impact of {topic.lower()}
across multiple industries. Our research involved 1,247 participants from 89 organizations
over a 24-month period.

Key findings indicate that {topic.lower()} implementation leads to:
- 42% improvement in operational efficiency
- 28% reduction in costs over 18 months
- 67% of participants reporting positive outcomes

Dr. James Morrison, a leading expert in the field, notes: "The evidence clearly
supports strategic investment in {topic.lower()}. Organizations that adopt early
see sustained competitive advantages."

Statistical analysis (p < 0.001) confirms strong correlation between {topic.lower()}
adoption and improved performance metrics. The research methodology included
randomized controlled trials and longitudinal tracking.

Limitations include potential selection bias and the need for longer-term studies.
Future research should examine sector-specific variations.""",
            },
            {
                "url": f"https://techcrunch.com/{key_term.lower()}-industry-trends-2026",
                "title": f"Industry Report: {topic.title()} Trends Shaping 2026",
                "author": "Maria Rodriguez, Technology Editor",
                "published_date": "2026-01-08",
                "content": f"""The {topic.lower()} landscape is evolving rapidly as enterprises
accelerate adoption. According to Gartner's latest report, 73% of organizations
plan to increase {topic.lower()} investments this year.

Market analysis reveals:
- Global market size projected to reach $156 billion by 2028
- Year-over-year growth rate of 34%
- Enterprise adoption up 45% from previous year

"We're seeing a fundamental shift in how companies approach {topic.lower()},"
says industry analyst Mark Thompson. "Early skepticism has given way to
strategic prioritization."

Key trends include integration with existing workflows, emphasis on ROI
measurement, and growing focus on scalability. Major vendors including
Microsoft, Google, and Amazon are expanding their offerings.

Challenges remain around talent acquisition, with 58% of organizations
reporting skills gaps as a primary concern.""",
            },
            {
                "url": f"https://hbr.org/{key_term.lower()}-strategic-implementation",
                "title": f"Strategic Implementation of {topic.title()}: A Framework",
                "author": "Prof. Michael Chang, Harvard Business School",
                "published_date": "2025-10-22",
                "content": f"""Successful {topic.lower()} implementation requires more than
technology investment—it demands strategic alignment and organizational change.

Our research across 200 Fortune 500 companies identifies five critical success factors:

1. Executive sponsorship: 89% of successful implementations had C-suite champions
2. Change management: Organizations with formal programs saw 3x better outcomes
3. Phased rollout: Incremental approaches reduced risk by 60%
4. Metrics alignment: Clear KPIs correlated with 45% higher success rates
5. Culture readiness: Cultural fit assessments predicted outcomes with 78% accuracy

"The technology is only 30% of the equation," notes transformation expert
Lisa Park. "The remaining 70% is people and process."

ROI analysis shows average payback period of 14 months for well-executed
implementations. However, 35% of projects fail to meet initial objectives,
typically due to inadequate planning or change resistance.""",
            },
            {
                "url": f"https://nature.com/articles/{key_term.lower()}-scientific-review",
                "title": f"Scientific Review: {topic.title()} - Current State and Future Directions",
                "author": "Dr. Emily Watson et al.",
                "published_date": "2025-09-30",
                "content": f"""This systematic review analyzes 156 peer-reviewed studies on
{topic.lower()} published between 2020-2025.

Meta-analysis findings:
- Effect size (Cohen's d): 0.72 (medium-large effect)
- Heterogeneity: I² = 45% (moderate)
- Publication bias: Egger's test p = 0.23 (not significant)

The evidence base strongly supports {topic.lower()} efficacy across multiple
outcome measures. Subgroup analysis reveals larger effects in:
- Technology sector (d = 0.89)
- Healthcare applications (d = 0.81)
- Financial services (d = 0.67)

Mechanistic studies suggest {topic.lower()} works through improved information
processing and decision-making capabilities. Neural imaging studies (n = 234)
show consistent patterns of enhanced cognitive efficiency.

Research gaps include long-term outcome data, cost-effectiveness analyses,
and understanding of individual variation in response.""",
            },
            {
                "url": f"https://forbes.com/{key_term.lower()}-roi-analysis",
                "title": f"The ROI Reality: What {topic.title()} Actually Delivers",
                "author": "David Kim, Business Analyst",
                "published_date": "2025-12-01",
                "content": f"""Beyond the hype, what returns are companies actually seeing from
{topic.lower()} investments? We analyzed financial data from 500 implementations.

Financial outcomes:
- Average ROI: 287% over 3 years
- Median payback period: 16 months
- Cost reduction: 23-31% in operational expenses

However, results vary significantly:
- Top quartile: 450%+ ROI
- Bottom quartile: Negative returns (15% of cases)

"Success isn't guaranteed," cautions CFO Jennifer Adams. "The difference
between winners and losers comes down to execution and strategic fit."

Investment patterns show:
- Initial investment: $2.3M average for mid-size companies
- Ongoing costs: 15-20% of initial investment annually
- Hidden costs: Training (often underestimated by 40%)

Best practices from high performers include rigorous vendor selection,
pilot programs before full rollout, and continuous optimization cycles.""",
            },
        ]

        return results

    async def _analyze_sources(
        self, search_results: List[Dict[str, Any]], topic: str
    ) -> List[Source]:
        """
        Analyze sources using LLM for credibility and content extraction.

        Args:
            search_results: Raw search results
            topic: Research topic for relevance assessment

        Returns:
            List of analyzed Source objects
        """
        sources = []
        model_config = self._get_model_config()

        for result in search_results:
            # Use LLM to analyze each source
            analysis = await self._analyze_single_source(result, topic, model_config)

            source = Source(
                url=result.get("url", ""),
                title=result.get("title", ""),
                author=result.get("author"),
                publication_date=result.get("published_date"),
                credibility_score=analysis.get("credibility_score", 0.5),
                key_quotes=analysis.get("key_quotes", []),
                key_facts=analysis.get("key_facts", []),
            )
            sources.append(source)

        # Sort by credibility
        sources.sort(key=lambda s: s.credibility_score, reverse=True)
        return sources

    async def _analyze_single_source(
        self,
        result: Dict[str, Any],
        topic: str,
        model_config: AgentModelConfig,
    ) -> Dict[str, Any]:
        """Analyze a single source using LLM."""
        prompt = f"""Analyze the following source for research on "{topic}":

URL: {result.get('url', 'N/A')}
Title: {result.get('title', 'N/A')}
Author: {result.get('author', 'Unknown')}
Published: {result.get('published_date', 'Unknown')}

Content:
{result.get('content', 'No content available')[:2000]}

Provide analysis in JSON format:
{{
    "credibility_score": <0.0-1.0 based on source authority, author expertise, publication reputation>,
    "relevance_score": <0.0-1.0 based on relevance to topic>,
    "key_facts": ["fact 1", "fact 2", "fact 3"],
    "key_quotes": ["quote 1", "quote 2"],
    "credibility_factors": ["factor 1", "factor 2"]
}}

Be objective. Extract only verifiable facts and direct quotes."""

        try:
            result_response = await self.registry.generate(
                prompt=prompt,
                provider=model_config.provider,
                model=model_config.model,
                config=GenerationConfig(
                    max_tokens=1000,
                    temperature=0.2,
                    system_prompt=self.SYSTEM_PROMPTS["source_analysis"],
                ),
            )

            analysis = self._parse_json_object(result_response.content)
            if analysis:
                return analysis

        except Exception as e:
            self.logger.warning(f"LLM source analysis failed: {e}")

        # Fallback to basic analysis
        return self._basic_source_analysis(result)

    def _basic_source_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Basic source analysis without LLM."""
        url = result.get("url", "")
        content = result.get("content", "")
        domain = urlparse(url).netloc.lower()

        # Calculate basic credibility
        score = 0.5
        if any(d in domain for d in ["edu", "gov", "nature.com", "science.org"]):
            score += 0.3
        elif any(d in domain for d in ["forbes.com", "hbr.org", "techcrunch.com"]):
            score += 0.2

        if result.get("author"):
            score += 0.1
        if len(content) > 500:
            score += 0.1

        score = min(1.0, score)

        # Extract basic facts (sentences with numbers)
        facts = []
        for sentence in content.split("."):
            if re.search(r"\d+%|\d+\s*(million|billion)", sentence):
                facts.append(sentence.strip())
                if len(facts) >= 3:
                    break

        # Extract quotes
        quotes = re.findall(r'"([^"]{30,200})"', content)[:2]

        return {
            "credibility_score": score,
            "relevance_score": 0.7,
            "key_facts": facts,
            "key_quotes": quotes,
            "credibility_factors": ["basic analysis"],
        }

    async def _synthesize_findings(
        self, sources: List[Source], topic: str
    ) -> List[str]:
        """
        Use LLM to synthesize key findings across sources.

        Args:
            sources: Analyzed sources
            topic: Research topic

        Returns:
            List of synthesized key findings
        """
        if not sources:
            return [f"Insufficient sources found for research on {topic}"]

        model_config = self._get_model_config()

        # Compile all facts from sources
        all_facts = []
        for source in sources:
            for fact in source.key_facts:
                all_facts.append(f"[{source.title}]: {fact}")

        prompt = f"""Synthesize key findings from research on "{topic}".

Sources analyzed: {len(sources)}
Average credibility: {sum(s.credibility_score for s in sources) / len(sources):.2f}

Facts extracted from sources:
{chr(10).join(all_facts[:20])}

Top quotes:
{chr(10).join(q for s in sources[:3] for q in s.key_quotes[:1])}

Generate 5-7 synthesized key findings that:
1. Combine insights from multiple sources
2. Highlight consensus and important disagreements
3. Prioritize well-supported claims
4. Note confidence levels where appropriate

Output as a JSON array of strings."""

        try:
            result = await self.registry.generate(
                prompt=prompt,
                provider=model_config.provider,
                model=model_config.model,
                config=GenerationConfig(
                    max_tokens=1500,
                    temperature=0.3,
                    system_prompt=self.SYSTEM_PROMPTS["synthesis"],
                ),
            )

            findings = self._parse_json_array(result.content)
            if findings:
                return findings[:7]

        except Exception as e:
            self.logger.warning(f"LLM synthesis failed: {e}")

        # Fallback: return top facts from high-credibility sources
        findings = []
        for source in sources:
            if source.credibility_score >= 0.7 and source.key_facts:
                findings.append(source.key_facts[0])
                if len(findings) >= 5:
                    break

        return findings or [f"Research on {topic} from {len(sources)} sources"]

    def _extract_data_points(self, sources: List[Source]) -> Dict[str, Any]:
        """Extract structured data points from sources."""
        data_points = {
            "source_count": len(sources),
            "high_credibility_sources": len(
                [s for s in sources if s.credibility_score >= 0.7]
            ),
            "average_credibility": (
                sum(s.credibility_score for s in sources) / len(sources)
                if sources
                else 0.0
            ),
            "total_facts_extracted": sum(len(s.key_facts) for s in sources),
            "total_quotes_extracted": sum(len(s.key_quotes) for s in sources),
            "source_domains": list(set(urlparse(s.url).netloc for s in sources)),
        }

        # Extract statistics
        statistics = []
        for source in sources:
            for fact in source.key_facts:
                percentages = re.findall(r"(\d+(?:\.\d+)?%)", fact)
                statistics.extend(percentages)
                large_numbers = re.findall(
                    r"(\$?\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|M|B))",
                    fact,
                    re.IGNORECASE,
                )
                statistics.extend(large_numbers)

        if statistics:
            data_points["statistics_found"] = list(set(statistics))[:15]

        return data_points

    async def _identify_gaps(
        self,
        sources: List[Source],
        findings: List[str],
        requirements: Dict[str, Any],
        topic: str,
    ) -> List[str]:
        """
        Use LLM to identify research gaps and recommendations.

        Args:
            sources: Analyzed sources
            findings: Synthesized findings
            requirements: Original requirements
            topic: Research topic

        Returns:
            List of identified gaps and recommendations
        """
        model_config = self._get_model_config()

        prompt = f"""Analyze research completeness for topic: "{topic}"

Requirements:
- Focus areas: {requirements.get('focus_areas', ['general'])}
- Content type: {requirements.get('content_type', 'general')}
- Depth requested: {requirements.get('depth', 'standard')}

Research summary:
- Sources found: {len(sources)}
- High-credibility sources: {len([s for s in sources if s.credibility_score >= 0.7])}
- Source domains: {list(set(urlparse(s.url).netloc for s in sources))}

Key findings identified:
{chr(10).join(f"- {f}" for f in findings)}

Identify research gaps and recommendations:
1. Topics not adequately covered
2. Missing perspectives or source types
3. Areas needing more authoritative sources
4. Suggested additional research directions

Output as a JSON array of specific, actionable recommendations."""

        try:
            result = await self.registry.generate(
                prompt=prompt,
                provider=model_config.provider,
                model=model_config.model,
                config=GenerationConfig(
                    max_tokens=800,
                    temperature=0.3,
                    system_prompt=self.SYSTEM_PROMPTS["gap_analysis"],
                ),
            )

            gaps = self._parse_json_array(result.content)
            if gaps:
                return gaps[:5]

        except Exception as e:
            self.logger.warning(f"LLM gap analysis failed: {e}")

        # Fallback to basic gap analysis
        return self._basic_gap_analysis(sources, findings, requirements)

    def _basic_gap_analysis(
        self,
        sources: List[Source],
        findings: List[str],
        requirements: Dict[str, Any],
    ) -> List[str]:
        """Basic gap analysis without LLM."""
        gaps = []

        high_quality = len([s for s in sources if s.credibility_score >= 0.7])
        if high_quality < 2:
            gaps.append("Need more high-credibility sources (academic, .gov, established publications)")

        if len(findings) < 3:
            gaps.append("Key findings are limited - consider expanding search queries")

        focus_areas = requirements.get("focus_areas", [])
        for area in focus_areas:
            covered = any(area.lower() in f.lower() for f in findings)
            if not covered:
                gaps.append(f"Focus area '{area}' not well covered in research")

        domains = [urlparse(s.url).netloc for s in sources]
        if len(set(domains)) < len(sources) * 0.5:
            gaps.append("Source diversity is low - consider broader search")

        return gaps

    def _parse_json_array(self, content: str) -> List[str]:
        """Parse JSON array from LLM response."""
        try:
            # Try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to find JSON array in content
        match = re.search(r"\[.*?\]", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return []

    def _parse_json_object(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse JSON object from LLM response."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in content
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return None

    async def refine_research(
        self,
        brief: ResearchBrief,
        additional_queries: Optional[List[str]] = None,
    ) -> ResearchBrief:
        """
        Refine existing research with additional sources.

        Args:
            brief: Existing research brief to refine
            additional_queries: Optional specific queries to run

        Returns:
            Updated ResearchBrief with additional sources and findings
        """
        queries = additional_queries or []

        # Add queries based on identified gaps
        for gap in brief.research_gaps[:3]:
            queries.append(f"{brief.topic} {gap}")

        # Execute additional search
        new_results = await self._execute_search(brief.topic, queries)

        # Analyze new sources
        new_sources = await self._analyze_sources(new_results, brief.topic)

        # Merge with existing (avoiding duplicates by URL)
        existing_urls = {s.url for s in brief.sources}
        unique_new_sources = [s for s in new_sources if s.url not in existing_urls]

        # Combine sources
        all_sources = brief.sources + unique_new_sources
        all_sources.sort(key=lambda s: s.credibility_score, reverse=True)
        all_sources = all_sources[:self.max_sources]

        # Re-synthesize findings
        key_findings = await self._synthesize_findings(all_sources, brief.topic)
        data_points = self._extract_data_points(all_sources)
        research_gaps = await self._identify_gaps(
            all_sources, key_findings, {}, brief.topic
        )

        return ResearchBrief(
            topic=brief.topic,
            sources=all_sources,
            key_findings=key_findings,
            data_points=data_points,
            research_gaps=research_gaps,
        )
