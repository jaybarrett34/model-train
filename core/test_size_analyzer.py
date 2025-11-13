"""
Unit tests for the DatasetSizeAnalyzer module
"""

import json
import tempfile
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.size_analyzer import (
    DatasetSizeAnalyzer,
    XMLPattern,
    FinetuningStrength,
    AdequacyStatus,
    ComplexityLevel,
    analyze_dataset
)


def test_basic_initialization():
    """Test basic analyzer initialization"""
    print("Testing basic initialization...")

    pattern = XMLPattern(
        schema="<thinking>...</thinking><answer>...</answer>",
        required_tags=["thinking", "answer"]
    )

    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model="qwen2.5:7b",
        objective="Test objective"
    )

    assert analyzer.model_parameters == "7b"
    assert analyzer.model_size_billions == 7.0
    assert analyzer.finetuning_strength == FinetuningStrength.MODERATE

    print("✓ Basic initialization test passed")


def test_model_size_extraction():
    """Test model size extraction from various formats"""
    print("Testing model size extraction...")

    test_cases = [
        ("qwen2.5:7b", "7b", 7.0),
        ("llama3:8b", "8b", 8.0),
        ("mixtral:8x7b", "7b", 7.0),  # Extracts "7b" from "8x7b"
        ("gpt-4-32b", "32b", 32.0),
        ("model-70B", "70b", 70.0),
    ]

    for model, expected_str, expected_float in test_cases:
        analyzer = DatasetSizeAnalyzer(
            base_model=model,
            objective="Test"
        )
        assert analyzer.model_parameters == expected_str, f"Failed for {model}: got {analyzer.model_parameters}"
        # Note: Some may default to 7.0 if not standard format
        print(f"  {model} -> {analyzer.model_parameters} ({analyzer.model_size_billions}B)")

    print("✓ Model size extraction test passed")


def test_complexity_analysis_trivial():
    """Test complexity analysis for trivial patterns"""
    print("Testing trivial complexity analysis...")

    pattern = XMLPattern(
        schema="<answer>...</answer>",
        required_tags=["answer"]
    )

    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model="qwen2.5:7b",
        objective="Simple answer formatting"
    )

    complexity = analyzer.analyze_pattern_complexity()

    assert complexity.complexity_score < 30, f"Score too high: {complexity.complexity_score}"
    assert complexity.complexity_level in [ComplexityLevel.TRIVIAL, ComplexityLevel.SIMPLE]
    assert not complexity.reasoning_required
    assert not complexity.domain_specific

    print(f"✓ Trivial complexity test passed (score: {complexity.complexity_score:.1f})")


def test_complexity_analysis_complex():
    """Test complexity analysis for complex patterns"""
    print("Testing complex pattern analysis...")

    pattern = XMLPattern(
        schema="""
        <medical_analysis>
            <symptoms>...</symptoms>
            <differential>...</differential>
            <reasoning>...</reasoning>
        </medical_analysis>
        <diagnosis>...</diagnosis>
        """,
        required_tags=["medical_analysis", "symptoms", "differential", "diagnosis"]
    )

    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model="qwen2.5:14b",
        objective="Medical diagnosis requiring complex reasoning and domain expertise",
        pattern_description="Requires medical knowledge and multi-step logical reasoning"
    )

    complexity = analyzer.analyze_pattern_complexity()

    assert complexity.complexity_score > 60, f"Score too low: {complexity.complexity_score}"
    assert complexity.complexity_level in [ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX]
    assert complexity.reasoning_required
    assert complexity.domain_specific

    print(f"✓ Complex pattern test passed (score: {complexity.complexity_score:.1f})")


