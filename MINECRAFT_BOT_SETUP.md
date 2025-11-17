# Minecraft Chatbot Training Setup

This guide will help you set up and train a Minecraft chatbot using Qwen2.5:14b-instruct with structured XML output patterns.

## Overview

The Minecraft chatbot is trained to respond using a specific XML structure:
- `<thinking>` - Internal reasoning about scenarios and which commands to use
- `<command>` - Minecraft console commands to execute (rigorously limited to valid Minecraft commands)
- `<speak>` - Player-facing chat responses

## Prerequisites

1. **Ollama installed and running**
   ```bash
   # Install Ollama (Linux)
   curl -fsSL https://ollama.com/install.sh | sh

   # Or download from: https://ollama.com/download
   ```

2. **Pull the Qwen2.5:14b-instruct model**
   ```bash
   ollama pull qwen2.5:14b-instruct
   ```

3. **Start Ollama server**
   ```bash
   ollama serve
   # Should start on http://localhost:11434
   ```

4. **Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
model-train/
├── projects/
│   └── minecraft-bot.json          # Project configuration
├── datasets/
│   └── minecraft-bot-training.jsonl # Training examples (20 examples)
├── models/                          # Trained models will be saved here
└── start_minecraft_training.py     # Training starter script
```

## Training Dataset

The training dataset includes 20 diverse examples demonstrating:

### Example Scenarios:
1. **Item requests** - Player asks for items (diamond sword, building blocks, etc.)
2. **Environment changes** - Weather, time, gamemode modifications
3. **Player assistance** - Health/food restoration, teleportation, mob removal
4. **Complex tasks** - Multi-command sequences, enchanted items, beacon setup
5. **Emergency responses** - Combat assistance, lava death recovery

### XML Pattern Structure:

```xml
<thinking>
The player needs a diamond sword. I should use the /give command
to provide them with a diamond sword. This is a straightforward
item request that can be fulfilled with a single command.
</thinking>

<command>
/give @p diamond_sword 1
</command>

<speak>
Here's your diamond sword! Use it wisely in your adventures.
</speak>
```

### Valid Minecraft Commands

The `<command>` tag is rigorously constrained to only valid Minecraft commands:

**Item Management:**
- `/give <player> <item> [amount]` - Give items to players
- `/clear [player]` - Clear inventory

**World Modification:**
- `/setblock <x> <y> <z> <block>` - Set a single block
- `/fill <x1> <y1> <z1> <x2> <y2> <z2> <block>` - Fill area with blocks

**Player Management:**
- `/tp <target> <x> <y> <z>` - Teleport players
- `/gamemode <mode> [player]` - Change game mode
- `/effect give <player> <effect> [duration] [amplifier]` - Apply effects
- `/xp add <player> <amount>` - Give experience

**Entity Management:**
- `/summon <entity> [x] [y] [z]` - Summon entities
- `/kill <target>` - Kill entities

**Environment:**
- `/time set <value>` - Set time of day
- `/weather <clear|rain|thunder>` - Set weather

**Other:**
- `/enchant <player> <enchantment> [level]` - Enchant items
- `/difficulty <level>` - Set difficulty
- `/setworldspawn [x] [y] [z]` - Set world spawn

## Training Configuration

The project is configured in `projects/minecraft-bot.json`:

```json
{
  "name": "minecraft-bot",
  "base_model": "qwen2.5:14b-instruct",
  "ai_config": {
    "provider": "ollama",
    "model": "qwen2.5:14b-instruct",
    "base_url": "http://localhost:11434",
    "temperature": 0.8
  },
  "training_config": {
    "max_seq_length": 2048,
    "lora_r": 16,              # LoRA rank
    "lora_alpha": 32,          # LoRA alpha
    "batch_size": 2,
    "learning_rate": 0.0002,
    "num_train_epochs": 3,
    "optim": "adamw_8bit",     # Memory-efficient optimizer
    "bf16": true               # Use bfloat16 precision
  }
}
```

### Training Parameters Explained:

- **LoRA (Low-Rank Adaptation)**: Efficient fine-tuning method that only trains a small subset of parameters
  - `lora_r: 16` - Rank of the LoRA update matrices (higher = more capacity, more memory)
  - `lora_alpha: 32` - Scaling factor for LoRA updates

- **Batch Size**: 2 - Number of examples processed together (limited by GPU memory)
- **Learning Rate**: 2e-4 - Step size for parameter updates
- **Epochs**: 3 - Number of complete passes through the training data
- **bf16**: Use bfloat16 precision for faster training on modern GPUs

## Quick Start

### Option 1: Using the Starter Script

```bash
# Run the setup verification and get training instructions
python start_minecraft_training.py
```

This script will:
1. Check if Ollama is running
2. Verify the qwen2.5:14b-instruct model is available
3. Verify project files are in place
4. Show training commands and examples

### Option 2: Using the CLI

```bash
# Start the backend server (in one terminal)
python -m backend.main

# Train the model (in another terminal)
model-train train start minecraft-bot \
  --dataset datasets/minecraft-bot-training.jsonl \
  --epochs 3 \
  --lora-rank 16 \
  --batch-size 2

# Monitor training progress
model-train train status <job-id> --watch
```

### Option 3: Using the Web UI

```bash
# Terminal 1: Start backend
python -m backend.main

# Terminal 2: Start frontend
cd frontend
npm run dev

