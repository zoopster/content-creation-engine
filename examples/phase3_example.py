"""
Phase 3 Example - Production Agent and Document Generation

This example demonstrates Phase 3 capabilities:
1. Production Agent with document generation
2. Multiple output formats (HTML, Markdown, DOCX, PDF, PPTX)
3. Brand template application
4. Content repurposing between formats
5. Batch production workflows
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.production.production import ProductionAgent
from agents.creation.creation import CreationAgent
from agents.base.models import ContentBrief, ContentType, ToneType, DraftContent
from templates.brand.brand_config import get_brand_template
from skills.content_repurpose.content_repurpose import ContentRepurposeSkill


def example_1_production_basics():
    """Example 1: Basic document production in multiple formats."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Document Production")
    print("="*60 + "\n")

    # Create a sample draft content
    draft = DraftContent(
        content="""# AI in Healthcare: Transforming Patient Care

## Introduction

Artificial Intelligence is revolutionizing healthcare delivery by enabling faster diagnoses, personalized treatments, and improved patient outcomes.

## Key Benefits

AI-powered systems can analyze medical images with accuracy comparable to human experts. Machine learning models predict patient risks and suggest preventive measures. Natural language processing helps doctors extract insights from medical records.

## Implementation Challenges

Healthcare organizations face challenges integrating AI into existing workflows. Data privacy and security remain critical concerns. Regulatory compliance adds complexity to AI deployment.

## Future Outlook

The future of AI in healthcare looks promising, with innovations in drug discovery, robotic surgery, and remote patient monitoring on the horizon.

## Conclusion

As AI technology matures, healthcare providers must balance innovation with patient safety and ethical considerations.""",
        content_type=ContentType.ARTICLE,
        word_count=145,
        metadata={
            "target_audience": "Healthcare professionals",
            "tone": "professional"
        },
        format="markdown"
    )

    # Initialize Production Agent
    producer = ProductionAgent(config={
        "output_dir": "output",
        "brand_template": "professional"
    })

    print("Generating documents in multiple formats...\n")

    # Generate HTML
    print("1. Generating HTML...")
    html_output = producer.process({
        "draft_content": draft,
        "output_format": "html"
    })
    print(f"   ✓ HTML created: {html_output.file_path}")

    # Generate Markdown
    print("2. Generating Markdown...")
    md_output = producer.process({
        "draft_content": draft,
        "output_format": "markdown"
    })
    print(f"   ✓ Markdown created: {md_output.file_path}")

    # Generate DOCX (if available)
    print("3. Generating DOCX...")
    docx_output = producer.process({
        "draft_content": draft,
        "output_format": "docx"
    })
    print(f"   ✓ DOCX created: {docx_output.file_path}")

    # Generate PDF (if available)
    print("4. Generating PDF...")
    pdf_output = producer.process({
        "draft_content": draft,
        "output_format": "pdf"
    })
    print(f"   ✓ PDF created: {pdf_output.file_path}")

    # Generate PPTX (if available)
    print("5. Generating PPTX...")
    pptx_output = producer.process({
        "draft_content": draft,
        "output_format": "pptx"
    })
    print(f"   ✓ PPTX created: {pptx_output.file_path}")

    print(f"\n✅ Example 1 Complete: Generated {5} different formats")


def example_2_brand_templates():
    """Example 2: Using different brand templates."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Brand Template Variations")
    print("="*60 + "\n")

    # Create sample content
    draft = DraftContent(
        content="""# Modern Tech Solutions

## Innovation at Scale

We deliver cutting-edge technology solutions that transform businesses.

## Our Approach

Our team combines technical expertise with business acumen to create impactful solutions.""",
        content_type=ContentType.BLOG_POST,
        word_count=30,
        format="markdown"
    )

    # Try different brand templates
    templates = ["professional", "modern", "tech", "creative"]

    for template_name in templates:
        print(f"\nGenerating with '{template_name}' template...")

        producer = ProductionAgent(config={
            "output_dir": "output",
            "brand_template": template_name
        })

        output = producer.process({
            "draft_content": draft,
            "output_format": "html"
        })

        print(f"   ✓ Created: {output.file_path}")
        print(f"   Template: {template_name}")

    print(f"\n✅ Example 2 Complete: Generated HTML with {len(templates)} brand templates")


def example_3_content_repurposing():
    """Example 3: Repurposing content between formats."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Content Repurposing")
    print("="*60 + "\n")

    # Create article content
    article = DraftContent(
        content="""# The Future of Remote Work

## Shifting Workplace Dynamics

Remote work has become the new normal for millions of professionals worldwide. Organizations are adapting their policies and infrastructure to support distributed teams effectively.

## Technology Enablers

Cloud platforms, collaboration tools, and video conferencing have made remote work seamless. These technologies bridge the gap between physical and virtual workspaces.

## Benefits and Challenges

While remote work offers flexibility and cost savings, it also presents challenges in team cohesion and work-life balance. Organizations must address these proactively.

## Looking Ahead

The future workplace will likely be hybrid, combining the best of remote and in-office work. Companies that embrace this model will attract and retain top talent.""",
        content_type=ContentType.ARTICLE,
        word_count=120,
        metadata={
            "target_audience": "Business professionals",
            "tone": "professional"
        }
    )

    # Initialize repurpose skill
    repurpose = ContentRepurposeSkill()

    print("Original: Article about remote work\n")

    # Repurpose to social post
    print("1. Repurposing to Social Post...")
    social_result = repurpose.execute(
        source_content=article,
        target_format=ContentType.SOCIAL_POST,
        platform="linkedin"
    )
    print(f"   ✓ Social post created")
    print(f"   Preview: {social_result['content'][:100]}...")

    # Repurpose to email
    print("\n2. Repurposing to Email...")
    email_result = repurpose.execute(
        source_content=article,
        target_format=ContentType.EMAIL
    )
    print(f"   ✓ Email created")
    print(f"   Preview: {email_result['content'][:100]}...")

    # Repurpose to presentation
    print("\n3. Repurposing to Presentation...")
    pres_result = repurpose.execute(
        source_content=article,
        target_format=ContentType.PRESENTATION
    )
    print(f"   ✓ Presentation structure created")
    print(f"   Preview: {pres_result['content'][:100]}...")

    print(f"\n✅ Example 3 Complete: Repurposed article to 3 formats")


