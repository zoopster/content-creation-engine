# Phase 3 Testing Guide

Complete guide for setting up and testing the Phase 3 document generation features.

## Prerequisites

- **Python 3.8+** installed
- **pip** package manager
- **macOS, Linux, or Windows** (commands may vary slightly)

---

## 1. Environment Setup

### Option A: Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd /Users/johnpugh/Documents/source/content-creation-engine

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify activation (should show venv path)
which python
```

### Option B: System-Wide Installation

```bash
# Install directly to system Python (not recommended)
cd /Users/johnpugh/Documents/source/content-creation-engine
pip3 install -r requirements.txt
```

---

## 2. Install Dependencies

### Full Installation (All Features)

```bash
# Install all Phase 3 dependencies
pip install -r requirements.txt

# Verify installations
python -c "import docx; print('✓ python-docx installed')"
python -c "import pptx; print('✓ python-pptx installed')"
python -c "import reportlab; print('✓ reportlab installed')"
python -c "from PIL import Image; print('✓ Pillow installed')"
```

### Minimal Installation (Test Fallbacks)

```bash
# Install only PyYAML to test graceful fallbacks
pip install pyyaml>=6.0.1

# This lets you test:
# - Markdown generation (no dependencies)
# - HTML generation (no dependencies)
# - Fallback behavior for DOCX/PDF/PPTX
```

### Selective Installation (Test Individual Formats)

```bash
# Test only DOCX
pip install python-docx>=1.1.0

# Test only PDF
pip install reportlab>=4.0.0 Pillow>=10.0.0

# Test only PPTX
pip install python-pptx>=0.6.23
```

---

## 3. Verify Installation

Create a simple verification script:

```bash
# Create test script
cat > test_dependencies.py << 'EOF'
#!/usr/bin/env python3
"""Verify Phase 3 dependencies."""

def check_dependency(name, import_name=None):
    import_name = import_name or name
    try:
        __import__(import_name)
        print(f"✓ {name:20} INSTALLED")
        return True
    except ImportError:
        print(f"✗ {name:20} NOT INSTALLED")
        return False

print("\n=== Phase 3 Dependencies ===\n")
results = {
    "python-docx": check_dependency("python-docx", "docx"),
    "python-pptx": check_dependency("python-pptx", "pptx"),
    "reportlab": check_dependency("reportlab"),
    "Pillow": check_dependency("Pillow", "PIL"),
    "pyyaml": check_dependency("pyyaml", "yaml")
}

print("\n=== Summary ===")
installed = sum(results.values())
total = len(results)
print(f"{installed}/{total} dependencies installed")

if installed == total:
    print("\n✓ All Phase 3 dependencies ready!")
else:
    print("\n⚠ Some dependencies missing - features will use fallbacks")
EOF

# Run verification
python3 test_dependencies.py
```

---

## 4. Create Test Data

Create sample content for testing:

```python
# Create test_data.py
cat > test_data.py << 'EOF'
"""Sample test data for Phase 3 testing."""

from agents.base.models import DraftContent, ContentType

# Sample article content
SAMPLE_ARTICLE = """# The Future of AI in Healthcare

## Introduction

Artificial intelligence is transforming the healthcare industry in unprecedented ways. From diagnostic tools to personalized treatment plans, AI technologies are enhancing patient care and operational efficiency.

## Key Benefits

### Improved Diagnostics

AI algorithms can analyze medical images with remarkable accuracy, often detecting conditions that human eyes might miss. This leads to earlier interventions and better patient outcomes.

### Personalized Treatment

Machine learning models can process vast amounts of patient data to recommend customized treatment plans based on individual genetic profiles and medical histories.

### Operational Efficiency

Healthcare facilities are using AI to optimize scheduling, reduce wait times, and streamline administrative tasks, allowing medical staff to focus on patient care.

## Challenges

- Data privacy and security concerns
- Need for regulatory frameworks
- Integration with existing systems
- Training healthcare professionals

## Conclusion

While challenges remain, the potential of AI in healthcare is immense. Continued collaboration between technologists and medical professionals will be key to realizing this potential.
"""

def create_test_draft():
    """Create a test DraftContent object."""
    return DraftContent(
        content=SAMPLE_ARTICLE,
        content_type=ContentType.ARTICLE,
        word_count=250,
        metadata={
            "target_audience": "Healthcare professionals",
            "tone": "professional"
        },
        format="markdown"
    )

if __name__ == "__main__":
    draft = create_test_draft()
    print(f"Created test draft: {draft.content_type.value}")
    print(f"Word count: {draft.word_count}")
    print(f"Preview: {draft.content[:100]}...")
EOF
```

---

## 5. Component Testing

### Test 1: Brand Templates

```python
# test_brand_templates.py
cat > test_brand_templates.py << 'EOF'
"""Test brand template enhancements."""

