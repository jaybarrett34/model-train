# Dataset Size Analyzer Guide

## Overview

The Dataset Size Analyzer is a comprehensive tool for estimating optimal training dataset sizes based on pattern complexity, model parameters, and training objectives. It provides research-based heuristics and quality analysis to help determine adequate training data requirements.

## Features

- **Pattern Complexity Analysis**: Automatically analyzes XML patterns to determine complexity scores
- **Size Estimation**: Calculates minimum, optimal, and maximum dataset sizes based on multiple factors
- **Quality Metrics**: Analyzes existing datasets for duplicates, diversity, and overfitting risks
- **Recommendations**: Provides actionable recommendations for improving dataset quality
- **Multiple Output Formats**: Supports both human-readable text and JSON output
- **Model-Aware**: Adjusts estimates based on model size (1B to 70B+ parameters)
- **Fine-tuning Aware**: Considers LoRA rank and fine-tuning strength

## Installation

The size analyzer is included in the core module:

```python
from core import DatasetSizeAnalyzer, XMLPattern, FinetuningStrength
```

## Quick Start

### Basic Usage

```python
from core import DatasetSizeAnalyzer, XMLPattern

# Define your XML pattern
pattern = XMLPattern(
    schema="<thinking>...</thinking><answer>...</answer>",
    required_tags=["thinking", "answer"]
)

# Create analyzer
analyzer = DatasetSizeAnalyzer(
    xml_pattern=pattern,
    base_model="qwen2.5:7b",
    objective="Teach model to show reasoning before answering"
)

# Generate report
report = analyzer.analyze()
print(report)
```

### Analyzing Existing Dataset

```python
# Analyze with an existing dataset
report = analyzer.analyze(dataset_path="data/training_data.jsonl")
print(report)
```

## Core Components

### DatasetSizeAnalyzer

Main class for dataset analysis and size estimation.

**Parameters:**
- `xml_pattern` (XMLPattern, optional): XML pattern specification
- `base_model` (str): Model identifier (e.g., "qwen2.5:7b", "llama3:8b")
- `objective` (str): Training objective description
- `finetuning_strength` (FinetuningStrength): Light, moderate, or heavy
- `lora_rank` (int, optional): LoRA rank if using LoRA fine-tuning
- `pattern_description` (str, optional): Additional pattern description

**Methods:**
- `analyze_pattern_complexity()`: Analyze XML pattern complexity
- `estimate_dataset_size()`: Calculate size recommendations
- `analyze_dataset_quality(dataset_path)`: Analyze existing dataset
- `analyze(dataset_path=None)`: Comprehensive analysis with report

### Complexity Levels

The analyzer classifies patterns into five complexity levels:

| Level | Score | Description | Base Size Range |
|-------|-------|-------------|-----------------|
| TRIVIAL | 0-20 | Simple format changes | 30-300 examples |
| SIMPLE | 21-40 | Basic patterns | 50-600 examples |
| MODERATE | 41-60 | Standard complexity | 100-1500 examples |
| COMPLEX | 61-80 | Advanced patterns | 300-3500 examples |
| VERY_COMPLEX | 81-100 | Complex reasoning/domain | 1000-15000 examples |

### Complexity Scoring Factors

1. **Tag Count** (0-25 points): Number of unique XML tags
2. **Tag Depth** (0-20 points): Nesting level of XML structure
3. **Constraints** (0-25 points): Number of requirements and constraints
4. **Reasoning** (0-15 points): Whether pattern requires logical reasoning
5. **Domain Knowledge** (0-15 points): Whether pattern is domain-specific

### Fine-tuning Strengths

```python
from core import FinetuningStrength

# Light: Minimal behavior adjustment (0.7x multiplier)
FinetuningStrength.LIGHT

# Moderate: Standard fine-tuning (1.0x multiplier)
FinetuningStrength.MODERATE

# Heavy: Deep behavior modification (1.4x multiplier)
FinetuningStrength.HEAVY
```

## Size Estimation Heuristics

The analyzer uses research-based heuristics:

### Base Guidelines

- **Simple format changes**: 50-200 examples
- **New behavior patterns**: 200-1000 examples
- **Complex reasoning**: 1000-5000 examples
- **Domain knowledge**: 5000+ examples

### Adjustment Factors

