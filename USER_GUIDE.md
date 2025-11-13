# User Guide - Model Fine-Tuning Application

A comprehensive step-by-step guide for users of all experience levels. This guide covers everything from your first project to advanced techniques and best practices.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Your First Project](#your-first-project)
3. [Common Workflows](#common-workflows)
4. [Best Practices](#best-practices)
5. [Choosing Dataset Size](#choosing-dataset-size)
6. [Model Selection Guide](#model-selection-guide)
7. [Parameter Tuning Tips](#parameter-tuning-tips)
8. [Advanced Techniques](#advanced-techniques)

---

## Getting Started

### Prerequisites Check

Before you begin, ensure you have:

✓ **Python 3.10 or higher** installed
✓ **pip** package manager
✓ **8GB+ RAM** (16GB+ recommended)
✓ **GPU with CUDA** (optional but recommended) OR **Mac with M1/M2/M3** chip
✓ **20GB+ free disk space** for models and datasets
✓ **API keys** for at least one AI provider (Ollama is free and runs locally)

### Installation Steps

1. **Clone and Install**:
   ```bash
   git clone <repository-url>
   cd model-train
   pip install -r requirements.txt
   ```

2. **Set Up Configuration**:
   ```bash
   cp .env.example .env
   ```

3. **Edit .env file** with your API keys:
   ```bash
   # For local AI (free, no API key needed)
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama2

   # For Cloud AI (requires API keys)
   ANTHROPIC_API_KEY=sk-ant-...  # Get from https://console.anthropic.com
   OPENAI_API_KEY=sk-...          # Get from https://platform.openai.com

   # For model downloads
   HUGGINGFACE_TOKEN=hf_...       # Get from https://huggingface.co/settings/tokens
   ```

4. **Install Ollama (recommended for beginners)**:
   ```bash
   # macOS
   brew install ollama
   ollama serve &
   ollama pull llama2

   # Linux
   curl https://ollama.ai/install.sh | sh
   ollama serve &
   ollama pull llama2
   ```

5. **Start the Backend**:
   ```bash
   python -m backend.main
   # Should see: "Model Fine-Tuning Application Started"
   # Visit http://localhost:8000/docs to verify
   ```

6. **Choose Your Interface**:

   **Option A: Web UI (Easiest for beginners)**
   ```bash
   cd frontend
   npm install
   npm run dev
   # Open browser to http://localhost:5173
   ```

   **Option B: TUI (Terminal Interface)**
   ```bash
   python -m cli.tui
   ```

   **Option C: CLI (Command Line)**
   ```bash
   model-train --help
   ```

---

## Your First Project

This tutorial will walk you through creating a simple chatbot using the Web UI. Estimated time: **30 minutes**.

### Step 1: Create a New Project (5 minutes)

1. **Open the Web UI** at `http://localhost:5173`
2. **Click "New Project"** button
3. **Fill in the form**:
   - **Name**: `my-first-chatbot` (no spaces, lowercase)
   - **Objective**: "Train a friendly chatbot that uses XML tags to structure its responses with thinking and speaking sections"
   - **Base Model**: Select `unsloth/llama-2-7b-bnb-4bit` (good for beginners)
   - **Dataset Format**: Select `sharegpt` (recommended)
   - **AI Provider**: Select `ollama` (if installed) or `anthropic`
   - **AI Model**: `llama2` (for Ollama) or `claude-sonnet-4-5-20250929` (for Claude)

4. **Click "Create Project"**

**What just happened?**
You created a project configuration that defines:
- What you want to train (the objective)
- Which base model to start from
- How to generate training data
- What format to use for the dataset

### Step 2: Define XML Patterns (10 minutes)

XML patterns define the structure of your model's output. For our chatbot, we'll use two tags:

1. **Click "XML Editor"** in the navigation
2. **Select your project**: `my-first-chatbot`
3. **Add first pattern**:
   - **Tag Name**: `thinking`
   - **Description**: "Internal reasoning and analysis before responding to the user"
   - **Constraint Type**: `free_form`
   - **Required**: Yes
   - **Click "Add Tag"**

4. **Add second pattern**:
   - **Tag Name**: `response`
   - **Description**: "The actual response to show the user"
   - **Constraint Type**: `free_form`
   - **Required**: Yes
   - **Click "Add Tag"**

5. **Preview** should show:
   ```xml
   <thinking>Internal reasoning goes here...</thinking>
   <response>Response to user goes here...</response>
   ```

6. **Click "Save Patterns"**

**Why XML patterns?**
XML patterns help train your model to:
- Structure its outputs consistently
- Separate internal reasoning from user-facing responses
- Make outputs easier to parse programmatically
- Improve reasoning quality by forcing step-by-step thinking

### Step 3: Generate Training Data (10 minutes)

1. **Navigate to "Generate Data"** page
2. **Select your project**: `my-first-chatbot`
3. **Configure generation**:
   - **Number of Examples**: `100` (start small for your first run)
   - **Temperature**: `0.8` (good balance of creativity and consistency)
   - **Batch Size**: `10` (how many to generate at once)

4. **Click "Generate Dataset"**

5. **Wait for generation** (may take 5-10 minutes depending on provider)
   - Watch the progress bar
   - Review log messages
   - You'll see messages like "Generated example 1/100..."

**What's happening?**
The system is:
1. Reading your project objective and XML patterns
2. Using AI to generate conversational examples
3. Validating each example has the required XML tags
4. Saving to a dataset file in ShareGPT format

**Troubleshooting generation**:
- If stuck at 0%: Check that backend is running and AI provider is accessible
- If validation errors: AI might be struggling with XML format, try reducing temperature
- If very slow: Ollama models are slower but free; Claude/GPT are faster with API keys

### Step 4: Review Your Dataset (5 minutes)

1. **Go to "Datasets"** page
2. **Click on your generated dataset** to view
3. **Review a few examples** - they should look like:
   ```json
   {
     "conversations": [
       {
         "from": "human",
         "value": "What's the weather like today?"
       },
       {
         "from": "gpt",
         "value": "<thinking>The user is asking about weather. I should provide a helpful response about checking weather sources.</thinking>\n<response>I don't have access to real-time weather data, but you can check weather.com or your local weather service for current conditions in your area!</response>"
       }
     ]
   }
   ```

**Quality Check**:
- ✓ Each example has both `thinking` and `response` tags
- ✓ Thinking shows reasoning process
- ✓ Responses are helpful and relevant
- ✗ If many examples lack XML tags, regenerate with lower temperature

### Step 5: Start Training (Optional - requires GPU)

**Note**: Training requires significant compute resources. You can skip this step if:
- You don't have a GPU/Mac M1+
- You want to just practice the workflow first

1. **Navigate to "Training"** page
2. **Configure training**:
   - **Project**: `my-first-chatbot`
   - **Dataset**: Select the dataset you just generated
   - **LoRA Rank**: `16` (good default)
   - **Learning Rate**: `0.0002` (2e-4)
   - **Epochs**: `3`
   - **Batch Size**: `2` (reduce to `1` if out of memory)

3. **Click "Start Training"**

4. **Monitor progress**:
   - Training loss should decrease over time
   - Typical training time: 30 minutes to 2 hours depending on hardware
   - You can cancel at any time

**Understanding the metrics**:
- **Loss**: How wrong the model is (lower = better). Should decrease steadily.
- **Epoch**: One pass through all training data. More epochs = more learning.
- **Step**: Individual training updates. Total steps = (examples ÷ batch_size) × epochs
- **Learning Rate**: How fast the model learns. Too high = unstable, too low = slow

**Common issues**:
- **CUDA Out of Memory**: Reduce batch size to 1, or use smaller model
- **Loss not decreasing**: Try higher learning rate (2e-4 → 3e-4)
- **Loss drops too fast**: May overfit, reduce learning rate or epochs

### Step 6: Use Your Model

After training completes:

1. **Export to GGUF** (for use with Ollama):
   ```bash
   model-train model export my-first-chatbot --format gguf
   ```

2. **Create Ollama model**:
   ```bash
   ollama create my-chatbot -f models/my-first-chatbot/Modelfile
   ```

3. **Test it**:
   ```bash
   ollama run my-chatbot "Hello! How are you today?"
   ```

**Congratulations!** You've completed your first fine-tuning project! 🎉

---

## Common Workflows

### Workflow 1: Minecraft Bot Assistant

**Objective**: Train a bot that can help players in Minecraft using commands.

**XML Patterns**:
```xml
<observe>What the bot sees in the environment</observe>
<think>Reasoning about what to do</think>
<command>Minecraft command to execute</command>
<speak>What to say to the player</speak>
```

**Example Training Data**:
```
Human: "I need help finding diamonds"
Bot:
<observe>Player is at Y level 70, has iron pickaxe, no diamonds found yet</observe>
<think>Diamonds spawn between Y 5-12. Player needs to go deeper. Should guide them safely.</think>
<command>/tp @p ~ 11 ~</command>
<speak>Let's head down to Y level 11, the best height for diamonds! I'll teleport you there.</speak>
```

**Best Settings**:
- Model: `unsloth/llama-2-7b-bnb-4bit` or `unsloth/mistral-7b-bnb-4bit`
- Examples: 200-500
- Temperature: 0.7 (needs consistency for commands)
- LoRA Rank: 16-32
- Epochs: 3-5

### Workflow 2: Code Formatter

**Objective**: Format and explain code with structure analysis.

**XML Patterns**:
```xml
<analysis>Code structure analysis</analysis>
<issues>Problems found</issues>
<formatted>Formatted code</formatted>
<explanation>What changed and why</explanation>
```

**Example Training Data**:
```
Human: "Format this Python code: def foo(x,y):return x+y"

Bot:
<analysis>Single line function definition, missing spacing and docstring</analysis>
<issues>No spaces after commas, no docstring, no type hints</issues>
<formatted>
def foo(x: int, y: int) -> int:
    """Add two numbers together."""
    return x + y
</formatted>
<explanation>Added type hints, docstring, proper spacing, and multi-line format following PEP 8</explanation>
```

**Best Settings**:
- Model: `unsloth/qwen2.5-14b-instruct-bnb-4bit` (good at code)
- Examples: 500-1000
- Temperature: 0.6 (more deterministic for code)
- LoRA Rank: 32-64 (code needs more capacity)
- Epochs: 5-7

### Workflow 3: Customer Support Bot

**Objective**: Handle customer inquiries with empathy and structure.

**XML Patterns**:
```xml
<understand>Customer's issue and emotion</understand>
<action>What action to take (search_kb, escalate, resolve)</action>
<response>Response to customer</response>
<internal_notes>Notes for tracking system</internal_notes>
```

**Example Training Data**:
```
Human: "I've been waiting 3 days for my refund and nobody has responded!"

Bot:
<understand>Customer is frustrated about delayed refund and lack of communication. Issue: refund status</understand>
<action>search_kb: refund_timeline; escalate: urgent_refund_team</action>
<response>I sincerely apologize for the delay and lack of communication. That's definitely not the experience we want for you. Let me escalate this to our refunds team immediately. You should receive an update within 2 hours. I'm also adding a note to prioritize your case.</response>
<internal_notes>Customer frustrated - 3 day delay on refund. Escalating to urgent queue. Follow up required in 2 hours.</internal_notes>
```

**Best Settings**:
- Model: `unsloth/llama-2-13b-bnb-4bit` (larger for better empathy)
- Examples: 300-800
- Temperature: 0.8 (needs human-like variation)
- LoRA Rank: 16-32
- Epochs: 3-5

### Workflow 4: Data Extraction Bot

**Objective**: Extract structured information from text.

**XML Patterns**:
```xml
<entities>Named entities found</entities>
<relationships>Relationships between entities</relationships>
<metadata>Document metadata</metadata>
<summary>Brief summary</summary>
```

**Best Settings**:
- Model: `unsloth/mistral-7b-instruct-bnb-4bit`
- Examples: 400-600
- Temperature: 0.5 (extraction should be consistent)
- LoRA Rank: 32
- Epochs: 5-7

---

## Best Practices for Training Data

### Quality Over Quantity

**Don't:** Generate 10,000 low-quality examples
**Do:** Generate 200-500 high-quality, diverse examples

**High-quality example characteristics**:
- ✓ Covers edge cases and variations
- ✓ XML tags are consistently formatted
- ✓ Thinking shows clear reasoning
- ✓ Outputs are accurate and helpful
- ✓ Examples vary in complexity

### Diversity is Key

Your training data should include:

1. **Different input types**:
   - Short questions
   - Long, detailed queries
   - Ambiguous requests
   - Multi-part questions

2. **Various difficulty levels**:
   - Simple, straightforward cases (40%)
   - Medium complexity (40%)
   - Complex, multi-step problems (20%)

3. **Edge cases**:
   - Requests with missing information
   - Ambiguous or unclear inputs
   - Out-of-scope requests
   - Error handling scenarios

### Temperature Guidelines

**Temperature** controls randomness in generation:

- **0.1-0.3**: Very consistent, deterministic
  - Use for: Code formatting, data extraction, factual Q&A
  - Risk: May be repetitive or boring

- **0.5-0.7**: Balanced creativity and consistency
  - Use for: General chatbots, tutoring, customer support
  - Risk: Some variation, generally safe

- **0.8-1.0**: Creative, diverse outputs
  - Use for: Creative writing, brainstorming, storytelling
  - Risk: May occasionally be inconsistent or off-topic

- **1.1-2.0**: Very creative, unpredictable
  - Use for: Experimental creative tasks
  - Risk: High variation, potential nonsense

### Validation is Critical

Always validate generated data before training:

```bash
# Use the analyze command to check dataset quality
model-train analyze dataset my-project --validate
```

**Red flags to watch for**:
- ✗ Missing XML tags (should be 0%)
- ✗ Malformed XML (should be 0%)
- ✗ Repetitive or identical examples (should be <5%)
- ✗ Broken or incomplete reasoning
- ✗ Offensive or inappropriate content

### Iterative Improvement

**Process**:
1. Generate small batch (50-100 examples)
2. Review manually for quality
3. Adjust temperature/prompts if needed
4. Generate larger batch (200-500)
5. Train on dataset
6. Test model performance
7. Identify weaknesses
8. Generate more data targeting those weaknesses
9. Repeat steps 5-8

---

## Choosing Dataset Size

### General Guidelines

| Model Size | Minimum Examples | Recommended | Maximum Useful |
|------------|------------------|-------------|----------------|
| 7B | 100 | 300-500 | 2,000 |
| 13B | 200 | 500-800 | 5,000 |
| 14B+ | 300 | 800-1,500 | 10,000 |

### Task Complexity Factor

Multiply base recommendations by complexity:

**Simple tasks** (×0.5):
- Single XML tag
- Straightforward Q&A
- Simple classification
- Example: 7B model → 150-250 examples

**Medium tasks** (×1.0):
- 2-4 XML tags
- Multi-step reasoning
- Moderate variation
- Example: 7B model → 300-500 examples

**Complex tasks** (×2.0):
- 5+ XML tags
- Complex reasoning
- High variation needed
- Example: 7B model → 600-1,000 examples

### Budget Considerations

**Using Ollama** (local, free):
- Generation speed: ~20-30 examples/hour
- Cost: $0
- Recommendation: 200-500 examples (7-15 hours)

**Using Claude/GPT** (API, paid):
- Generation speed: ~100-200 examples/hour
- Cost: $5-20 per 500 examples (varies by model)
- Recommendation: 500-1,000 examples (5-10 hours, $10-40)

### Signs You Need More Data

During/after training, watch for:

- ✗ **Inconsistent XML formatting**: Model sometimes forgets tags
- ✗ **Poor generalization**: Works on training examples but fails on new ones
- ✗ **Memorization**: Model repeats training examples verbatim
- ✗ **High validation loss**: Model struggling to learn patterns

**Solution**: Generate 50-100 more examples and continue training

### Signs You Have Enough Data

- ✓ **Consistent formatting**: XML tags always present and correct
- ✓ **Good generalization**: Handles new inputs well
- ✓ **Low training loss**: <1.0 after a few epochs
- ✓ **Varied responses**: Doesn't repeat memorized patterns

---

## Model Selection Guide

### Model Comparison Table

| Model | Size | RAM Needed | Speed | Code | Chat | Reasoning | Best For |
|-------|------|------------|-------|------|------|-----------|----------|
| **Llama-2-7B** | 7B | 8GB | Fast | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | General chatbots |
| **Llama-2-13B** | 13B | 16GB | Medium | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Customer service |
| **Mistral-7B** | 7B | 8GB | Fast | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Balanced tasks |
| **Qwen2.5-14B** | 14B | 16GB | Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Code & analysis |
| **CodeLlama-7B** | 7B | 8GB | Fast | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Pure code tasks |
| **Phi-2** | 2.7B | 4GB | Very Fast | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Edge devices |

### Selection Decision Tree

```
Start here: What's your primary task?

├─ Code-related (formatting, generation, review)
│  ├─ Pure code tasks → CodeLlama-7B
│  └─ Code + explanations → Qwen2.5-14B or Mistral-7B
│
├─ Conversational (chatbot, support, tutoring)
│  ├─ Need empathy/nuance → Llama-2-13B
│  └─ General conversation → Llama-2-7B or Mistral-7B
│
├─ Analysis/Reasoning (data extraction, decision making)
│  ├─ Complex reasoning → Qwen2.5-14B
│  └─ Simple extraction → Mistral-7B
│
└─ Resource-constrained (limited RAM, CPU only)
   └─ Phi-2 or Llama-2-7B
```

### Hardware-Based Recommendations

**GPU Memory**:
- **4GB VRAM**: Phi-2, Llama-2-7B (4-bit)
- **8GB VRAM**: Llama-2-7B, Mistral-7B, CodeLlama-7B (4-bit)
- **16GB VRAM**: Llama-2-13B, Qwen2.5-14B (4-bit), or 7B models (8-bit)
- **24GB+ VRAM**: Any 7B/13B in 8-bit, or 13B/14B in 4-bit

**CPU-Only** (with 16GB+ RAM):
- Phi-2, Llama-2-7B (very slow training, 10-50x slower than GPU)

**Mac M1/M2/M3** (with 16GB+ unified memory):
- Any 7B model works well with MPS
- 13B models work with 16GB+ unified memory

### Quantization Explained

**4-bit quantization** (`bnb-4bit`):
- Reduces model size by ~75%
- Minimal quality loss (<5%)
- Recommended for most users
- Example: 7B model uses ~4GB instead of ~14GB

**8-bit quantization** (`bnb-8bit`):
- Reduces model size by ~50%
- Negligible quality loss (<2%)
- Use if you have extra VRAM
- Example: 7B model uses ~7GB instead of ~14GB

**No quantization** (full precision):
- Full model size
- Best quality but needs 2-4x more memory
- Only for research/comparison purposes

**Recommendation**: Always use 4-bit for training, you can export to other formats later.

---

## Parameter Tuning Tips

### LoRA Rank (r)

**What it does**: Controls how many parameters to train. Higher = more capacity but slower.

**Recommendations**:
- **r=8**: Minimum for simple tasks (single XML tag, basic chat)
- **r=16**: Good default for most tasks (2-4 XML tags, chatbots)
- **r=32**: Better for complex tasks (5+ tags, coding, analysis)
- **r=64**: Maximum for very complex tasks (large code projects)

**Trade-offs**:
- Higher rank = Better quality but slower training and larger adapter files
- Lower rank = Faster but may not capture complex patterns

**How to choose**:
1. Start with r=16
2. If model struggles with complex patterns, increase to 32
3. If training is very slow, decrease to 8
4. If results plateau, try doubling

### Learning Rate (lr)

**What it does**: How fast the model updates. Higher = faster learning but less stable.

**Recommendations**:
- **1e-4 (0.0001)**: Conservative, very stable, slower convergence
- **2e-4 (0.0002)**: Good default for most tasks
- **3e-4 (0.0003)**: Faster learning, slightly less stable
- **5e-4 (0.0005)**: Aggressive, may be unstable

**Signs learning rate is too high**:
- Loss jumps around erratically
- Loss increases instead of decreasing
- NaN or infinity values

**Signs learning rate is too low**:
- Loss decreases very slowly
- Training takes too long
- Loss plateaus early

**Adaptive strategy**:
```
Epoch 1-2: Use 2e-4 (learn quickly)
Epoch 3-5: Use 1e-4 (fine-tune carefully)
```

### Batch Size

**What it does**: How many examples to process together. Higher = more stable but needs more memory.

**Recommendations**:
- **batch_size=1**: Minimum, use if out of memory
- **batch_size=2**: Good default for 7B models with 8GB VRAM
- **batch_size=4**: Better if you have 16GB+ VRAM
- **batch_size=8+**: Only with very large VRAM (24GB+)

**With Gradient Accumulation**:
```
Effective batch = batch_size × gradient_accumulation_steps

Examples:
- batch_size=2, grad_accum=4 → effective batch of 8
- batch_size=1, grad_accum=8 → effective batch of 8 (same result, less memory)
```

**Recommendation**: Use batch_size=2 with gradient_accumulation_steps=4 for best of both worlds.

### Number of Epochs

**What it does**: How many times to pass through the entire dataset.

**Recommendations**:
- **1-2 epochs**: Very large datasets (1000+ examples)
- **3-5 epochs**: Medium datasets (300-1000 examples) - **RECOMMENDED**
- **5-7 epochs**: Small datasets (100-300 examples)
- **10+ epochs**: Tiny datasets (<100 examples) but risk overfitting

**Overfitting warning signs**:
- Training loss keeps decreasing but validation loss increases
- Model memorizes training examples word-for-word
- Poor performance on new examples

**Underfitting warning signs**:
- Training loss is still high (>1.5)
- Model doesn't follow XML patterns consistently
- Responses are generic or off-topic

**Sweet spot**: Training loss around 0.3-0.8 after final epoch

### Warmup Steps

**What it does**: Gradually increase learning rate at the start to prevent instability.

**Recommendations**:
- **5 steps**: Default for most tasks
- **10 steps**: If training is unstable at the start
- **0 steps**: If dataset is very small (<100 examples)

**Formula**: warmup_steps = 5-10% of total training steps
```
Example: 200 examples, batch_size=2, 3 epochs
Total steps = (200/2) × 3 = 300 steps
Warmup = 300 × 0.05 = 15 steps
```

### Max Sequence Length

**What it does**: Maximum length of input+output text. Longer = more context but slower.

**Recommendations**:
- **512**: Short conversations, quick responses
- **1024**: Medium conversations, code snippets
- **2048**: Long conversations, detailed explanations (DEFAULT)
- **4096**: Very long context, large code files
- **8192+**: Extreme cases only

**Memory impact**:
- Doubling sequence length roughly doubles memory usage
- If running out of memory, try 1024 instead of 2048

### Example Configuration Sets

**Fast Training** (prototyping):
```json
{
  "lora_r": 8,
  "learning_rate": 3e-4,
  "batch_size": 4,
  "num_epochs": 3,
  "max_seq_length": 1024
}
```

**Balanced** (recommended):
```json
{
  "lora_r": 16,
  "learning_rate": 2e-4,
  "batch_size": 2,
  "gradient_accumulation_steps": 4,
  "num_epochs": 3,
  "max_seq_length": 2048
}
```

**High Quality** (if you have time/resources):
```json
{
  "lora_r": 32,
  "learning_rate": 2e-4,
  "batch_size": 4,
  "gradient_accumulation_steps": 2,
  "num_epochs": 5,
  "max_seq_length": 2048
}
```

**Memory Constrained** (4GB VRAM):
```json
{
  "lora_r": 16,
  "learning_rate": 2e-4,
  "batch_size": 1,
  "gradient_accumulation_steps": 8,
  "num_epochs": 3,
  "max_seq_length": 1024
}
```

---

## Advanced Techniques

### Multi-Task Training

Train one model on multiple related tasks:

```bash
# Create separate projects for each task
model-train project create chatbot-general --objective "General conversation"
model-train project create chatbot-code --objective "Code assistance"
model-train project create chatbot-math --objective "Math tutoring"

# Generate data for each
model-train generate chatbot-general --count 300
model-train generate chatbot-code --count 300
model-train generate chatbot-math --count 300

# Merge datasets manually
cat datasets/chatbot-*/*.json > datasets/combined.json

# Train on combined dataset
# (requires manual project setup with combined dataset)
```

### Curriculum Learning

Start with easy examples, gradually increase difficulty:

```bash
# Phase 1: Simple examples (200)
model-train generate my-project --count 200 --mode simple

# Train phase 1
model-train train start my-project --epochs 3

# Phase 2: Add medium examples (300)
model-train generate my-project --count 300 --mode medium

# Continue training with more data
model-train train start my-project --epochs 2 --resume

# Phase 3: Add hard examples (200)
model-train generate my-project --count 200 --mode complex

# Final training phase
model-train train start my-project --epochs 2 --resume
```

### Synthetic Data Augmentation

Improve diversity by varying prompts:

```python
# In your generation prompts, vary:
# 1. Conversation style (formal vs casual)
# 2. Response length (concise vs detailed)
# 3. Domain knowledge level (beginner vs expert)
# 4. Emotional tone (neutral vs enthusiastic)
```

### Model Merging

Combine multiple fine-tuned models:

```bash
# Train model on task A
model-train train start task-a-project

# Train separate model on task B
model-train train start task-b-project

# Merge (requires mergekit library)
mergekit-merge --config merge_config.yml
```

### Evaluation-Driven Development

**1. Create test set** (20% of data, held out):
```bash
# Generate 500 examples
model-train generate my-project --count 500

# Manually split: 400 train, 100 test
# Keep test set separate
```

**2. Train and evaluate**:
```bash
model-train train start my-project

# Test on held-out examples
# Measure: XML tag accuracy, response quality, reasoning coherence
```

**3. Iterate**:
- If test accuracy < 80%: Generate more diverse data
- If test accuracy > 95%: Try harder examples
- If model memorizes: Reduce epochs or add regularization

---

## Troubleshooting Common Scenarios

### Scenario 1: Model Forgets XML Tags

**Symptoms**:
- Sometimes includes tags, sometimes doesn't
- Tags appear incorrectly formatted
- Missing closing tags

**Solutions**:
1. Increase training data (add 100-200 more examples)
2. Ensure 100% of training examples have correct XML
3. Increase number of epochs (3 → 5)
4. Lower temperature during generation (0.8 → 0.6)
5. Add more examples with explicit XML in context

### Scenario 2: Repetitive or Generic Responses

**Symptoms**:
- Model gives same response to different inputs
- Responses are vague and non-specific
- Lack of variety in outputs

**Solutions**:
1. Increase generation temperature (0.7 → 0.9)
2. Add more diverse examples to training data
3. Include more edge cases and variations
4. Reduce training epochs (may be overfitting)
5. Use different AI models for generation (try Claude if using Ollama)

### Scenario 3: Poor Reasoning Quality

**Symptoms**:
- Thinking tags exist but don't show real reasoning
- Conclusions don't follow from thinking
- Logical errors or contradictions

**Solutions**:
1. Use more capable generation model (Llama-2 → Claude/GPT-4)
2. Add more complex examples to dataset
3. Increase LoRA rank (16 → 32)
4. Use larger base model (7B → 13B)
5. Train for more epochs (3 → 5-7)

### Scenario 4: Training is Very Slow

**Symptoms**:
- Training taking hours per epoch
- System becomes unresponsive
- Estimated time shows days

**Solutions**:
1. Reduce batch size (4 → 2 → 1)
2. Reduce max_seq_length (2048 → 1024)
3. Use smaller model (13B → 7B)
4. Enable gradient checkpointing (should be default)
5. Verify GPU is being used: `nvidia-smi` or `torch.cuda.is_available()`

### Scenario 5: Out of Memory Errors

**Symptoms**:
- "CUDA out of memory"
- "RuntimeError: CUDA error"
- System crashes during training

**Solutions**:
```python
# Immediate fixes:
1. Reduce batch_size to 1
2. Reduce max_seq_length to 1024 or 512
3. Close other GPU applications
4. Restart backend to clear memory

# Longer-term:
5. Use smaller model
6. Enable 4-bit quantization (should be default)
7. Add gradient checkpointing
8. Increase swap space (Linux)
```

---

## Next Steps

After completing this guide, you should be able to:
- ✓ Create and configure projects
- ✓ Design effective XML patterns
- ✓ Generate high-quality training data
- ✓ Train models with appropriate parameters
- ✓ Troubleshoot common issues
- ✓ Choose the right model for your task

**Continue Learning**:
1. Read [EXAMPLES.md](EXAMPLES.md) for more real-world use cases
2. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for programmatic access
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand system internals
4. Visit [FAQ.md](FAQ.md) for additional troubleshooting

**Community Resources**:
- Share your projects in GitHub Discussions
- Report issues or request features on GitHub Issues
- Contribute examples and improvements via Pull Requests

Happy training! 🚀