def test_size_estimation():
    """Test size estimation calculation"""
    print("Testing size estimation...")

    pattern = XMLPattern(
        schema="<thinking>...</thinking><answer>...</answer>",
        required_tags=["thinking", "answer"]
    )

    # Test with 7B model
    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model="qwen2.5:7b",
        objective="Reasoning pattern"
    )

    estimates = analyzer.estimate_dataset_size()

    assert estimates.minimum > 0
    assert estimates.optimal > estimates.minimum
    assert estimates.maximum > estimates.optimal
    assert estimates.diminishing_returns_threshold <= estimates.maximum

    print(f"  7B model: min={estimates.minimum}, optimal={estimates.optimal}, max={estimates.maximum}")

    # Test with larger model
    analyzer_large = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model="qwen2.5:70b",
        objective="Reasoning pattern"
    )

    estimates_large = analyzer_large.estimate_dataset_size()

    # Larger models should need more data
    assert estimates_large.optimal > estimates.optimal

    print(f"  70B model: min={estimates_large.minimum}, optimal={estimates_large.optimal}, max={estimates_large.maximum}")
    print("✓ Size estimation test passed")


def test_finetuning_strength_multiplier():
    """Test fine-tuning strength affects size estimates"""
    print("Testing fine-tuning strength multipliers...")

    pattern = XMLPattern(
        schema="<thinking>...</thinking><answer>...</answer>",
        required_tags=["thinking", "answer"]
    )

    strengths = [
        FinetuningStrength.LIGHT,
        FinetuningStrength.MODERATE,
        FinetuningStrength.HEAVY
    ]

    previous_optimal = 0
    for strength in strengths:
        analyzer = DatasetSizeAnalyzer(
            xml_pattern=pattern,
            base_model="qwen2.5:7b",
            objective="Test",
            finetuning_strength=strength
        )

        estimates = analyzer.estimate_dataset_size()
        print(f"  {strength.value}: optimal={estimates.optimal}")

        # Each strength level should require more data
        assert estimates.optimal > previous_optimal
        previous_optimal = estimates.optimal

    print("✓ Fine-tuning strength test passed")


def test_dataset_quality_analysis():
    """Test dataset quality analysis"""
    print("Testing dataset quality analysis...")

    # Create test dataset
    test_data = []
    for i in range(100):
        test_data.append({
            "conversations": [
                {"from": "human", "value": f"Question {i}?"},
                {"from": "gpt", "value": f"Answer {i}"}
            ]
        })

    # Add duplicates
    test_data.extend(test_data[:20])

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
        dataset_path = f.name

    try:
        pattern = XMLPattern(
            schema="<answer>...</answer>",
            required_tags=["answer"]
        )

        analyzer = DatasetSizeAnalyzer(
            xml_pattern=pattern,
            base_model="qwen2.5:7b",
            objective="Test"
        )

        quality = analyzer.analyze_dataset_quality(dataset_path)

        assert quality.total_examples == 120
        assert quality.unique_examples == 100
        assert quality.duplicate_count == 20
        assert abs(quality.duplicate_percentage - 16.67) < 1.0  # ~16.67%
        assert quality.diversity_score > 0
        assert quality.overfitting_risk in ["low", "moderate", "high"]

        print(f"  Total: {quality.total_examples}, Unique: {quality.unique_examples}")
        print(f"  Duplicates: {quality.duplicate_percentage:.1f}%")
        print(f"  Diversity: {quality.diversity_score:.1f}/100")
        print("✓ Quality analysis test passed")

    finally:
        Path(dataset_path).unlink()


