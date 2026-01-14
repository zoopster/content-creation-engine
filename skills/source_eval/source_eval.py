"""
Source Evaluation Skill - Credibility scoring and bias detection.

Evaluates the credibility and quality of information sources
for content research.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, List, Any, Optional
from datetime import datetime
from agents.base.agent import Skill
from agents.base.models import Source


class SourceEvalSkill(Skill):
    """
    Evaluates source credibility and quality.

    Functions:
    - Credibility scoring based on domain, recency, author
    - Bias detection
    - Source type classification
    - Authority assessment
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("source-eval", config)
        self.trusted_domains = self._load_trusted_domains()
        self.domain_categories = self._load_domain_categories()

    def _load_trusted_domains(self) -> Dict[str, float]:
        """
        Load trusted domain list with base credibility scores.

        Returns:
            Dictionary mapping domains to base credibility scores
        """
        # High-credibility sources (academic, government, established media)
        return {
            # Academic and research
            "arxiv.org": 0.9,
            "scholar.google.com": 0.9,
            "ncbi.nlm.nih.gov": 0.9,
            "ieee.org": 0.9,
            "nature.com": 0.95,
            "science.org": 0.95,
            "sciencedirect.com": 0.85,

            # Government and institutions
            "gov": 0.9,  # Any .gov domain
            "edu": 0.85,  # Any .edu domain

            # Established media and publications
            "reuters.com": 0.8,
            "apnews.com": 0.8,
            "bbc.com": 0.8,
            "nytimes.com": 0.75,
            "wsj.com": 0.75,
            "economist.com": 0.75,

            # Tech and business publications
            "techcrunch.com": 0.7,
            "wired.com": 0.7,
            "arstechnica.com": 0.7,
            "hbr.org": 0.75,
            "forbes.com": 0.65,

            # Industry resources
            "stackoverflow.com": 0.7,
            "github.com": 0.7,
            "medium.com": 0.5,  # Varies widely by author
        }

    def _load_domain_categories(self) -> Dict[str, List[str]]:
        """
        Load domain category classifications.

        Returns:
            Dictionary mapping categories to domain lists
        """
        return {
            "academic": ["arxiv.org", "scholar.google.com", "ncbi.nlm.nih.gov", "ieee.org"],
            "government": [".gov"],
            "news": ["reuters.com", "apnews.com", "bbc.com", "nytimes.com"],
            "industry": ["techcrunch.com", "wired.com", "arstechnica.com"],
            "business": ["hbr.org", "forbes.com", "wsj.com", "economist.com"],
            "community": ["stackoverflow.com", "github.com", "medium.com"]
        }

    def execute(
        self,
        url: str,
        title: str,
        snippet: Optional[str] = None,
        author: Optional[str] = None,
        publication_date: Optional[str] = None,
        full_content: Optional[str] = None
    ) -> Source:
        """
        Evaluate a source and create Source object with credibility score.

        Args:
            url: Source URL
            title: Article/page title
            snippet: Brief description or snippet
            author: Author name (if available)
            publication_date: Publication date (if available)
            full_content: Full content text (if available)

        Returns:
            Source object with credibility score
        """
        self.logger.info(f"Evaluating source: {url}")

        # Calculate credibility score
        credibility_score = self._calculate_credibility(
            url, title, author, publication_date, full_content
        )

        # Extract key information
        key_facts = self._extract_key_facts(snippet or "", full_content)
        key_quotes = self._extract_key_quotes(full_content) if full_content else []

        # Create Source object
        source = Source(
            url=url,
            title=title,
            author=author,
            publication_date=publication_date,
            credibility_score=credibility_score,
            key_quotes=key_quotes,
            key_facts=key_facts
        )

        self.logger.info(f"Source credibility score: {credibility_score:.2f}")
        return source

    def _calculate_credibility(
        self,
        url: str,
        title: str,
        author: Optional[str],
        publication_date: Optional[str],
        content: Optional[str]
    ) -> float:
        """
        Calculate overall credibility score for a source.

        Args:
            url: Source URL
            title: Title
            author: Author (if available)
            publication_date: Publication date (if available)
            content: Full content (if available)

        Returns:
            Credibility score (0.0 - 1.0)
        """
        scores = []
        weights = []

        # Domain credibility (weight: 0.4)
        domain_score = self._score_domain(url)
        scores.append(domain_score)
        weights.append(0.4)

        # Recency score (weight: 0.2)
        if publication_date:
            recency_score = self._score_recency(publication_date)
            scores.append(recency_score)
            weights.append(0.2)

        # Author presence (weight: 0.1)
        if author:
            scores.append(0.8)
            weights.append(0.1)

        # Content quality indicators (weight: 0.3)
        if content:
            quality_score = self._score_content_quality(content, title)
            scores.append(quality_score)
            weights.append(0.3)

        # Calculate weighted average
        if not scores:
            return 0.5  # Default neutral score

        total_weight = sum(weights)
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))

        return weighted_sum / total_weight

    def _score_domain(self, url: str) -> float:
        """
        Score based on domain reputation.

        Args:
            url: Source URL

        Returns:
            Domain credibility score (0.0 - 1.0)
        """
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]

            # Check exact domain match
            if domain in self.trusted_domains:
                return self.trusted_domains[domain]

            # Check for .gov or .edu domains
            if domain.endswith(".gov"):
                return self.trusted_domains.get("gov", 0.9)
            if domain.endswith(".edu"):
                return self.trusted_domains.get("edu", 0.85)

            # Check for partial matches (e.g., subdomains)
            for trusted_domain, score in self.trusted_domains.items():
                if trusted_domain in domain:
                    return score * 0.9  # Slight penalty for subdomain

            # Unknown domain - neutral score
            return 0.5

        except Exception:
            return 0.3  # Invalid URL - low score

    def _score_recency(self, publication_date: str) -> float:
        """
        Score based on how recent the content is.

        Args:
            publication_date: Publication date string

        Returns:
            Recency score (0.0 - 1.0)
        """
        try:
            # Try to parse date (supports ISO format and common formats)
            from dateutil import parser
            pub_date = parser.parse(publication_date)

            # Calculate age in days
            age_days = (datetime.now() - pub_date).days

            # Scoring by age
            if age_days <= 30:
                return 1.0
            elif age_days <= 180:
                return 0.9
            elif age_days <= 365:
                return 0.8
            elif age_days <= 730:  # 2 years
                return 0.7
            elif age_days <= 1095:  # 3 years
                return 0.6
            else:
                return 0.5

        except Exception:
            # If date parsing fails, return neutral score
            return 0.6

    def _score_content_quality(self, content: str, title: str) -> float:
        """
        Score content quality based on indicators.

        Args:
            content: Full content text
            title: Article title

        Returns:
            Quality score (0.0 - 1.0)
        """
        if not content or len(content) < 100:
            return 0.3

        score = 0.5  # Base score

        # Length indicator (substantial content is better)
        if len(content) > 1000:
            score += 0.1
        if len(content) > 2000:
            score += 0.1

        # Has citations or references
        if any(indicator in content.lower() for indicator in ["references", "sources", "citation"]):
            score += 0.1

        # Has data or statistics
        if any(char in content for char in ["%", "$"]) or any(word in content.lower() for word in ["data", "study", "research"]):
            score += 0.1

        # Avoid clickbait indicators
        clickbait_indicators = ["you won't believe", "shocking", "one weird trick", "doctors hate"]
        if any(indicator in (content + title).lower() for indicator in clickbait_indicators):
            score -= 0.2

        return min(1.0, max(0.0, score))

    def _extract_key_facts(self, snippet: str, content: Optional[str] = None) -> List[str]:
        """
        Extract key factual statements from content.

        Args:
            snippet: Content snippet
            content: Full content (if available)

        Returns:
            List of key facts
        """
        # Simple implementation - just use snippet for now
        # In production, this would use NLP to extract facts
        if snippet:
            return [snippet]
        return []

    def _extract_key_quotes(self, content: str, max_quotes: int = 3) -> List[str]:
        """
        Extract notable quotes from content.

        Args:
            content: Full content text
            max_quotes: Maximum number of quotes to extract

        Returns:
            List of key quotes
        """
        if not content:
            return []

        import re

        # Find text in quotes
        quoted_text = re.findall(r'"([^"]{20,200})"', content)

        # Return up to max_quotes
        return quoted_text[:max_quotes]

    def categorize_source(self, url: str) -> str:
        """
        Categorize the source type.

        Args:
            url: Source URL

        Returns:
            Source category (academic, news, industry, etc.)
        """
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            if domain.startswith("www."):
                domain = domain[4:]

            # Check categories
            for category, domains in self.domain_categories.items():
                for cat_domain in domains:
                    if cat_domain in domain:
                        return category

            return "general"

        except Exception:
            return "unknown"

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return ""
