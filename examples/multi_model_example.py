#!/usr/bin/env python3
"""
Multi-Model Content Generation Example

Demonstrates the model provider abstraction layer, showing how to:
1. Configure multiple LLM providers (Anthropic, OpenAI)
2. Use different models for different tasks
3. Generate content with agent-specific model configurations
4. Switch providers at runtime

Prerequisites:
    Set environment variables:
    - ANTHROPIC_API_KEY (for Claude models)
    - OPENAI_API_KEY (for GPT models)

Usage:
    python examples/multi_model_example.py
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import (
    AnthropicProvider,
    OpenAIProvider,
    ModelRegistry,
    AgentModelConfig,
    GenerationConfig,
    ModelConfigManager,
    get_registry,
)
from agents.base.models import (
    ContentBrief,
    ContentType,
    ToneType,
    ResearchBrief,
    Source,
)


async def demo_basic_generation():
    """Demonstrate basic text generation with different providers."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Text Generation")
    print("=" * 60)

    registry = ModelRegistry()

    # Register available providers
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if anthropic_key:
        registry.register_provider("anthropic", AnthropicProvider(api_key=anthropic_key))
        print("✓ Anthropic provider registered")
    else:
        print("✗ Anthropic: No API key found (set ANTHROPIC_API_KEY)")

    if openai_key:
        registry.register_provider("openai", OpenAIProvider(api_key=openai_key))
        print("✓ OpenAI provider registered")
    else:
        print("✗ OpenAI: No API key found (set OPENAI_API_KEY)")

    if not registry.list_providers():
        print("\nNo providers available. Please set API keys.")
        return

    # List available models
    print("\nAvailable models:")
    for model in registry.list_all_models()[:5]:
        print(f"  - {model.display_name} ({model.id}) - {model.provider}")

    # Generate with first available provider
    provider_name = registry.list_providers()[0]
    provider = registry.get_provider(provider_name)
    model = provider.list_models()[0]

    print(f"\nGenerating with {model.display_name}...")

    result = await registry.generate(
        prompt="Write a one-paragraph summary about the benefits of AI in healthcare.",
        provider=provider_name,
        model=model.id,
        config=GenerationConfig(max_tokens=256, temperature=0.7),
    )

    print(f"\n--- Generated Content ({result.total_tokens} tokens) ---")
    print(result.content[:500] + "..." if len(result.content) > 500 else result.content)


async def demo_agent_configurations():
    """Demonstrate agent-specific model configurations."""
    print("\n" + "=" * 60)
    print("DEMO 2: Agent-Specific Model Configurations")
    print("=" * 60)

    # Use the config manager
    config_manager = ModelConfigManager()

    print("\nDefault agent configurations:")
    for agent_name in ["research", "creation", "social", "editing"]:
        agent_config = config_manager.get_agent_config(agent_name)
        print(f"  {agent_name}:")
        print(f"    Provider: {agent_config.provider}")
        print(f"    Model: {agent_config.model}")
        if agent_config.config:
            print(f"    Temperature: {agent_config.config.temperature}")
            print(f"    Max Tokens: {agent_config.config.max_tokens}")

    # Configure registry from config manager
    registry = config_manager.configure_registry()

    if not registry.list_providers():
        print("\nNo providers configured. Please set API keys.")
        return

    # Generate for specific agent
    print("\nGenerating content for 'creation' agent...")

    result = await registry.generate_for_agent(
        agent_name="creation",
        prompt="Write an engaging introduction paragraph for an article about sustainable energy.",
    )

    print(f"\n--- Creation Agent Output ---")
    print(f"Model: {result.model}")
    print(f"Tokens: {result.total_tokens}")
    print(result.content[:400] + "..." if len(result.content) > 400 else result.content)