from templates.brand.brand_config import get_brand_template

print("\n=== Testing Brand Templates ===\n")

# Test all predefined templates
templates = ["professional", "modern", "tech", "creative", "minimal"]

for name in templates:
    template = get_brand_template(name)

    # Verify new layout fields exist
    assert hasattr(template, 'document_layout'), f"{name} missing document_layout"
    assert hasattr(template, 'presentation_layout'), f"{name} missing presentation_layout"

    # Check document layout
    doc_layout = template.document_layout
    print(f"✓ {name.title():12} - Doc: {doc_layout.page_size}, "
          f"Margins: {doc_layout.margin_top}in, "
          f"Pres: {doc_layout.page_width}x{doc_layout.page_height}")

print("\n✓ All brand templates have layout configurations!")
EOF

python3 test_brand_templates.py
```

### Test 2: Production Agent (Markdown & HTML)

```python
# test_production_native.py
cat > test_production_native.py << 'EOF'
"""Test Production Agent native formats (no external dependencies)."""

from agents.production.production import ProductionAgent
from test_data import create_test_draft

print("\n=== Testing Production Agent (Native Formats) ===\n")

# Initialize agent
agent = ProductionAgent(config={
    "output_dir": "output/test",
    "brand_template": "professional"
})

print(f"Brand template: {agent.brand_template.name}")
print(f"Output directory: {agent.output_dir}")
print()

# Test Markdown generation
print("1. Testing Markdown generation...")
draft = create_test_draft()
result = agent.process({
    "draft_content": draft,
    "output_format": "markdown"
})
print(f"   ✓ Generated: {result.file_path}")
print(f"   ✓ Format: {result.file_format}")
print(f"   ✓ File size: {result.metadata.get('file_size')} bytes")
print()

# Test HTML generation
print("2. Testing HTML generation...")
result = agent.process({
    "draft_content": draft,
    "output_format": "html"
})
print(f"   ✓ Generated: {result.file_path}")
print(f"   ✓ Format: {result.file_format}")
print(f"   ✓ Brand colors applied: {result.metadata.get('colors')}")
print()

print("✓ Native format generation successful!")
print(f"\nCheck output files in: {agent.output_dir}")
EOF

python3 test_production_native.py
```

### Test 3: DOCX Generation

```python
# test_docx_generation.py
cat > test_docx_generation.py << 'EOF'
"""Test DOCX generation with brand templates."""

from agents.production.production import ProductionAgent
from templates.brand.brand_config import get_brand_template
from test_data import create_test_draft

print("\n=== Testing DOCX Generation ===\n")

agent = ProductionAgent(config={"output_dir": "output/test"})

if not agent.has_docx:
    print("⚠ python-docx not installed - will test fallback to HTML")
else:
    print("✓ python-docx installed - testing full DOCX generation")

print()

# Test with different brand templates
templates = ["professional", "modern", "tech"]

for template_name in templates:
    print(f"Testing with {template_name} template...")

    draft = create_test_draft()
    result = agent.process({
        "draft_content": draft,
        "output_format": "docx",
        "template_override": template_name
    })

    print(f"   ✓ Generated: {result.file_path}")
    print(f"   ✓ Format: {result.file_format}")
    print()

print("✓ DOCX generation test complete!")
print("\nTo verify:")
print("1. Open the generated .docx files in Microsoft Word or LibreOffice")
print("2. Check that brand colors appear in headings")
print("3. Verify page margins and fonts match brand template")
EOF

python3 test_docx_generation.py
```

### Test 4: PDF Generation

```python
# test_pdf_generation.py
cat > test_pdf_generation.py << 'EOF'
"""Test PDF generation with brand templates."""

from agents.production.production import ProductionAgent
from test_data import create_test_draft

print("\n=== Testing PDF Generation ===\n")

agent = ProductionAgent(config={"output_dir": "output/test"})

if not agent.has_reportlab:
    print("⚠ reportlab not installed - will test fallback to HTML")
else:
    print("✓ reportlab installed - testing full PDF generation")

print()

draft = create_test_draft()

# Test PDF with Professional template
result = agent.process({
    "draft_content": draft,
    "output_format": "pdf",
    "template_override": "professional"
})

print(f"✓ Generated: {result.file_path}")
print(f"✓ Format: {result.file_format}")
print(f"✓ Page size: {result.metadata.get('page_size', 'letter')}")
print()

print("✓ PDF generation test complete!")
print("\nTo verify:")
print("1. Open the PDF in Adobe Reader or Preview")
print("2. Check brand colors in headings")
print("3. Verify professional layout and typography")
EOF

python3 test_pdf_generation.py
```

### Test 5: PPTX Generation

```python
# test_pptx_generation.py
cat > test_pptx_generation.py << 'EOF'
"""Test PPTX generation with brand templates."""

