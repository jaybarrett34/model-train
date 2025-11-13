#!/usr/bin/env python3
"""
Comprehensive examples demonstrating the Data Synthesis Module

This script shows various use cases including:
1. Minecraft assistant training data generation
2. Different generation modes (pseudorandom, patterned, forced)
3. Multiple AI providers
4. Batch generation
5. Different output formats
"""

import os
import json
from core.synthesis import (
    OllamaProvider,
    ClaudeProvider,
    OpenAIProvider,
    DataSynthesizer,
    GenerationMode,
    GenerationConfig,
    XMLPattern,
    save_dataset,
    to_sharegpt_format,
    to_alpaca_format
)


# ============================================================================
# Example 1: Minecraft Assistant with Ollama (Local)
# ============================================================================

def example_minecraft_ollama():
    """Generate Minecraft assistant training data using local Ollama"""
    print("\n" + "="*70)
    print("Example 1: Minecraft Assistant with Ollama")
    print("="*70)

    # Define XML pattern for Minecraft responses
    minecraft_pattern = XMLPattern(
        schema="",
        required_tags=["think", "command", "speak"],
        optional_tags=[]
    )

    # Initialize Ollama provider
    provider = OllamaProvider(model="llama2", base_url="http://localhost:11434")

    # Check connection
    if not provider.validate_connection():
        print("❌ Ollama is not running. Start it with: ollama serve")
        return

    print("✓ Connected to Ollama")

    # Create synthesizer with pseudorandom mode
    config = GenerationConfig(
        mode=GenerationMode.PSEUDORANDOM,
        temperature=0.8,
        max_tokens=512,
        retry_attempts=3,
        batch_size=5
    )

    synthesizer = DataSynthesizer(
        provider=provider,
        xml_pattern=minecraft_pattern,
        config=config
    )

    # Generate single example
    print("\n→ Generating single example...")
    example = synthesizer.generate_single(
        objective="Help the player mine diamonds efficiently",
        input_text="What should I do to get diamonds?"
    )

    print(f"\nInput: {example['input']}")
    print(f"Output: {example['output']}")

    # Generate batch
    print("\n→ Generating batch of examples...")
    objectives = [
        "Help the player find diamonds at the correct Y-level",
        "Build a simple wooden house for protection",
        "Fight hostile mobs effectively",
        "Gather wood resources efficiently",
        "Navigate to specific coordinates"
    ]

    inputs = [
        "What should I do to get diamonds?",
        "Can you build me a shelter?",
        "There are zombies attacking!",
        "I need wood for crafting",
        "Take me to coordinates 100, 64, 200"
    ]

    examples = synthesizer.generate_batch(
        objectives=objectives,
        inputs=inputs,
        show_progress=True
    )

    print(f"\n✓ Generated {len(examples)} examples")

    # Save in different formats
    save_dataset(examples, "minecraft_sharegpt.json", format_type="sharegpt")
    save_dataset(examples, "minecraft_alpaca.json", format_type="alpaca")
    save_dataset(examples, "minecraft_raw.json", format_type="raw")

    print("\n✓ Saved datasets:")
    print("  - minecraft_sharegpt.json (ShareGPT format)")
    print("  - minecraft_alpaca.json (Alpaca format)")
    print("  - minecraft_raw.json (Raw format)")

    # Print stats
    stats = synthesizer.get_stats()
    print(f"\n📊 Statistics:")
    print(f"  Total generated: {stats['total_generated']}")
    print(f"  API requests: {stats['provider_stats']['request_count']}")


# ============================================================================
# Example 2: Patterned Generation with Templates
# ============================================================================

def example_patterned_generation():
    """Demonstrate patterned generation mode with templates"""
    print("\n" + "="*70)
    print("Example 2: Patterned Generation with Templates")
    print("="*70)

    provider = OllamaProvider(model="llama2")

    if not provider.validate_connection():
        print("❌ Ollama is not running")
        return

    pattern = XMLPattern(
        required_tags=["think", "action"],
        optional_tags=["speak"]
    )

    config = GenerationConfig(
        mode=GenerationMode.PATTERNED,
        temperature=0.7
    )

    synthesizer = DataSynthesizer(
        provider=provider,
        xml_pattern=pattern,
        config=config
    )

    # Define template
    template = """
<think>The player wants to [FILL: action description]</think>
<action>[FILL: specific action]</action>
<speak>[FILL: response to player]</speak>
"""

    print("\n→ Generating with template...")
    example = synthesizer.generate_single(
        objective="Help player craft a pickaxe",
        input_text="How do I make a pickaxe?",
        mode=GenerationMode.PATTERNED,
        template=template
    )

    print(f"\nGenerated output:\n{example['output']}")