async def demo_provider_comparison():
    """Compare outputs from different providers."""
    print("\n" + "=" * 60)
    print("DEMO 3: Provider Comparison")
    print("=" * 60)

    registry = get_registry()

    if len(registry.list_providers()) < 2:
        print("Need both Anthropic and OpenAI API keys for comparison demo.")
        print(f"Available providers: {registry.list_providers()}")
        return

    prompt = "Explain machine learning in 2-3 sentences for a business executive."

    print(f"\nPrompt: {prompt}\n")

    for provider_name in ["anthropic", "openai"]:
        provider = registry.get_provider(provider_name)
        model = provider.list_models()[0]  # Use first model

        print(f"--- {provider_name.upper()} ({model.id}) ---")

        result = await registry.generate(
            prompt=prompt,
            provider=provider_name,
            model=model.id,
            config=GenerationConfig(max_tokens=150, temperature=0.5),
        )

        print(result.content)
        print(f"[{result.total_tokens} tokens]\n")


async def demo_llm_creation_agent():
    """Demonstrate the LLM-powered creation agent."""
    print("\n" + "=" * 60)
    print("DEMO 4: LLM-Powered Content Creation")
    print("=" * 60)

    # Check if we have a provider available
    registry = get_registry()
    if not registry.list_providers():
        print("No providers available. Please set API keys.")
        return

    try:
        from agents.creation import LLMCreationAgent
    except ImportError as e:
        print(f"Import error: {e}")
        return

    # Create a research brief for context
    research_brief = ResearchBrief(
        topic="Artificial Intelligence in Modern Healthcare",
        sources=[
            Source(
                url="https://example.com/ai-healthcare",
                title="AI Transforming Healthcare Delivery",
                credibility_score=0.9,
                key_facts=[
                    "AI diagnostic tools show 94% accuracy in detecting certain cancers",
                    "Healthcare AI market projected to reach $45B by 2030",
                    "Machine learning reduces administrative burden by 30%",
                ],
                key_quotes=[
                    "AI will not replace doctors, but doctors who use AI will replace those who don't.",
                ],
            ),
        ],
    )

    # Create content brief
    brief = ContentBrief(
        content_type=ContentType.BLOG_POST,
        target_audience="Healthcare administrators and technology decision-makers",
        key_messages=[
            "AI is transforming healthcare delivery and patient outcomes",
            "Early adoption provides competitive advantage",
            "Implementation requires strategic planning and change management",
        ],
        tone=ToneType.PROFESSIONAL,
        word_count_range=(300, 500),
        structure_requirements=[
            "Introduction",
            "Current State of AI in Healthcare",
            "Benefits and ROI",
            "Implementation Considerations",
            "Conclusion",
        ],
        seo_keywords=["healthcare AI", "medical technology", "digital health"],
        research_brief=research_brief,
        brand_guidelines={
            "preferred_terms": ["innovative", "patient-centered", "evidence-based"],
            "avoided_terms": ["revolutionary", "disruptive"],
            "tone": "professional",
        },
    )

    # Create agent with default configuration
    agent = LLMCreationAgent()

    print("\nGenerating blog post with LLM Creation Agent...")
    print(f"Using registry providers: {registry.list_providers()}")

    try:
        draft = await agent.process_async({"content_brief": brief})

        print(f"\n--- Generated Blog Post ---")
        print(f"Content Type: {draft.content_type.value}")
        print(f"Word Count: {draft.word_count}")
        print(f"Model Used: {draft.metadata.get('model', 'N/A')}")
        print(f"Provider: {draft.metadata.get('provider', 'N/A')}")
        print(f"Tokens Used: {draft.metadata.get('tokens_used', 'N/A')}")
        print(f"Brand Voice Passed: {draft.metadata.get('brand_voice_passed', 'N/A')}")
        print("\n--- Content Preview ---")
        preview = draft.content[:800]
        if len(draft.content) > 800:
            preview += "\n\n[... content truncated ...]"
        print(preview)

    except Exception as e:
        print(f"Error generating content: {e}")
        import traceback
        traceback.print_exc()


