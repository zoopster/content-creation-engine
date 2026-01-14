# MVP Deployment Guide

This guide provides step-by-step instructions for deploying a Minimum Viable Product (MVP) of the Content Creation Engine.

## MVP Scope

The MVP includes:
- **Core Workflow**: Complete article production pipeline (Research → Creation → Production)
- **Agents**: Orchestrator, Research, Creation, Production
- **Skills**: Content Brief, Brand Voice, Long-Form Writing, DOCX generation
- **Output**: Generate complete articles as Markdown and DOCX files
- **Validation**: Quality gate enforcement at each workflow stage

**Not Included in MVP** (Future phases):
- Social media content generation
- PowerPoint/PDF generation
- Content repurposing
- External API integrations (real web search, AI APIs)
- Advanced template customization

## Prerequisites

### System Requirements

- **Python**: 3.12 or higher (recommended)
- **Operating System**: macOS, Linux, or Windows
- **Disk Space**: 100MB minimum
- **Memory**: 512MB minimum

### Required Tools

1. **Python 3.12+**
   ```bash
   python3 --version  # Should show 3.12 or higher
   ```

2. **pip** (Python package manager)
   ```bash
   pip3 --version
   ```

3. **git** (version control)
   ```bash
   git --version
   ```

## Deployment Steps

### 1. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/zoopster/content-creation-engine.git
cd content-creation-engine
```

### 2. Create Virtual Environment

**Recommended**: Use a virtual environment to isolate dependencies.

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

Your prompt should now show `(venv)` prefix.

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

**Expected packages for MVP**:
- pyyaml (workflow configuration)
- python-docx (Word document generation)
- pytest (testing framework)

### 4. Verify Installation

Run the quick test to ensure everything is working:

```bash
# Run basic tests
python3 -m pytest tests/test_phase3_quick.py -v
```

Expected output: All tests should pass.

### 5. Configure Brand Settings (Optional)

The MVP includes default brand settings. To customize:

```bash
# Edit brand configuration
nano templates/brand/brand_config.py
```

Key settings to customize:
- `BRAND_NAME`: Your organization name
- `TONE`: Desired content tone (professional, casual, technical, etc.)
- `VOCABULARY`: Preferred and avoided terms

### 6. Test MVP Workflow

Run the end-to-end example to verify deployment:

```bash
# Run Phase 2 end-to-end workflow
python3 examples/phase2_endtoend.py
```

**Expected behavior**:
1. Creates workflow request
2. Generates research brief
3. Produces article draft
4. Validates brand voice
5. Outputs results to console

You should see:
```
=== Phase 2: End-to-End Workflow Examples ===

Example 1: Complete Article Production
...
✓ Research completed
✓ Content created
✓ Quality validated
```

### 7. Generate Your First Article

Create a simple script or use Python interactive mode:

```python
from agents.workflow_executor import WorkflowExecutor
from agents.base.models import WorkflowRequest, ContentType

# Initialize executor
executor = WorkflowExecutor()

# Create request
request = WorkflowRequest(
    request_text="Write an article about the benefits of cloud computing for small businesses",
    content_types=[ContentType.ARTICLE],
    additional_context={
        "target_audience": "Small business owners",
        "word_count": 1000,
        "tone": "professional but accessible"
    }
)

# Execute workflow
result = executor.execute(request)

# Check results
if result.success:
    draft = result.outputs.get("draft_content")
    print(f"\n✓ Article generated: {draft.word_count} words")
    print(f"\nFirst 200 characters:")
    print(draft.content[:200])
else:
    print(f"✗ Failed: {result.error}")
```

### 8. Generate DOCX Output

To create Word documents:

```bash
# Run Phase 3 production example
python3 examples/phase3_production.py
```

This will:
1. Generate article content
2. Convert to DOCX format
3. Save to `output/` directory (created automatically)

**Output location**: `output/article_YYYYMMDD_HHMMSS.docx`

## Production Deployment Options

### Option 1: Local Server Deployment

For a single-user or small team setup:

```bash
# Keep the virtual environment activated
source venv/bin/activate

