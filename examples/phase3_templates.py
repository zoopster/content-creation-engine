"""
Phase 3 Example: Brand Template System and Production

This example demonstrates:
1. Using predefined brand templates
2. Creating custom templates
3. Generating branded output in multiple formats
4. Comparing different template styles
5. Complete workflow with production
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.workflow_executor import WorkflowExecutor
from agents.production.production_v2 import ProductionAgentV2
from agents.base.models import WorkflowRequest, ContentType, DraftContent
from templates.brand.brand_config import (
    get_brand_template, create_custom_template, BRAND_TEMPLATES
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_template_showcase():
    """Example 1: Showcase all predefined templates."""
    print("=" * 80)
    print("EXAMPLE 1: Brand Template Showcase")
    print("=" * 80)

    print("\n📊 Available Brand Templates:\n")

    for template_name, template in BRAND_TEMPLATES.items():
        print(f"### {template.name} Template")
        print(f"   Company: {template.company_name}")
        print(f"   Colors:")
        print(f"     - Primary: {template.colors.primary}")
        print(f"     - Secondary: {template.colors.secondary}")
        print(f"     - Accent: {template.colors.accent}")
        print(f"   Typography:")
        print(f"     - Headings: {template.typography.heading_font}")
        print(f"     - Body: {template.typography.body_font}")
        print(f"   Style: {template.color_scheme.value.title()}")
        print()


def example_generate_with_template():
    """Example 2: Generate content with a specific template."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Generate Content with Professional Template")
    print("=" * 80)

    # Create a simple draft
    draft = DraftContent(
        content="""# Sustainable Agriculture Practices

Sustainable agriculture represents an important development in the field. Research shows significant benefits and measurable impact across multiple dimensions.

## Key Benefits

Organizations implementing sustainable agriculture report improved outcomes by 35% on average. Key factors include proper implementation, stakeholder engagement, and ongoing monitoring.

## Implementation Strategies

Studies indicate that sustainable agriculture adoption continues to grow, with market size expected to reach $150B by 2027. This demonstrates strong industry commitment to environmental stewardship.

## Conclusion

Understanding sustainable agriculture provides valuable insights for agricultural professionals. As the landscape continues to evolve, staying informed about developments becomes increasingly important.""",
        content_type=ContentType.ARTICLE,
        word_count=98
    )

    # Create production agent with professional template
    agent = ProductionAgentV2(config={
        "brand_template": "professional",
        "output_dir": "output"
    })

    print(f"\n📝 Generating output with Professional template...")
    print(f"   Company: Professional Corp")
    print(f"   Primary Color: #2C3E50")

    # Generate HTML output
    output = agent.process({
        "draft_content": draft,
        "output_format": "html"
    })

    print(f"\n✅ Generated: {output.file_path}")
    print(f"   Format: {output.file_format}")
    print(f"   Template: {output.metadata.get('brand_template')}")
    print(f"   File Size: {output.metadata.get('file_size')} bytes")

    return output


def example_template_comparison():
    """Example 3: Generate same content with different templates."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Template Comparison")
    print("=" * 80)

    # Create sample content
    draft = DraftContent(
        content="""# Innovation in Technology

Technology innovation drives progress across industries. Modern solutions enable organizations to achieve unprecedented efficiency and effectiveness.

## Impact Areas

Key impact areas include automation, data analytics, and user experience improvements. These capabilities transform how organizations operate and serve customers.

## Future Outlook

The technology landscape continues to evolve rapidly. Organizations that embrace innovation position themselves for long-term success.""",
        content_type=ContentType.ARTICLE,
        word_count=65
    )

    # Test with multiple templates
    templates_to_test = ["professional", "modern", "tech"]

    outputs = []
    for template_name in templates_to_test:
        print(f"\n🎨 Generating with {template_name.title()} template...")

        agent = ProductionAgentV2(config={
            "brand_template": template_name,
            "output_dir": "output"
        })

        output = agent.process({
            "draft_content": draft,
            "output_format": "html"
        })

        template = get_brand_template(template_name)
        print(f"   Company: {template.company_name}")
        print(f"   Primary: {template.colors.primary}")
        print(f"   Output: {output.file_path}")

        outputs.append(output)

    print(f"\n✅ Generated {len(outputs)} versions with different brand templates")
    print(f"\n💡 Tip: Open the HTML files in a browser to see the visual differences!")

    return outputs


def example_custom_template():
    """Example 4: Create and use a custom template."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Custom Brand Template")
    print("=" * 80)

    # Create custom template
    print("\n🎨 Creating custom template: 'My Startup'")

    custom = create_custom_template(
        name="My Startup",
        primary_color="#7C3AED",  # Purple
        secondary_color="#A78BFA",  # Light purple
        accent_color="#F59E0B",  # Amber
        heading_font="Arial",
        body_font="Arial",
        company_name="My Startup Inc."
    )

    print(f"   Company: {custom.company_name}")
    print(f"   Primary Color: {custom.colors.primary}")
    print(f"   Accent Color: {custom.colors.accent}")

    # Create production agent
    agent = ProductionAgentV2(config={
        "output_dir": "output"
    })
    agent.brand_template = custom

    # Generate content
    draft = DraftContent(
        content="""# Welcome to My Startup

We're building the future of technology. Our innovative approach combines cutting-edge solutions with user-centric design.

## Our Mission

Empowering businesses through innovative technology solutions that drive real results.

## Get Started

Ready to transform your business? Contact us today to learn more.""",
        content_type=ContentType.ARTICLE,
        word_count=45
    )

    output = agent.process({
        "draft_content": draft,
        "output_format": "html"
    })

    print(f"\n✅ Generated custom branded output: {output.file_path}")

    return output