1. **Model Size Multiplier**:
   - 70B+: 1.5x
   - 30-69B: 1.3x
   - 13-29B: 1.15x
   - 7-12B: 1.0x
   - 3-6B: 0.85x

2. **Fine-tuning Strength Multiplier**:
   - Light: 0.7x
   - Moderate: 1.0x
   - Heavy: 1.4x

3. **LoRA Rank Multiplier**:
   - Rank 128+: 1.3x
   - Rank 64-127: 1.15x
   - Rank 16-63: 1.0x
   - Rank <16: 0.9x

## Quality Metrics

### Metrics Provided

- **Duplicate Detection**: Identifies exact duplicate examples
- **Diversity Score**: Measures example uniqueness (0-100)
- **Variance Score**: Measures content variation (0-100)
- **Pattern Analysis**: Counts unique input/output patterns
- **Overfitting Risk**: Assesses risk level (low/moderate/high)

### Quality Thresholds

**Overfitting Risk Assessment**:
- **High Risk**: Uniqueness <70%, Diversity <50%, or Variance <30%
- **Moderate Risk**: Uniqueness <85%, Diversity <70%, or Variance <50%
- **Low Risk**: Above moderate thresholds

## Report Structure

The analysis report includes:

1. **Model Configuration**: Model info, size, fine-tuning settings
2. **Pattern Complexity**: Complexity score, level, and factors
3. **Size Analysis**: Current size, recommendations, adequacy status
4. **Quality Metrics**: Duplicates, diversity, variance, risk assessment
5. **Performance Estimates**: Expected performance and training time
6. **Recommendations**: Actionable suggestions for improvement
7. **Warnings**: Potential issues and risks
8. **Augmentation Strategies**: Suggested data generation approaches

## Advanced Examples

### Example 1: Complex Domain-Specific Pattern

```python
from core import DatasetSizeAnalyzer, XMLPattern, FinetuningStrength

# Medical diagnosis pattern
pattern = XMLPattern(
    schema="""
    <clinical_thinking>
        <symptoms_analysis>...</symptoms_analysis>
        <differential_diagnosis>...</differential_diagnosis>
        <reasoning>...</reasoning>
    </clinical_thinking>
    <diagnosis>...</diagnosis>
    <confidence_level>...</confidence_level>
    <recommended_tests>...</recommended_tests>
    """,
    required_tags=[
        "clinical_thinking", "symptoms_analysis",
        "differential_diagnosis", "diagnosis"
    ],
    optional_tags=["confidence_level", "recommended_tests"]
)

analyzer = DatasetSizeAnalyzer(
    xml_pattern=pattern,
    base_model="qwen2.5:32b",
    objective="Train model for medical diagnosis reasoning",
    finetuning_strength=FinetuningStrength.HEAVY,
    lora_rank=128,
    pattern_description="Complex medical reasoning requiring domain expertise in symptom analysis and differential diagnosis"
)

report = analyzer.analyze()
print(f"Complexity: {report.complexity_analysis.complexity_score}/100")
print(f"Optimal Size: {report.size_estimates.optimal} examples")
print(f"Reasoning Required: {report.complexity_analysis.reasoning_required}")
print(f"Domain Specific: {report.complexity_analysis.domain_specific}")
```

### Example 2: Model Comparison

```python
models = ["qwen2.5:7b", "qwen2.5:14b", "qwen2.5:32b", "qwen2.5:70b"]

for model in models:
    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model=model,
        objective=objective
    )
    report = analyzer.analyze()
    print(f"{model}: {report.size_estimates.optimal} examples")
```

### Example 3: Dataset Quality Analysis

```python
# Analyze existing dataset quality
analyzer = DatasetSizeAnalyzer(
    xml_pattern=pattern,
    base_model="qwen2.5:7b",
    objective="Reasoning pattern"
)

report = analyzer.analyze(dataset_path="data/training.jsonl")

# Check quality metrics
quality = report.quality_metrics
print(f"Duplicates: {quality.duplicate_percentage:.1f}%")
print(f"Diversity: {quality.diversity_score:.1f}/100")
print(f"Overfitting Risk: {quality.overfitting_risk}")

# Follow recommendations
for i, rec in enumerate(report.recommendations, 1):
    print(f"{i}. {rec}")
```