def example_4_batch_production():
    """Example 4: Batch production of multiple documents."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Production")
    print("="*60 + "\n")

    # Create multiple drafts
    drafts = [
        DraftContent(
            content=f"# Document {i+1}\n\nThis is sample content for document {i+1}.\n\n## Section 1\n\nContent here.",
            content_type=ContentType.BLOG_POST,
            word_count=15
        )
        for i in range(3)
    ]

    producer = ProductionAgent(config={
        "output_dir": "output",
        "brand_template": "professional"
    })

    print(f"Batch producing {len(drafts)} documents in HTML and Markdown...\n")

    outputs = producer.batch_produce(
        drafts=drafts,
        output_formats=["html", "markdown"]
    )

    print(f"\n✅ Example 4 Complete: Generated {len(outputs)} files")
    for output in outputs:
        print(f"   - {output.file_path}")


def example_5_end_to_end_workflow():
    """Example 5: Complete workflow from creation to production."""
    print("\n" + "="*60)
    print("EXAMPLE 5: End-to-End Workflow (Creation → Production)")
    print("="*60 + "\n")

    # Step 1: Create content brief
    print("Step 1: Creating content brief...")
    brief = ContentBrief(
        content_type=ContentType.ARTICLE,
        target_audience="Software developers",
        key_messages=[
            "Python remains the most popular programming language",
            "Python excels in data science and machine learning",
            "Python's ecosystem continues to grow"
        ],
        tone=ToneType.TECHNICAL,
        structure_requirements=[
            "Introduction",
            "Current trends",
            "Use cases",
            "Conclusion"
        ],
        word_count_range=(400, 600),
        seo_keywords=["python", "programming", "data science"],
        brand_guidelines={}
    )
    print("   ✓ Brief created")

    # Step 2: Generate content with Creation Agent
    print("\nStep 2: Generating content...")
    creator = CreationAgent()
    draft = creator.process({
        "content_brief": brief,
        "additional_context": {}
    })
    print(f"   ✓ Content generated ({draft.word_count} words)")

    # Step 3: Produce documents with Production Agent
    print("\nStep 3: Producing final documents...")
    producer = ProductionAgent(config={
        "output_dir": "output",
        "brand_template": "tech"
    })

    # Generate multiple formats
    formats = ["html", "markdown", "docx"]
    outputs = []

    for fmt in formats:
        output = producer.process({
            "draft_content": draft,
            "output_format": fmt
        })
        outputs.append(output)
        print(f"   ✓ {fmt.upper()} created: {output.file_path}")

    print(f"\n✅ Example 5 Complete: End-to-end workflow produced {len(outputs)} files")


def main():
    """Run all Phase 3 examples."""
    print("\n" + "="*60)
    print("PHASE 3 EXAMPLES - Production Agent & Document Generation")
    print("="*60)
    print("\nDemonstrating Phase 3 capabilities:")
    print("- Production Agent with multi-format support")
    print("- Brand template system")
    print("- Content repurposing")
    print("- Batch production")
    print("- End-to-end workflows")

    try:
        # Run examples
        example_1_production_basics()
        example_2_brand_templates()
        example_3_content_repurposing()
        example_4_batch_production()
        example_5_end_to_end_workflow()

        # Summary
        print("\n" + "="*60)
        print("PHASE 3 EXAMPLES COMPLETE")
        print("="*60)
        print("\n✅ All examples completed successfully!")
        print("\nGenerated files can be found in the 'output' directory.")
        print("\nNext Steps:")
        print("- Review generated documents")
        print("- Experiment with different brand templates")
        print("- Try repurposing your own content")
        print("- Integrate with Orchestrator for full automation")

    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("\nNote: Some examples may require optional dependencies:")
        print("- DOCX generation: pip install python-docx")
        print("- PDF generation: pip install reportlab Pillow")
        print("- PPTX generation: pip install python-pptx")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
