#!/usr/bin/env python3
"""
Phase 3 Production Examples - Document Generation & Content Repurposing

Demonstrates:
1. All document formats (Markdown, HTML, DOCX, PDF, PPTX)
2. Brand template application
3. Batch production (multiple formats)
4. Content repurposing
5. End-to-end workflow with production
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.production.production import ProductionAgent
from agents.workflow_executor import WorkflowExecutor, WorkflowRequest
from agents.base.models import DraftContent, ContentType
from templates.brand.brand_config import get_brand_template
from skills.content_repurpose.content_repurpose import ContentRepurposeSkill


# Sample content for testing
SAMPLE_CONTENT = """# Cloud Migration Best Practices

## Executive Summary

Moving to the cloud offers significant benefits, but successful migration requires careful planning and execution. This guide outlines key best practices for enterprise cloud migration.

## Key Benefits of Cloud Migration

### Cost Optimization

Cloud infrastructure eliminates upfront capital expenses and converts them to operational expenses. Organizations can scale resources based on actual demand, reducing waste.

### Enhanced Scalability

Cloud platforms provide elastic scalability, allowing businesses to handle traffic spikes without over-provisioning infrastructure.

### Improved Security

Leading cloud providers invest heavily in security, offering enterprise-grade protection that many organizations cannot match with on-premises solutions.

## Migration Strategy

- **Assessment Phase**: Evaluate current infrastructure and identify cloud-ready applications
- **Planning Phase**: Design target architecture and migration sequence
- **Pilot Migration**: Test with non-critical workloads
- **Full Migration**: Execute phased migration plan
- **Optimization**: Refine and optimize cloud resources post-migration

## Common Challenges

Organizations often face challenges around data transfer, application compatibility, and team training. Addressing these early is critical for success.

## Conclusion

Cloud migration is a strategic initiative that requires executive support, technical expertise, and careful change management. Following these best practices increases the likelihood of a successful transition.
"""


def example1_all_formats():
    """Example 1: Generate document in all formats."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Generate All Document Formats")
    print("="*70)

    # Create draft content
    draft = DraftContent(
        content=SAMPLE_CONTENT,
        content_type=ContentType.WHITEPAPER,
        word_count=300,
        metadata={
            "target_audience": "IT Executives",
            "tone": "professional"
        }
    )

    # Initialize Production Agent
    agent = ProductionAgent(config={
        "output_dir": "output/phase3_examples",
        "brand_template": "tech"
    })

    print(f"\nUsing brand template: {agent.brand_template.name}")
    print(f"Primary color: {agent.brand_template.colors.primary}")
    print(f"Company: {agent.brand_template.company_name}")

    # Generate all formats
    formats = ["markdown", "html", "docx", "pdf", "pptx"]

    print(f"\nGenerating {len(formats)} formats...")
    outputs = agent.batch_produce([draft], formats)

    print(f"\n✓ Generated {len(outputs)} files:")
    for output in outputs:
        print(f"  {output.file_format:10} → {output.file_path}")
        print(f"               Brand: {output.metadata.get('brand_template', 'N/A')}")

    print(f"\nCheck output in: {agent.output_dir}/")


def example2_brand_comparison():
    """Example 2: Compare different brand templates."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Brand Template Comparison")
    print("="*70)

    draft = DraftContent(
        content=SAMPLE_CONTENT,
        content_type=ContentType.WHITEPAPER,
        word_count=300,
        metadata={}
    )

    # Test with 3 different templates
    templates = ["professional", "modern", "creative"]

    for template_name in templates:
        print(f"\n--- {template_name.upper()} Template ---")

        agent = ProductionAgent(config={
            "output_dir": f"output/phase3_examples/brand_{template_name}",
            "brand_template": template_name
        })

        template = agent.brand_template
        print(f"Primary color: {template.colors.primary}")
        print(f"Heading font: {template.typography.heading_font}")

        # Generate HTML for quick preview
        result = agent.process({
            "draft_content": draft,
            "output_format": "html"
        })

        print(f"✓ Generated: {result.file_path}")


def example3_content_repurposing():
    """Example 3: Content repurposing transformations."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Content Repurposing")
    print("="*70)

    draft = DraftContent(
        content=SAMPLE_CONTENT,
        content_type=ContentType.WHITEPAPER,
        word_count=300,
        metadata={}
    )

    repurpose_skill = ContentRepurposeSkill()

    # Transform to social post
    print("\n1. Whitepaper → LinkedIn Post")
    result = repurpose_skill.execute(draft, ContentType.SOCIAL_POST, platform="linkedin")

    if result["success"]:
        print(f"✓ Success!")
        print(f"\nPreview:")
        print("-" * 50)
        print(result["content"][:300] + "...")
        print("-" * 50)

    # Transform to presentation
    print("\n2. Whitepaper → Presentation Structure")
    result = repurpose_skill.execute(draft, ContentType.PRESENTATION)

    if result["success"]:
        print(f"✓ Success!")
        print(f"\nSlide structure (first 400 chars):")
        print("-" * 50)
        print(result["content"][:400] + "...")
        print("-" * 50)

    # Transform to email
    print("\n3. Whitepaper → Email Summary")
    result = repurpose_skill.execute(draft, ContentType.EMAIL)

    if result["success"]:
        print(f"✓ Success!")
        print(f"\nEmail preview:")
        print("-" * 50)
        print(result["content"][:400] + "...")
        print("-" * 50)


