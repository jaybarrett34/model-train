#!/usr/bin/env python3
"""
Minecraft Chatbot Training Starter Script

This script demonstrates how to set up and start training for the Minecraft chatbot
using the qwen2.5:14b-instruct model with the structured XML output pattern.

Prerequisites:
1. Ollama installed and running: ollama serve
2. Qwen2.5:14b-instruct model pulled: ollama pull qwen2.5:14b-instruct
3. Python dependencies installed: pip install -r requirements.txt
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("✓ Ollama is running")
            print(f"  Available models: {len(models)}")

            # Check if qwen2.5:14b-instruct is available
            qwen_available = any('qwen2.5' in m.get('name', '') for m in models)
            if qwen_available:
                print("✓ Qwen2.5 model is available")
            else:
                print("⚠ Qwen2.5:14b-instruct not found. Run: ollama pull qwen2.5:14b-instruct")
                return False
            return True
        else:
            print("✗ Ollama is not responding correctly")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False


def verify_project_setup():
    """Verify that the project structure is set up correctly"""
    print("\nVerifying project setup...")

    project_file = project_root / "projects" / "minecraft-bot.json"
    dataset_file = project_root / "datasets" / "minecraft-bot-training.jsonl"

    if not project_file.exists():
        print(f"✗ Project file not found: {project_file}")
        return False
    print(f"✓ Project file found: {project_file}")

    if not dataset_file.exists():
        print(f"✗ Dataset file not found: {dataset_file}")
        return False
    print(f"✓ Dataset file found: {dataset_file}")

    # Load and verify project config
    with open(project_file, 'r') as f:
        project = json.load(f)

    print(f"\nProject Configuration:")
    print(f"  Name: {project['name']}")
    print(f"  Model: {project['base_model']}")
    print(f"  XML Patterns: {len(project['xml_patterns'])} tags defined")
    for pattern in project['xml_patterns']:
        print(f"    - <{pattern['tag_name']}>: {pattern['description']}")

    # Count training examples
    with open(dataset_file, 'r') as f:
        examples = [json.loads(line) for line in f if line.strip()]
    print(f"\n  Training examples: {len(examples)}")

    return True


def start_training():
    """Start the training process"""
    print("\n" + "="*60)
    print("STARTING MINECRAFT CHATBOT TRAINING")
    print("="*60)

    print("\nTraining Configuration:")
    print("  Base Model: qwen2.5:14b-instruct (via Ollama)")
    print("  Method: LoRA fine-tuning")
    print("  LoRA Rank: 16")
    print("  Epochs: 3")
    print("  Batch Size: 2")
    print("  Learning Rate: 2e-4")
    print("  Max Sequence Length: 2048")
    print("\nXML Output Pattern:")
    print("  <thinking> - Internal reasoning about scenarios and commands")
    print("  <command>  - Minecraft console commands to execute")
    print("  <speak>    - Player-facing chat responses")

    print("\n" + "-"*60)
    print("To start training via the CLI:")
    print("-"*60)
    print("model-train train start minecraft-bot \\")
    print("  --dataset datasets/minecraft-bot-training.jsonl \\")
    print("  --epochs 3 \\")
    print("  --lora-rank 16 \\")
    print("  --batch-size 2")

    print("\n" + "-"*60)
    print("To start training via the API:")
    print("-"*60)
    print("""
# Start the backend server
python -m backend.main &

# Make API request
curl -X POST http://localhost:8000/api/v1/train \\
  -H "Content-Type: application/json" \\
  -d '{
    "project_name": "minecraft-bot",
    "dataset_path": "datasets/minecraft-bot-training.jsonl",
    "training_config": {
      "num_train_epochs": 3,
      "lora_r": 16,
      "batch_size": 2,
      "learning_rate": 0.0002,
      "max_seq_length": 2048
    }
  }'
""")

    print("\n" + "-"*60)
    print("To test the trained model:")
    print("-"*60)
    print("""
# After training completes, test with:
ollama run minecraft-bot-trained

# Example prompt:
User: I need a diamond pickaxe with efficiency
Bot: <thinking>The player needs an enchanted diamond pickaxe...</thinking>
     <command>/give @p diamond_pickaxe{Enchantments:[{id:efficiency,lvl:5}]} 1</command>
     <speak>Here's a diamond pickaxe with Efficiency V! Happy mining!</speak>
""")


def main():
    """Main execution function"""
    print("Minecraft Chatbot Training Setup")
    print("="*60)

    # Check Ollama connection
    print("\nStep 1: Checking Ollama connection...")
    ollama_ok = check_ollama_connection()

    # Verify project setup
    print("\nStep 2: Verifying project structure...")
    project_ok = verify_project_setup()

    if not project_ok:
        print("\n✗ Project setup incomplete. Please check the files.")
        return 1

    # Show training instructions
    start_training()

    if not ollama_ok:
        print("\n⚠ NOTE: Ollama is not running or qwen2.5:14b-instruct is not available.")
        print("   Install Ollama: https://ollama.com/download")
        print("   Pull the model: ollama pull qwen2.5:14b-instruct")
        print("   Start Ollama: ollama serve")
        return 1

    print("\n" + "="*60)
    print("✓ Everything is ready for training!")
    print("="*60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