# ============================================================================
# Example 3: Forced Mode with Locked Parts
# ============================================================================

def example_forced_generation():
    """Demonstrate forced mode with locked parts"""
    print("\n" + "="*70)
    print("Example 3: Forced Generation with Locked Parts")
    print("="*70)

    provider = OllamaProvider(model="llama2")

    if not provider.validate_connection():
        print("❌ Ollama is not running")
        return

    pattern = XMLPattern(
        required_tags=["think", "command", "speak"]
    )

    config = GenerationConfig(
        mode=GenerationMode.FORCED,
        temperature=0.9
    )

    synthesizer = DataSynthesizer(
        provider=provider,
        xml_pattern=pattern,
        config=config
    )

    # Define locked parts
    locked_parts = {
        "command": "/tp @p ~ ~-60 ~",
        "location": "diamond level (Y=-59)"
    }

    print("\n→ Generating with locked command...")
    example = synthesizer.generate_single(
        objective="Teleport player to diamond mining level",
        input_text="Take me to diamond level",
        mode=GenerationMode.FORCED,
        locked_parts=locked_parts
    )

    print(f"\nGenerated output:\n{example['output']}")
    print(f"\n✓ Command '/tp @p ~ ~-60 ~' was preserved")


# ============================================================================
# Example 4: Claude Provider (Cloud API)
# ============================================================================

def example_claude_provider():
    """Generate data using Claude API"""
    print("\n" + "="*70)
    print("Example 4: Claude Provider (Anthropic API)")
    print("="*70)

    # Get API key from environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set in environment")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Initialize Claude provider
    provider = ClaudeProvider(
        api_key=api_key,
        model="claude-sonnet-4-5-20250929"
    )

    print("✓ Initialized Claude provider")

    pattern = XMLPattern(
        required_tags=["think", "command", "speak"]
    )

    config = GenerationConfig(
        mode=GenerationMode.PSEUDORANDOM,
        temperature=0.8,
        max_tokens=1024
    )

    synthesizer = DataSynthesizer(
        provider=provider,
        xml_pattern=pattern,
        config=config
    )

    print("\n→ Generating high-quality example with Claude...")
    example = synthesizer.generate_single(
        objective="Create a sophisticated Minecraft assistant response for diamond mining",
        input_text="What should I do to get diamonds?"
    )

    print(f"\nInput: {example['input']}")
    print(f"Output:\n{example['output']}")

    stats = synthesizer.get_stats()
    print(f"\n📊 Tokens used: {stats['provider_stats']['total_tokens']}")


# ============================================================================
# Example 5: OpenAI Provider
# ============================================================================

def example_openai_provider():
    """Generate data using OpenAI API"""
    print("\n" + "="*70)
    print("Example 5: OpenAI Provider")
    print("="*70)

    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set in environment")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        return

    # Initialize OpenAI provider
    provider = OpenAIProvider(
        api_key=api_key,
        model="gpt-4"
    )

    print("✓ Initialized OpenAI provider")

    pattern = XMLPattern(
        required_tags=["think", "command", "speak"]
    )

    config = GenerationConfig(
        mode=GenerationMode.PSEUDORANDOM,
        temperature=0.8
    )

    synthesizer = DataSynthesizer(
        provider=provider,
        xml_pattern=pattern,
        config=config
    )

    print("\n→ Generating example with GPT-4...")
    example = synthesizer.generate_single(
        objective="Generate a Minecraft assistant response",
        input_text="What should I do to get diamonds?"
    )

    print(f"\nInput: {example['input']}")
    print(f"Output:\n{example['output']}")


# ============================================================================
# Example 6: Generate Variations from Pattern Examples
# ============================================================================