def example_multi_format_output():
    """Example 5: Generate multiple formats from same content."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Multi-Format Output")
    print("=" * 80)

    draft = DraftContent(
        content="""# Quarterly Business Review

## Executive Summary

This quarter demonstrated strong performance across all key metrics. Revenue increased by 25% year-over-year, with customer satisfaction scores reaching an all-time high.

## Key Highlights

- Revenue growth: 25%
- New customers: 150
- Customer satisfaction: 95%
- Product releases: 3 major updates

## Strategic Initiatives

Our focus on product innovation and customer success continues to drive results. The team's dedication has been instrumental in achieving these milestones.

## Next Quarter Goals

We're positioned for continued growth with several strategic initiatives planned for the coming months.""",
        content_type=ContentType.ARTICLE,
        word_count=95
    )

    # Create agent with tech template
    agent = ProductionAgentV2(config={
        "brand_template": "tech",
        "output_dir": "output"
    })

    # Generate in multiple formats
    formats = ["markdown", "html"]
    outputs = []

    for format_type in formats:
        print(f"\n📄 Generating {format_type.upper()} output...")

        output = agent.process({
            "draft_content": draft,
            "output_format": format_type
        })

        print(f"   ✅ Created: {output.file_path}")
        print(f"   Size: {output.metadata.get('file_size')} bytes")

        outputs.append(output)

    print(f"\n✅ Generated {len(outputs)} different format versions")

    return outputs


def example_end_to_end_workflow():
    """Example 6: Complete workflow with template system."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: End-to-End Workflow with Templates")
    print("=" * 80)

    # Create workflow executor with specific template
    executor = WorkflowExecutor(config={
        "production": {
            "brand_template": "modern",
            "output_dir": "output"
        },
        "enforce_quality_gates": True
    })

    # Create request
    request = WorkflowRequest(
        request_text="Create content about digital transformation",
        content_types=[ContentType.ARTICLE],
        additional_context={
            "target_audience": "Business executives",
            "output_format": "html"  # Specify format
        }
    )

    print(f"\n📝 Request: {request.request_text}")
    print(f"🎨 Template: Modern (sleek design, coral accents)")
    print(f"\n🚀 Executing complete workflow...\n")

    # Execute workflow
    result = executor.execute(request)

    # Display results
    print(f"\n{'='*80}")
    print(f"WORKFLOW RESULTS")
    print(f"{'='*80}")
    print(f"✅ Success: {result.success}")
    print(f"📊 Steps: {len(result.steps_completed)}")

    if "draft_content" in result.outputs:
        draft = result.outputs["draft_content"]
        print(f"\n📄 Content Generated:")
        print(f"   Words: {draft.word_count}")
        print(f"   Type: {draft.content_type.value}")

    # Note: In Phase 3, we'd generate production output here
    print(f"\n💡 Production output would be generated with Modern template")
    print(f"   Primary Color: #1A1A1A (Almost black)")
    print(f"   Accent Color: #FF6B6B (Coral red)")

    return result


def print_summary():
    """Print Phase 3 summary."""
    print("\n\n" + "=" * 80)
    print("PHASE 3: TEMPLATE SYSTEM COMPLETE")
    print("=" * 80)
    print("\n✅ Template System Features:")
    print("   ✓ 5 predefined brand templates")
    print("   ✓ Custom template creation")
    print("   ✓ Full color and typography control")
    print("   ✓ Branded HTML generation")
    print("   ✓ Branded Markdown generation")
    print("   ✓ Template comparison capabilities")
    print("\n📊 Available Templates:")
    print("   • Professional - Corporate communications")
    print("   • Modern - Tech startups, contemporary")
    print("   • Tech - Technology companies")
    print("   • Creative - Design agencies")
    print("   • Minimal - Minimalist brands")
    print("\n📄 Output Formats:")
    print("   • Markdown (with brand headers/footers)")
    print("   • HTML (fully styled with brand CSS)")
    print("   • DOCX (requires python-docx library)")
    print("   • PDF (requires reportlab library)")
    print("   • PPTX (requires python-pptx library)")
    print("\n📚 Documentation:")
    print("   • templates/TEMPLATES.md - Complete guide")
    print("   • templates/brand/brand_config.py - Template definitions")
    print("   • agents/production/production_v2.py - Production agent")
    print("\n🎨 Next Steps:")
    print("   1. Open generated HTML files to see branded output")
    print("   2. Customize templates for your brand")
    print("   3. Integrate with Phase 2 workflows")
    print("   4. Install optional libraries for DOCX/PDF/PPTX")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n🎨 Content Creation Engine - Phase 3 Template Examples\n")

    try:
        # Run all examples
        example_template_showcase()
        output1 = example_generate_with_template()
        outputs2 = example_template_comparison()
        output3 = example_custom_template()
        outputs4 = example_multi_format_output()
        result5 = example_end_to_end_workflow()

        # Print summary
        print_summary()

        # Show output directory
        print(f"\n📁 Generated files saved to: ./output/")
        print(f"   Open .html files in a web browser to see branded output!\n")

    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
