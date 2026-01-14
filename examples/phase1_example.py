"""
Phase 1 Example: Orchestrator, Content Brief, and Brand Voice

This example demonstrates how to use the Phase 1 components:
1. Create a workflow request
2. Use Orchestrator to plan execution
3. Create a content brief from research
4. Validate content with brand voice

Note: Research, Creation, and Production agents will be implemented in later phases.
For this example, we create mock data for those components.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.orchestrator.orchestrator import OrchestratorAgent
from agents.base.models import (
    WorkflowRequest, ContentType, ToneType,
    ResearchBrief, Source, DraftContent
)
from skills import ContentBriefSkill, BrandVoiceSkill


def example_workflow_planning():
    """Example 1: Use Orchestrator to plan a workflow."""
    print("=" * 70)
    print("EXAMPLE 1: Workflow Planning with Orchestrator")
    print("=" * 70)

    # Create orchestrator
    orchestrator = OrchestratorAgent()

    # Create a content request
    request = WorkflowRequest(
        request_text="Write an article about AI in healthcare diagnostics",
        content_types=[ContentType.ARTICLE],
        priority="high",
        additional_context={
            "target_length": "1200 words",
            "audience": "healthcare professionals"
        }
    )

    print(f"\n📝 Request: {request.request_text}")
    print(f"📋 Content Types: {[ct.value for ct in request.content_types]}")

    # Process request to get execution plan
    result = orchestrator.process(request)

    print(f"\n✅ Workflow Selected: {result['workflow_type']}")
    print(f"📖 Description: {result['workflow_description']}")
    print(f"\n🔄 Execution Plan:")
    for i, step in enumerate(result['execution_plan'], 1):
        agent_or_skill = step.get('agent') or step.get('skill')
        print(f"  {i}. {agent_or_skill}")
        print(f"     Input: {step['input']}")
        print(f"     Output: {step['output']}")
        if step.get('quality_gate'):
            print(f"     Quality Gate: {step['quality_gate']}")

    # Show available workflows
    print(f"\n📚 Available Workflows:")
    workflows = orchestrator.get_available_workflows()
    for wf_type, description in workflows.items():
        print(f"  - {wf_type}: {description}")


def example_content_brief_creation():
    """Example 2: Create a content brief from research."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 2: Content Brief Creation")
    print("=" * 70)

    # Create content brief skill
    skill = ContentBriefSkill()

    # Mock research brief (in production, this comes from Research Agent)
    research = ResearchBrief(
        topic="AI in Healthcare Diagnostics",
        sources=[
            Source(
                url="https://example.com/ai-healthcare-1",
                title="AI Transforming Medical Diagnosis",
                author="Dr. Jane Smith",
                publication_date="2025-12",
                credibility_score=0.9,
                key_facts=[
                    "AI reduces diagnostic errors by 35%",
                    "Average diagnosis time decreased from 4 hours to 45 minutes"
                ],
                key_quotes=[
                    "AI doesn't replace doctors, it augments their capabilities"
                ]
            ),
            Source(
                url="https://example.com/ai-healthcare-2",
                title="Machine Learning in Radiology",
                author="Healthcare Tech Review",
                publication_date="2026-01",
                credibility_score=0.85,
                key_facts=[
                    "AI achieves 94% accuracy in detecting lung cancer from X-rays",
                    "Reduces radiologist workload by 40%"
                ]
            ),
            Source(
                url="https://example.com/ai-healthcare-3",
                title="Economic Impact of AI Diagnostics",
                credibility_score=0.75,
                key_facts=[
                    "Healthcare systems save $150B annually with AI diagnostics",
                    "Patient outcomes improve by 25%"
                ]
            )
        ],
        key_findings=[
            "AI significantly reduces diagnostic errors and saves time",
            "Machine learning excels in image-based diagnostics like radiology",
            "AI augments rather than replaces healthcare professionals",
            "Economic benefits are substantial for healthcare systems",
            "Patient outcomes improve with AI-assisted diagnosis"
        ],
        data_points={
            "error_reduction": "35%",
            "time_savings": "4 hours to 45 minutes",
            "accuracy_rate": "94%",
            "cost_savings": "$150B annually",
            "outcome_improvement": "25%"
        }
    )

    print(f"\n🔬 Research Topic: {research.topic}")
    print(f"📚 Sources: {len(research.sources)}")
    print(f"💡 Key Findings: {len(research.key_findings)}")

    # Validate research
    is_valid, errors = research.validate()
    print(f"\n✅ Research Valid: {is_valid}")
    if errors:
        print(f"⚠️  Validation Errors: {errors}")

    # Create content brief
    brief = skill.execute(
        research_brief=research,
        content_type=ContentType.ARTICLE,
        target_audience="Healthcare professionals and medical administrators",
        additional_requirements={
            "tone": ToneType.PROFESSIONAL,
            "word_count_range": (1000, 1500)
        }
    )

    print(f"\n📋 Content Brief Created:")
    print(f"  Content Type: {brief.content_type.value}")
    print(f"  Target Audience: {brief.target_audience}")
    print(f"  Tone: {brief.tone.value}")
    print(f"  Word Count Range: {brief.word_count_range[0]}-{brief.word_count_range[1]}")
    print(f"\n  Key Messages:")
    for i, message in enumerate(brief.key_messages, 1):
        print(f"    {i}. {message}")
    print(f"\n  Structure Requirements:")
    for i, section in enumerate(brief.structure_requirements, 1):
        print(f"    {i}. {section}")
    print(f"\n  SEO Keywords: {', '.join(brief.seo_keywords[:8])}")

    # Validate brief
    is_valid, errors = brief.validate()
    print(f"\n✅ Brief Valid: {is_valid}")
    if errors:
        print(f"⚠️  Validation Errors: {errors}")

    return brief