async def demo_custom_configuration():
    """Demonstrate custom model configuration."""
    print("\n" + "=" * 60)
    print("DEMO 5: Custom Model Configuration")
    print("=" * 60)

    # Create custom configuration
    custom_config = {
        "providers": {
            "anthropic": {
                "enabled": True,
                "default_model": "claude-3-5-haiku-20241022",
            },
            "openai": {
                "enabled": True,
                "default_model": "gpt-4o-mini",
            },
        },
        "agents": {
            "research": {
                "provider": "anthropic",
                "model": "claude-3-5-haiku-20241022",  # Fast for research
                "config": {
                    "max_tokens": 2048,
                    "temperature": 0.3,
                },
            },
            "creation": {
                "provider": "openai",
                "model": "gpt-4o",  # High quality for creation
                "config": {
                    "max_tokens": 4096,
                    "temperature": 0.7,
                },
            },
        },
    }

    manager = ModelConfigManager(config=custom_config)
    registry = manager.configure_registry()

    print("Custom configuration applied:")
    print(f"  Available providers: {registry.list_providers()}")

    research_config = manager.get_agent_config("research")
    creation_config = manager.get_agent_config("creation")

    print(f"\n  Research Agent:")
    print(f"    Provider: {research_config.provider}")
    print(f"    Model: {research_config.model}")

    print(f"\n  Creation Agent:")
    print(f"    Provider: {creation_config.provider}")
    print(f"    Model: {creation_config.model}")

    # Generate with each configuration
    if registry.list_providers():
        print("\nGenerating with custom configurations...")

        for agent_name in ["research", "creation"]:
            config = manager.get_agent_config(agent_name)
            if config.provider in registry.list_providers():
                result = await registry.generate_for_agent(
                    agent_name,
                    f"Write a brief {agent_name}-style paragraph about AI.",
                )
                print(f"\n--- {agent_name.upper()} output ({result.model}) ---")
                print(result.content[:200] + "...")


async def demo_llm_research_agent():
    """Demonstrate the LLM-powered research agent."""
    print("\n" + "=" * 60)
    print("DEMO 6: LLM-Powered Research Agent")
    print("=" * 60)

    # Check if we have a provider available
    registry = get_registry()
    if not registry.list_providers():
        print("No providers available. Please set API keys.")
        return

    try:
        from agents.research import LLMResearchAgent
    except ImportError as e:
        print(f"Import error: {e}")
        return

    # Create research agent with default config
    agent = LLMResearchAgent()

    print("\nResearching topic: 'Artificial Intelligence in Modern Healthcare'")
    print(f"Using registry providers: {registry.list_providers()}")

    try:
        brief = await agent.process_async({
            "topic": "Artificial Intelligence in Modern Healthcare",
            "requirements": {
                "focus_areas": ["patient outcomes", "operational efficiency", "cost reduction"],
                "content_type": "business",
                "depth": "standard",
            }
        })

        print(f"\n--- Research Brief ---")
        print(f"Topic: {brief.topic}")
        print(f"Sources found: {len(brief.sources)}")
        print(f"High-credibility sources: {brief.data_points.get('high_credibility_sources', 'N/A')}")
        print(f"Average credibility: {brief.data_points.get('average_credibility', 0):.2f}")

        print(f"\n--- Top Sources ---")
        for source in brief.sources[:3]:
            print(f"  • {source.title}")
            print(f"    Credibility: {source.credibility_score:.2f}")
            print(f"    URL: {source.url[:50]}...")

        print(f"\n--- Key Findings ({len(brief.key_findings)}) ---")
        for i, finding in enumerate(brief.key_findings[:5], 1):
            preview = finding[:100] + "..." if len(finding) > 100 else finding
            print(f"  {i}. {preview}")

        print(f"\n--- Statistics Found ---")
        stats = brief.data_points.get("statistics_found", [])
        if stats:
            print(f"  {', '.join(stats[:8])}")
        else:
            print("  No statistics extracted")

        print(f"\n--- Research Gaps ---")
        for gap in brief.research_gaps[:3]:
            print(f"  • {gap}")

    except Exception as e:
        print(f"Error during research: {e}")
        import traceback
        traceback.print_exc()


