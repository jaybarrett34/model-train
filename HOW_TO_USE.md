# 🚀 How to Use Model-Train - Complete Guide

## ✅ Project Status: COMPLETE & READY TO USE

All components have been successfully implemented and pushed to: `claude/create-model-app-011CV6EHMfrmmSEfZVCqnfdq`

## 📦 What You Have

A complete model fine-tuning platform with:
- ✅ **Web UI** (React + drag-and-drop XML editor)
- ✅ **TUI** (Terminal interface with Textual)
- ✅ **CLI** (Command-line automation)
- ✅ **Backend API** (FastAPI)
- ✅ **Core Modules** (XML engine, synthesis, training, analysis)
- ✅ **Documentation** (7 guides, 4,500+ lines)
- ✅ **Tests & Examples** (Complete workflows)

## 🎯 Quick Start (Choose Your Path)

### Path 1: One-Command Start (Easiest)

```bash
cd /home/user/model-train
./start.sh
```

This will:
1. Create virtual environment
2. Install dependencies
3. Start backend (port 8000)
4. Start frontend (port 5173)
5. Open browser automatically

**Access**: http://localhost:5173

### Path 2: Docker (For Deployment)

```bash
docker-compose up -d
```

**Access**: http://localhost:8000 (API) and http://localhost:5173 (UI)

### Path 3: Manual Setup (For Development)

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# Terminal 1: Backend
python -m backend.main

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Terminal 3: Test
python test_integration.py --num-examples 5
```

## 🎨 Choose Your Interface

### Option 1: Web UI (Best for Beginners)

**Start:**
```bash
./start.sh
```

**Features:**
- Drag-and-drop XML pattern editor (Scratch-like)
- Visual constraint configuration
- Real-time data generation preview
- Training progress graphs
- Dataset size analyzer with recommendations

**Perfect for:**
- First-time users
- Visual learners
- Complex pattern design
- Interactive exploration

### Option 2: TUI (Best for Terminal Users)

**Start:**
```bash
./tui.sh
# or
python -m cli.main tui
```

**Features:**
- Full keyboard navigation
- Real-time training monitoring
- Project management
- Log streaming
- Auto-refresh status

**Keyboard Shortcuts:**
- `Q` - Quit
- `H` - Home
- `P` - Projects
- `X` - XML Editor
- `G` - Generate Data
- `T` - Training

**Perfect for:**
- SSH/remote sessions
- Terminal enthusiasts
- Quick iterations
- Server environments

### Option 3: CLI (Best for Automation)

**Start:**
```bash
model-train --help
```

**Features:**
- Scriptable commands
- JSON output mode
- Progress bars
- Tab completion
- Pipeline integration

**Examples:**
```bash
# Create project
model-train project create minecraft-bot \
  --objective "Minecraft assistant" \
  --model "unsloth/qwen2.5-7b-instruct-bnb-4bit"

# Add XML pattern
model-train xml add-tag minecraft-bot think --constraint free_form
model-train xml add-tag minecraft-bot command --constraint list \
  --values "/tp ~0 ~1 ~0" "/give @p diamond"

# Generate data
model-train generate minecraft-bot --count 100 --provider ollama

# Analyze dataset
model-train analyze dataset minecraft-bot --estimate-size

# Train model
model-train train start minecraft-bot --steps 100 --lora-rank 16

# Export model
model-train model export minecraft-bot --format gguf
```

**Perfect for:**
- Automation scripts
- CI/CD pipelines
- Batch processing
- Reproducible workflows

## 📝 Your First Project (Step-by-Step)

Let's create a **Minecraft Command Assistant** that generates structured responses.

### Step 1: Choose Your Approach

<details>
<summary><b>🌐 Using Web UI</b></summary>

1. Start application: `./start.sh`
2. Open http://localhost:5173
3. Click "**New Project**"
4. Fill in:
   - Name: `minecraft-bot`
   - Objective: `Help players with Minecraft commands`
   - Base Model: `unsloth/qwen2.5-7b-instruct-bnb-4bit`
   - Dataset Format: `ShareGPT`
5. Click "**Create**"

</details>

<details>
<summary><b>🖥️ Using TUI</b></summary>

1. Start TUI: `./tui.sh`
2. Press `P` for Projects
3. Press `N` for New Project
4. Fill in form fields
5. Press Enter to submit

</details>

<details>
<summary><b>⌨️ Using CLI</b></summary>

```bash
model-train project create minecraft-bot \
  --objective "Help players with Minecraft commands" \
  --model "unsloth/qwen2.5-7b-instruct-bnb-4bit" \
  --dataset-format sharegpt