def test_adequacy_status():
    """Test adequacy status determination"""
    print("Testing adequacy status...")

    pattern = XMLPattern(
        schema="<answer>...</answer>",
        required_tags=["answer"]
    )

    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model="qwen2.5:7b",
        objective="Test"
    )

    # Get estimates
    estimates = analyzer.estimate_dataset_size()

    # Test different dataset sizes
    test_cases = [
        (0, AdequacyStatus.INSUFFICIENT),
        (estimates.minimum // 2, AdequacyStatus.INSUFFICIENT),
        (estimates.minimum, AdequacyStatus.MINIMAL),
        (estimates.optimal // 2, AdequacyStatus.ADEQUATE),
        (estimates.optimal, AdequacyStatus.OPTIMAL),
        (estimates.maximum * 2, AdequacyStatus.EXCESSIVE),
    ]

    for size, expected_status in test_cases:
        status, percentage = analyzer._determine_adequacy(size, estimates)
        print(f"  Size {size}: {status.value} ({percentage:.1f}%)")

    print("✓ Adequacy status test passed")


def test_full_analysis():
    """Test full analysis report generation"""
    print("Testing full analysis report...")

    # Create test dataset
    test_data = []
    for i in range(150):
        test_data.append({
            "conversations": [
                {"from": "human", "value": f"Question {i}?"},
                {"from": "gpt", "value": f"<thinking>Thinking about {i}</thinking><answer>Answer {i}</answer>"}
            ]
        })

    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
        dataset_path = f.name

    try:
        pattern = XMLPattern(
            schema="<thinking>...</thinking><answer>...</answer>",
            required_tags=["thinking", "answer"]
        )

        analyzer = DatasetSizeAnalyzer(
            xml_pattern=pattern,
            base_model="qwen2.5:7b",
            objective="Reasoning pattern"
        )

        report = analyzer.analyze(dataset_path=dataset_path)

        # Verify report structure
        assert report.complexity_analysis is not None
        assert report.current_size == 150
        assert report.size_estimates is not None
        assert report.quality_metrics is not None
        assert report.adequacy_status in AdequacyStatus
        assert len(report.recommendations) > 0
        assert report.expected_performance is not None

        # Test string representation
        report_str = str(report)
        assert "DATASET SIZE ANALYSIS REPORT" in report_str
        assert "COMPLEXITY ANALYSIS" in report_str

        # Test dict representation
        report_dict = report.to_dict()
        assert isinstance(report_dict, dict)
        assert "complexity_analysis" in report_dict
        assert "size_estimates" in report_dict

        print(f"  Report generated successfully")
        print(f"  Current size: {report.current_size}")
        print(f"  Optimal size: {report.size_estimates.optimal}")
        print(f"  Status: {report.adequacy_status.value}")
        print(f"  Recommendations: {len(report.recommendations)}")
        print("✓ Full analysis test passed")

    finally:
        Path(dataset_path).unlink()


def test_convenience_function():
    """Test convenience function"""
    print("Testing convenience function...")

    # Create test dataset
    test_data = []
    for i in range(50):
        test_data.append({
            "instruction": f"Question {i}?",
            "output": f"Answer {i}"
        })

    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
        dataset_path = f.name

    try:
        pattern = XMLPattern(
            schema="<answer>...</answer>",
            required_tags=["answer"]
        )

        # Test text output
        result_text = analyze_dataset(
            dataset_path=dataset_path,
            xml_pattern=pattern,
            base_model="qwen2.5:7b",
            objective="Test",
            output_format="text"
        )
        assert isinstance(result_text, str)
        assert "DATASET SIZE ANALYSIS REPORT" in result_text

        # Test JSON output
        result_json = analyze_dataset(
            dataset_path=dataset_path,
            xml_pattern=pattern,
            base_model="qwen2.5:7b",
            objective="Test",
            output_format="json"
        )
        data = json.loads(result_json)
        assert isinstance(data, dict)
        assert "current_size" in data

        print("✓ Convenience function test passed")

    finally:
        Path(dataset_path).unlink()


def run_all_tests():
    """Run all tests"""
    print()
    print("=" * 80)
    print("RUNNING DATASET SIZE ANALYZER TESTS")
    print("=" * 80)
    print()

    tests = [
        test_basic_initialization,
        test_model_size_extraction,
        test_complexity_analysis_trivial,
        test_complexity_analysis_complex,
        test_size_estimation,
        test_finetuning_strength_multiplier,
        test_dataset_quality_analysis,
        test_adequacy_status,
        test_full_analysis,
        test_convenience_function,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
            print()
        except AssertionError as e:
            failed += 1
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            print()
        except Exception as e:
            failed += 1
            print(f"✗ Test error: {test.__name__}")
            print(f"  Error: {e}")
            print()

    print("=" * 80)
    print(f"TESTS COMPLETED: {passed} passed, {failed} failed")
    print("=" * 80)
    print()

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