from agents.production.production import ProductionAgent
from test_data import create_test_draft

print("\n=== Testing PPTX Generation ===\n")

agent = ProductionAgent(config={"output_dir": "output/test"})

if not agent.has_pptx:
    print("⚠ python-pptx not installed - will test fallback to HTML")
else:
    print("✓ python-pptx installed - testing full PPTX generation")

print()

draft = create_test_draft()

# Test PPTX with Creative template
result = agent.process({
    "draft_content": draft,
    "output_format": "pptx",
    "template_override": "creative"
})

print(f"✓ Generated: {result.file_path}")
print(f"✓ Format: {result.file_format}")
print(f"✓ Slides: {result.metadata.get('slides', 'unknown')}")
print()

print("✓ PPTX generation test complete!")
print("\nTo verify:")
print("1. Open the PPTX in PowerPoint, Keynote, or Google Slides")
print("2. Check that H1 headings became section slides")
print("3. Check that H2 headings became content slide titles")
print("4. Verify brand colors throughout")
EOF

python3 test_pptx_generation.py
```

### Test 6: Batch Production

```python
# test_batch_production.py
cat > test_batch_production.py << 'EOF'
"""Test batch production of multiple formats."""

from agents.production.production import ProductionAgent
from test_data import create_test_draft

print("\n=== Testing Batch Production ===\n")

agent = ProductionAgent(config={"output_dir": "output/test"})

print("Available formats:")
print(f"  - Markdown: Always available")
print(f"  - HTML: Always available")
print(f"  - DOCX: {'✓' if agent.has_docx else '✗ (will use HTML fallback)'}")
print(f"  - PDF: {'✓' if agent.has_reportlab else '✗ (will use HTML fallback)'}")
print(f"  - PPTX: {'✓' if agent.has_pptx else '✗ (will use HTML fallback)'}")
print()

# Create test draft
draft = create_test_draft()

# Produce all formats
formats = ["markdown", "html", "docx", "pdf", "pptx"]

print(f"Producing article in {len(formats)} formats...")
outputs = agent.batch_produce([draft], formats, template_override="modern")

print(f"\n✓ Generated {len(outputs)} files:")
for output in outputs:
    print(f"   - {output.file_format:8} → {output.file_path}")

print("\n✓ Batch production test complete!")
EOF

python3 test_batch_production.py
```

### Test 7: Content Repurpose

```python
# test_content_repurpose.py
cat > test_content_repurpose.py << 'EOF'
"""Test content repurposing transformations."""

from skills.content_repurpose.content_repurpose import ContentRepurposeSkill
from agents.base.models import ContentType
from test_data import create_test_draft

print("\n=== Testing Content Repurpose ===\n")

skill = ContentRepurposeSkill()

# Test transformations
draft = create_test_draft()

# Article → Social
print("1. Article → Social Post (LinkedIn)...")
result = skill.execute(draft, ContentType.SOCIAL_POST, platform="linkedin")
print(f"   ✓ Success: {result['success']}")
print(f"   ✓ Transformation: {result['metadata']['transformation']}")
print(f"   Preview: {result['content'][:100]}...")
print()

# Article → Presentation
print("2. Article → Presentation...")
result = skill.execute(draft, ContentType.PRESENTATION)
print(f"   ✓ Success: {result['success']}")
print(f"   Preview (first 200 chars):\n{result['content'][:200]}...")
print()

# Article → Email
print("3. Article → Email...")
result = skill.execute(draft, ContentType.EMAIL)
print(f"   ✓ Success: {result['success']}")
print(f"   Preview:\n{result['content'][:300]}...")
print()

print("✓ Content repurposing test complete!")
EOF

python3 test_content_repurpose.py
```

---

## 6. End-to-End Workflow Test

Create a comprehensive test that exercises the entire system:

```python
# test_end_to_end.py
cat > test_end_to_end.py << 'EOF'
"""Complete end-to-end workflow test."""

from agents.production.production import ProductionAgent
from templates.brand.brand_config import get_brand_template
from skills.content_repurpose.content_repurpose import ContentRepurposeSkill
from agents.base.models import ContentType
from test_data import create_test_draft

print("\n" + "="*60)
print("PHASE 3 END-TO-END WORKFLOW TEST")
print("="*60 + "\n")

# Step 1: Initialize
print("Step 1: Initialize Production Agent")
agent = ProductionAgent(config={
    "output_dir": "output/e2e_test",
    "brand_template": "tech"
})
print(f"   ✓ Agent initialized with {agent.brand_template.name} template")
print(f"   ✓ Output directory: {agent.output_dir}")
print()

# Step 2: Generate article in all formats
print("Step 2: Generate Article in All Formats")
draft = create_test_draft()
formats = ["markdown", "html", "docx", "pdf", "pptx"]
outputs = agent.batch_produce([draft], formats)

