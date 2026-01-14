"""
Brand Voice Skill - Ensures consistent voice and style across all content.

Validates content against brand guidelines including vocabulary,
tone, sentence structure, and style preferences.
"""

import re
from typing import Dict, List, Any, Optional, Set
from agents.base.agent import Skill
from agents.base.models import DraftContent, BrandVoiceResult, ToneType


class BrandVoiceSkill(Skill):
    """
    Validates and enforces brand voice consistency.

    Functions:
    - Vocabulary alignment (preferred/avoided terms)
    - Sentence structure patterns
    - Tone calibration per content type
    - Consistency validation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("brand-voice", config)
        self.guidelines = self._load_guidelines()
        self.vocabulary = self._load_vocabulary()

    def _load_guidelines(self) -> Dict[str, Any]:
        """Load brand voice guidelines."""
        # Default guidelines - in production, load from config/database
        return {
            "sentence_length": {
                "max_words": 25,
                "recommended_avg": 15,
                "warning_threshold": 30
            },
            "paragraph_length": {
                "max_sentences": 5,
                "recommended_avg": 3
            },
            "passive_voice": {
                "max_percentage": 10,
                "threshold": 15
            },
            "readability": {
                "min_score": 60,  # Flesch reading ease
                "target_score": 70
            },
            "tone_keywords": {
                ToneType.PROFESSIONAL: ["implement", "strategy", "optimize", "analyze", "framework"],
                ToneType.CONVERSATIONAL: ["you", "we", "let's", "simply", "just"],
                ToneType.TECHNICAL: ["algorithm", "architecture", "protocol", "implementation", "system"],
                ToneType.EDUCATIONAL: ["learn", "understand", "example", "step", "guide"],
                ToneType.PERSUASIVE: ["proven", "results", "transform", "success", "effective"],
                ToneType.INSPIRATIONAL: ["achieve", "potential", "vision", "innovate", "empower"]
            }
        }

    def _load_vocabulary(self) -> Dict[str, List[str]]:
        """Load brand vocabulary preferences."""
        # Default vocabulary - in production, load from config/database
        return {
            "preferred_terms": [
                "customer",
                "solution",
                "innovative",
                "data-driven",
                "streamline"
            ],
            "avoided_terms": [
                "cheap",
                "easy",
                "best",
                "revolutionary",
                "game-changing"
            ],
            "inclusive_language": [
                "they/them instead of he/she",
                "people with disabilities not disabled people",
                "chair/moderator not chairman"
            ]
        }

    def execute(
        self,
        draft_content: DraftContent,
        target_tone: Optional[ToneType] = None,
        custom_guidelines: Optional[Dict[str, Any]] = None
    ) -> BrandVoiceResult:
        """
        Validate content against brand voice guidelines.

        Args:
            draft_content: Content to validate
            target_tone: Expected tone (from ContentBrief)
            custom_guidelines: Optional custom guidelines to apply

        Returns:
            BrandVoiceResult with validation results
        """
        self.logger.info(f"Validating brand voice for {draft_content.content_type.value}")

        # Merge custom guidelines
        guidelines = {**self.guidelines, **(custom_guidelines or {})}

        # Run validation checks
        checks = [
            self._check_vocabulary(draft_content.content),
            self._check_sentence_length(draft_content.content, guidelines),
            self._check_tone_alignment(draft_content.content, target_tone, guidelines),
            self._check_passive_voice(draft_content.content, guidelines),
            self._check_readability(draft_content.content, guidelines)
        ]

        # Aggregate results
        issues = []
        suggestions = []
        scores = []

        for check_result in checks:
            issues.extend(check_result.get("issues", []))
            suggestions.extend(check_result.get("suggestions", []))
            scores.append(check_result.get("score", 1.0))

        # Calculate overall score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        passed = overall_score >= 0.7 and len(issues) == 0

        result = BrandVoiceResult(
            passed=passed,
            score=overall_score,
            issues=issues,
            suggestions=suggestions
        )

        self.logger.info(f"Brand voice validation: {'PASSED' if passed else 'FAILED'} (score: {overall_score:.2f})")
        return result

    def _check_vocabulary(self, content: str) -> Dict[str, Any]:
        """Check for avoided terms and suggest alternatives."""
        issues = []
        suggestions = []
        content_lower = content.lower()

        # Check for avoided terms
        for term in self.vocabulary["avoided_terms"]:
            if term in content_lower:
                issues.append(f"Avoid using '{term}'")
                # Find alternatives from preferred terms
                suggestions.append(f"Consider using brand-preferred terminology instead of '{term}'")

        # Calculate vocabulary score
        avoided_count = sum(1 for term in self.vocabulary["avoided_terms"] if term in content_lower)
        preferred_count = sum(1 for term in self.vocabulary["preferred_terms"] if term in content_lower)

        # Score based on ratio of preferred to avoided
        total = avoided_count + preferred_count
        score = 1.0 - (avoided_count / max(total, 1))

        return {
            "score": score,
            "issues": issues,
            "suggestions": suggestions
        }

    def _check_sentence_length(self, content: str, guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Check sentence length against guidelines."""
        issues = []
        suggestions = []

        # Split into sentences (simple approach)
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return {"score": 1.0, "issues": [], "suggestions": []}

        # Analyze sentence lengths
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        max_length = max(lengths)

        sentence_config = guidelines["sentence_length"]

        # Check average
        if avg_length > sentence_config["recommended_avg"] * 1.5:
            suggestions.append(
                f"Average sentence length ({avg_length:.1f} words) is high. "
                f"Aim for {sentence_config['recommended_avg']} words."
            )

        # Check for overly long sentences
        long_sentences = [i for i, length in enumerate(lengths) if length > sentence_config["warning_threshold"]]
        if long_sentences:
            issues.append(
                f"{len(long_sentences)} sentence(s) exceed {sentence_config['warning_threshold']} words"
            )
            suggestions.append("Consider breaking long sentences into shorter ones for clarity")

        # Calculate score
        score = max(0.0, 1.0 - (avg_length - sentence_config["recommended_avg"]) / 20)

        return {
            "score": score,
            "issues": issues,
            "suggestions": suggestions
        }

    def _check_tone_alignment(
        self,
        content: str,
        target_tone: Optional[ToneType],
        guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if content matches target tone."""
        if not target_tone:
            return {"score": 1.0, "issues": [], "suggestions": []}

        issues = []
        suggestions = []
        content_lower = content.lower()

        # Get tone keywords
        tone_keywords = guidelines["tone_keywords"].get(target_tone, [])

        # Count tone keyword matches
        matches = sum(1 for keyword in tone_keywords if keyword in content_lower)

        # Score based on keyword presence
        score = min(1.0, matches / max(len(tone_keywords) * 0.3, 1))

        if score < 0.5:
            suggestions.append(
                f"Content may not match {target_tone.value} tone. "
                f"Consider incorporating: {', '.join(tone_keywords[:3])}"
            )

        return {
            "score": score,
            "issues": issues,
            "suggestions": suggestions
        }

    def _check_passive_voice(self, content: str, guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Check for excessive passive voice."""
        issues = []
        suggestions = []

        # Simple passive voice detection (be + past participle)
        passive_patterns = [
            r'\bis\s+\w+ed\b',
            r'\bare\s+\w+ed\b',
            r'\bwas\s+\w+ed\b',
            r'\bwere\s+\w+ed\b',
            r'\bbeen\s+\w+ed\b',
            r'\bbe\s+\w+ed\b'
        ]

        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return {"score": 1.0, "issues": [], "suggestions": []}

        passive_count = 0
        for sentence in sentences:
            for pattern in passive_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    passive_count += 1
                    break

        passive_percentage = (passive_count / len(sentences)) * 100
        threshold = guidelines["passive_voice"]["threshold"]

        if passive_percentage > threshold:
            issues.append(
                f"Passive voice usage ({passive_percentage:.1f}%) exceeds {threshold}%"
            )
            suggestions.append("Prefer active voice for clarity and engagement")

        # Calculate score
        score = max(0.0, 1.0 - (passive_percentage / 100))

        return {
            "score": score,
            "issues": issues,
            "suggestions": suggestions
        }

    def _check_readability(self, content: str, guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Check content readability."""
        issues = []
        suggestions = []

        # Simple readability approximation
        # Count sentences and words
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = content.split()

        if not sentences or not words:
            return {"score": 1.0, "issues": [], "suggestions": []}

        # Count syllables (very rough approximation)
        syllable_count = sum(self._count_syllables(word) for word in words)

        # Flesch Reading Ease approximation
        # Score = 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllable_count / len(words)

        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        flesch_score = max(0, min(100, flesch_score))

        min_score = guidelines["readability"]["min_score"]

        if flesch_score < min_score:
            suggestions.append(
                f"Readability score ({flesch_score:.1f}) is below target ({min_score}). "
                "Use shorter sentences and simpler words."
            )

        # Normalize score to 0-1
        score = flesch_score / 100

        return {
            "score": score,
            "issues": issues,
            "suggestions": suggestions
        }

    def _count_syllables(self, word: str) -> int:
        """Rough syllable count for a word."""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith('e'):
            count -= 1

        # Ensure at least 1 syllable
        return max(1, count)
