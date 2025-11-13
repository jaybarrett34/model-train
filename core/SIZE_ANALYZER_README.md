# Dataset Size Analyzer Module

## Quick Reference

The Dataset Size Analyzer (`core/size_analyzer.py`) helps estimate optimal training dataset sizes and analyze dataset quality.

## Files Created

- `/home/user/model-train/core/size_analyzer.py` - Main module (1400+ lines)
- `/home/user/model-train/core/test_size_analyzer.py` - Unit tests
- `/home/user/model-train/examples/size_analyzer_example.py` - Usage examples
- `/home/user/model-train/docs/size_analyzer_guide.md` - Comprehensive guide

## Quick Start

```python
from core import DatasetSizeAnalyzer, XMLPattern

# Define pattern
pattern = XMLPattern(
    schema="<thinking>...</thinking><answer>...</answer>",
    required_tags=["thinking", "answer"]
)

# Create analyzer
analyzer = DatasetSizeAnalyzer(
    xml_pattern=pattern,
    base_model="qwen2.5:7b",
    objective="Teach reasoning pattern"
)

# Analyze
report = analyzer.analyze(dataset_path="data.jsonl")
print(report)
```

## Key Features

1. **Pattern Complexity Analysis** (0-100 score)
   - Analyzes XML structure
   - Detects reasoning requirements
   - Identifies domain-specific patterns

2. **Size Estimation**
   - Minimum required examples
   - Optimal dataset size
   - Diminishing returns threshold
   - Adjusts for model size (1B-70B+)
   - Considers LoRA rank and fine-tuning strength

3. **Quality Analysis**
   - Duplicate detection
   - Diversity scoring
   - Variance analysis
   - Overfitting risk assessment

4. **Comprehensive Reports**
   - Current dataset status
   - Recommendations
   - Warnings
   - Augmentation strategies

## Complexity Levels

| Level | Score | Examples Needed |
|-------|-------|----------------|
| Trivial | 0-20 | 30-300 |
| Simple | 21-40 | 50-600 |
| Moderate | 41-60 | 100-1500 |
| Complex | 61-80 | 300-3500 |
| Very Complex | 81-100 | 1000-15000 |

## Research-Based Heuristics

- **Simple format changes**: 50-200 examples
- **New behavior patterns**: 200-1000 examples
- **Complex reasoning**: 1000-5000 examples
- **Domain knowledge**: 5000+ examples

Adjusted by:
- Model size (larger = more data)
- Fine-tuning strength (heavier = more data)
- LoRA rank (higher = more data)

## Running Examples

```bash
# Run comprehensive examples
python examples/size_analyzer_example.py

# Run tests
python core/test_size_analyzer.py
```

## Common Use Cases

### 1. Check if dataset is sufficient

```python
report = analyzer.analyze(dataset_path="data.jsonl")
if report.adequacy_status == "insufficient":
    print(f"Need {report.size_estimates.minimum - report.current_size} more examples")
```

### 2. Compare model requirements

```python
for model in ["7b", "14b", "32b", "70b"]:
    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model=f"qwen2.5:{model}"
    )
    report = analyzer.analyze()
    print(f"{model}: {report.size_estimates.optimal} examples")
```

### 3. Check quality before training

```python
report = analyzer.analyze(dataset_path="data.jsonl")
quality = report.quality_metrics

if quality.duplicate_percentage > 10:
    print("⚠️ Too many duplicates")
if quality.overfitting_risk == "high":
    print("⚠️ High overfitting risk")
if quality.diversity_score < 60:
    print("⚠️ Low diversity")
```

## Documentation

See `/home/user/model-train/docs/size_analyzer_guide.md` for comprehensive documentation including:
- Detailed API reference
- Advanced examples
- Integration guides
- Best practices
- Troubleshooting

## Exports

From `core` package:
- `DatasetSizeAnalyzer` - Main analyzer class
- `FinetuningStrength` - Light/Moderate/Heavy enum
- `AdequacyStatus` - Dataset status enum
- `ComplexityLevel` - Pattern complexity enum
- `SizeEstimate` - Size estimates dataclass
- `QualityMetrics` - Quality metrics dataclass
- `ComplexityAnalysis` - Complexity analysis dataclass
- `AnalysisReport` - Full report dataclass
- `analyze_dataset()` - Convenience function

## Example Output

```
================================================================================
DATASET SIZE ANALYSIS REPORT
================================================================================

MODEL CONFIGURATION
--------------------------------------------------------------------------------
Base Model: qwen2.5:7b
Model Size: 7b
Fine-tuning Strength: moderate
LoRA Rank: N/A

PATTERN COMPLEXITY ANALYSIS
--------------------------------------------------------------------------------
Complexity Score: 40.0/100
Complexity Level: SIMPLE
Unique XML Tags: 2
Tag Depth: 1
Constraint Count: 2
Reasoning Required: Yes
Domain Specific: No

DATASET SIZE ANALYSIS
--------------------------------------------------------------------------------
Current Size: 150 examples
Minimum Required: 50 examples
Optimal Size: 250 examples
Maximum Useful: 600 examples
Diminishing Returns: 400 examples

Adequacy Status: ADEQUATE
Progress to Optimal: 60.0%

QUALITY METRICS
--------------------------------------------------------------------------------
Total Examples: 150
Unique Examples: 145
Duplicates: 5 (3.3%)
Diversity Score: 96.7/100
Variance Score: 85.2/100
Overfitting Risk: LOW

RECOMMENDATIONS
--------------------------------------------------------------------------------
1. Dataset is adequate. Adding 100 more examples would reach optimal size
```

## Integration with Synthesis

```python
from core import DataSynthesizer, OllamaProvider, DatasetSizeAnalyzer

# Analyze requirements
analyzer = DatasetSizeAnalyzer(...)
report = analyzer.analyze()
target = report.size_estimates.optimal

# Generate data
provider = OllamaProvider(model="qwen2.5:7b")
synthesizer = DataSynthesizer(provider=provider, xml_pattern=pattern)

# Generate until target reached
while current_size < target:
    batch = synthesizer.generate_batch(objective, count=10)
    current_size += len(batch)
```

## Tests

All tests pass:
- Basic initialization
- Model size extraction
- Complexity analysis (trivial and complex)
- Size estimation
- Fine-tuning strength multipliers
- Dataset quality analysis
- Adequacy status determination
- Full analysis report generation
- Convenience function

Run: `python core/test_size_analyzer.py`

## Support

For issues or questions:
1. Check examples: `examples/size_analyzer_example.py`
2. Read guide: `docs/size_analyzer_guide.md`
3. Review tests: `core/test_size_analyzer.py`
4. Examine source: `core/size_analyzer.py`
