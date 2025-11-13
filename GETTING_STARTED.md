# Getting Started with Model-Train

Welcome! This guide will get you up and running in **under 10 minutes**.

## What is Model-Train?

Model-Train is a complete platform for fine-tuning language models with structured outputs. You can:

1. **Define XML patterns** - Create custom output formats with drag-and-drop
2. **Generate training data** - Use AI to create synthetic examples
3. **Analyze dataset size** - Get recommendations on optimal data amounts
4. **Fine-tune models** - Use Unsloth + QLoRA for efficient training
5. **Export models** - Get your model in GGUF, HuggingFace, or other formats

## Prerequisites

**Required:**
- Python 3.10+
- 8GB RAM minimum (16GB recommended)
- GPU with 8GB+ VRAM (or Mac M1/M2/M3/M4)

**Optional:**
- Ollama installed for local AI (recommended)
- API keys for Claude or OpenAI

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd /home/user/model-train

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env (optional - only if using API keys)
nano .env
```

### 3. Start the Application

**Option A: All-in-One Launcher (Recommended)**
```bash
./start.sh
```

This will:
- Check dependencies
- Start backend API (port 8000)
- Start frontend Web UI (port 5173)
- Open your browser automatically

**Option B: Docker**
```bash
docker-compose up -d
```

**Option C: Manual Start**
```bash
# Terminal 1: Backend
python -m backend.main

# Terminal 2: Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### 4. Access the Application

Once started, you can access:

- **Web UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Choose Your Interface

Model-Train offers three interfaces:

### 🌐 Web UI (Best for Beginners)

Beautiful drag-and-drop interface with visual feedback.

```bash
./start.sh
# Open http://localhost:5173
```

**Perfect for:**
- Visual learners
- First-time users
- Complex XML pattern design
- Real-time dataset preview

### 🖥️ TUI (Best for Terminal Users)

Full-featured terminal interface with keyboard navigation.

```bash
./tui.sh
# or
python -m cli.main tui
```

**Perfect for:**
- SSH/remote sessions
- Keyboard-driven workflows
- Quick iterations
- Developers who live in the terminal

### ⌨️ CLI (Best for Automation)

Command-line interface for scripting and automation.

```bash
model-train project create minecraft-bot --objective "Minecraft assistant"
model-train generate minecraft-bot --count 100
model-train train start minecraft-bot --steps 100
```

**Perfect for:**
- Scripts and automation
- CI/CD pipelines
- Batch processing
- Reproducible workflows

## Your First Project (10 Minutes)

Let's create a Minecraft assistant bot that generates structured commands.

### Step 1: Create Project

**Web UI:**
1. Click "New Project"
2. Name: `minecraft-bot`
3. Objective: `Help players with Minecraft commands`
4. Base Model: `unsloth/qwen2.5-7b-instruct-bnb-4bit`
5. Click "Create"

**CLI:**
```bash
model-train project create minecraft-bot \
  --objective "Help players with Minecraft commands" \
  --model "unsloth/qwen2.5-7b-instruct-bnb-4bit"
```

### Step 2: Define XML Pattern

**Web UI:**
1. Go to "XML Editor"
2. Drag tags from palette:
   - `<think>` - Reasoning (free-form)
   - `<command>` - Minecraft command (list constraint)
   - `<speak>` - Response to player (free-form)
3. Configure constraints:
   - For `<command>`, add list: `/tp ~0 ~1 ~0`, `/give @p diamond`, etc.
4. Save pattern

**CLI:**
```bash
model-train xml add-tag minecraft-bot think \
  --constraint free_form \
  --description "Internal reasoning"

model-train xml add-tag minecraft-bot command \
  --constraint list \
  --values "/tp ~0 ~1 ~0" "/give @p diamond" "/time set day"

model-train xml add-tag minecraft-bot speak \
  --constraint free_form \
  --description "Response to player"
```

### Step 3: Generate Training Data

**Web UI:**
1. Go to "Data Generator"
2. Select provider: Ollama (or API if you have keys)
3. Set count: 50 (start small)
4. Mode: Pseudorandom
5. Click "Generate"
6. Wait for progress bar
7. Preview examples

**CLI:**
```bash
model-train generate minecraft-bot \
  --count 50 \
  --mode pseudorandom \
  --provider ollama
```

### Step 4: Analyze Dataset Size

**Web UI:**
1. Go to "Size Analyzer"
2. Click "Analyze"
3. View recommendations:
   - Pattern complexity score
   - Minimum/optimal/maximum sizes
   - Current adequacy status
   - Quality metrics