# Run your custom workflow script
python3 my_workflow.py
```

### Option 2: Docker Deployment (Future)

Docker support not included in MVP. Plan for Phase 4.

### Option 3: Cloud Deployment (Future)

Cloud deployment (AWS, GCP, Azure) planned for Phase 5.

## Configuration

### Environment Variables (Optional)

Create a `.env` file for sensitive configuration:

```bash
# .env (already in .gitignore)
BRAND_NAME=YourCompany
DEFAULT_TONE=professional
OUTPUT_DIRECTORY=./output
LOG_LEVEL=INFO
```

### Directory Structure

After deployment, your structure should look like:

```
content-creation-engine/
├── venv/                   # Virtual environment (created during setup)
├── output/                 # Generated content (auto-created)
├── agents/                 # Core agent implementations
├── skills/                 # Skill modules
├── examples/               # Usage examples
├── templates/              # Brand and content templates
└── tests/                  # Test suite
```

## Testing the Deployment

### Quick Test Checklist

Run through this checklist to verify MVP is working:

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list` shows python-docx, pyyaml, pytest)
- [ ] Tests pass (`pytest tests/test_phase3_quick.py`)
- [ ] Phase 2 example runs (`python3 examples/phase2_endtoend.py`)
- [ ] Phase 3 example creates DOCX (`python3 examples/phase3_production.py`)
- [ ] Output directory contains generated files

### Test Article Generation

```bash
# Simple test script
cat > test_mvp.py << 'EOF'
from agents.workflow_executor import WorkflowExecutor
from agents.base.models import WorkflowRequest, ContentType

executor = WorkflowExecutor()
request = WorkflowRequest(
    request_text="Write a brief article about sustainable technology",
    content_types=[ContentType.ARTICLE]
)
result = executor.execute(request)

if result.success:
    print("✓ MVP is working correctly!")
    print(f"Generated {result.outputs['draft_content'].word_count} words")
else:
    print(f"✗ Error: {result.error}")
EOF

python3 test_mvp.py
```

## Common Issues and Troubleshooting

### Issue: `ModuleNotFoundError`

**Symptom**: `ModuleNotFoundError: No module named 'docx'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Permission Denied on Output

**Symptom**: `PermissionError: [Errno 13] Permission denied: 'output/'`

**Solution**:
```bash
# Create output directory manually
mkdir -p output
chmod 755 output
```

### Issue: Tests Failing

**Symptom**: `pytest` shows failed tests

**Solution**:
```bash
# Run verbose tests to see details
python3 -m pytest tests/test_phase3_quick.py -v -s

# Check Python version (must be 3.8+)
python3 --version

# Verify all dependencies installed
pip list | grep -E "(pyyaml|docx|pytest)"
```

### Issue: Import Errors

**Symptom**: `ImportError: attempted relative import with no known parent package`

**Solution**:
```bash
# Run scripts from project root directory
cd /path/to/content-creation-engine
python3 examples/phase2_endtoend.py

# Don't run: cd examples && python3 phase2_endtoend.py
```

### Issue: Output Files Not Generated

**Symptom**: Script runs but no files in `output/`

**Solution**:
```bash
# Check if output directory exists
ls -la output/

# If not, create it
mkdir -p output

# Run Phase 3 example which explicitly saves files
python3 examples/phase3_production.py

# Check for files
ls -la output/
```

## Usage Examples

### Example 1: Generate Blog Post

```python
from agents.workflow_executor import WorkflowExecutor
from agents.base.models import WorkflowRequest, ContentType

executor = WorkflowExecutor()
request = WorkflowRequest(
    request_text="Create a blog post about AI in healthcare",
    content_types=[ContentType.ARTICLE],
    additional_context={
        "target_audience": "Healthcare professionals",
        "word_count": 1200,
        "tone": "authoritative",
        "include_sections": ["Introduction", "Current Applications",
                            "Benefits", "Challenges", "Future Outlook"]
    }
)

