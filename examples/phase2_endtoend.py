"""
Phase 2 End-to-End Example: Complete Workflow Execution

This example demonstrates the full content creation workflow:
1. User submits a content request
2. Orchestrator plans the workflow
3. Research Agent gathers sources and findings
4. Content Brief Skill structures the requirements
5. Creation Agent generates the content
6. Brand Voice Skill validates consistency
7. Production (mock) prepares final output

This shows Phase 2's end-to-end integration of all components.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.workflow_executor import WorkflowExecutor
from agents.base.models import WorkflowRequest, ContentType
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_single_article_workflow():
    """Example 1: Single article production workflow."""
    print("=" * 80)
    print("EXAMPLE 1: Single Article Production Workflow")
    print("=" * 80)

    # Create workflow executor
    executor = WorkflowExecutor(config={
        "enforce_quality_gates": True,
        "strict_quality_gates": False
    })

    # Create content request
    request = WorkflowRequest(
        request_text="Write an article about sustainable agriculture practices",
        content_types=[ContentType.ARTICLE],
        priority="normal",
        additional_context={
            "target_audience": "Farmers and agricultural professionals",
            "tone": "professional",
            "word_count_range": (1000, 1500)
        }
    )

    print(f"\n📝 Request: {request.request_text}")
    print(f"📋 Content Type: {request.content_types[0].value}")
    print(f"👥 Audience: {request.additional_context['target_audience']}")

    # Execute workflow
    print(f"\n🚀 Executing workflow...\n")
    result = executor.execute(request)

    # Display results
    print(f"\n{'='*80}")
    print(f"WORKFLOW RESULTS")
    print(f"{'='*80}")
    print(f"✅ Success: {result.success}")
    print(f"🔄 Workflow Type: {result.workflow_type}")
    print(f"⏱️  Start Time: {result.start_time}")
    print(f"⏱️  End Time: {result.end_time}")

    print(f"\n📊 Steps Completed ({len(result.steps_completed)}):")
    for step in result.steps_completed:
        status = "✅" if step["success"] else "❌"
        print(f"  {status} {step['step']}: {step['output_type']}")
        if step.get("error"):
            print(f"     ⚠️  Error: {step['error']}")

    # Show generated content
    if "draft_content" in result.outputs:
        draft = result.outputs["draft_content"]
        print(f"\n📄 Generated Content:")
        print(f"   Word Count: {draft.word_count}")
        print(f"   Format: {draft.format}")
        print(f"\n   Content Preview (first 500 chars):")
        print(f"   {'-'*76}")
        print(f"   {draft.content[:500]}...")
        print(f"   {'-'*76}")

    # Show brand voice results
    if "brand_voice_result" in result.outputs:
        brand = result.outputs["brand_voice_result"]
        print(f"\n🎨 Brand Voice Validation:")
        print(f"   Passed: {brand.passed}")
        print(f"   Score: {brand.score:.2f}")
        if brand.issues:
            print(f"   Issues: {len(brand.issues)}")
            for issue in brand.issues[:3]:
                print(f"     - {issue}")
        if brand.suggestions:
            print(f"   Suggestions: {len(brand.suggestions)}")
            for suggestion in brand.suggestions[:2]:
                print(f"     - {suggestion}")

    # Show research brief summary
    if "research_brief" in result.outputs:
        research = result.outputs["research_brief"]
        print(f"\n🔬 Research Summary:")
        print(f"   Topic: {research.topic}")
        print(f"   Sources: {len(research.sources)}")
        print(f"   Key Findings: {len(research.key_findings)}")
        if research.key_findings:
            print(f"   Top Finding: {research.key_findings[0]}")

    return result


def example_multi_platform_campaign():
    """Example 2: Multi-platform campaign workflow."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 2: Multi-Platform Campaign Workflow")
    print("=" * 80)

    # Create workflow executor
    executor = WorkflowExecutor(config={
        "enforce_quality_gates": True
    })

    # Create multi-platform request
    request = WorkflowRequest(
        request_text="Create content about AI-powered customer service",
        content_types=[
            ContentType.ARTICLE,
            ContentType.SOCIAL_POST,
            ContentType.EMAIL
        ],
        priority="high",
        additional_context={
            "target_audience": "Business leaders and CX professionals",
            "campaign_name": "AI Customer Service 2026"
        }
    )

    print(f"\n📝 Request: {request.request_text}")
    print(f"📋 Content Types: {[ct.value for ct in request.content_types]}")
    print(f"🎯 Campaign: {request.additional_context['campaign_name']}")

    # Execute workflow
    print(f"\n🚀 Executing multi-platform workflow...\n")
    result = executor.execute(request)

    # Display results
    print(f"\n{'='*80}")
    print(f"WORKFLOW RESULTS")
    print(f"{'='*80}")
    print(f"✅ Success: {result.success}")
    print(f"🔄 Workflow Type: {result.workflow_type}")

    print(f"\n📊 Steps Completed ({len(result.steps_completed)}):")
    step_counts = {}
    for step in result.steps_completed:
        step_name = step["step"]
        step_counts[step_name] = step_counts.get(step_name, 0) + 1
        status = "✅" if step["success"] else "❌"
        count = f" ({step_counts[step_name]})" if step_counts[step_name] > 1 else ""
        print(f"  {status} {step_name}{count}: {step['output_type']}")

    # Show content briefs
    if "content_briefs" in result.outputs:
        briefs = result.outputs["content_briefs"]
        print(f"\n📋 Content Briefs Created: {len(briefs)}")
        for brief in briefs:
            print(f"   - {brief.content_type.value}: {brief.word_count_range[0]}-{brief.word_count_range[1]} words")

    # Show drafts
    if "drafts" in result.outputs:
        drafts = result.outputs["drafts"]
        print(f"\n📄 Content Generated: {len(drafts)}")
        for draft in drafts:
            print(f"   - {draft.content_type.value}: {draft.word_count} words")

    # Show brand voice results
    if "brand_voice_results" in result.outputs:
        brand_results = result.outputs["brand_voice_results"]
        print(f"\n🎨 Brand Voice Validation: {len(brand_results)} pieces")
        for i, brand in enumerate(brand_results):
            content_type = drafts[i].content_type.value if "drafts" in result.outputs and i < len(drafts) else f"Item {i+1}"
            print(f"   - {content_type}: {'PASSED' if brand.passed else 'FAILED'} (score: {brand.score:.2f})")

    # Show production outputs
    if "production_outputs" in result.outputs:
        outputs = result.outputs["production_outputs"]
        print(f"\n📦 Production Outputs: {len(outputs)}")
        for output in outputs:
            print(f"   - {output.file_path} ({output.file_format})")

    return result


