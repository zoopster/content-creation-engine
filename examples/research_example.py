"""
Example usage of the Research Agent with web search integration.

This script demonstrates:
1. Basic research agent usage with simulated data
2. Integration with WebSearch tool for real searches
3. Complete workflow from search to ResearchBrief
4. Error handling and validation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.research.research import ResearchAgent
from skills.web_search.web_search import WebSearchSkill
from agents.base.models import ContentType
import json


def example_1_basic_usage():
    """
    Example 1: Basic research agent usage with simulated search results.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Research Agent Usage")
    print("="*80 + "\n")

    # Initialize the agent
    agent = ResearchAgent(config={
        "min_sources": 2,
        "max_sources": 5,
        "min_credibility": 0.5
    })

    # Prepare research input
    input_data = {
        "topic": "Multi-agent systems for content creation",
        "requirements": {
            "recent_only": True,
            "focus_areas": ["AI agents", "workflow automation"],
            "content_type": "technical"
        }
    }

    print(f"Research Topic: {input_data['topic']}")
    print(f"Requirements: {json.dumps(input_data['requirements'], indent=2)}\n")

    # Note: In this example, the agent will return minimal results
    # because we're not providing actual search results
    # See example_2 for integration with WebSearch tool

    try:
        # Execute research
        research_brief = agent.process(input_data)

        # Display results
        print(f"✓ Research completed!")
        print(f"  Sources found: {len(research_brief.sources)}")
        print(f"  Key findings: {len(research_brief.key_findings)}")
        print(f"  Research gaps: {len(research_brief.research_gaps)}")

        # Validate
        is_valid, errors = research_brief.validate()
        if is_valid:
            print(f"\n✓ Research brief passed validation")
        else:
            print(f"\n⚠ Validation warnings:")
            for error in errors:
                print(f"  - {error}")

        # Show key findings
        if research_brief.key_findings:
            print(f"\nKey Findings:")
            for i, finding in enumerate(research_brief.key_findings, 1):
                print(f"  {i}. {finding}")

        # Show research gaps
        if research_brief.research_gaps:
            print(f"\nResearch Gaps:")
            for gap in research_brief.research_gaps:
                print(f"  - {gap}")

    except Exception as e:
        print(f"✗ Error during research: {e}")


def example_2_with_web_search():
    """
    Example 2: Research agent with WebSearch tool integration.

    This example shows how to integrate with the WebSearch tool
    to perform actual web searches.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Research Agent with WebSearch Tool")
    print("="*80 + "\n")

    # Initialize components
    agent = ResearchAgent()
    search_skill = WebSearchSkill(config={"max_results": 10})

    topic = "AI agents for automated content generation 2024"

    print(f"Research Topic: {topic}\n")

    # Step 1: Optimize the search query
    requirements = {
        "recent_only": True,
        "content_type": "technical",
        "must_include": ["machine learning", "automation"]
    }

    optimized_query = search_skill.optimize_query(topic, requirements)
    print(f"Optimized Query: {optimized_query}\n")

    # Step 2: Execute web search
    # Note: This is where you would use the WebSearch tool
    # For demonstration, we'll use simulated results
    print("Executing web search...")

    # REAL IMPLEMENTATION WOULD BE:
    # from claude_tools import WebSearch
    # search_results = WebSearch(query=optimized_query)
    # parsed_results = [search_skill.parse_search_result(r) for r in search_results]

    # SIMULATED RESULTS for demonstration:
    simulated_results = [
        {
            "title": "Multi-Agent Systems in Modern AI: A Technical Overview",
            "url": "https://arxiv.org/paper/ai-agents-2024",
            "content": """This research paper examines multi-agent systems for content automation.
            Research shows that collaborative AI agents can improve content generation efficiency by 45%.
            The study found that specialized agents handling different aspects of content creation
            (research, writing, editing) produce higher quality outputs than monolithic systems.
            According to the findings, agent-based systems reduce production time while maintaining
            consistency across deliverables.""",
            "published_date": "2024-03-15",
            "author": "Dr. Sarah Chen",
            "source": "arXiv"
        },
        {
            "title": "Workflow Automation with AI Agents",
            "url": "https://techcrunch.com/2024/ai-workflow-automation",
            "content": """AI-powered workflow automation is transforming content creation.
            Companies using multi-agent systems report 60% faster content production.
            The technology enables parallel processing of research and writing tasks.
            Experts predict that 80% of routine content will be agent-generated by 2025.""",
            "published_date": "2024-02-20",
            "author": "John Martinez",
            "source": "TechCrunch"
        },
        {
            "title": "Content Generation: The Role of Machine Learning",
            "url": "https://ieee.org/content-ml-2024",
            "content": """Machine learning models are increasingly used in content generation workflows.
            Studies indicate that ML-based content assistants improve writing quality scores by 30%.
            The integration of natural language processing enables context-aware content creation.
            Automation of repetitive tasks allows human creators to focus on strategy and creativity.""",
            "published_date": "2024-01-10",
            "author": "Prof. Michael Wong",
            "source": "IEEE"
        },
        {
            "title": "You Won't Believe These AI Writing Tools!!! Shocking Results",
            "url": "https://clickbait-blog.com/ai-tools",
            "content": """Check out these amazing AI tools! They're revolutionary!
            Everyone is using them! Don't miss out!""",
            "published_date": "2024-04-01",
            "source": "Random Blog"
        }
    ]

    print(f"Found {len(simulated_results)} search results\n")

    # Step 3: Process with Research Agent
    # The agent expects to use its internal search, so we need to simulate
    # providing the results through the agent's pipeline

    # Create a custom processing flow
    print("Processing search results...\n")

    # Evaluate sources using agent's methods
    sources = agent._evaluate_sources(simulated_results)

    print("Source Evaluation:")
    for i, source in enumerate(sources, 1):
        print(f"  {i}. {source.title}")
        print(f"     URL: {source.url}")
        print(f"     Credibility: {source.credibility_score:.2f}")
        print(f"     Facts: {len(source.key_facts)}")
        print(f"     Quotes: {len(source.key_quotes)}")
        print()

    # Filter by credibility
    quality_sources = [s for s in sources if s.credibility_score >= 0.5]
    print(f"Quality Sources (credibility >= 0.5): {len(quality_sources)}\n")

    # Extract findings
    key_findings = agent._extract_key_findings(quality_sources, topic)
    data_points = agent._extract_data_points(quality_sources)

    print("Key Findings:")
    for i, finding in enumerate(key_findings, 1):
        print(f"  {i}. {finding}")

    print(f"\nData Points:")
    print(f"  Total sources: {data_points['source_count']}")
    print(f"  High credibility sources: {data_points['high_credibility_sources']}")
    print(f"  Average credibility: {data_points['average_credibility']:.2f}")
    print(f"  Facts extracted: {data_points['total_facts_extracted']}")
    print(f"  Quotes extracted: {data_points['total_quotes_extracted']}")

    if "statistics_found" in data_points:
        print(f"  Statistics: {data_points['statistics_found'][:3]}")


