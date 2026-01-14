# Contributing to Content Creation Engine

Thank you for your interest in contributing to the Content Creation Engine! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [CI/CD Pipeline](#cicd-pipeline)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/content-creation-engine.git
cd content-creation-engine
```

### 2. Set Up Development Environment

```bash
# Use the automated setup script
./setup_and_test.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install Development Dependencies

```bash
pip install flake8 black isort pytest pytest-cov safety bandit
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

## Development Workflow

### Branch Naming Convention

- `feature/` - New features or enhancements
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

Examples:
- `feature/social-media-integration`
- `fix/docx-generation-error`
- `docs/update-api-examples`

### Commit Message Guidelines

Follow the conventional commits format:

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

Examples:
```
feat: add PDF generation skill

Implements PDF output using reportlab library with brand template support.

Closes #42
```

```
fix: resolve missing import in DOCX generation

Added missing WD_ALIGN_PARAGRAPH import in _add_headers_footers method.
```

## CI/CD Pipeline

### Automated Tests

When you push code or create a pull request, GitHub Actions automatically runs:

1. **Test Suite** (`ci.yml`)
   - Runs on Python 3.8, 3.9, 3.10, 3.11, 3.12
   - Tests on Ubuntu, macOS, and Windows
   - Executes MVP test suite
   - Runs pytest (if tests exist)

2. **Code Quality Checks** (`ci.yml`)
   - Flake8 linting
   - Black code formatting
   - isort import ordering

3. **Security Scan** (`ci.yml`)
   - Safety check for dependency vulnerabilities
   - Bandit security linter

### Running Tests Locally

Before pushing, run tests locally:

```bash
# Run MVP test suite
python mvp_test.py

# Run pytest (if available)
pytest tests/ -v

# Run linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Check formatting
black --check .

# Check imports
isort --check-only .
```

### Auto-formatting Code

```bash
# Format code with black
black .

# Sort imports
isort .
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable and function names
- Add docstrings to all classes and functions
- Maximum line length: 127 characters

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input provided
    """
    pass
```

### Type Hints

Use type hints for function parameters and return values:

```python
from typing import List, Dict, Optional

def process_content(
    content: str,
    options: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Process content with optional configuration."""
    pass
```

## Testing Guidelines

### Test Coverage

- Write tests for new features
- Maintain or improve code coverage
- Test edge cases and error conditions

### Test Structure

```python
def test_feature_name():
    """Test description."""
    # Arrange
    input_data = {...}

    # Act
    result = function_to_test(input_data)

    # Assert
    assert result.success
    assert result.output == expected_output
```

### MVP Test Integration

If your changes affect core functionality, update `mvp_test.py`:

```python
def test_your_new_feature():
    """Test new feature functionality"""
    print_header("Testing Your New Feature")

    try:
        # Your test code here
        print("✓ Feature working correctly")
        return True
    except Exception as e:
        print(f"✗ Feature test failed: {e}")
        return False
```

## Submitting Changes

### Pull Request Process

1. **Update Documentation**
   - Update README.md if adding features
   - Add/update docstrings
   - Update CHANGELOG if significant change

2. **Ensure Tests Pass**
   ```bash
   python mvp_test.py
   pytest tests/ -v
   ```

3. **Check Code Quality**
   ```bash
   black --check .
   isort --check-only .
   flake8 .
   ```

4. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to GitHub and create a pull request
   - Fill out the PR template
   - Link related issues
   - Request review from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (describe)

## Testing
- [ ] MVP test suite passes
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Tests pass locally
```

## Project Structure

Understanding the codebase structure:

```
content-creation-engine/
├── agents/              # Agent implementations
│   ├── base/           # Base classes and models
│   ├── orchestrator/   # Orchestrator agent
│   ├── research/       # Research agent
│   ├── creation/       # Creation agent
│   └── production/     # Production agent
├── skills/             # Modular skills
│   ├── content_brief/
│   ├── brand_voice/
│   └── ...
├── examples/           # Usage examples
├── templates/          # Templates and configurations
├── tests/              # Test suite
└── .github/            # GitHub Actions workflows
```

## Adding New Features

### Adding a New Skill

1. Create skill directory: `skills/your_skill/`
2. Implement skill class (inherit from `Skill`)
3. Add `SKILL.md` documentation
4. Create reference materials in `references/`
5. Add tests
6. Update relevant agent to use the skill

### Adding a New Agent

1. Create agent directory: `agents/your_agent/`
2. Implement agent class (inherit from `Agent`)
3. Add `AGENT.md` documentation
4. Update Orchestrator routing if needed
5. Add tests
6. Update workflow executor

## Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check existing docs in the repository

## Release Process

Releases are automated via GitHub Actions when tags are pushed:

```bash
# Tag a new version
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Git commit history (Co-Authored-By)

Thank you for contributing to Content Creation Engine!