def example_social_only_workflow():
    """Example 3: Social media content only."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 3: Social Media Content Workflow")
    print("=" * 80)

    # Create workflow executor
    executor = WorkflowExecutor()

    # Create social-only request
    request = WorkflowRequest(
        request_text="Create a LinkedIn post about remote work productivity",
        content_types=[ContentType.SOCIAL_POST],
        additional_context={
            "platform": "linkedin",
            "target_audience": "Remote workers and managers",
            "include_hashtags": True
        }
    )

    print(f"\n📝 Request: {request.request_text}")
    print(f"📋 Platform: {request.additional_context['platform']}")

    # Execute workflow
    print(f"\n🚀 Executing social workflow...\n")
    result = executor.execute(request)

    # Display results
    print(f"\n{'='*80}")
    print(f"SOCIAL CONTENT RESULTS")
    print(f"{'='*80}")
    print(f"✅ Success: {result.success}")

    # Show generated social content
    if "draft_content" in result.outputs:
        draft = result.outputs["draft_content"]
        print(f"\n📱 Social Post Generated:")
        print(f"   Character Count: {draft.metadata.get('character_count', 'N/A')}")
        print(f"   Platform: {draft.metadata.get('platform', 'N/A')}")
        print(f"\n   Content:")
        print(f"   {'-'*76}")
        print(f"   {draft.content}")
        print(f"   {'-'*76}")

    return result


def example_with_quality_gate_enforcement():
    """Example 4: Demonstrating quality gate enforcement."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 4: Quality Gate Enforcement")
    print("=" * 80)

    # Create executor with strict quality gates
    executor = WorkflowExecutor(config={
        "enforce_quality_gates": True,
        "research": {
            "min_sources": 2,
            "min_credibility": 0.6
        }
    })

    # Create request
    request = WorkflowRequest(
        request_text="Write about quantum computing applications",
        content_types=[ContentType.ARTICLE],
        additional_context={
            "target_audience": "Technical professionals",
            "tone": "technical"
        }
    )

    print(f"\n📝 Request: {request.request_text}")
    print(f"⚡ Quality Gates: ENABLED")
    print(f"   - Research completeness check")
    print(f"   - Brief alignment check")
    print(f"   - Brand voice consistency check")

    # Execute workflow
    print(f"\n🚀 Executing with quality gates...\n")
    result = executor.execute(request)

    # Show quality gate results
    print(f"\n{'='*80}")
    print(f"QUALITY GATE RESULTS")
    print(f"{'='*80}")

    for step in result.steps_completed:
        if "quality_gate" in step.get("step", "").lower() or step.get("error"):
            status = "✅ PASSED" if step["success"] else "⚠️  WARNING"
            print(f"{status} - {step['step']}")
            if step.get("error"):
                print(f"   Issue: {step['error']}")

    if result.success:
        print(f"\n✅ All quality gates passed successfully!")
    else:
        print(f"\n⚠️  Some quality gates had warnings (execution continued)")

    return result


def print_summary():
    """Print overall summary."""
    print("\n\n" + "=" * 80)
    print("PHASE 2 IMPLEMENTATION COMPLETE")
    print("=" * 80)
    print("\n✅ End-to-End Workflows Implemented:")
    print("   ✓ Research Agent with source gathering")
    print("   ✓ Content Brief generation")
    print("   ✓ Content Creation (long-form and social)")
    print("   ✓ Brand Voice validation")
    print("   ✓ Quality gate enforcement")
    print("   ✓ Multi-platform campaigns")
    print("\n📊 Workflow Types Available:")
    print("   • Article Production")
    print("   • Multi-Platform Campaign")
    print("   • Social Media Content")
    print("   • Email Sequences")
    print("   • Presentations")
    print("\n🎯 Key Features:")
    print("   • Automatic workflow selection")
    print("   • Quality gates at each step")
    print("   • Error handling and logging")
    print("   • Configurable components")
    print("   • Detailed execution tracking")
    print("\n📝 Next Steps (Phase 3):")
    print("   • Production Agent for final formatting")
    print("   • Document generation (DOCX, PDF, PPTX)")
    print("   • Template system")
    print("   • Content repurposing capabilities")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n🚀 Content Creation Engine - Phase 2 End-to-End Examples\n")

    # Run all examples
    try:
        result1 = example_single_article_workflow()
        result2 = example_multi_platform_campaign()
        result3 = example_social_only_workflow()
        result4 = example_with_quality_gate_enforcement()

        # Print summary
        print_summary()

    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