```

</details>

### Step 2: Define XML Pattern

Your pattern will look like this:
```xml
<think>Internal reasoning about the task</think>
<command>/tp ~0 ~-60 ~0</command>
<speak>Response to the player</speak>
```

<details>
<summary><b>🌐 Using Web UI</b></summary>

1. Navigate to "**XML Editor**"
2. From left sidebar, drag these tags to the canvas:
   - `<think>` - Set constraint: **free_form**
   - `<command>` - Set constraint: **list** with values:
     - `/tp ~0 ~1 ~0`
     - `/give @p diamond`
     - `/time set day`
     - `/weather clear`
   - `<speak>` - Set constraint: **free_form**
3. Click "**Save Pattern**"

</details>

<details>
<summary><b>🖥️ Using TUI</b></summary>

1. Press `X` for XML Editor
2. Press `A` to add tags
3. Enter tag details for each
4. Press `S` to save

</details>

<details>
<summary><b>⌨️ Using CLI</b></summary>

```bash
model-train xml add-tag minecraft-bot think --constraint free_form
model-train xml add-tag minecraft-bot command --constraint list \
  --values "/tp ~0 ~1 ~0" "/give @p diamond" "/time set day"
model-train xml add-tag minecraft-bot speak --constraint free_form
```

</details>

### Step 3: Generate Training Data

Start with 50 examples to test, then scale up to 200-500 for production.

<details>
<summary><b>🌐 Using Web UI</b></summary>

1. Go to "**Data Generator**"
2. Configure:
   - Provider: **Ollama** (or Claude/OpenAI if you have API keys)
   - Model: `llama2` (or your preferred model)
   - Count: `50`
   - Mode: **Pseudorandom**
3. Click "**Generate**"
4. Watch progress bar
5. Preview generated examples in the table

</details>

<details>
<summary><b>🖥️ Using TUI</b></summary>

1. Press `G` for Generation
2. Fill in parameters
3. Watch progress bar and logs

</details>

<details>
<summary><b>⌨️ Using CLI</b></summary>

```bash
model-train generate minecraft-bot \
  --count 50 \
  --mode pseudorandom \
  --provider ollama \
  --model llama2
```

</details>

### Step 4: Analyze Dataset Size

This critical step tells you if you have enough data!

<details>
<summary><b>🌐 Using Web UI</b></summary>

1. Go to "**Size Analyzer**"
2. Click "**Analyze**"
3. View report:
   - **Pattern Complexity**: 45/100 (Moderate)
   - **Current Size**: 50 examples
   - **Recommended**: 200-500 examples
   - **Status**: 🟡 Insufficient (needs more)
   - **Quality**: Check for duplicates and diversity
4. If inadequate, generate more data

</details>

<details>
<summary><b>⌨️ Using CLI</b></summary>

```bash
model-train analyze dataset minecraft-bot --estimate-size
```

**Output:**
```
Pattern Complexity: 45/100 (MODERATE)
Current Size: 50
Recommended: 200-500
Status: INSUFFICIENT ⚠️
Quality: 8.5/10

Recommendations:
• Generate 150-450 more examples
• Increase diversity in command types
• Add edge cases
```

</details>

### Step 5: Train Your Model

Once you have adequate data (200+ examples):

<details>
<summary><b>🌐 Using Web UI</b></summary>

1. Go to "**Training Dashboard**"
2. Configure:
   - LoRA Rank: `16`
   - LoRA Alpha: `16`
   - Learning Rate: `2e-4`
   - Batch Size: `2`
   - Max Steps: `100` (for testing) or `500` (for production)
3. Click "**Start Training**"
4. Monitor:
   - Loss curve graph
   - Current step / total steps
   - ETA countdown
   - Live logs
5. Wait for completion (~5-10 minutes on RTX 4090)

</details>

<details>
<summary><b>🖥️ Using TUI</b></summary>

1. Press `T` for Training
2. Configure parameters
3. Watch real-time metrics with auto-refresh

</details>

<details>
<summary><b>⌨️ Using CLI</b></summary>

```bash
# Start training
model-train train start minecraft-bot \
  --steps 500 \
  --lora-rank 16 \
  --learning-rate 2e-4 \
  --batch-size 2

# Watch progress
model-train train status <job-id> --watch
```

</details>

### Step 6: Export Your Model

<details>
<summary><b>🌐 Using Web UI</b></summary>

1. Go to "**Model Exporter**"
2. Select:
   - Format: **GGUF** (for Ollama)
   - Quantization: **q4_k_m** (good balance)
   - Merge adapters: ✅ Yes
3. Click "**Export**"
4. Find model at: `models/minecraft-bot.gguf`

</details>

<details>
<summary><b>⌨️ Using CLI</b></summary>

```bash
model-train model export minecraft-bot --format gguf --quantization q4_k_m
```

</details>

### Step 7: Use Your Model!

**Load into Ollama:**
```bash
# Create Modelfile
cat > Modelfile <<EOF
FROM /home/user/model-train/models/minecraft-bot.gguf
PARAMETER temperature 0.7
SYSTEM You are a Minecraft assistant that helps players with commands.
EOF

# Import to Ollama
ollama create minecraft-bot -f Modelfile