async def demo_full_workflow():
    """Demonstrate complete research-to-content workflow."""
    print("\n" + "=" * 60)
    print("DEMO 7: Full Research → Creation Workflow")
    print("=" * 60)

    registry = get_registry()
    if not registry.list_providers():
        print("No providers available. Please set API keys.")
        return

    try:
        from agents.research import LLMResearchAgent
        from agents.creation import LLMCreationAgent
    except ImportError as e:
        print(f"Import error: {e}")
        return

    # Step 1: Research
    print("\n[Step 1] Conducting LLM-powered research...")
    research_agent = LLMResearchAgent(config={
        "temperature": 0.2,  # Low for accuracy
    })

    research_brief = await research_agent.process_async({
        "topic": "Remote Work Best Practices",
        "requirements": {
            "focus_areas": ["productivity", "team collaboration", "work-life balance"],
            "recent_only": True,
        }
    })

    print(f"  ✓ Research complete: {len(research_brief.sources)} sources, {len(research_brief.key_findings)} findings")

    # Step 2: Create content brief
    print("\n[Step 2] Creating content brief...")
    content_brief = ContentBrief(
        content_type=ContentType.ARTICLE,
        target_audience="HR managers and team leaders",
        key_messages=research_brief.key_findings[:5],
        tone=ToneType.PROFESSIONAL,
        word_count_range=(500, 800),
        structure_requirements=[
            "Introduction",
            "Key Productivity Strategies",
            "Team Collaboration Tools",
            "Maintaining Work-Life Balance",
            "Conclusion and Action Items",
        ],
        seo_keywords=["remote work", "productivity", "team management"],
        research_brief=research_brief,
        brand_guidelines={
            "preferred_terms": ["effective", "practical", "actionable"],
            "avoided_terms": ["unprecedented", "new normal"],
            "tone": "professional",
        },
    )
    print(f"  ✓ Content brief created")

    # Step 3: Generate content
    print("\n[Step 3] Generating article with LLM...")
    creation_agent = LLMCreationAgent(config={
        "temperature": 0.7,  # Higher for creativity
    })

    draft = await creation_agent.process_async({"content_brief": content_brief})

    print(f"  ✓ Article generated: {draft.word_count} words")
    print(f"  Model: {draft.metadata.get('model', 'N/A')}")
    print(f"  Brand voice: {'✓ Passed' if draft.metadata.get('brand_voice_passed') else '✗ Failed'}")

    print(f"\n--- Generated Article Preview ---")
    preview = draft.content[:600]
    if len(draft.content) > 600:
        preview += "\n\n[... article continues ...]"
    print(preview)


async def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("MULTI-MODEL CONTENT CREATION ENGINE DEMO")
    print("=" * 60)

    # Check for API keys
    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))

    print(f"\nEnvironment:")
    print(f"  ANTHROPIC_API_KEY: {'✓ Set' if has_anthropic else '✗ Not set'}")
    print(f"  OPENAI_API_KEY: {'✓ Set' if has_openai else '✗ Not set'}")

    if not has_anthropic and not has_openai:
        print("\n⚠️  No API keys found. Set at least one to run demos:")
        print("   export ANTHROPIC_API_KEY=your-key")
        print("   export OPENAI_API_KEY=your-key")
        return

    # Run demos
    await demo_basic_generation()
    await demo_agent_configurations()
    await demo_provider_comparison()
    await demo_llm_creation_agent()
    await demo_custom_configuration()
    await demo_llm_research_agent()
    await demo_full_workflow()

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
