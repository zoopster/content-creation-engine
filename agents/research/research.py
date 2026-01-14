"""
Research Agent - Gathers and validates source material for content creation.

Responsibilities:
- Execute web searches with query optimization
- Evaluate source credibility and recency
- Extract key facts, quotes, and data points
- Synthesize findings into structured briefs
- Identify gaps requiring additional research
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, List, Any, Optional
from agents.base.agent import Agent
from agents.base.models import ResearchBrief, Source
from datetime import datetime
import re
from urllib.parse import urlparse


class ResearchAgent(Agent):
    """
    Gathers and validates source material for content creation.

    Uses web search to find relevant sources, evaluates their credibility,
    extracts key information, and synthesizes findings into a ResearchBrief.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("research", config)
        self.min_sources = config.get("min_sources", 3) if config else 3
        self.max_sources = config.get("max_sources", 10) if config else 10
        self.min_credibility = config.get("min_credibility", 0.5) if config else 0.5

    def process(self, input_data: Dict[str, Any]) -> ResearchBrief:
        """
        Execute research workflow for a given topic.

        Args:
            input_data: Dictionary with 'topic' and optional 'requirements'

        Returns:
            ResearchBrief with sources, findings, and data points
        """
        topic = input_data.get("topic")
        if not topic:
            raise ValueError("Topic is required for research")

        requirements = input_data.get("requirements", {})

        self.logger.info(f"Starting research on topic: {topic}")

        # Step 1: Execute web search
        search_results = self._web_search(topic, requirements)
        self.logger.info(f"Found {len(search_results)} initial search results")

        # Step 2: Evaluate and filter sources
        evaluated_sources = self._evaluate_sources(search_results)
        self.logger.info(f"Evaluated {len(evaluated_sources)} sources")

        # Filter by credibility and limit
        quality_sources = [
            s for s in evaluated_sources
            if s.credibility_score >= self.min_credibility
        ][:self.max_sources]

        self.logger.info(f"Selected {len(quality_sources)} quality sources")

        # Step 3: Extract facts and synthesize findings
        key_findings = self._extract_key_findings(quality_sources, topic)
        data_points = self._extract_data_points(quality_sources)

        # Step 4: Identify research gaps
        research_gaps = self._identify_gaps(quality_sources, key_findings, requirements)

        # Step 5: Create research brief
        research_brief = ResearchBrief(
            topic=topic,
            sources=quality_sources,
            key_findings=key_findings,
            data_points=data_points,
            research_gaps=research_gaps
        )

        # Validate output
        is_valid, errors = research_brief.validate()
        if not is_valid:
            self.logger.warning(f"Research brief validation issues: {errors}")
            # If we don't have enough sources, log but continue
            if len(quality_sources) < self.min_sources:
                self.logger.error(f"Insufficient quality sources: {len(quality_sources)} < {self.min_sources}")

        self.log_execution(input_data, research_brief, {
            "total_sources": len(search_results),
            "quality_sources": len(quality_sources),
            "key_findings_count": len(key_findings)
        })

        return research_brief

    def _web_search(self, topic: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute web search for the topic.

        Args:
            topic: Search topic
            requirements: Additional search requirements

        Returns:
            List of search result dictionaries
        """
        # Optimize query based on requirements
        query = self._optimize_query(topic, requirements)

        self.logger.info(f"Executing search with query: {query}")

        # Note: In a real implementation, this would use the WebSearch tool
        # For Phase 2, return mock search results for testing
        return self._generate_mock_search_results(topic, query)

    def _optimize_query(self, topic: str, requirements: Dict[str, Any]) -> str:
        """
        Optimize search query based on topic and requirements.

        Args:
            topic: Base topic
            requirements: Additional requirements (recency, focus areas, etc.)

        Returns:
            Optimized search query
        """
        query = topic

        # Add date constraints if specified
        if requirements.get("recent_only"):
            current_year = datetime.now().year
            query += f" {current_year}"

        # Add focus areas if specified
        focus_areas = requirements.get("focus_areas", [])
        if focus_areas:
            query += " " + " ".join(focus_areas)

        # Add content type hints
        content_type = requirements.get("content_type")
        if content_type == "technical":
            query += " technical implementation"
        elif content_type == "business":
            query += " business impact"

        return query

    def _evaluate_sources(self, search_results: List[Dict[str, Any]]) -> List[Source]:
        """
        Evaluate credibility of search results.

        Args:
            search_results: Raw search results

        Returns:
            List of Source objects with credibility scores
        """
        sources = []

        for result in search_results:
            url = result.get("url", "")
            title = result.get("title", "")
            content = result.get("content", "")

            # Extract metadata
            author = result.get("author")
            pub_date = result.get("published_date")

            # Calculate credibility score
            credibility_score = self._calculate_credibility(url, title, content, result)

            # Extract key information
            key_quotes = self._extract_quotes(content)
            key_facts = self._extract_facts(content, title)

            source = Source(
                url=url,
                title=title,
                author=author,
                publication_date=pub_date,
                credibility_score=credibility_score,
                key_quotes=key_quotes[:3],  # Top 3 quotes
                key_facts=key_facts[:5]  # Top 5 facts
            )

            sources.append(source)

        # Sort by credibility score
        sources.sort(key=lambda s: s.credibility_score, reverse=True)

        return sources

    def _calculate_credibility(
        self,
        url: str,
        title: str,
        content: str,
        result: Dict[str, Any]
    ) -> float:
        """
        Calculate credibility score for a source.

        Args:
            url: Source URL
            title: Article title
            content: Article content
            result: Full search result dictionary

        Returns:
            Credibility score (0.0 to 1.0)
        """
        score = 0.5  # Base score

        # Domain reputation
        domain = urlparse(url).netloc.lower()

        # High reputation domains
        high_rep_domains = [
            'edu', 'gov', 'ieee.org', 'acm.org', 'nature.com',
            'science.org', 'scholar.google', 'arxiv.org',
            'techcrunch.com', 'wired.com', 'arstechnica.com'
        ]
        if any(rep_domain in domain for rep_domain in high_rep_domains):
            score += 0.3

        # Medium reputation domains
        med_rep_domains = [
            'forbes.com', 'bloomberg.com', 'reuters.com',
            'wsj.com', 'nytimes.com', 'theguardian.com'
        ]
        if any(rep_domain in domain for rep_domain in med_rep_domains):
            score += 0.2

        # Penalize low-quality indicators
        low_quality_indicators = ['blog.', 'medium.com', 'wordpress.com']
        if any(indicator in domain for indicator in low_quality_indicators):
            score -= 0.1

        # Content quality indicators
        if len(content) > 1000:  # Substantial content
            score += 0.1

        if result.get("author"):  # Has author attribution
            score += 0.1

        if result.get("published_date"):  # Has publication date
            score += 0.05

        # Title quality (not clickbait)
        clickbait_indicators = ['you won\'t believe', 'shocking', '!!!', 'one weird trick']
        if any(indicator in title.lower() for indicator in clickbait_indicators):
            score -= 0.2

        # Normalize to 0.0 - 1.0 range
        return max(0.0, min(1.0, score))

    def _extract_quotes(self, content: str) -> List[str]:
        """
        Extract quotable statements from content.

        Args:
            content: Source content

        Returns:
            List of extracted quotes
        """
        if not content:
            return []

        quotes = []

        # Look for quoted text
        quote_pattern = r'"([^"]{50,300})"'
        matches = re.findall(quote_pattern, content)
        quotes.extend(matches[:3])

        # If no quotes found, extract important-looking sentences
        if not quotes:
            sentences = content.split('.')
            for sentence in sentences[:10]:
                sentence = sentence.strip()
                # Look for sentences with strong indicators
                if any(word in sentence.lower() for word in ['research shows', 'study found', 'according to', 'expert']):
                    if 50 < len(sentence) < 300:
                        quotes.append(sentence)
                        if len(quotes) >= 3:
                            break

        return quotes

    def _extract_facts(self, content: str, title: str) -> List[str]:
        """
        Extract key facts from content.

        Args:
            content: Source content
            title: Source title

        Returns:
            List of extracted facts
        """
        if not content:
            return []

        facts = []

        # Look for sentences with numbers/statistics
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for numbers, percentages, or statistical indicators
            if re.search(r'\d+[%]|\d+\s*(million|billion|thousand)', sentence):
                if 30 < len(sentence) < 200:
                    facts.append(sentence)
            # Look for definitive statements
            elif any(word in sentence.lower() for word in ['is', 'are', 'has', 'have', 'will', 'can']):
                if 30 < len(sentence) < 200 and len(facts) < 5:
                    facts.append(sentence)

        return facts[:5]

    def _extract_key_findings(self, sources: List[Source], topic: str) -> List[str]:
        """
        Synthesize key findings from multiple sources.

        Args:
            sources: Evaluated sources
            topic: Research topic

        Returns:
            List of key findings
        """
        findings = []

        # Aggregate facts from all sources
        all_facts = []
        for source in sources:
            all_facts.extend(source.key_facts)

        # Use top facts from high-credibility sources
        high_cred_sources = [s for s in sources if s.credibility_score >= 0.7]

        for source in high_cred_sources[:5]:  # Top 5 sources
            if source.key_facts:
                findings.append(source.key_facts[0])

        # If we don't have enough findings, add more from other sources
        if len(findings) < 3:
            for source in sources:
                if source.key_facts and source.key_facts[0] not in findings:
                    findings.append(source.key_facts[0])
                    if len(findings) >= 5:
                        break

        # Ensure we have at least some findings
        if not findings and sources:
            findings.append(f"Research conducted on {topic} from {len(sources)} sources")

        return findings[:5]

    def _extract_data_points(self, sources: List[Source]) -> Dict[str, Any]:
        """
        Extract structured data points from sources.

        Args:
            sources: Evaluated sources

        Returns:
            Dictionary of data points
        """
        data_points = {
            "source_count": len(sources),
            "high_credibility_sources": len([s for s in sources if s.credibility_score >= 0.7]),
            "average_credibility": sum(s.credibility_score for s in sources) / len(sources) if sources else 0.0,
            "total_facts_extracted": sum(len(s.key_facts) for s in sources),
            "total_quotes_extracted": sum(len(s.key_quotes) for s in sources),
            "source_domains": list(set(urlparse(s.url).netloc for s in sources))
        }

        # Extract any numbers/statistics from facts
        statistics = []
        for source in sources:
            for fact in source.key_facts:
                # Find percentages
                percentages = re.findall(r'(\d+(?:\.\d+)?%)', fact)
                statistics.extend(percentages)

                # Find large numbers
                large_numbers = re.findall(r'(\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|thousand))', fact)
                statistics.extend(large_numbers)

        if statistics:
            data_points["statistics_found"] = statistics[:10]

        return data_points

    def _identify_gaps(
        self,
        sources: List[Source],
        key_findings: List[str],
        requirements: Dict[str, Any]
    ) -> List[str]:
        """
        Identify gaps in research coverage.

        Args:
            sources: Evaluated sources
            key_findings: Extracted findings
            requirements: Original requirements

        Returns:
            List of identified research gaps
        """
        gaps = []

        # Check if we have enough high-quality sources
        high_quality_count = len([s for s in sources if s.credibility_score >= 0.7])
        if high_quality_count < 2:
            gaps.append("Need more high-credibility sources")

        # Check if we have enough findings
        if len(key_findings) < 3:
            gaps.append("Need more key findings - research may be incomplete")

        # Check for required focus areas
        focus_areas = requirements.get("focus_areas", [])
        if focus_areas:
            # Simple check: see if focus areas appear in findings
            for area in focus_areas:
                area_covered = any(area.lower() in finding.lower() for finding in key_findings)
                if not area_covered:
                    gaps.append(f"Focus area '{area}' not well covered in research")

        # Check for diverse sources
        domains = [urlparse(s.url).netloc for s in sources]
        unique_domains = len(set(domains))
        if unique_domains < len(sources) * 0.5:
            gaps.append("Sources lack diversity - too many from same domains")

        return gaps

    def _generate_mock_search_results(self, topic: str, query: str) -> List[Dict[str, Any]]:
        """
        Generate mock search results for Phase 2 testing.

        In production, this would be replaced by actual web search API calls.

        Args:
            topic: Search topic
            query: Optimized query

        Returns:
            List of mock search results
        """
        # Extract key terms from topic
        words = topic.split()
        key_term = words[0] if words else "topic"

        # Generate 3-5 mock results
        results = [
            {
                "url": f"https://example.org/{key_term.lower()}-comprehensive-guide",
                "title": f"Comprehensive Guide to {topic.title()}",
                "author": "Industry Expert",
                "published_date": "2025-12-15",
                "content": f"{topic} represents an important development in the field. Research shows significant benefits and measurable impact across multiple dimensions. Organizations implementing {topic.lower()} report improved outcomes by 35% on average. Key factors include proper implementation, stakeholder engagement, and ongoing monitoring. Studies indicate that {topic.lower()} adoption continues to grow, with market size expected to reach $150B by 2027."
            },
            {
                "url": f"https://research.edu/{key_term.lower()}-study-2025",
                "title": f"Research Study: Impact of {topic.title()}",
                "author": "Dr. Academic Researcher",
                "published_date": "2025-11-20",
                "content": f"This study examines the impact of {topic.lower()} on industry practices. Findings demonstrate 40% improvement in efficiency metrics. The research involved 500 participants across 50 organizations. Data analysis reveals strong correlation between {topic.lower()} adoption and positive outcomes. Statistical significance: p < 0.01. Key recommendations include structured implementation approach and continuous evaluation."
            },
            {
                "url": f"https://tech-news.com/{key_term.lower()}-trends-2026",
                "title": f"Latest Trends in {topic.title()} for 2026",
                "author": "Tech News Editorial Team",
                "published_date": "2026-01-10",
                "content": f"Industry leaders are increasingly adopting {topic.lower()} to drive innovation. Recent surveys show 68% of enterprises plan to implement {topic.lower()} solutions this year. Market analysis predicts continued growth, with adoption rates accelerating. Key trends include integration with existing systems, focus on ROI measurement, and emphasis on user experience. Early adopters report competitive advantages and improved operational metrics."
            },
            {
                "url": f"https://business-insights.com/{key_term.lower()}-roi",
                "title": f"Business ROI of {topic.title()}: Analysis and Insights",
                "author": "Business Analyst",
                "published_date": "2025-10-05",
                "content": f"Financial analysis shows strong ROI for {topic.lower()} investments. Companies report average payback period of 18 months. Cost savings average 25% annually after implementation. Key success factors include executive sponsorship, proper resource allocation, and phased rollout approach. Risk factors to consider include change management challenges and integration complexity."
            },
            {
                "url": f"https://industry-forum.com/{key_term.lower()}-best-practices",
                "title": f"Best Practices for {topic.title()} Implementation",
                "author": "Industry Practitioner",
                "published_date": "2025-09-12",
                "content": f"Practical guidance for implementing {topic.lower()} based on real-world experience. Best practices include thorough planning, pilot programs, stakeholder engagement, and iterative improvement. Common pitfalls to avoid: rushing implementation, inadequate training, poor communication. Success metrics should include both quantitative and qualitative measures. Regular review and adjustment essential for long-term success."
            }
        ]

        # Return 3-4 results randomly
        import random
        num_results = random.randint(3, min(4, len(results)))
        return results[:num_results]
