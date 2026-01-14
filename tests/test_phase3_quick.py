#!/usr/bin/env python3
"""
Quick Phase 3 Test - Runs all basic tests.

Usage:
    python3 tests/test_phase3_quick.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.production.production import ProductionAgent
from templates.brand.brand_config import get_brand_template
from tests.test_data import create_test_draft


def test_dependencies():
    """Test 1: Check dependencies."""
    print("\n" + "="*60)
    print("TEST 1: Dependencies")
    print("="*60)

    deps = {
        "python-docx": "docx",
        "python-pptx": "pptx",
        "reportlab": "reportlab",
        "Pillow": "PIL"
    }

    results = {}
    for name, module in deps.items():
        try:
            __import__(module)
            print(f"✓ {name:20} INSTALLED")
            results[name] = True
        except ImportError:
            print(f"✗ {name:20} NOT INSTALLED (will use fallback)")
            results[name] = False

    return results


def test_brand_templates():
    """Test 2: Brand template enhancements."""
    print("\n" + "="*60)
    print("TEST 2: Brand Templates")
    print("="*60)

    templates = ["professional", "modern", "tech", "creative", "minimal"]

    for name in templates:
        template = get_brand_template(name)

        # Verify new fields
        assert hasattr(template, 'document_layout'), f"{name} missing document_layout"
        assert hasattr(template, 'presentation_layout'), f"{name} missing presentation_layout"

        print(f"✓ {name:12} has document & presentation layouts")

    print("\n✓ All templates validated!")


def test_production_agent():
    """Test 3: Production Agent."""
    print("\n" + "="*60)
    print("TEST 3: Production Agent")
    print("="*60)

    agent = ProductionAgent(config={
        "output_dir": "output/quick_test",
        "brand_template": "professional"
    })

    print(f"✓ Agent initialized")
    print(f"  Brand: {agent.brand_template.name}")
    print(f"  Output: {agent.output_dir}")

    draft = create_test_draft()

    # Test Markdown (always works)
    print("\nTesting Markdown...")
    result = agent.process({
        "draft_content": draft,
        "output_format": "markdown"
    })
    print(f"✓ Generated: {result.file_path}")

    # Test HTML (always works)
    print("\nTesting HTML...")
    result = agent.process({
        "draft_content": draft,
        "output_format": "html"
    })
    print(f"✓ Generated: {result.file_path}")

    return agent


def test_all_formats(agent, deps):
    """Test 4: All document formats."""
    print("\n" + "="*60)
    print("TEST 4: All Document Formats")
    print("="*60)

    draft = create_test_draft()
    formats = ["docx", "pdf", "pptx"]

    for fmt in formats:
        print(f"\nTesting {fmt.upper()}...")
        result = agent.process({
            "draft_content": draft,
            "output_format": fmt
        })
        print(f"✓ Generated: {result.file_path}")
        print(f"  Format: {result.file_format}")
        if result.file_format != fmt:
            print(f"  (Used {result.file_format} fallback)")


def main():
    """Run all quick tests."""
    print("\n" + "="*60)
    print("PHASE 3 QUICK TEST SUITE")
    print("="*60)

    try:
        # Run tests
        deps = test_dependencies()
        test_brand_templates()
        agent = test_production_agent()
        test_all_formats(agent, deps)

        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print("✓ All tests passed!")
        print(f"\nGenerated files in: {agent.output_dir}/")
        print("\nTo verify:")
        print("1. Check the output directory for generated files")
        print("2. Open DOCX, PDF, PPTX files in respective applications")
        print("3. Verify brand colors and formatting")

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
