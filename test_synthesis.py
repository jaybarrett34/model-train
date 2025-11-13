#!/usr/bin/env python3
"""
Test script for the Data Synthesis Module

This script runs basic tests to ensure the module is working correctly.
"""

import sys


def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from core.synthesis import (
            GenerationMode,
            GenerationConfig,
            XMLPattern,
            ValidationError,
            AIProviderError,
            AIProvider,
            OllamaProvider,
            ClaudeProvider,
            OpenAIProvider,
            XMLValidator,
            DataSynthesizer,
            to_sharegpt_format,
            to_alpaca_format,
            save_dataset,
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_xml_validator():
    """Test XML validation"""
    print("\nTesting XML validator...")
    from core.synthesis import XMLValidator, XMLPattern

    pattern = XMLPattern(
        schema="",
        required_tags=["think", "command"],
        optional_tags=["speak"]
    )

    # Test valid XML
    valid_text = "<think>Test</think><command>test command</command>"
    is_valid, error = XMLValidator.validate_xml_structure(valid_text, pattern)
    if is_valid:
        print("✓ Valid XML recognized correctly")
    else:
        print(f"❌ Valid XML rejected: {error}")
        return False

    # Test invalid XML (missing required tag)
    invalid_text = "<think>Test</think>"
    is_valid, error = XMLValidator.validate_xml_structure(invalid_text, pattern)
    if not is_valid:
        print("✓ Invalid XML detected correctly")
    else:
        print("❌ Invalid XML not detected")
        return False

    # Test XML extraction
    text_with_tags = "<think>Some reasoning here</think><command>/tp</command>"
    content = XMLValidator.extract_xml_content(text_with_tags, "think")
    if content == "Some reasoning here":
        print("✓ XML extraction working")
    else:
        print(f"❌ XML extraction failed: got '{content}'")
        return False

    return True


def test_config():
    """Test configuration objects"""
    print("\nTesting configuration...")
    from core.synthesis import GenerationConfig, GenerationMode, XMLPattern

    # Test GenerationConfig
    config = GenerationConfig(
        mode=GenerationMode.PSEUDORANDOM,
        temperature=0.8,
        max_tokens=1024
    )
    if config.temperature == 0.8 and config.mode == GenerationMode.PSEUDORANDOM:
        print("✓ GenerationConfig working")
    else:
        print("❌ GenerationConfig failed")
        return False

    # Test XMLPattern
    pattern = XMLPattern(
        schema="test",
        required_tags=["tag1", "tag2"]
    )
    if pattern.required_tags == ["tag1", "tag2"] and pattern.optional_tags == []:
        print("✓ XMLPattern working")
    else:
        print("❌ XMLPattern failed")
        return False

    return True


def test_format_conversion():
    """Test format conversion functions"""
    print("\nTesting format conversion...")
    from core.synthesis import to_sharegpt_format, to_alpaca_format

    test_examples = [
        {
            "input": "Test input",
            "output": "Test output",
            "metadata": {"mode": "test"}
        }
    ]

    # Test ShareGPT format
    sharegpt = to_sharegpt_format(test_examples)
    if (
        len(sharegpt) == 1 and
        "conversations" in sharegpt[0] and
        sharegpt[0]["conversations"][0]["from"] == "human" and
        sharegpt[0]["conversations"][1]["from"] == "gpt"
    ):
        print("✓ ShareGPT format conversion working")
    else:
        print("❌ ShareGPT format conversion failed")
        return False

    # Test Alpaca format
    alpaca = to_alpaca_format(test_examples)
    if (
        len(alpaca) == 1 and
        "instruction" in alpaca[0] and
        "input" in alpaca[0] and
        "output" in alpaca[0]
    ):
        print("✓ Alpaca format conversion working")
    else:
        print("❌ Alpaca format conversion failed")
        return False

    return True


def test_provider_initialization():
    """Test provider initialization (without API calls)"""
    print("\nTesting provider initialization...")
    from core.synthesis import OllamaProvider, ClaudeProvider, OpenAIProvider

    # Test Ollama
    try:
        ollama = OllamaProvider(model="llama2")
        print("✓ OllamaProvider initialized")
    except Exception as e:
        print(f"❌ OllamaProvider initialization failed: {e}")
        return False

    # Test Claude
    try:
        claude = ClaudeProvider(api_key="test-key")
        print("✓ ClaudeProvider initialized")
    except Exception as e:
        print(f"❌ ClaudeProvider initialization failed: {e}")
        return False

    # Test OpenAI
    try:
        openai = OpenAIProvider(api_key="test-key")
        print("✓ OpenAIProvider initialized")
    except Exception as e:
        print(f"❌ OpenAIProvider initialization failed: {e}")
        return False

    return True


def test_synthesizer_initialization():
    """Test DataSynthesizer initialization"""
    print("\nTesting DataSynthesizer initialization...")
    from core.synthesis import (
        DataSynthesizer,
        OllamaProvider,
        XMLPattern,
        GenerationConfig
    )

    try:
        provider = OllamaProvider(model="llama2")
        pattern = XMLPattern(schema="", required_tags=["test"])
        config = GenerationConfig()

        synthesizer = DataSynthesizer(
            provider=provider,
            xml_pattern=pattern,
            config=config
        )
        print("✓ DataSynthesizer initialized")
        return True
    except Exception as e:
        print(f"❌ DataSynthesizer initialization failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("="*70)
    print("Data Synthesis Module - Test Suite")
    print("="*70)

    tests = [
        ("Imports", test_imports),
        ("XML Validator", test_xml_validator),
        ("Configuration", test_config),
        ("Format Conversion", test_format_conversion),
        ("Provider Initialization", test_provider_initialization),
        ("DataSynthesizer Initialization", test_synthesizer_initialization),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(1)