### Example 4: JSON Output for Integration

```python
import json

analyzer = DatasetSizeAnalyzer(
    xml_pattern=pattern,
    base_model="qwen2.5:7b",
    objective=objective
)

report = analyzer.analyze(dataset_path="data/training.jsonl")

# Export to JSON
json_data = json.dumps(report.to_dict(), indent=2)

# Save to file
with open("analysis_report.json", "w") as f:
    f.write(json_data)

# Or use directly in code
data = report.to_dict()
if data['adequacy_status'] == 'insufficient':
    print(f"Need {data['size_estimates']['minimum'] - data['current_size']} more examples")
```

### Example 5: Convenience Function

```python
from core import analyze_dataset, XMLPattern

pattern = XMLPattern(
    schema="<thinking>...</thinking><answer>...</answer>",
    required_tags=["thinking", "answer"]
)

# Quick analysis with text output
report_text = analyze_dataset(
    dataset_path="data/training.jsonl",
    xml_pattern=pattern,
    base_model="qwen2.5:7b",
    objective="Reasoning pattern",
    output_format="text"
)
print(report_text)

# Or JSON output
report_json = analyze_dataset(
    dataset_path="data/training.jsonl",
    xml_pattern=pattern,
    base_model="qwen2.5:7b",
    objective="Reasoning pattern",
    output_format="json"
)
data = json.loads(report_json)
```

## Adequacy Status Levels

| Status | Meaning | Action |
|--------|---------|--------|
| INSUFFICIENT | Below minimum threshold | Generate more data immediately |
| MINIMAL | At minimum threshold | Consider adding more examples |
| ADEQUATE | Within recommended range | Dataset is usable, more helps |
| OPTIMAL | At optimal size | Focus on quality over quantity |
| EXCESSIVE | Beyond diminishing returns | Additional data provides minimal benefit |

## Best Practices

### 1. Start with Analysis

Always analyze your pattern complexity before generating data:

```python
complexity = analyzer.analyze_pattern_complexity()
print(f"Complexity: {complexity.complexity_score}/100")
print(f"Level: {complexity.complexity_level.value}")
```

### 2. Check Quality Early

Analyze dataset quality at regular intervals:

```python
# After generating first batch
report = analyzer.analyze(dataset_path="data.jsonl")
if report.quality_metrics.duplicate_percentage > 10:
    print("Too many duplicates - improve generation diversity")
```

### 3. Use Recommendations

Follow the analyzer's recommendations:

```python
report = analyzer.analyze(dataset_path="data.jsonl")
for rec in report.recommendations:
    print(f"TODO: {rec}")
```

### 4. Monitor Overfitting Risk

Keep overfitting risk low:

```python
if report.quality_metrics.overfitting_risk == "high":
    # Increase diversity
    # Remove duplicates
    # Add more varied examples
```

### 5. Consider Your Use Case

Adjust estimates based on your specific needs:

- **Production systems**: Aim for optimal size
- **Experimentation**: Minimal size may suffice
- **Critical applications**: Consider exceeding optimal size
- **Resource-constrained**: Start with minimum, iterate

## Interpreting Results

### Complexity Score

- **0-20 (Trivial)**: Very simple patterns, minimal training needed
- **21-40 (Simple)**: Basic patterns, moderate training data
- **41-60 (Moderate)**: Standard complexity, substantial training data
- **61-80 (Complex)**: Advanced patterns, large training set
- **81-100 (Very Complex)**: Requires extensive training data and care

### Expected Performance

- **Poor**: Dataset insufficient, training unlikely to succeed
- **Fair**: Basic learning possible, limited generalization
- **Good**: Should learn patterns, may have edge case issues
- **Excellent**: Strong learning expected, good generalization

### Diversity Score

- **0-40**: Very low - high overfitting risk
- **41-60**: Low - improve variety
- **61-80**: Good - acceptable diversity
- **81-100**: Excellent - high variety

## Common Patterns and Estimates

### Simple Reasoning Pattern

```
Pattern: <thinking>...</thinking><answer>...</answer>
Complexity: ~40/100 (Simple)
7B Model: 50-250 examples (optimal: 250)
14B Model: 57-287 examples (optimal: 287)
```

### Multi-Step Problem Solving

