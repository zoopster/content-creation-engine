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
