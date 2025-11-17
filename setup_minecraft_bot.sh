#!/bin/bash
# Minecraft Bot Setup Script
# This script sets up the Minecraft chatbot project from the example files

set -e

echo "=================================================="
echo "Minecraft Chatbot Setup"
echo "=================================================="
echo ""

# Create directories if they don't exist
echo "Creating directories..."
mkdir -p projects
mkdir -p datasets
mkdir -p models
echo "✓ Directories created"
echo ""

# Copy project configuration
echo "Setting up project configuration..."
if [ -f "projects/minecraft-bot.json" ]; then
    echo "⚠ projects/minecraft-bot.json already exists"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp examples/minecraft-bot/project-config.example projects/minecraft-bot.json
        echo "✓ Project configuration copied"
    else
        echo "○ Keeping existing project configuration"
    fi
else
    cp examples/minecraft-bot/project-config.example projects/minecraft-bot.json
    echo "✓ Project configuration copied"
fi
echo ""

# Copy training data
echo "Setting up training dataset..."
if [ -f "datasets/minecraft-bot-training.jsonl" ]; then
    echo "⚠ datasets/minecraft-bot-training.jsonl already exists"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp examples/minecraft-bot/training-data.example datasets/minecraft-bot-training.jsonl
        echo "✓ Training dataset copied"
    else
        echo "○ Keeping existing training dataset"
    fi
else
    cp examples/minecraft-bot/training-data.example datasets/minecraft-bot-training.jsonl
    echo "✓ Training dataset copied"
fi
echo ""

# Verify setup
echo "Verifying setup..."
python3 start_minecraft_training.py
echo ""

echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh"
echo "2. Pull model: ollama pull qwen2.5:14b-instruct"
echo "3. Start Ollama: ollama serve"
echo "4. Start training: python -m backend.main &"
echo "   Then run: model-train train start minecraft-bot"
echo ""
echo "See MINECRAFT_BOT_SETUP.md for detailed instructions."
