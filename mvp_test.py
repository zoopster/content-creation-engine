#!/usr/bin/env python3
"""
MVP Test Script
Quick validation that the Content Creation Engine MVP is working correctly.
"""

import sys
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def test_imports():
    """Test that all required modules can be imported"""
    print_header("Testing Module Imports")

    try:
        from agents.workflow_executor import WorkflowExecutor
        from agents.base.models import WorkflowRequest, ContentType
        from agents.orchestrator.orchestrator import OrchestratorAgent
        from skills.content_brief.content_brief import ContentBriefSkill
        from skills.brand_voice.brand_voice import BrandVoiceSkill
        print("✓ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("\nPlease ensure you've run: pip install -r requirements.txt")
        return False

def test_workflow_execution():
    """Test basic workflow execution"""
    print_header("Testing Workflow Execution")

    try:
        from agents.workflow_executor import WorkflowExecutor
        from agents.base.models import WorkflowRequest, ContentType

        executor = WorkflowExecutor()
        request = WorkflowRequest(
            request_text="Write a brief article about renewable energy",
            content_types=[ContentType.ARTICLE],
            additional_context={
                "target_audience": "General public",
                "word_count": 500
            }
        )

        print("Executing workflow...")
        result = executor.execute(request)

        if result.success:
            draft = result.outputs.get("draft_content")
            print(f"✓ Workflow executed successfully")
            print(f"  - Generated {draft.word_count} words")
            print(f"  - Content type: {draft.content_type}")
            print(f"\nFirst 150 characters of content:")
            print(f"  {draft.content[:150]}...")
            return True
        else:
            print(f"✗ Workflow failed: {result.error}")
            return False

    except Exception as e:
        print(f"✗ Workflow execution error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_generation():
    """Test DOCX document generation"""
    print_header("Testing Document Generation")

    try:
        from agents.production.production import ProductionAgent
        from agents.base.models import AgentInput, ContentType
        import os

        production = ProductionAgent()

        # Sample markdown content
        content = """# Test Article

This is a test article to verify DOCX generation is working.

## Introduction

The Content Creation Engine MVP is successfully deployed.

## Key Features

- Multi-agent orchestration
- Quality gate validation
- Document generation

## Conclusion

Everything is working as expected.
"""

        agent_input = AgentInput(
            content={
                "markdown_content": content,
                "format": "docx",
                "title": "MVP Test Article"
            },
            content_type=ContentType.ARTICLE
        )

        print("Generating DOCX document...")
        result = production.process(agent_input)

        if result.success:
            file_path = result.outputs.get("file_path")
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"✓ Document generated successfully")
                print(f"  - File: {file_path}")
                print(f"  - Size: {file_size} bytes")
                return True
            else:
                print(f"✗ Document file not found: {file_path}")
                return False
        else:
            print(f"✗ Document generation failed: {result.error}")
            return False

    except Exception as e:
        print(f"✗ Document generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quality_gates():
    """Test quality gate validation"""
    print_header("Testing Quality Gates")

    try:
        from skills.brand_voice.brand_voice import BrandVoiceSkill

        brand_skill = BrandVoiceSkill()

        # Test content
        test_content = """
        This is a professional article about technology innovation.
        The content demonstrates clear communication and proper structure.
        It avoids excessive jargon while maintaining authority.
        """

        print("Validating content against brand guidelines...")
        result = brand_skill.execute({
            "content": test_content,
            "content_type": "article"
        })

        if result.success:
            validation = result.outputs.get("validation")
            print(f"✓ Brand validation completed")
            print(f"  - Compliance score: {validation.compliance_score:.2f}")
            print(f"  - Issues found: {len(validation.issues)}")
            if validation.suggestions:
                print(f"  - Suggestions: {len(validation.suggestions)}")
            return True
        else:
            print(f"✗ Validation failed: {result.error}")
            return False

    except Exception as e:
        print(f"✗ Quality gate error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all MVP tests"""
    print("\n" + "=" * 60)
    print("  CONTENT CREATION ENGINE - MVP TEST SUITE")
    print("  Version: 1.0.0 (Phase 3)")
    print("  Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    tests = [
        ("Module Imports", test_imports),
        ("Workflow Execution", test_workflow_execution),
        ("Document Generation", test_document_generation),
        ("Quality Gates", test_quality_gates)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 MVP is fully functional and ready to use!")
        print("\nNext steps:")
        print("  1. Review examples in examples/ directory")
        print("  2. Read MVP_DEPLOYMENT.md for usage instructions")
        print("  3. Customize brand settings in templates/brand/brand_config.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("  1. Ensure dependencies are installed: pip install -r requirements.txt")
        print("  2. Check Python version: python3 --version (need 3.8+)")
        print("  3. Review MVP_DEPLOYMENT.md for detailed setup instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())
