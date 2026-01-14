# Brand Voice Skill

## Purpose

Apply consistent voice and style across all content by validating against brand guidelines.

## Function

Validates `DraftContent` against brand voice rules:
- Vocabulary alignment (preferred/avoided terms)
- Sentence structure patterns
- Tone calibration per content type
- Readability and clarity
- Passive voice usage

## Key Functions

### 1. Vocabulary Check
Ensures content uses brand-preferred terminology and avoids discouraged terms.

**Example Avoided Terms**:
- "cheap" (use "cost-effective" instead)
- "easy" (use "straightforward" or "simple")
- "best" (use "leading" or "effective")

### 2. Sentence Length Analysis
Monitors sentence length to ensure readability:
- **Recommended Average**: 15 words
- **Maximum**: 25 words
- **Warning Threshold**: 30 words

### 3. Tone Alignment
Validates content matches the target tone using keyword analysis:
- **Professional**: implement, strategy, optimize, analyze, framework
- **Conversational**: you, we, let's, simply, just
- **Technical**: algorithm, architecture, protocol, implementation
- **Educational**: learn, understand, example, step, guide

### 4. Passive Voice Detection
Flags excessive passive voice usage:
- **Threshold**: Maximum 10-15% of sentences
- **Recommendation**: Prefer active voice for engagement

### 5. Readability Scoring
Uses Flesch Reading Ease score:
- **Target**: 70+ (easily understood by 13-15 year olds)
- **Minimum**: 60 (understood by 13-15 year olds)

## Usage

```python
from skills.brand_voice.brand_voice import BrandVoiceSkill
from agents.base.models import DraftContent, ContentType, ToneType

# Create skill instance
skill = BrandVoiceSkill()

# Prepare content
draft = DraftContent(
    content="Your article content here...",
    content_type=ContentType.ARTICLE,
    word_count=1200
)

# Validate
result = skill.execute(
    draft_content=draft,
    target_tone=ToneType.PROFESSIONAL
)

# Check results
if result.passed:
    print(f"✅ Brand voice validated (score: {result.score})")
else:
    print(f"❌ Issues found:")
    for issue in result.issues:
        print(f"  - {issue}")
    print(f"\nSuggestions:")
    for suggestion in result.suggestions:
        print(f"  - {suggestion}")
```

## Validation Output

`BrandVoiceResult` includes:
- **passed** (bool): Whether validation passed (score >= 0.7 and no critical issues)
- **score** (float): Overall score 0.0-1.0
- **issues** (List[str]): Critical problems that must be fixed
- **suggestions** (List[str]): Recommendations for improvement

## Quality Gate: Brand Consistency

This skill enforces Quality Gate 3 in the workflow.

✅ **Passes If**:
- Overall score >= 0.7
- No critical issues
- Vocabulary compliant
- Readability acceptable

❌ **Fails If**:
- Score < 0.7
- Excessive passive voice (>15%)
- Avoided terms present
- Readability too low (<60)

## Configuration

### Custom Guidelines

```python
custom_guidelines = {
    "sentence_length": {
        "max_words": 20,
        "recommended_avg": 12
    },
    "passive_voice": {
        "max_percentage": 5,
        "threshold": 10
    }
}

result = skill.execute(
    draft_content=draft,
    custom_guidelines=custom_guidelines
)
```

### Custom Vocabulary

```python
config = {
    "vocabulary": {
        "preferred_terms": ["innovative", "streamline", "optimize"],
        "avoided_terms": ["disrupt", "leverage", "synergy"]
    }
}

skill = BrandVoiceSkill(config=config)
```

## Validation Checks Breakdown

| Check | Weight | Scoring Method |
|-------|--------|----------------|
| Vocabulary | 20% | Ratio of preferred to avoided terms |
| Sentence Length | 20% | Deviation from recommended average |
| Tone Alignment | 20% | Keyword match percentage |
| Passive Voice | 20% | Percentage of passive sentences |
| Readability | 20% | Flesch Reading Ease score |

## Integration with Workflow

**Input**: `DraftContent` from Creation Agent
**Output**: `BrandVoiceResult`
**Quality Gate**: Brand Consistency (Gate 3)

**Workflow Position**:
Research → Content Brief → Creation → **Brand Voice** → Production

## Best Practices

### For Content Creators
1. Review brand vocabulary list before writing
2. Use active voice whenever possible
3. Keep sentences concise (< 20 words)
4. Match tone to content type
5. Aim for Flesch score > 70

### For Brand Managers
1. Define clear vocabulary preferences
2. Provide examples of good/bad tone
3. Set realistic readability targets
4. Update guidelines based on feedback
5. Document exceptions for technical content

## Reference Files

- `references/voice-guidelines.md` - Detailed brand voice rules
- `references/word-choices.md` - Comprehensive vocabulary list
- `references/examples/before-after.md` - Content improvement examples
- `references/examples/tone-spectrum.md` - Tone examples by type

## Future Enhancements

- Machine learning-based tone detection
- Industry-specific vocabulary libraries
- Competitor content comparison
- Automated rewriting suggestions
- Integration with grammar checkers
- Custom rule builder UI