# Test it!
ollama run minecraft-bot "I need diamonds"
```

**Expected Output:**
```xml
<think>The player needs diamonds. They spawn at Y=-59 to Y=16, with peak at Y=-59. I should teleport them to mining level.</think>
<command>/tp ~0 ~-60 ~0</command>
<speak>Taking you to Y=-60, the best level for diamond mining! Start mining and you'll find them soon.</speak>
```

## 📊 Understanding the Size Analyzer

The size analyzer is your secret weapon for determining optimal dataset size.

### What It Tells You

1. **Pattern Complexity** (0-100 score)
   - 0-20: Trivial (e.g., simple formatting)
   - 20-40: Simple (e.g., basic commands)
   - 40-60: Moderate (e.g., structured responses)
   - 60-80: Complex (e.g., reasoning + actions)
   - 80-100: Very Complex (e.g., multi-step planning)

2. **Size Recommendations**
   - **Minimum**: Bare minimum to see any effect
   - **Optimal**: Best quality/cost balance
   - **Maximum**: Diminishing returns beyond this

3. **Adequacy Status**
   - 🔴 **Insufficient**: Need more data
   - 🟡 **Adequate**: Usable but could improve
   - 🟢 **Optimal**: Perfect size
   - 🔵 **Excessive**: More won't help much

4. **Quality Metrics**
   - Duplicate percentage
   - Diversity score
   - Variance analysis
   - Overfitting risk

### Example Analysis

```
Pattern: Minecraft Assistant
Complexity: 45/100 (MODERATE)

Current: 50 examples
Minimum: 100 examples
Optimal: 300 examples  ⭐ TARGET THIS
Maximum: 800 examples

Status: INSUFFICIENT ⚠️

Quality:
- Duplicates: 2% (excellent)
- Diversity: 75/100 (good)
- Variance: High (good)
- Overfitting Risk: Low

Recommendations:
1. Generate 250 more examples
2. Add more command variety
3. Include edge cases
4. Test different player scenarios
```

## 🔧 Advanced Usage

### Multi-Provider Data Generation

Mix AI providers for diversity:

```bash
# Generate 50 from Ollama
model-train generate myproject --count 50 --provider ollama

# Generate 50 from Claude
model-train generate myproject --count 50 --provider anthropic

# Generate 50 from OpenAI
model-train generate myproject --count 50 --provider openai
```

### Nested XML Patterns

Create hierarchical structures:

```xml
<response>
  <analysis>
    <observation>...</observation>
    <reasoning>...</reasoning>
  </analysis>
  <action>
    <command>...</command>
    <explanation>...</explanation>
  </action>
</response>
```

### Forced Generation Mode

Lock specific parts while varying others:

```python
# In Web UI: Select "Forced" mode
# Lock the <command> tag to specific values
# Let AI vary <think> and <speak>
```

### Parameter Tuning

For better results:

```bash
# Higher LoRA rank for more capacity
model-train train start myproject --lora-rank 64

# More steps for better convergence
model-train train start myproject --steps 1000

# Lower learning rate for stability
model-train train start myproject --learning-rate 1e-4
```

## 🐛 Troubleshooting

### "Connection refused" error

**Problem**: Backend isn't running

**Solution:**
```bash
python -m backend.main
# Check it's running at http://localhost:8000/health
```

### "Out of memory" during training

**Problem**: Batch size too large for your GPU

**Solution:**
```bash
model-train train start myproject \
  --batch-size 1 \
  --gradient-accumulation 8
```

### Generated data doesn't match pattern

**Problem**: AI not following XML structure

**Solution:**
1. Check pattern definition
2. Add more examples to the prompt
3. Try different AI provider
4. Increase temperature for more variety

### Model quality is poor

**Problem**: Not enough data or wrong parameters

**Solution:**
1. Run size analyzer
2. Generate more data (aim for "optimal" size)
3. Increase training steps
4. Try higher LoRA rank

## 📚 Documentation

- **GETTING_STARTED.md** - This guide (you are here!)
- **USER_GUIDE.md** - Complete tutorials and best practices
- **API_DOCUMENTATION.md** - REST API reference
- **ARCHITECTURE.md** - System design
- **EXAMPLES.md** - 8 real-world use cases
- **FAQ.md** - 33+ Q&A
- **CHANGELOG.md** - Version history

## 💡 Tips for Success

1. **Start Small**: 50 examples → test → scale to 300
2. **Use Analyzer**: Always check dataset adequacy before training
3. **Monitor Training**: Watch loss curve for convergence
4. **Test Early**: Export at 100 steps to verify direction
5. **Iterate**: Generate → Analyze → Train → Test → Repeat
6. **Document**: Save prompts and configs in git
7. **Version**: Keep multiple exports with different parameters

## 🎯 Next Steps

Now that you know how to use Model-Train:

1. ✅ Try the Minecraft example above
2. ✅ Explore `EXAMPLES.md` for more use cases
3. ✅ Read `USER_GUIDE.md` for best practices
4. ✅ Check `FAQ.md` for common questions
5. ✅ Build your custom application!

## 🎉 You're Ready!

You now have everything you need to:
- Create custom XML patterns
- Generate high-quality training data
- Analyze dataset requirements
- Fine-tune models efficiently
- Export for production use

**Happy Training! 🚀**

---

**Questions?** Check `FAQ.md` or `USER_GUIDE.md`

**Issues?** Review `TROUBLESHOOTING` section above

**Ideas?** See `EXAMPLES.md` for inspiration