# Open browser to http://localhost:5173
# Navigate to the minecraft-bot project and start training
```

### Option 4: Using the API Directly

```bash
# Start the backend
python -m backend.main &

# Start training via API
curl -X POST http://localhost:8000/api/v1/train \
  -H "Content-Type: application/json" \
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
```

## Training Process

1. **Setup Phase**:
   - Load base model (qwen2.5:14b-instruct)
   - Apply LoRA adapters
   - Load training dataset

2. **Training Phase**:
   - 3 epochs through 20 examples = 60 training steps
   - Logs metrics every 10 steps
   - Saves checkpoint every 500 steps

3. **Export Phase**:
   - Merge LoRA weights with base model
   - Export to GGUF format for Ollama
   - Save to `models/minecraft-bot/`

## Expected Training Time

- **GPU (NVIDIA RTX 3090)**: ~15-20 minutes
- **GPU (NVIDIA RTX 4090)**: ~10-15 minutes
- **CPU**: Not recommended (will take hours)

## Testing the Trained Model

### Load the model in Ollama:

```bash
# Create Modelfile
cat > Modelfile << EOF
FROM ./models/minecraft-bot/model.gguf
TEMPLATE """{{ .System }}

{{ .Prompt }}"""
SYSTEM """You are a Minecraft assistant. Always respond using the XML format:
<thinking>reasoning here</thinking>
<command>minecraft commands here</command>
<speak>player message here</speak>"""
EOF

# Create the model
ollama create minecraft-bot -f Modelfile

# Test it
ollama run minecraft-bot
```

### Example Interactions:

```
User: I need food and I'm hurt
Bot: <thinking>The player is hurt and hungry. I should restore both health and hunger. I'll use instant health effect for immediate healing and saturation for hunger.</thinking>
<command>/effect give @p minecraft:instant_health 1 2
/effect give @p minecraft:saturation 30 255</command>
<speak>You're fully healed and well-fed now! Your health and hunger bars should be completely filled.</speak>

User: Build me a flat area
Bot: <thinking>The player needs a flat building area. I'll use the /fill command to create a large flat platform around the player's position.</thinking>
<command>/fill ~-25 ~ ~-25 ~25 ~ ~25 stone</command>
<speak>I've created a 50x50 stone platform for you to build on!</speak>

User: Give me creative mode
Bot: <thinking>The player wants creative mode for building. I'll use the gamemode command to switch them to creative.</thinking>
<command>/gamemode creative @p</command>
<speak>I've switched you to creative mode! You can now fly and build much faster.</speak>
```

## Expanding the Dataset

To improve the model, add more examples to `datasets/minecraft-bot-training.jsonl`:

### Using the Data Generation Feature:

```python
from core.synthesis import DataSynthesizer, OllamaProvider, GenerationConfig

# Initialize provider
provider = OllamaProvider(model="qwen2.5:14b-instruct")

# Load project
with open("projects/minecraft-bot.json") as f:
    project = json.load(f)

# Generate more examples
synthesizer = DataSynthesizer(provider, project)
new_examples = synthesizer.generate(
    num_examples=50,
    config=GenerationConfig(temperature=0.8)
)

# Append to dataset
with open("datasets/minecraft-bot-training.jsonl", "a") as f:
    for example in new_examples:
        f.write(json.dumps(example) + "\n")
```

## Troubleshooting

### Issue: Ollama connection refused
```
✗ Cannot connect to Ollama: Connection refused
```
**Solution**: Start Ollama with `ollama serve`

### Issue: Model not found
```
⚠ Qwen2.5:14b-instruct not found
```
**Solution**: Pull the model with `ollama pull qwen2.5:14b-instruct`

### Issue: CUDA out of memory
```
RuntimeError: CUDA out of memory
```
**Solutions**:
- Reduce batch_size to 1
- Reduce max_seq_length to 1024
- Use gradient_accumulation_steps to simulate larger batches

### Issue: Model outputs wrong format
**Solution**: Train for more epochs or add more diverse examples to the dataset

## Advanced Configuration

### Custom Training Parameters:

Edit `projects/minecraft-bot.json` to adjust:

```json
"training_config": {
  "lora_r": 32,              // Increase for more capacity
  "num_train_epochs": 5,     // Train longer
  "learning_rate": 0.0001,   // Lower for more stable training
  "warmup_steps": 100        // Gradual learning rate warmup
}
```

### Custom XML Patterns:

Add or modify patterns in the project config:

```json
"xml_patterns": [
  {
    "tag_name": "thinking",
    "description": "Internal reasoning",
    "constraints": "Must analyze scenario",
    "required": true
  },
  {
    "tag_name": "command",
    "description": "Minecraft commands",
    "constraints": "Valid MC commands only",
    "required": true
  },
  {
    "tag_name": "speak",
    "description": "Player message",
    "constraints": "Friendly and helpful",
    "required": true
  }
]
```

## Next Steps

1. **Generate more training data**: Use the synthesis module to create 100-500 more examples
2. **Train longer**: Increase epochs to 5-10 for better performance
3. **Fine-tune parameters**: Experiment with LoRA rank, learning rate, and batch size
4. **Test extensively**: Try edge cases and unusual player requests
5. **Deploy**: Integrate with your Minecraft server's chat system

## Resources

- [Ollama Documentation](https://ollama.com/docs)
- [Qwen2.5 Model Card](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [Minecraft Commands Reference](https://minecraft.wiki/w/Commands)

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [FAQ.md](FAQ.md)
- Open an issue on GitHub