def example_3_custom_configuration():
    """
    Example 3: Research agent with custom configuration.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Custom Configuration")
    print("="*80 + "\n")

    # Configure agent with strict requirements
    agent = ResearchAgent(config={
        "min_sources": 5,           # Require 5 sources minimum
        "max_sources": 15,          # Allow up to 15 sources
        "min_credibility": 0.7      # Only high-credibility sources
    })

    print("Agent Configuration:")
    print(f"  Minimum sources: {agent.min_sources}")
    print(f"  Maximum sources: {agent.max_sources}")
    print(f"  Minimum credibility: {agent.min_credibility}\n")

    # Research a business-focused topic
    input_data = {
        "topic": "ROI of marketing automation",
        "requirements": {
            "content_type": "business",
            "focus_areas": ["ROI metrics", "case studies", "cost savings"],
            "domains": ["forbes.com", "harvard.edu", "mckinsey.com"],
            "year": 2024
        }
    }

    print(f"Topic: {input_data['topic']}")
    print(f"Focus: Business/ROI analysis")
    print(f"Target domains: {input_data['requirements']['domains']}\n")

    try:
        research_brief = agent.process(input_data)

        print("✓ Research completed")

        # Execution summary
        summary = agent.get_execution_summary()
        print(f"\nAgent Execution Summary:")
        print(f"  Total executions: {summary['total_executions']}")
        print(f"  Last execution: {summary['last_execution']}")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_4_workflow_integration():
    """
    Example 4: Integration with orchestrator workflow.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Workflow Integration")
    print("="*80 + "\n")

    from agents.orchestrator.orchestrator import OrchestratorAgent
    from agents.base.models import WorkflowRequest

    # Initialize orchestrator and research agent
    orchestrator = OrchestratorAgent()
    research_agent = ResearchAgent()

    # Create a workflow request
    request = WorkflowRequest(
        request_text="Create an article about AI-powered content automation",
        content_types=[ContentType.ARTICLE],
        priority="high"
    )

    print(f"Workflow Request: {request.request_text}")
    print(f"Content Type: {request.content_types[0].value}\n")

    # Orchestrator creates execution plan
    result = orchestrator.process(request)

    print(f"Workflow Type: {result['workflow_type']}")
    print(f"Description: {result['workflow_description']}\n")

    print("Execution Plan:")
    for i, step in enumerate(result['execution_plan'], 1):
        agent_or_skill = step.get('agent', step.get('skill'))
        output = step.get('output')
        print(f"  {i}. {agent_or_skill} → {output}")

    # Extract research step
    research_step = result['execution_plan'][0]
    print(f"\n→ Executing Step 1: Research Agent")

    # Execute research
    research_input = {
        "topic": result['requirements']['topic']
    }

    research_brief = research_agent.process(research_input)

    print(f"  ✓ Research Brief created")
    print(f"  ✓ Next step: {result['execution_plan'][1].get('skill', 'content-brief')}")
    print(f"  → Output will be passed to Creation Agent")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("RESEARCH AGENT EXAMPLES")
    print("="*80)

    try:
        example_1_basic_usage()
        example_2_with_web_search()
        example_3_custom_configuration()
        example_4_workflow_integration()

        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n✗ Example failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