**CLI:**
```bash
model-train analyze dataset minecraft-bot --estimate-size
```

### Step 5: Train Model

**Web UI:**
1. Go to "Training Dashboard"
2. Configure:
   - LoRA Rank: 16
   - Learning Rate: 2e-4
   - Max Steps: 100
3. Click "Start Training"
4. Watch progress:
   - Loss graph
   - ETA counter
   - Real-time logs

**CLI:**
```bash
model-train train start minecraft-bot \
  --steps 100 \
  --lora-rank 16 \
  --learning-rate 2e-4
```

### Step 6: Export Model

**Web UI:**
1. Go to "Model Exporter"
2. Select format: GGUF (for Ollama)
3. Quantization: q4_k_m
4. Click "Export"
5. Model saved to `models/minecraft-bot.gguf`

**CLI:**
```bash
model-train model export minecraft-bot --format gguf
```

### Step 7: Use Your Model

**Load into Ollama:**
```bash
# Create Modelfile
echo "FROM models/minecraft-bot.gguf" > Modelfile

# Create Ollama model
ollama create minecraft-bot -f Modelfile

# Test it
ollama run minecraft-bot "I need diamonds"
```

Expected output:
```xml
<think>The player needs diamonds, I should direct them to the right mining level</think>
<command>/tp ~0 ~-60 ~0</command>
<speak>I'm taking you to Y=-60 where diamonds spawn. Start mining!</speak>
```

## Next Steps

### Improve Your Model

1. **Generate more data** - 200-500 examples for better quality
2. **Add variety** - More command types, scenarios
3. **Use analyzer** - Check dataset quality and diversity
4. **Train longer** - Increase steps to 500-1000

### Try Advanced Features

1. **Nested XML** - Create complex hierarchical patterns
2. **Multi-provider** - Mix Ollama + Claude for diverse data
3. **Forced generation** - Lock specific parts while varying others
4. **Curriculum learning** - Start simple, add complexity

### Explore Other Use Cases

Check `EXAMPLES.md` for:
- Code formatter
- Customer support bot
- Data extraction tool
- SQL query generator
- Creative writing assistant

## Common Issues

### "Connection refused" when starting

**Solution:** Check if ports are available:
```bash
lsof -i :8000  # Backend port
lsof -i :5173  # Frontend port
```

### "Out of memory" during training

**Solution:** Reduce batch size:
```bash
model-train train start myproject \
  --batch-size 1 \
  --gradient-accumulation 8
```

### "Model not found" error

**Solution:** Models are downloaded on first use. Ensure internet connection:
```bash
model-train model download unsloth/qwen2.5-7b-instruct-bnb-4bit
```

### Generation is slow

**Solution:** Use local Ollama with smaller models:
```bash
ollama pull llama2:7b
# Then select "llama2:7b" in Web UI or CLI
```

## Getting Help

- **Documentation**: See `README.md`, `USER_GUIDE.md`, `FAQ.md`
- **Examples**: Check `EXAMPLES.md` for real use cases
- **API Reference**: Visit http://localhost:8000/docs
- **Architecture**: See `ARCHITECTURE.md` for technical details

## Keyboard Shortcuts

### Web UI
- `Ctrl+S` - Save project
- `Ctrl+G` - Generate data
- `Ctrl+T` - Start training

### TUI
- `Q` - Quit
- `H` - Home
- `P` - Projects
- `X` - XML Editor
- `G` - Generate
- `T` - Training

### CLI
- `Tab` - Auto-complete commands
- `--help` - Show help for any command
- `--json` - Output as JSON for scripting

## Tips for Success

1. **Start small** - 50 examples first, then scale up
2. **Validate early** - Use size analyzer before training
3. **Monitor training** - Watch loss curve for convergence
4. **Test incrementally** - Export and test after 100 steps
5. **Use version control** - Save project configs in git
6. **Document patterns** - Add descriptions to XML tags
7. **Review generated data** - Check quality before training

## What's Next?

You're now ready to:
- ✅ Create custom XML patterns
- ✅ Generate synthetic training data
- ✅ Analyze dataset quality
- ✅ Fine-tune models efficiently
- ✅ Export for production use

**Happy training! 🚀**

For detailed tutorials, see `USER_GUIDE.md`.
For API integration, see `API_DOCUMENTATION.md`.
For architecture details, see `ARCHITECTURE.md`.
