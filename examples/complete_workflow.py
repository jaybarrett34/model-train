#!/usr/bin/env python3
"""
Complete Workflow Example: Minecraft Assistant Model Training

This example demonstrates the complete workflow from start to finish:
1. Define XML patterns for structured output
2. Create a project with training configuration
3. Generate synthetic training data using AI
4. Analyze dataset size and quality
5. Train the model using Unsloth
6. Export the model in various formats

This is a standalone script that can be run directly.
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.synthesis import (
    DataSynthesizer,
    GenerationConfig,
    GenerationMode,
    XMLPattern,
    OllamaProvider,
    save_dataset
)
from core.xml_engine import XMLPattern as EngineXMLPattern, XMLTag, ConstraintType
from core.size_analyzer import DatasetSizeAnalyzer, FinetuningStrength
from core.training import UnslothTrainer, LoRAConfig, TrainingConfig


def step1_define_xml_patterns():
    """Step 1: Define XML patterns for Minecraft assistant."""
    print("=" * 80)
    print("STEP 1: Defining XML Patterns")
    print("=" * 80)

    # Define XML pattern using xml_engine
    pattern = EngineXMLPattern(
        tags=[
            XMLTag(
                "think",
                constraint_type=ConstraintType.FREE_FORM,
                required=True
            ),
            XMLTag(
                "command",
                constraint_type=ConstraintType.REGEX,
                pattern=r"^/\w+.*",  # Must start with /
                required=True
            ),
            XMLTag(
                "speak",
                constraint_type=ConstraintType.FREE_FORM,
                required=True
            )
        ],
        name="MinecraftAssistantPattern",
        description="Pattern for Minecraft assistant responses with thinking, commands, and speech"
    )

    # Print template
    print("\nXML Template:")
    print(pattern.generate_template())

    # For synthesis, create simpler pattern
    synthesis_pattern = XMLPattern(
        schema="",
        required_tags=["think", "command", "speak"]
    )

    print("\nPattern defined successfully!")
    return synthesis_pattern


def step2_create_project_config():
    """Step 2: Create project configuration."""
    print("\n" + "=" * 80)
    print("STEP 2: Creating Project Configuration")
    print("=" * 80)

    config = {
        "name": "minecraft-assistant",
        "objective": """Train a Minecraft assistant AI that:
        - Understands player requests
        - Shows reasoning in <think> tags
        - Generates valid Minecraft commands in <command> tags
        - Provides helpful responses in <speak> tags""",
        "base_model": "unsloth/llama-2-7b-bnb-4bit",
        "dataset_format": "sharegpt",
        "num_examples": 100,  # Start with 100 examples
        "provider": "ollama",
        "model": "llama2"
    }

    print(f"\nProject: {config['name']}")
    print(f"Objective: {config['objective']}")
    print(f"Base Model: {config['base_model']}")
    print(f"Target Examples: {config['num_examples']}")

    return config


def step3_generate_training_data(pattern, config):
    """Step 3: Generate synthetic training data."""
    print("\n" + "=" * 80)
    print("STEP 3: Generating Synthetic Training Data")
    print("=" * 80)

    # Initialize AI provider
    print("\nInitializing Ollama provider...")
    provider = OllamaProvider(
        model=config['model'],
        base_url="http://localhost:11434"
    )

    # Validate connection
    if not provider.validate_connection():
        print("ERROR: Cannot connect to Ollama. Make sure Ollama is running.")
        print("Start Ollama with: ollama serve")
        sys.exit(1)

    print("✓ Connected to Ollama")

    # Create generation config
    gen_config = GenerationConfig(
        mode=GenerationMode.PSEUDORANDOM,
        temperature=0.8,
        max_tokens=512,
        batch_size=10,
        rate_limit_delay=0.5
    )

    # Initialize synthesizer
    synthesizer = DataSynthesizer(
        provider=provider,
        xml_pattern=pattern,
        config=gen_config
    )

    # Define diverse objectives for Minecraft tasks
    objectives = [
        "Help player find diamonds",
        "Build a house for the player",
        "Defend against hostile mobs",
        "Navigate to specific coordinates",
        "Gather wood resources",
        "Create a farm",
        "Explore a cave",
        "Trade with villagers",
        "Craft tools and weapons",
        "Set up a mine",
    ] * (config['num_examples'] // 10)  # Repeat to reach target count

    objectives = objectives[:config['num_examples']]

    print(f"\nGenerating {len(objectives)} training examples...")
    print("This may take a few minutes...\n")

    start_time = time.time()
    examples = synthesizer.generate_batch(
        objectives=objectives,
        show_progress=True
    )
    elapsed = time.time() - start_time

    print(f"\n✓ Generated {len(examples)} examples in {elapsed:.1f}s")
    print(f"Stats: {synthesizer.get_stats()}")

    # Save dataset
    dataset_dir = Path("./datasets")
    dataset_dir.mkdir(exist_ok=True)

    dataset_path = dataset_dir / f"minecraft_assistant_{len(examples)}ex.json"
    save_dataset(examples, str(dataset_path), format_type=config['dataset_format'])

    print(f"✓ Dataset saved to: {dataset_path}")

    return str(dataset_path), examples


def step4_analyze_dataset(pattern, config, dataset_path):
    """Step 4: Analyze dataset size and quality."""
    print("\n" + "=" * 80)
    print("STEP 4: Analyzing Dataset Size and Quality")
    print("=" * 80)

    # Initialize analyzer
    analyzer = DatasetSizeAnalyzer(
        xml_pattern=pattern,
        base_model=config['base_model'],
        objective=config['objective'],
        finetuning_strength=FinetuningStrength.MODERATE,
        lora_rank=16
    )

    # Perform analysis
    print("\nAnalyzing dataset...")
    report = analyzer.analyze(dataset_path=dataset_path)

    # Print report
    print("\n" + str(report))

    return report


def step5_train_model(config, dataset_path):
    """Step 5: Train the model using Unsloth."""
    print("\n" + "=" * 80)
    print("STEP 5: Training Model with Unsloth")
    print("=" * 80)

    # Create output directory
    output_dir = Path(f"./models/{config['name']}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nOutput directory: {output_dir}")
    print(f"Base model: {config['base_model']}")
    print(f"Dataset: {dataset_path}")

    # Initialize trainer
    print("\nInitializing UnslothTrainer...")
    trainer = UnslothTrainer(
        base_model=config['base_model'],
        dataset_path=dataset_path,
        output_dir=str(output_dir),
        dataset_format=config['dataset_format'],
        max_seq_length=512,
        load_in_4bit=True
    )

    # Create configs
    lora_config = LoRAConfig(
        rank=16,
        alpha=16,
        dropout=0.05,
        use_gradient_checkpointing=True
    )

    training_config = TrainingConfig(
        learning_rate=2e-4,
        batch_size=2,
        gradient_accumulation_steps=4,
        num_epochs=3,
        warmup_steps=10,
        max_seq_length=512,
        logging_steps=1,
        save_steps=50,
        fp16=False,
        bf16=True
    )

    # Setup
    print("\nSetting up model and LoRA adapters...")
    trainer.setup(lora_config=lora_config)

    # Train
    print("\nStarting training...")
    print("This will take several minutes to hours depending on your hardware...\n")

    start_time = time.time()
    trainer.train(
        lora_config=lora_config,
        training_config=training_config
    )
    elapsed = time.time() - start_time

    print(f"\n✓ Training completed in {elapsed:.1f}s ({elapsed/60:.1f} minutes)")

    # Save model
    print("\nSaving trained model...")
    trainer.save_model()
    print("✓ Model saved")

    return trainer, output_dir


def step6_export_model(trainer, config, output_dir):
    """Step 6: Export model in various formats."""
    print("\n" + "=" * 80)
    print("STEP 6: Exporting Model")
    print("=" * 80)

    # Save merged model (LoRA adapters merged into base weights)
    print("\nExporting merged model...")
    merged_path = output_dir / "merged"
    trainer.save_merged_model(str(merged_path))
    print(f"✓ Merged model saved to: {merged_path}")

    # Export to GGUF format for Ollama/llama.cpp
    print("\nExporting to GGUF format...")
    gguf_path = output_dir / f"{config['name']}.gguf"
    try:
        trainer.export_gguf(str(gguf_path), quantization_method="q4_k_m")
        print(f"✓ GGUF model saved to: {gguf_path}")

        # Create Ollama Modelfile
        print("\nCreating Ollama Modelfile...")
        trainer.export_to_ollama(config['name'])
        print(f"✓ Ollama Modelfile created")
        print(f"\nTo use with Ollama, run:")
        print(f"  ollama create {config['name']} -f {output_dir}/Modelfile")
    except Exception as e:
        print(f"⚠ GGUF export failed (this is optional): {e}")

    # Cleanup
    print("\nCleaning up...")
    trainer.cleanup()
    print("✓ Cleanup complete")


def main():
    """Run the complete workflow."""
    print("=" * 80)
    print("COMPLETE WORKFLOW: Minecraft Assistant Model Training")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Define XML patterns")
    print("2. Create project configuration")
    print("3. Generate synthetic training data")
    print("4. Analyze dataset quality")
    print("5. Train the model")
    print("6. Export in multiple formats")
    print("\nPress Ctrl+C to cancel\n")

    try:
        # Step 1: Define patterns
        pattern = step1_define_xml_patterns()

        # Step 2: Create config
        config = step2_create_project_config()

        # Step 3: Generate data
        dataset_path, examples = step3_generate_training_data(pattern, config)

        # Step 4: Analyze dataset
        report = step4_analyze_dataset(pattern, config, dataset_path)

        # Ask user if they want to proceed with training
        print("\n" + "=" * 80)
        response = input("\nDataset ready. Proceed with training? (y/n): ")
        if response.lower() != 'y':
            print("Training cancelled. Dataset saved for later use.")
            return

        # Step 5: Train model
        trainer, output_dir = step5_train_model(config, dataset_path)

        # Step 6: Export model
        step6_export_model(trainer, config, output_dir)

        # Success!
        print("\n" + "=" * 80)
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nYour trained model is ready at: {output_dir}")
        print("\nNext steps:")
        print("1. Test the model with sample inputs")
        print("2. Deploy using the exported formats")
        print("3. Iterate on the dataset if needed")

    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