result = executor.execute(request)
print(result.outputs["draft_content"].content)
```

### Example 2: Generate with Custom Brand Voice

```python
from agents.workflow_executor import WorkflowExecutor
from agents.base.models import WorkflowRequest, ContentType

# Brand voice will automatically validate against configured guidelines
request = WorkflowRequest(
    request_text="Write about cybersecurity best practices",
    content_types=[ContentType.ARTICLE],
    additional_context={
        "brand_voice": "technical_professional",
        "avoid_jargon": False,  # Technical audience
        "tone": "expert"
    }
)

executor = WorkflowExecutor()
result = executor.execute(request)

# Check brand validation results
validation = result.outputs.get("brand_validation")
if validation:
    print(f"Brand compliance score: {validation.compliance_score}")
```

### Example 3: Export to DOCX

```python
from agents.production.production import ProductionAgent
from agents.base.models import AgentInput, ContentType
from datetime import datetime

# Create production agent
production = ProductionAgent()

# Prepare content
content = """
# My Article Title

This is the introduction paragraph...

## Section 1
Content here...
"""

# Generate DOCX
agent_input = AgentInput(
    content={
        "markdown_content": content,
        "format": "docx",
        "title": "My Article"
    },
    content_type=ContentType.ARTICLE
)

result = production.process(agent_input)

if result.success:
    # File automatically saved to output/
    print(f"✓ Document created: {result.outputs['file_path']}")
```

## Performance Expectations

### MVP Performance Metrics

- **Article Generation**: ~2-5 seconds (mock research data)
- **DOCX Export**: ~1-2 seconds
- **Full Workflow**: ~5-10 seconds
- **Memory Usage**: ~50-100MB

**Note**: These metrics are for MVP with mock data. Real API integrations (Phase 4+) will be slower.

## Next Steps After MVP

Once MVP is deployed and validated:

1. **Phase 4 Enhancement**:
   - Add real web search integration
   - Implement content repurposing
   - Add social media content generation

2. **Production Hardening**:
   - Add error logging
   - Implement retry logic
   - Add monitoring/metrics

3. **Scaling**:
   - Parallel workflow execution
   - Queue-based processing
   - API service wrapper

4. **Integration**:
   - CMS integration (WordPress, etc.)
   - Social platform APIs
   - Email marketing tools

## Support and Documentation

- **Quick Start**: See [QUICKSTART.md](./QUICKSTART.md)
- **Architecture**: See [CLAUDE.md](./CLAUDE.md)
- **Phase Details**: See PHASE1_COMPLETE.md, PHASE2_COMPLETE.md, PHASE3_COMPLETE.md
- **Examples**: Check `examples/` directory
- **Issues**: Report at https://github.com/zoopster/content-creation-engine/issues

## Security Considerations

### MVP Security Notes

- No external API calls (all mock data)
- No user authentication (single-user system)
- Local file system only
- No network exposure

### For Production

Before production deployment:
- [ ] Add input validation
- [ ] Implement authentication
- [ ] Sanitize file paths
- [ ] Add rate limiting
- [ ] Enable secure logging
- [ ] Review dependency vulnerabilities (`pip audit`)

## Maintenance

### Regular Updates

```bash
# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install --upgrade -r requirements.txt

# Run tests to verify
pytest tests/
```

### Backup

Important directories to backup:
- `templates/brand/` - Custom brand configuration
- `output/` - Generated content (if needed)
- `.env` - Environment configuration (if using)

## Uninstallation

To remove the MVP:

```bash
# Deactivate virtual environment
deactivate

# Remove project directory
cd ..
rm -rf content-creation-engine

# That's it! All dependencies were in the virtual environment
```

## License

[License details in main README.md]

## Version

- **MVP Version**: 1.0.0
- **Based on**: Phase 3 Complete
- **Last Updated**: 2026-01-14