def example_pattern_variations():
    """Generate variations based on example patterns"""
    print("\n" + "="*70)
    print("Example 6: Generate Variations from Example Patterns")
    print("="*70)

    provider = OllamaProvider(model="llama2")

    if not provider.validate_connection():
        print("❌ Ollama is not running")
        return

    pattern = XMLPattern(
        required_tags=["think", "command", "speak"]
    )

    config = GenerationConfig(
        mode=GenerationMode.PSEUDORANDOM,
        temperature=0.9,  # Higher temperature for more variation
        rate_limit_delay=1.0
    )

    synthesizer = DataSynthesizer(
        provider=provider,
        xml_pattern=pattern,
        config=config
    )

    # Seed examples to learn from
    seed_examples = [
        {
            "input": "What should I do to get diamonds?",
            "output": "<think>I need to help them mine diamonds at y-level -59</think><command>/tp ~ ~-60 ~</command><speak>Let me take you to diamond level</speak>"
        },
        {
            "input": "Can you build a house?",
            "output": "<think>I should construct a basic shelter using available materials</think><command>/give @p oak_planks 64</command><speak>I'll help you build a wooden house</speak>"
        }
    ]

    print("\n→ Generating 3 variations per pattern...")
    variations = synthesizer.generate_from_pattern_examples(
        examples=seed_examples,
        num_variations=3,
        mode=GenerationMode.PSEUDORANDOM
    )

    print(f"\n✓ Generated {len(variations)} variations")

    # Show first variation
    if variations:
        print(f"\nExample variation:")
        print(f"Input: {variations[0]['input']}")
        print(f"Output: {variations[0]['output']}")

    # Save variations
    save_dataset(variations, "pattern_variations.json", format_type="sharegpt")
    print(f"\n✓ Saved to pattern_variations.json")


# ============================================================================
# Example 7: Format Conversion
# ============================================================================

def example_format_conversion():
    """Demonstrate converting between different formats"""
    print("\n" + "="*70)
    print("Example 7: Format Conversion")
    print("="*70)

    # Sample data
    raw_examples = [
        {
            "input": "What should I do to get diamonds?",
            "output": "<think>I need to help them mine diamonds at y-level -59</think><command>/tp ~ ~-60 ~</command><speak>Let me take you to diamond level</speak>",
            "metadata": {"mode": "pseudorandom", "timestamp": 1234567890}
        },
        {
            "input": "Can you build a house?",
            "output": "<think>I should construct a basic shelter</think><command>/give @p oak_planks 64</command><speak>I'll help you build a wooden house</speak>",
            "metadata": {"mode": "pseudorandom", "timestamp": 1234567891}
        }
    ]

    # Convert to ShareGPT
    sharegpt_data = to_sharegpt_format(raw_examples)
    print("\n→ ShareGPT format:")
    print(json.dumps(sharegpt_data[0], indent=2))

    # Convert to Alpaca
    alpaca_data = to_alpaca_format(
        raw_examples,
        instruction_prefix="You are a Minecraft assistant. "
    )
    print("\n→ Alpaca format:")
    print(json.dumps(alpaca_data[0], indent=2))

    # Save both formats
    save_dataset(raw_examples, "converted_sharegpt.json", format_type="sharegpt")
    save_dataset(raw_examples, "converted_alpaca.json", format_type="alpaca")

    print("\n✓ Saved converted datasets")


# ============================================================================
# Main Menu
# ============================================================================

def main():
    """Run example demonstrations"""
    print("\n" + "="*70)
    print("Data Synthesis Module - Examples")
    print("="*70)

    examples = {
        "1": ("Minecraft with Ollama (Local)", example_minecraft_ollama),
        "2": ("Patterned Generation", example_patterned_generation),
        "3": ("Forced Generation with Locked Parts", example_forced_generation),
        "4": ("Claude Provider (Cloud)", example_claude_provider),
        "5": ("OpenAI Provider (Cloud)", example_openai_provider),
        "6": ("Pattern Variations", example_pattern_variations),
        "7": ("Format Conversion", example_format_conversion),
        "all": ("Run All Examples", None)
    }

    print("\nAvailable examples:")
    for key, (description, _) in examples.items():
        print(f"  {key}. {description}")

    choice = input("\nSelect example (1-7, 'all', or 'q' to quit): ").strip()

    if choice == 'q':
        return

    if choice == 'all':
        for key, (_, func) in examples.items():
            if func:  # Skip the 'all' entry
                try:
                    func()
                except Exception as e:
                    print(f"\n❌ Error in example: {e}")
    elif choice in examples:
        _, func = examples[choice]
        if func:
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