```
Pattern: <analysis>...</analysis><steps>...</steps><solution>...</solution>
Complexity: ~55/100 (Moderate)
7B Model: 100-500 examples (optimal: 500)
14B Model: 115-575 examples (optimal: 575)
```

### Domain-Specific Reasoning

```
Pattern: Complex multi-tag with domain knowledge
Complexity: ~75/100 (Complex)
7B Model: 300-1200 examples (optimal: 1200)
14B Model: 345-1380 examples (optimal: 1380)
```

## Troubleshooting

### Issue: Complexity Score Too Low

**Problem**: Analyzer rates pattern as simpler than expected

**Solutions**:
- Add more detailed `pattern_description`
- Include more required tags
- Use more complex XML schema structure
- Emphasize reasoning/domain requirements in objective

### Issue: Dataset Quality Low

**Problem**: High duplicate rate or low diversity

**Solutions**:
- Use multiple generation prompts
- Vary generation parameters (temperature)
- Use multiple AI providers
- Implement template variations
- Add constraints for uniqueness

### Issue: Recommendations Unclear

**Problem**: Not sure how to implement recommendations

**Solutions**:
- Check specific metrics (duplicates, diversity, variance)
- Review augmentation strategies section
- Start with easiest recommendations first
- Re-analyze after each improvement

### Issue: Model Size Not Recognized

**Problem**: Model name doesn't match expected format

**Solution**: Use standard format like "model:7b" or "model:14b"

## Integration Examples

### With DataSynthesizer

```python
from core import DataSynthesizer, OllamaProvider, DatasetSizeAnalyzer

# Analyze required size
analyzer = DatasetSizeAnalyzer(
    xml_pattern=pattern,
    base_model="qwen2.5:7b",
    objective=objective
)
report = analyzer.analyze()
target_size = report.size_estimates.optimal

# Generate data
provider = OllamaProvider(model="qwen2.5:7b")
synthesizer = DataSynthesizer(provider=provider, xml_pattern=pattern)

# Generate until target reached
current_size = 0
while current_size < target_size:
    batch = synthesizer.generate_batch(objective, count=10)
    current_size += len(batch)

    # Re-analyze quality
    if current_size % 50 == 0:
        report = analyzer.analyze(dataset_path="data.jsonl")
        print(f"Progress: {report.adequacy_percentage:.1f}%")
```

### In Training Pipeline

```python
# Pre-training analysis
analyzer = DatasetSizeAnalyzer(...)
report = analyzer.analyze(dataset_path="training_data.jsonl")

if report.adequacy_status == "insufficient":
    raise ValueError(f"Need {report.size_estimates.minimum - report.current_size} more examples")

if report.quality_metrics.overfitting_risk == "high":
    print("WARNING: High overfitting risk detected")

# Proceed with training
# ... training code ...
```

## API Reference

### Classes

- `DatasetSizeAnalyzer`: Main analyzer class
- `ComplexityAnalysis`: Pattern complexity results
- `SizeEstimate`: Size recommendations
- `QualityMetrics`: Dataset quality analysis
- `AnalysisReport`: Comprehensive report

### Enums

- `ComplexityLevel`: TRIVIAL, SIMPLE, MODERATE, COMPLEX, VERY_COMPLEX
- `AdequacyStatus`: INSUFFICIENT, MINIMAL, ADEQUATE, OPTIMAL, EXCESSIVE
- `FinetuningStrength`: LIGHT, MODERATE, HEAVY

### Functions

- `analyze_dataset()`: Convenience function for quick analysis

## Limitations

1. **Heuristic-Based**: Estimates are based on general heuristics, not guarantees
2. **Pattern-Dependent**: Results vary based on pattern description quality
3. **Use Case Specific**: Actual requirements may differ for specific applications
4. **Hardware Agnostic**: Training time estimates assume reasonable hardware
5. **Static Analysis**: Cannot predict actual model performance

## Future Enhancements

Planned improvements:
- ML-based complexity estimation
- Historical performance tracking
- Dataset versioning support
- Active learning recommendations
- Automated data generation integration

## Support

For issues, questions, or feature requests:
- Check examples in `examples/size_analyzer_example.py`
- Review this documentation
- Examine source code in `core/size_analyzer.py`

## License

Part of the model-train project. See project LICENSE for details.
