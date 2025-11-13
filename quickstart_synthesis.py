#!/usr/bin/env python3
"""
Quick Start Script for Data Synthesis Module

This script demonstrates the most common use case: generating Minecraft
assistant training data using local Ollama.

Prerequisites:
1. Install dependencies: pip install -r requirements.txt
2. Install and start Ollama: ollama serve
3. Pull a model: ollama pull llama2
"""

from core.synthesis import (
    OllamaProvider,
    DataSynthesizer,
    GenerationConfig,
    XMLPattern,
    save_dataset
)


def main():
    print("\n" + "="*70)
    print("Data Synthesis Module - Quick Start")
    print("="*70)

    # Step 1: Define XML pattern for validation
    print("\n[1/5] Defining XML pattern...")
    pattern = XMLPattern(
        schema="",
        required_tags=["think", "command", "speak"],
        optional_tags=[]
    )
    print("✓ Pattern defined: <think>, <command>, <speak>")

    # Step 2: Initialize AI provider (Ollama)
    print("\n[2/5] Connecting to Ollama...")
    provider = OllamaProvider(
        model="llama2",
        base_url="http://localhost:11434"
    )

    # Validate connection
    if not provider.validate_connection():
        print("❌ Error: Cannot connect to Ollama")
        print("\nPlease ensure:")
        print("  1. Ollama is installed: https://ollama.ai")
        print("  2. Ollama is running: ollama serve")
        print("  3. Model is pulled: ollama pull llama2")
        return

    print("✓ Connected to Ollama")

    # Step 3: Configure generation settings
    print("\n[3/5] Configuring generation settings...")
    config = GenerationConfig(
        temperature=0.8,        # Creativity level (0.0-1.0)
        max_tokens=512,         # Max length of generated text
        retry_attempts=3,       # Retry if validation fails
        rate_limit_delay=0.5    # Delay between API calls (seconds)
    )
    print("✓ Configuration set")

    # Step 4: Create synthesizer
    print("\n[4/5] Initializing DataSynthesizer...")
    synthesizer = DataSynthesizer(
        provider=provider,
        xml_pattern=pattern,
        config=config
    )
    print("✓ DataSynthesizer ready")

    # Step 5: Generate training examples
    print("\n[5/5] Generating training examples...")
    print("This may take a few minutes...\n")

    # Define what we want to generate
    objectives = [
        "Help the player find and mine diamonds efficiently at the correct Y-level",
        "Build a simple wooden house for protection from monsters",
        "Defend the player from hostile mobs effectively",
        "Gather wood resources from trees",
        "Navigate to specific coordinates in the world"
    ]

    inputs = [
        "What should I do to get diamonds?",
        "Can you build me a shelter?",
        "There are zombies attacking!",
        "I need wood for crafting",
        "Take me to coordinates 100, 64, 200"
    ]

    # Generate batch of examples
    examples = synthesizer.generate_batch(
        objectives=objectives,
        inputs=inputs,
        show_progress=True
    )

    print(f"\n✓ Successfully generated {len(examples)} examples")

    # Display first example
    if examples:
        print("\n" + "-"*70)
        print("Example Output:")
        print("-"*70)
        print(f"Input:  {examples[0]['input']}")
        print(f"Output: {examples[0]['output']}")
        print("-"*70)

    # Save in different formats
    print("\nSaving datasets...")
    save_dataset(examples, "minecraft_sharegpt.json", format_type="sharegpt")
    save_dataset(examples, "minecraft_alpaca.json", format_type="alpaca")
    save_dataset(examples, "minecraft_raw.json", format_type="raw")

    print("\n✓ Datasets saved:")
    print("  • minecraft_sharegpt.json (ShareGPT format)")
    print("  • minecraft_alpaca.json (Alpaca format)")
    print("  • minecraft_raw.json (Raw format)")

    # Display statistics
    stats = synthesizer.get_stats()
    print("\n" + "="*70)
    print("Statistics:")
    print("="*70)
    print(f"  Total examples generated: {stats['total_generated']}")
    print(f"  API requests made:        {stats['provider_stats']['request_count']}")
    print("="*70)

    print("\n✓ Done! You can now use these datasets for training.")
    print("\nNext steps:")
    print("  1. Review the generated files")
    print("  2. Adjust temperature/config for different results")
    print("  3. Add more objectives and inputs")
    print("  4. Try different AI providers (Claude, OpenAI)")
    print("\nSee SYNTHESIS_README.md for detailed documentation.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nFor help, see SYNTHESIS_README.md")