print(f"   ✓ Generated {len(outputs)} files:")
for output in outputs:
    print(f"      {output.file_format:8} → {output.file_path}")
print()

# Step 3: Repurpose to social
print("Step 3: Repurpose Article → Social Media")
repurpose_skill = ContentRepurposeSkill()
social_result = repurpose_skill.execute(draft, ContentType.SOCIAL_POST)
print(f"   ✓ Created social post ({len(social_result['content'])} chars)")
print()

# Step 4: Repurpose to presentation
print("Step 4: Repurpose Article → Presentation")
pres_result = repurpose_skill.execute(draft, ContentType.PRESENTATION)
print(f"   ✓ Created presentation structure ({len(pres_result['content'])} chars)")
print()

# Step 5: Test brand template switching
print("Step 5: Test Brand Template Switching")
templates_tested = []
for template_name in ["professional", "creative", "minimal"]:
    result = agent.process({
        "draft_content": draft,
        "output_format": "html",
        "template_override": template_name
    })
    templates_tested.append(template_name)
    print(f"   ✓ Generated with {template_name} template")

print()

# Summary
print("="*60)
print("TEST SUMMARY")
print("="*60)
print(f"✓ {len(outputs)} document formats generated")
print(f"✓ 2 content repurposing transformations")
print(f"✓ {len(templates_tested)} brand templates tested")
print(f"\nAll files saved to: {agent.output_dir}")
print("\n✓ END-TO-END TEST COMPLETE!")
EOF

python3 test_end_to_end.py
```

---

## 7. Manual Verification Checklist

After running automated tests, manually verify:

### DOCX Files
- [ ] Open in Microsoft Word or LibreOffice
- [ ] Brand colors visible in headings (H1: primary, H2/H3: secondary)
- [ ] Correct font families applied
- [ ] Page margins match brand template
- [ ] Metadata page shows company name

### PDF Files
- [ ] Open in Adobe Reader or Preview
- [ ] Professional typography and layout
- [ ] Brand colors in headings
- [ ] Page numbers at bottom
- [ ] Content readable and well-formatted

### PPTX Files
- [ ] Open in PowerPoint, Keynote, or Google Slides
- [ ] Title slide has brand colors
- [ ] H1 headings became section divider slides
- [ ] H2 headings became content slide titles
- [ ] Bullet points properly formatted
- [ ] Closing slide with company info

---

## 8. Troubleshooting

### Issue: Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'docx'
# Solution: Install dependencies
pip install python-docx

# Error: ModuleNotFoundError: No module named 'agents'
# Solution: Run from project root
cd /Users/johnpugh/Documents/source/content-creation-engine
python3 test_production_native.py
```

### Issue: Permission Errors

```bash
# Error: PermissionError: [Errno 13] Permission denied: 'output/test'
# Solution: Create directory with proper permissions
mkdir -p output/test
chmod 755 output/test
```

### Issue: Fonts Not Appearing

```
# DOCX/PDF fonts may fall back if specified fonts not installed
# This is normal - the system will use similar fonts
# To install specific fonts (macOS):
# - Calibri: Install Microsoft Office
# - Arial: Usually pre-installed
# - Helvetica: Usually pre-installed
```

### Issue: Colors Not Showing

```python
# Check that brand template is being applied:
from templates.brand.brand_config import get_brand_template

template = get_brand_template("professional")
print(f"Primary color: {template.colors.primary}")  # Should show hex code

# Verify in output files:
# - DOCX: Open and check heading colors
# - PDF: Check if colors render (some viewers may not show colors)
# - HTML: Open in browser and inspect elements
```

---

## 9. Clean Up

```bash
# Remove test output
rm -rf output/test output/e2e_test

# Deactivate virtual environment
deactivate

# Remove virtual environment (if desired)
rm -rf venv
```

---

## 10. Next Steps

Once testing is complete:

1. **Install dependencies permanently**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the existing Phase 3 examples**:
   ```bash
   python3 examples/phase3_templates.py
   ```

3. **Integrate with workflows** (Phase 3 remaining work)

4. **Write unit tests** using pytest

---

## Quick Start (TL;DR)

```bash
# Setup
cd /Users/johnpugh/Documents/source/content-creation-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python3 test_dependencies.py      # Verify dependencies
python3 test_brand_templates.py   # Test templates
python3 test_production_native.py # Test Markdown/HTML
python3 test_batch_production.py  # Test all formats
python3 test_end_to_end.py        # Full workflow

# Check output
open output/e2e_test/              # View generated files
```

---

## Support

If you encounter issues:
1. Check that Python 3.8+ is installed: `python3 --version`
2. Verify virtual environment is activated
3. Ensure all dependencies installed: `pip list`
4. Check output directory permissions
5. Review error messages for missing dependencies
