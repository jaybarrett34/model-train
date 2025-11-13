"""
Example usage of the DatasetSizeAnalyzer module

This script demonstrates how to use the DatasetSizeAnalyzer to:
1. Analyze XML pattern complexity
2. Estimate optimal dataset sizes
3. Analyze existing dataset quality
4. Generate comprehensive reports with recommendations
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    DatasetSizeAnalyzer,
    XMLPattern,
    FinetuningStrength,
    analyze_dataset
)


def example_1_simple_pattern():
    """Example 1: Simple reasoning pattern"""
    print("=" * 80)
    print("EXAMPLE 1: Simple Reasoning Pattern")
    print("=" * 80)
    print()

    # Define a simple XML pattern
    pattern = XMLPattern(
        schema="<thinking>...</thinking><answer>...</answer>",
        required_tags=["thinking", "answer"]
    )

    # Create analyzer
    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model="qwen2.5:7b",
        objective="Teach model to show reasoning before answering",
        finetuning_strength=FinetuningStrength.LIGHT
    )

    # Generate report (without existing dataset)
    report = analyzer.analyze()
    print(report)
    print()


def example_2_complex_pattern():
    """Example 2: Complex Minecraft command pattern"""
    print("=" * 80)
    print("EXAMPLE 2: Complex Minecraft Command Pattern")
    print("=" * 80)
    print()

    # Define a complex XML pattern
    pattern = XMLPattern(
        schema="""
        <thinking>
            <analysis>...</analysis>
            <command_structure>...</command_structure>
            <validation>...</validation>
        </thinking>
        <minecraft_command>...</minecraft_command>
        <explanation>...</explanation>
        """,
        required_tags=["thinking", "analysis", "command_structure", "minecraft_command"],
        optional_tags=["validation", "explanation"]
    )

    # Create analyzer with more complex settings
    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model="qwen2.5:14b",
        objective="Teach Minecraft command formatting with reasoning and validation",
        finetuning_strength=FinetuningStrength.MODERATE,
        lora_rank=64,
        pattern_description="Complex multi-tag structure requiring domain knowledge of Minecraft commands and syntax validation"
    )

    # Generate report
    report = analyzer.analyze()
    print(report)
    print()


def example_3_with_dataset():
    """Example 3: Analyze existing dataset"""
    print("=" * 80)
    print("EXAMPLE 3: Analyze Existing Dataset")
    print("=" * 80)
    print()

    # Create a sample dataset file for demonstration
    import json
    import tempfile

    # Create sample data
    sample_data = []
    for i in range(150):
        sample_data.append({
            "conversations": [
                {
                    "from": "human",
                    "value": f"What is {i} + {i}?"
                },
                {
                    "from": "gpt",
                    "value": f"<thinking>I need to add {i} + {i}</thinking><answer>{i + i}</answer>"
                }
            ]
        })

    # Add some duplicates to demonstrate quality analysis
    sample_data.extend(sample_data[:10])

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in sample_data:
            f.write(json.dumps(item) + '\n')
        dataset_path = f.name

    try:
        # Define pattern
        pattern = XMLPattern(
            schema="<thinking>...</thinking><answer>...</answer>",
            required_tags=["thinking", "answer"]
        )

        # Create analyzer
        analyzer = DatasetSizeAnalyzer(
            xml_pattern=pattern,
            base_model="qwen2.5:7b",
            objective="Teach model to show reasoning before answering math questions",
            finetuning_strength=FinetuningStrength.MODERATE
        )

        # Analyze with dataset
        report = analyzer.analyze(dataset_path=dataset_path)
        print(report)
        print()

    finally:
        # Clean up temporary file
        Path(dataset_path).unlink()


def example_4_model_comparison():
    """Example 4: Compare requirements for different model sizes"""
    print("=" * 80)
    print("EXAMPLE 4: Model Size Comparison")
    print("=" * 80)
    print()

    pattern = XMLPattern(
        schema="<thinking>...</thinking><answer>...</answer>",
        required_tags=["thinking", "answer"]
    )

    models = ["qwen2.5:1b", "qwen2.5:7b", "qwen2.5:14b", "qwen2.5:32b", "qwen2.5:70b"]

    print("Comparing dataset size requirements for different model sizes:")
    print()
    print(f"{'Model':<20} {'Min':<10} {'Optimal':<10} {'Max':<10} {'Diminishing':<15}")
    print("-" * 70)

    for model in models:
        analyzer = DatasetSizeAnalyzer(
            xml_pattern=pattern,
            base_model=model,
            objective="Simple reasoning pattern"
        )

        report = analyzer.analyze()
        estimates = report.size_estimates

        print(f"{model:<20} {estimates.minimum:<10} {estimates.optimal:<10} {estimates.maximum:<10} {estimates.diminishing_returns_threshold:<15}")

    print()


def example_5_strength_comparison():
    """Example 5: Compare requirements for different fine-tuning strengths"""
    print("=" * 80)
    print("EXAMPLE 5: Fine-tuning Strength Comparison")
    print("=" * 80)
    print()

    pattern = XMLPattern(
        schema="<thinking>...</thinking><answer>...</answer>",
        required_tags=["thinking", "answer"]
    )

    strengths = [FinetuningStrength.LIGHT, FinetuningStrength.MODERATE, FinetuningStrength.HEAVY]

    print("Comparing dataset size requirements for different fine-tuning strengths:")
    print()
    print(f"{'Strength':<20} {'Min':<10} {'Optimal':<10} {'Max':<10} {'Diminishing':<15}")
    print("-" * 70)

    for strength in strengths:
        analyzer = DatasetSizeAnalyzer(
            xml_pattern=pattern,
            base_model="qwen2.5:7b",
            objective="Simple reasoning pattern",
            finetuning_strength=strength
        )

        report = analyzer.analyze()
        estimates = report.size_estimates

        print(f"{strength.value:<20} {estimates.minimum:<10} {estimates.optimal:<10} {estimates.maximum:<10} {estimates.diminishing_returns_threshold:<15}")

    print()


def example_6_json_output():
    """Example 6: JSON output format"""
    print("=" * 80)
    print("EXAMPLE 6: JSON Output Format")
    print("=" * 80)
    print()

    pattern = XMLPattern(
        schema="<thinking>...</thinking><answer>...</answer>",
        required_tags=["thinking", "answer"]
    )

    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model="qwen2.5:7b",
        objective="Simple reasoning pattern"
    )

    report = analyzer.analyze()

    # Convert to JSON
    import json
    json_output = json.dumps(report.to_dict(), indent=2)
    print(json_output)
    print()


def main():
    """Run all examples"""
    print()
    print("=" * 80)
    print("DATASET SIZE ANALYZER EXAMPLES")
    print("=" * 80)
    print()

    # Run examples
    example_1_simple_pattern()
    example_2_complex_pattern()
    example_3_with_dataset()
    example_4_model_comparison()
    example_5_strength_comparison()
    example_6_json_output()

    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
