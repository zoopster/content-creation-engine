#!/usr/bin/env python3
"""
Web Search Integration Example

Demonstrates real web search integration using Firecrawl or Serper providers.

Requirements:
    1. Set up a .env file with your API keys:
       - FIRECRAWL_API_KEY=fc-your-key  (recommended)
       - SERPER_API_KEY=your-serper-key  (alternative)

    2. Install required packages:
       pip install firecrawl-py aiohttp python-dotenv

    3. Enable web search:
       - Set ENABLE_WEB_SEARCH=true in .env
       - Or pass enable_web_search=True to the agent

Usage:
    # Run with mock search (no API key needed)
    python examples/web_search_example.py

    # Run with real search (requires API key)
    ENABLE_WEB_SEARCH=true python examples/web_search_example.py

    # Run with Firecrawl
    ENABLE_WEB_SEARCH=true FIRECRAWL_API_KEY=fc-your-key python examples/web_search_example.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Note: python-dotenv not installed, using environment variables directly")


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")


async def demo_search_provider():
    """Demonstrate direct search provider usage."""
    print_section("Search Provider Demo")

    from core.search import configure_search, get_search_provider, SearchConfig

    # Check what's configured
    firecrawl_key = os.environ.get("FIRECRAWL_API_KEY")
    serper_key = os.environ.get("SERPER_API_KEY")
    use_mock = os.environ.get("USE_MOCK_SEARCH", "").lower() == "true"

    print("Configuration:")
    print(f"  FIRECRAWL_API_KEY: {'configured' if firecrawl_key else 'not set'}")
    print(f"  SERPER_API_KEY: {'configured' if serper_key else 'not set'}")
    print(f"  USE_MOCK_SEARCH: {use_mock}")

    # Configure search
    configure_search(use_mock=use_mock or not (firecrawl_key or serper_key))

    # Get provider
    provider = get_search_provider()

    if not provider:
        print("\nNo search provider available!")
        return

    print(f"\nUsing search provider: {provider.name}")

    # Execute a search
    query = "AI agents multi-agent systems 2025"
    print(f"\nSearching for: '{query}'")

    from core.search.base import SearchConfig
    config = SearchConfig(max_results=5)

    results = await provider.search(query, config)

    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Source: {result.source}")
        print(f"   Score: {result.score:.2f}")
        if result.content:
            preview = result.content[:150] + "..." if len(result.content) > 150 else result.content
            print(f"   Content: {preview}")
        print()


async def demo_web_search_skill():
    """Demonstrate WebSearchSkill usage."""
    print_section("WebSearchSkill Demo")

    from skills.web_search import WebSearchSkill

    # Create skill with configuration
    skill = WebSearchSkill(config={
        "max_results": 5,
        "enable_filtering": True,
    })

    # Execute search
    query = "content creation automation AI"
    print(f"Searching for: '{query}'")

    results = await skill.execute_async(query, max_results=5)

    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        if result.get('content'):
            preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
            print(f"   Preview: {preview}")
        print()

    # Demonstrate query optimization
    print("\nQuery Optimization Demo:")
    requirements = {
        "recent_only": True,
        "content_type": "technical",
        "must_include": ["machine learning"],
    }
    optimized = skill.optimize_query("AI agents", requirements)
    print(f"  Original: 'AI agents'")
    print(f"  Optimized: '{optimized}'")


async def demo_research_agent():
    """Demonstrate LLMResearchAgent with real search."""
    print_section("LLMResearchAgent with Web Search")

    # Check if LLM API key is available
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if not (anthropic_key or openai_key):
        print("Note: No LLM API key found. Using mock LLM responses.")
        print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY for full demo.\n")

    # Check if web search is enabled
    enable_search = os.environ.get("ENABLE_WEB_SEARCH", "").lower() == "true"

    from agents.research import LLMResearchAgent

    # Create agent with web search enabled (using Firecrawl)
    agent = LLMResearchAgent(config={
        "enable_web_search": enable_search,
        "search_provider": "firecrawl",
        "min_sources": 3,
        "max_sources": 5,
    })

    print(f"Web search enabled: {agent.enable_web_search}")
    print(f"Search provider: {agent.search_provider_name or 'auto-detect (firecrawl)'}\n")

    # Execute research
    topic = "Multi-agent AI systems for content creation"
    print(f"Researching topic: '{topic}'\n")

    try:
        brief = await agent.process_async({
            "topic": topic,
            "requirements": {
                "recent_only": True,
                "content_type": "technical",
                "depth": "standard",
            }
        })

        print("Research Brief Generated:")
        print(f"  Topic: {brief.topic}")
        print(f"  Sources: {len(brief.sources)}")
        print(f"  Key Findings: {len(brief.key_findings)}")

        print("\nTop Sources:")
        for i, source in enumerate(brief.sources[:3], 1):
            print(f"  {i}. {source.title}")
            print(f"     Credibility: {source.credibility_score:.2f}")
            print(f"     URL: {source.url}")

        print("\nKey Findings:")
        for i, finding in enumerate(brief.key_findings[:3], 1):
            preview = finding[:100] + "..." if len(finding) > 100 else finding
            print(f"  {i}. {preview}")

        if brief.research_gaps:
            print("\nResearch Gaps Identified:")
            for gap in brief.research_gaps[:2]:
                print(f"  - {gap}")

    except Exception as e:
        print(f"Research failed: {e}")
        print("\nThis might be due to missing API keys.")
        print("Ensure you have either ANTHROPIC_API_KEY or OPENAI_API_KEY set.")


async def demo_multiple_queries():
    """Demonstrate searching with multiple queries."""
    print_section("Multiple Query Search Demo")

    from skills.web_search import WebSearchSkill

    skill = WebSearchSkill()

    queries = [
        "AI content generation tools 2025",
        "multi-agent systems architecture",
        "automated content creation workflow",
    ]

    print(f"Executing {len(queries)} queries in parallel...\n")

    results = await skill.search_multiple_queries(queries, max_results_per_query=3)

    print(f"Total unique results: {len(results)}\n")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result['title']}")
        print(f"   Source: {result.get('source', 'unknown')}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print(" WEB SEARCH INTEGRATION DEMO")
    print("="*60)

    print("\nThis demo shows the real web search integration for the")
    print("Content Creation Engine research capabilities.")

    # Show current configuration
    print("\nEnvironment Configuration:")
    print(f"  ENABLE_WEB_SEARCH: {os.environ.get('ENABLE_WEB_SEARCH', 'not set')}")
    print(f"  FIRECRAWL_API_KEY: {'set' if os.environ.get('FIRECRAWL_API_KEY') else 'not set'}")
    print(f"  SERPER_API_KEY: {'set' if os.environ.get('SERPER_API_KEY') else 'not set'}")
    print(f"  ANTHROPIC_API_KEY: {'set' if os.environ.get('ANTHROPIC_API_KEY') else 'not set'}")

    # Run demos
    asyncio.run(demo_search_provider())
    asyncio.run(demo_web_search_skill())
    asyncio.run(demo_multiple_queries())

    # Only run research agent demo if LLM API key is available
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        asyncio.run(demo_research_agent())
    else:
        print_section("LLMResearchAgent Demo (Skipped)")
        print("Skipping LLMResearchAgent demo - no LLM API key configured.")
        print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY to run this demo.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE")
    print("="*60)
    print("\nTo enable real web search:")
    print("  1. Get a Firecrawl API key from https://firecrawl.dev/")
    print("  2. Add to .env: FIRECRAWL_API_KEY=fc-your-key")
    print("  3. Add to .env: ENABLE_WEB_SEARCH=true")
    print("  4. Re-run this script")
    print()


if __name__ == "__main__":
    main()
