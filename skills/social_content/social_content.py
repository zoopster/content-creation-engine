"""
Social Content Skill - Creates platform-optimized social media content.

Supports:
- LinkedIn (3,000 chars max)
- Twitter/X (280 chars max)
- Instagram (2,200 chars max)
- Facebook (variable)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, List, Any, Optional
from agents.base.agent import Skill
from agents.base.models import ContentBrief, Platform


class SocialContentSkill(Skill):
    """
    Generates platform-specific social media content.

    Features:
    - Platform-specific formatting and constraints
    - Optimal hashtag strategies
    - Engagement-focused hooks
    - Call-to-action optimization
    - Thread/carousel support
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("social-content", config)
        self.platform_specs = self._initialize_platform_specs()
        self.hook_templates = self._initialize_hooks()

    def _initialize_platform_specs(self) -> Dict[str, Dict[str, Any]]:
        """Define platform-specific specifications."""
        return {
            "linkedin": {
                "max_length": 3000,
                "optimal_length": (150, 300),
                "hashtag_count": (3, 5),
                "hashtag_strategy": "professional",
                "supports_threads": False,
                "supports_media": True,
                "tone": "professional",
                "emoji_usage": "moderate",
                "line_breaks": "encouraged"
            },
            "twitter": {
                "max_length": 280,
                "optimal_length": (150, 250),
                "hashtag_count": (1, 2),
                "hashtag_strategy": "relevant",
                "supports_threads": True,
                "supports_media": True,
                "tone": "conversational",
                "emoji_usage": "moderate",
                "line_breaks": "limited"
            },
            "instagram": {
                "max_length": 2200,
                "optimal_length": (100, 500),
                "hashtag_count": (5, 15),
                "hashtag_strategy": "discovery",
                "supports_threads": False,
                "supports_media": True,  # Required
                "tone": "casual",
                "emoji_usage": "high",
                "line_breaks": "encouraged"
            },
            "facebook": {
                "max_length": 63206,
                "optimal_length": (40, 250),
                "hashtag_count": (1, 3),
                "hashtag_strategy": "minimal",
                "supports_threads": False,
                "supports_media": True,
                "tone": "conversational",
                "emoji_usage": "moderate",
                "line_breaks": "moderate"
            }
        }

    def _initialize_hooks(self) -> Dict[str, List[str]]:
        """Define hook templates by platform."""
        return {
            "question": [
                "Have you ever wondered {topic}?",
                "What if {scenario}?",
                "Are you ready to {action}?",
                "Can you believe {fact}?"
            ],
            "statistic": [
                "{number}% of {audience} {action}.",
                "Did you know? {statistic}",
                "Shocking: {statistic}",
                "{number} out of {total} {fact}"
            ],
            "bold_statement": [
                "Here's the truth: {statement}",
                "Let's be honest: {statement}",
                "{statement}. Period.",
                "Unpopular opinion: {statement}"
            ],
            "story": [
                "Let me tell you about {scenario}",
                "Here's what happened: {story}",
                "Picture this: {scenario}",
                "A while back, {story}"
            ],
            "problem": [
                "Struggling with {problem}?",
                "Tired of {problem}?",
                "{problem} is holding you back.",
                "Here's why {problem} happens"
            ]
        }

    def execute(
        self,
        content_brief: ContentBrief,
        platform: str = "linkedin",
        format_type: str = "single",  # or "thread", "carousel"
        **kwargs
    ) -> str:
        """
        Generate social content for a specific platform.

        Args:
            content_brief: Content brief with requirements
            platform: Target platform (linkedin, twitter, instagram, facebook)
            format_type: Post format (single, thread, carousel)
            **kwargs: Additional parameters (include_cta, emoji_density, etc.)

        Returns:
            Social media post content
        """
        platform = platform.lower()

        if platform not in self.platform_specs:
            self.logger.warning(f"Unknown platform {platform}, defaulting to linkedin")
            platform = "linkedin"

        self.logger.info(f"Generating {platform} content ({format_type})")

        # Get platform specifications
        specs = self.platform_specs[platform]

        # Generate based on format
        if format_type == "thread" and specs["supports_threads"]:
            return self._generate_thread(content_brief, platform, specs, **kwargs)
        elif format_type == "carousel":
            return self._generate_carousel_content(content_brief, platform, specs, **kwargs)
        else:
            return self._generate_single_post(content_brief, platform, specs, **kwargs)

    def _generate_single_post(
        self,
        brief: ContentBrief,
        platform: str,
        specs: Dict[str, Any],
        **kwargs
    ) -> str:
        """Generate a single social media post."""
        max_length = specs["max_length"]
        optimal_min, optimal_max = specs["optimal_length"]

        post_parts = []

        # 1. Hook (most important - first line determines engagement)
        hook = self._generate_hook(brief, platform, specs)
        post_parts.append(hook)

        # 2. Main content
        main_content = self._generate_main_content(brief, platform, specs)
        post_parts.append(f"\n\n{main_content}")

        # 3. Supporting points or data
        if brief.research_brief and brief.research_brief.sources:
            supporting = self._generate_supporting_points(brief, platform, specs)
            if supporting:
                post_parts.append(f"\n\n{supporting}")

        # 4. Call to action
        include_cta = kwargs.get("include_cta", True)
        if include_cta:
            cta = self._generate_cta(brief, platform, specs)
            post_parts.append(f"\n\n{cta}")

        # 5. Hashtags
        hashtags = self._generate_hashtags(brief, platform, specs)
        if hashtags:
            post_parts.append(f"\n\n{hashtags}")

        # Combine and check length
        full_post = "".join(post_parts)

        # Trim if too long
        if len(full_post) > max_length:
            full_post = self._trim_to_length(post_parts, max_length)

        # Check if within optimal range
        if optimal_min <= len(full_post) <= optimal_max:
            self.logger.info(f"Post length optimal: {len(full_post)} chars")
        elif len(full_post) < optimal_min:
            self.logger.warning(f"Post shorter than optimal: {len(full_post)} < {optimal_min}")
        else:
            self.logger.info(f"Post length: {len(full_post)} chars (above optimal but within limit)")

        return full_post

    def _generate_hook(self, brief: ContentBrief, platform: str, specs: Dict[str, Any]) -> str:
        """Generate an engaging opening hook."""
        # Try to use research data for hooks
        if brief.research_brief and brief.research_brief.sources:
            # Look for statistics first
            for source in brief.research_brief.sources:
                for fact in source.key_facts:
                    if any(indicator in fact for indicator in ['%', 'million', 'billion', 'increased', 'doubled']):
                        # Found a statistic - use it
                        emoji = self._get_emoji(platform, specs, "stat")
                        return f"{emoji} {fact}"

        # Use key message as hook
        if brief.key_messages:
            hook = brief.key_messages[0]

            # Make it punchy for Twitter
            if platform == "twitter" and len(hook) > 100:
                hook = hook[:97] + "..."

            # Add appropriate emoji
            emoji = self._get_emoji(platform, specs, "main")
            if emoji:
                return f"{emoji} {hook}"
            return hook

        return "Let's talk about something important."

    def _generate_main_content(self, brief: ContentBrief, platform: str, specs: Dict[str, Any]) -> str:
        """Generate main content body."""
        content_parts = []

        # Get key messages
        messages = brief.key_messages[1:4] if len(brief.key_messages) > 1 else brief.key_messages

        if platform == "twitter":
            # Twitter: Keep it concise
            if messages:
                content_parts.append(messages[0])
        elif platform == "linkedin":
            # LinkedIn: More detailed, professional
            for message in messages[:2]:
                content_parts.append(f"→ {message}")
        elif platform == "instagram":
            # Instagram: Storytelling, visual
            if messages:
                content_parts.append(messages[0])
                if len(messages) > 1:
                    content_parts.append(f"\n\n✨ {messages[1]}")
        else:  # facebook
            # Facebook: Conversational
            for message in messages[:2]:
                content_parts.append(message)

        return "\n\n".join(content_parts) if content_parts else ""

    def _generate_supporting_points(self, brief: ContentBrief, platform: str, specs: Dict[str, Any]) -> str:
        """Generate supporting points or data."""
        if platform == "twitter":
            # Twitter: Skip supporting points due to length
            return ""

        if not brief.research_brief or not brief.research_brief.sources:
            return ""

        points = []

        # Get interesting facts
        for source in brief.research_brief.sources[:2]:
            if source.key_facts:
                points.append(source.key_facts[0])
                if len(points) >= 2:
                    break

        if not points:
            return ""

        if platform == "linkedin":
            # LinkedIn: Bullet points
            formatted = "\n".join([f"• {point}" for point in points])
            return f"Key insights:\n{formatted}"
        elif platform == "instagram":
            # Instagram: Numbered with emojis
            emojis = ["1️⃣", "2️⃣", "3️⃣"]
            formatted = "\n".join([f"{emojis[i]} {point}" for i, point in enumerate(points)])
            return formatted
        else:
            return "\n".join(points)

    def _generate_cta(self, brief: ContentBrief, platform: str, specs: Dict[str, Any]) -> str:
        """Generate call-to-action."""
        if platform == "linkedin":
            return "What's your experience with this? Share your thoughts in the comments. 💭"
        elif platform == "twitter":
            return "Thoughts? 💬"
        elif platform == "instagram":
            return "Double tap if you agree! ❤️ Drop a comment below 👇"
        elif platform == "facebook":
            return "What do you think? Let us know in the comments!"
        else:
            return "Share your thoughts!"

    def _generate_hashtags(self, brief: ContentBrief, platform: str, specs: Dict[str, Any]) -> str:
        """Generate platform-appropriate hashtags."""
        if not brief.seo_keywords:
            return ""

        min_tags, max_tags = specs["hashtag_count"]

        # Convert keywords to hashtags
        hashtags = []
        for keyword in brief.seo_keywords[:max_tags]:
            # Clean and format
            tag = keyword.replace(" ", "").replace("-", "")
            # Title case for readability
            tag = "".join(word.capitalize() for word in keyword.split())
            hashtags.append(f"#{tag}")

        # Limit to recommended count
        hashtags = hashtags[:max_tags]

        # Ensure minimum count
        if len(hashtags) < min_tags and platform == "instagram":
            # Add generic relevant tags for Instagram
            generic_tags = ["#ContentCreation", "#DigitalMarketing", "#Technology"]
            hashtags.extend(generic_tags[:min_tags - len(hashtags)])

        return " ".join(hashtags)

    def _get_emoji(self, platform: str, specs: Dict[str, Any], context: str) -> str:
        """Get appropriate emoji based on platform and context."""
        emoji_usage = specs["emoji_usage"]

        if emoji_usage == "high":
            # Instagram - use emojis liberally
            emoji_map = {
                "main": "✨",
                "stat": "📊",
                "idea": "💡",
                "success": "🎯"
            }
            return emoji_map.get(context, "")
        elif emoji_usage == "moderate":
            # LinkedIn, Twitter - use sparingly
            if context == "stat":
                return "📈"
            return ""
        else:
            # Facebook or minimal usage
            return ""

    def _trim_to_length(self, post_parts: List[str], max_length: int) -> str:
        """Trim post to fit within max length."""
        # Start with essentials: hook + main content
        essential = post_parts[0] + (post_parts[1] if len(post_parts) > 1 else "")

        if len(essential) > max_length:
            # Trim essential content
            return essential[:max_length - 3] + "..."

        # Add parts until we hit the limit
        result = essential
        for part in post_parts[2:]:
            if len(result + part) <= max_length:
                result += part
            else:
                break

        return result

    def _generate_thread(
        self,
        brief: ContentBrief,
        platform: str,
        specs: Dict[str, Any],
        **kwargs
    ) -> str:
        """Generate a Twitter/X thread."""
        max_length = specs["max_length"]
        thread_parts = []

        # Tweet 1: Hook and main message
        hook = self._generate_hook(brief, platform, specs)
        thread_parts.append(f"1/ {hook}")

        # Tweets 2-N: Key messages
        for i, message in enumerate(brief.key_messages[:5], 2):
            tweet = f"{i}/ {message}"
            if len(tweet) > max_length:
                tweet = tweet[:max_length - 3] + "..."
            thread_parts.append(tweet)

        # Final tweet: CTA
        final_num = len(thread_parts) + 1
        cta = self._generate_cta(brief, platform, specs)
        thread_parts.append(f"{final_num}/ {cta}")

        # Add hashtags to first tweet if space
        if brief.seo_keywords:
            hashtags = self._generate_hashtags(brief, platform, specs)
            if len(thread_parts[0] + "\n\n" + hashtags) <= max_length:
                thread_parts[0] += f"\n\n{hashtags}"

        return "\n\n---\n\n".join(thread_parts)

    def _generate_carousel_content(
        self,
        brief: ContentBrief,
        platform: str,
        specs: Dict[str, Any],
        **kwargs
    ) -> str:
        """Generate content for carousel/multi-image posts."""
        slides = []

        # Slide 1: Title/Hook
        slides.append(f"[Slide 1]\n{brief.key_messages[0]}")

        # Slides 2-N: Key points
        for i, message in enumerate(brief.key_messages[1:], 2):
            slides.append(f"[Slide {i}]\n{message}")

            # Add supporting fact if available
            if brief.research_brief and brief.research_brief.sources:
                source_idx = (i - 2) % len(brief.research_brief.sources)
                source = brief.research_brief.sources[source_idx]
                if source.key_facts:
                    fact_idx = (i - 2) % len(source.key_facts)
                    slides.append(f"\n\n{source.key_facts[fact_idx]}")

        # Final slide: CTA
        slides.append(f"[Slide {len(slides) + 1}]\n{self._generate_cta(brief, platform, specs)}")

        # Caption for the carousel
        caption = self._generate_single_post(brief, platform, specs, include_cta=False)

        return f"[CAROUSEL POST]\n\nCaption:\n{caption}\n\n---\n\nSlides:\n" + "\n\n".join(slides)

    def preview_post(self, content: str, platform: str) -> Dict[str, Any]:
        """
        Generate a preview of how the post will look.

        Args:
            content: Post content
            platform: Platform name

        Returns:
            Dictionary with preview information
        """
        specs = self.platform_specs.get(platform.lower(), self.platform_specs["linkedin"])

        return {
            "platform": platform,
            "character_count": len(content),
            "max_length": specs["max_length"],
            "within_limits": len(content) <= specs["max_length"],
            "optimal_range": specs["optimal_length"],
            "is_optimal": specs["optimal_length"][0] <= len(content) <= specs["optimal_length"][1],
            "has_media_requirement": platform.lower() == "instagram",
            "preview": content[:200] + "..." if len(content) > 200 else content
        }