def example_brand_voice_validation():
    """Example 3: Validate content with brand voice."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 3: Brand Voice Validation")
    print("=" * 70)

    # Create brand voice skill
    skill = BrandVoiceSkill()

    # Mock draft content (in production, this comes from Creation Agent)
    good_content = """
    Artificial intelligence is transforming healthcare diagnostics in measurable ways.
    Medical professionals now leverage AI systems to reduce diagnostic errors by 35%
    while decreasing average diagnosis time from four hours to just 45 minutes.

    Machine learning algorithms achieve 94% accuracy when detecting lung cancer from
    X-ray images. This capability enables radiologists to focus on complex cases while
    AI handles routine screenings. The technology augments rather than replaces human
    expertise.

    Healthcare systems that implement AI diagnostics report substantial benefits.
    Organizations save approximately $150 billion annually through improved efficiency.
    Patient outcomes improve by 25% when AI assists with diagnosis and treatment planning.

    The data demonstrates clear value. AI doesn't revolutionize healthcare through
    disruption. Instead, it enhances existing practices with proven, measurable improvements
    that benefit both providers and patients.
    """

    bad_content = """
    AI is just totally revolutionizing healthcare in the most amazing way ever! It's
    incredibly easy to use and it's definitely the best solution for making diagnoses
    super simple. The technology is absolutely game-changing and will completely disrupt
    the entire medical field.

    Healthcare was fundamentally broken and needed this paradigm shift. Traditional
    methods are clearly inferior and this cheap, innovative solution leverages cutting-edge
    synergies to deliver unbelievable results. It's basically magic how the system works.

    Doctors who don't adopt this will be left behind in the dust. The future is now and
    it's insane how much better everything is. Patients are getting the most incredible
    care that's really, really effective. Healthcare has been disrupted forever.
    """

    # Test good content
    print("\n📝 Testing GOOD Content:")
    print("-" * 70)
    draft_good = DraftContent(
        content=good_content,
        content_type=ContentType.ARTICLE,
        word_count=len(good_content.split())
    )

    result_good = skill.execute(
        draft_content=draft_good,
        target_tone=ToneType.PROFESSIONAL
    )

    print(f"✅ Validation Passed: {result_good.passed}")
    print(f"📊 Score: {result_good.score:.2f}")
    if result_good.issues:
        print(f"\n⚠️  Issues ({len(result_good.issues)}):")
        for issue in result_good.issues:
            print(f"  - {issue}")
    if result_good.suggestions:
        print(f"\n💡 Suggestions ({len(result_good.suggestions)}):")
        for suggestion in result_good.suggestions:
            print(f"  - {suggestion}")

    # Test bad content
    print("\n\n📝 Testing BAD Content:")
    print("-" * 70)
    draft_bad = DraftContent(
        content=bad_content,
        content_type=ContentType.ARTICLE,
        word_count=len(bad_content.split())
    )

    result_bad = skill.execute(
        draft_content=draft_bad,
        target_tone=ToneType.PROFESSIONAL
    )

    print(f"✅ Validation Passed: {result_bad.passed}")
    print(f"📊 Score: {result_bad.score:.2f}")
    if result_bad.issues:
        print(f"\n⚠️  Issues ({len(result_bad.issues)}):")
        for issue in result_bad.issues:
            print(f"  - {issue}")
    if result_bad.suggestions:
        print(f"\n💡 Suggestions ({len(result_bad.suggestions)}):")
        for suggestion in result_bad.suggestions:
            print(f"  - {suggestion}")


def example_multi_platform_campaign():
    """Example 4: Multi-platform campaign workflow."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 4: Multi-Platform Campaign Planning")
    print("=" * 70)

    orchestrator = OrchestratorAgent()

    # Request content for multiple platforms
    request = WorkflowRequest(
        request_text="Create content about cloud security best practices",
        content_types=[
            ContentType.ARTICLE,
            ContentType.SOCIAL_POST,
            ContentType.EMAIL
        ],
        additional_context={
            "campaign_name": "Cloud Security 2026",
            "platforms": ["blog", "linkedin", "email_newsletter"]
        }
    )

    print(f"\n📝 Request: {request.request_text}")
    print(f"📋 Content Types: {[ct.value for ct in request.content_types]}")

    result = orchestrator.process(request)

    print(f"\n✅ Workflow Selected: {result['workflow_type']}")
    print(f"📖 Description: {result['workflow_description']}")
    print(f"\n🔄 Execution Plan ({len(result['execution_plan'])} steps):")
    for i, step in enumerate(result['execution_plan'], 1):
        agent_or_skill = step.get('agent') or step.get('skill')
        print(f"\n  Step {i}: {agent_or_skill}")
        if step.get('parallel'):
            print(f"    ⚡ Parallel execution for: {step.get('tracks')}")
        print(f"    Input: {step['input']}")
        print(f"    Output: {step['output']}")


if __name__ == "__main__":
    print("\n🚀 Content Creation Engine - Phase 1 Examples\n")

    # Run all examples
    example_workflow_planning()
    brief = example_content_brief_creation()
    example_brand_voice_validation()
    example_multi_platform_campaign()

    print("\n\n" + "=" * 70)
    print("✅ All Phase 1 examples completed!")
    print("=" * 70)
    print("\nNext Steps:")
    print("  - Phase 2: Implement Research and Creation Agents")
    print("  - Phase 3: Implement Production Agent")
    print("  - Phase 4: Add content repurposing capabilities")
    print("  - Phase 5: Quality gates and optimization\n")