def example4_workflow_with_production():
    """Example 4: End-to-end workflow with production."""
    print("\n" + "="*70)
    print("EXAMPLE 4: End-to-End Workflow with Production")
    print("="*70)

    # Initialize workflow executor
    executor = WorkflowExecutor(config={
        "production": {
            "output_dir": "output/phase3_examples/workflow",
            "brand_template": "modern"
        }
    })

    # Create request
    request = WorkflowRequest(
        request_text="Write a whitepaper about cloud security best practices",
        content_types=[ContentType.WHITEPAPER],
        additional_context={
            "target_audience": "Security professionals",
            "output_format": "pdf"  # Request PDF output
        }
    )

    print(f"\nRequest: {request.request_text}")
    print(f"Target format: PDF")

    # Execute workflow
    print("\nExecuting workflow...")
    result = executor.execute(request)

    # Display results
    print(f"\n✓ Workflow completed: {result.success}")
    print(f"Steps completed: {len(result.steps_completed)}")

    if "production_outputs" in result.outputs:
        outputs = result.outputs["production_outputs"]
        print(f"\nProduction outputs: {len(outputs)}")
        for output in outputs:
            print(f"  - {output.file_format}: {output.file_path}")

    print(f"\nWorkflow execution time: {result.start_time} → {result.end_time}")


def example5_multi_format_workflow():
    """Example 5: Multi-format production in one workflow."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Multi-Format Production Workflow")
    print("="*70)

    executor = WorkflowExecutor(config={
        "production": {
            "output_dir": "output/phase3_examples/multi_format",
            "brand_template": "professional"
        }
    })

    request = WorkflowRequest(
        request_text="Create an article about DevOps automation",
        content_types=[ContentType.ARTICLE],
        additional_context={
            "output_formats": ["html", "docx", "pdf"],  # Multiple formats
            "target_audience": "DevOps engineers"
        }
    )

    print(f"\nRequest: {request.request_text}")
    print(f"Requested formats: HTML, DOCX, PDF")

    # Execute workflow
    result = executor.execute(request)

    if result.success:
        print(f"\n✓ Workflow successful!")

        if "production_outputs" in result.outputs:
            outputs = result.outputs["production_outputs"]
            print(f"\nGenerated {len(outputs)} files:")
            for output in outputs:
                size = output.metadata.get("file_size", "unknown")
                print(f"  {output.file_format:6} → {output.file_path}")
                print(f"          Size: {size} bytes" if size != "unknown" else "")


def example6_custom_template_settings():
    """Example 6: Demonstrate template layout settings."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Template Layout Settings")
    print("="*70)

    # Show template configurations
    templates = ["professional", "tech", "minimal"]

    for name in templates:
        template = get_brand_template(name)

        print(f"\n{name.upper()} Template:")
        print(f"  Document Layout:")
        print(f"    Page: {template.document_layout.page_size}")
        print(f"    Margins: {template.document_layout.margin_top}\" top")
        print(f"    Spacing: {template.document_layout.paragraph_spacing_after}pt after paragraphs")

        print(f"  Presentation Layout:")
        print(f"    Dimensions: {template.presentation_layout.slide_width}\" x {template.presentation_layout.slide_height}\"")
        print(f"    Title size: {template.presentation_layout.slide_title_size}pt")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("PHASE 3: PRODUCTION & DOCUMENT GENERATION EXAMPLES")
    print("="*70)

    examples = [
        ("All Formats", example1_all_formats),
        ("Brand Comparison", example2_brand_comparison),
        ("Content Repurposing", example3_content_repurposing),
        ("Workflow with Production", example4_workflow_with_production),
        ("Multi-Format Workflow", example5_multi_format_workflow),
        ("Template Settings", example6_custom_template_settings)
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...")
    print("(Note: Some formats require dependencies - see TESTING_PHASE3.md)")

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n⚠ Example '{name}' failed: {e}")
            print("(This may be due to missing dependencies)")

    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("\nCheck output files in: output/phase3_examples/")
    print("\nFor dependency installation:")
    print("  pip install -r requirements.txt")
    print("\nFor testing setup:")
    print("  See TESTING_PHASE3.md")


if __name__ == "__main__":
    main()
