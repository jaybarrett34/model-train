# Minecraft Chatbot Example

This directory contains example files for setting up a Minecraft chatbot with structured XML output.

## Files

- `project-config.example` - Project configuration (copy to `../../projects/minecraft-bot.json`)
- `training-data.example` - Sample training data (copy to `../../datasets/minecraft-bot-training.jsonl`)
- `README.md` - This file

## Setup Instructions

1. **Copy the project configuration:**
   ```bash
   cp examples/minecraft-bot/project-config.example projects/minecraft-bot.json
   ```

2. **Copy the training data:**
   ```bash
   cp examples/minecraft-bot/training-data.example datasets/minecraft-bot-training.jsonl
   ```

3. **Install and start Ollama:**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh

   # Pull the model
   ollama pull qwen2.5:14b-instruct

   # Start Ollama server
   ollama serve
   ```

4. **Run the training setup script:**
   ```bash
   python start_minecraft_training.py
   ```

5. **Start training:**
   ```bash
   # Via CLI
   model-train train start minecraft-bot \
     --dataset datasets/minecraft-bot-training.jsonl \
     --epochs 3 \
     --lora-rank 16 \
     --batch-size 2

   # Or via API
   python -m backend.main &
   curl -X POST http://localhost:8000/api/v1/train \
     -H "Content-Type: application/json" \
     -d @examples/minecraft-bot/training-request.json
   ```

## XML Output Format

The bot is trained to respond with this structure:

```xml
<thinking>
Reasoning about what the player needs and which Minecraft
commands would be appropriate to use in this scenario
</thinking>

<command>
/give @p diamond_sword 1
</command>

<speak>
Here's your diamond sword! Use it wisely.
</speak>
```

### Tag Descriptions

- **`<thinking>`**: Internal reasoning process
  - Analyzes the scenario
  - Considers available tools and commands
  - Decides on the best approach
  - Must appear before action

- **`<command>`**: Minecraft console commands
  - Only valid Minecraft commands
  - Examples: /give, /tp, /time, /weather, /gamemode, /summon, etc.
  - Multiple commands separated by newlines
  - Rigorously constrained to valid syntax

- **`<speak>`**: Player-facing message
  - Friendly and helpful tone
  - Explains what's being done
  - Provides context to the player

## Training Data Examples

The example includes 5 diverse scenarios:

1. **Item Request**: Player asks for a diamond sword
2. **Environment Change**: Player needs light/daylight
3. **Teleportation**: Player wants to go to spawn
4. **Game Mode Change**: Player wants creative mode for building
5. **Combat Assistance**: Player is being attacked by a zombie

For production use, expand to 100-500 examples covering:
- All common Minecraft commands
- Various player needs and scenarios
- Edge cases and error handling
- Multi-step command sequences
- Complex interactions

## Minecraft Commands Reference

Valid commands that can be used in `<command>` tags:

### Item Management
- `/give <player> <item> [amount]` - Give items
- `/clear [player]` - Clear inventory

### Player Management
- `/tp <target> <x> <y> <z>` - Teleport
- `/gamemode <mode> [player]` - Change game mode
- `/effect give <player> <effect> [duration] [amplifier]` - Apply effects
- `/xp add <player> <amount>` - Give XP

### World Modification
- `/setblock <x> <y> <z> <block>` - Set block
- `/fill <x1> <y1> <z1> <x2> <y2> <z2> <block>` - Fill area
- `/time set <value>` - Set time
- `/weather <clear|rain|thunder>` - Set weather

### Entity Management
- `/summon <entity> [x] [y] [z]` - Summon entity
- `/kill <target>` - Kill entity

### Other Commands
- `/enchant <player> <enchantment> [level]` - Enchant items
- `/difficulty <level>` - Set difficulty
- `/setworldspawn [x] [y] [z]` - Set spawn

## See Also

- [Main Setup Guide](../../MINECRAFT_BOT_SETUP.md) - Complete setup instructions
- [Training Script](../../start_minecraft_training.py) - Automated training setup
- [Project README](../../README.md) - Platform overview
