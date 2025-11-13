# Frequently Asked Questions (FAQ)

Common questions, troubleshooting tips, and solutions for the Model Fine-Tuning Application.

## Table of Contents

### General Questions
1. [What can I do with this application?](#what-can-i-do-with-this-application)
2. [Do I need programming experience?](#do-i-need-programming-experience)
3. [How much does it cost to use?](#how-much-does-it-cost-to-use)
4. [What hardware do I need?](#what-hardware-do-i-need)
5. [Can I use this on a CPU-only machine?](#can-i-use-this-on-a-cpu-only-machine)

### Setup & Installation
6. [Installation fails with package errors](#installation-fails-with-package-errors)
7. [Backend won't start](#backend-wont-start)
8. [Frontend shows connection error](#frontend-shows-connection-error)
9. [Ollama connection refused](#ollama-connection-refused)
10. [HuggingFace token issues](#huggingface-token-issues)

### Data Generation
11. [Generation is very slow](#generation-is-very-slow)
12. [Generated data doesn't have XML tags](#generated-data-doesnt-have-xml-tags)
13. [How many examples do I need?](#how-many-examples-do-i-need)
14. [Can I mix different AI providers?](#can-i-mix-different-ai-providers)
15. [Examples are too repetitive](#examples-are-too-repetitive)

### Training
16. [CUDA out of memory error](#cuda-out-of-memory-error)
17. [Training is extremely slow](#training-is-extremely-slow)
18. [Loss is not decreasing](#loss-is-not-decreasing)
19. [Training crashes mid-process](#training-crashes-mid-process)
20. [How long does training take?](#how-long-does-training-take)

### Model Quality
21. [Model doesn't follow XML patterns](#model-doesnt-follow-xml-patterns)
22. [Responses are generic/repetitive](#responses-are-genericrepetitive)
23. [Model outputs nonsense](#model-outputs-nonsense)
24. [How do I improve model quality?](#how-do-i-improve-model-quality)
25. [Can I continue training an existing model?](#can-i-continue-training-an-existing-model)

### Performance & Optimization
26. [How to speed up training?](#how-to-speed-up-training)
27. [How to reduce memory usage?](#how-to-reduce-memory-usage)
28. [Best model for limited hardware?](#best-model-for-limited-hardware)
29. [Hardware requirements breakdown](#hardware-requirements-breakdown)

### Advanced Usage
30. [Can I use custom base models?](#can-i-use-custom-base-models)
31. [How to export for production?](#how-to-export-for-production)
32. [Can I run multiple trainings simultaneously?](#can-i-run-multiple-trainings-simultaneously)
33. [How to version control my models?](#how-to-version-control-my-models)

---

## General Questions

### What can I do with this application?

Fine-tune large language models to:
- Follow specific XML output patterns
- Specialize in particular domains (coding, customer support, etc.)
- Generate structured, consistent responses
- Implement custom behaviors and personalities

**Use cases**:
- Build chatbots with structured thinking
- Create domain-specific assistants (Minecraft, SQL, etc.)
- Format and analyze code
- Extract structured data from text
- Educational tutoring systems

### Do I need programming experience?

**Short answer**: Not required, but helpful.

**Web UI**: No programming needed
- Point-and-click interface
- Visual XML editor
- Progress tracking

**TUI**: Basic comfort with terminal
- Navigate with keyboard
- Understand basic concepts

**CLI**: Some programming helpful
- Comfortable with command line
- Understand bash/shell basics

**For customization**: Python knowledge needed
- Modify core logic
- Add new features
- Custom AI providers

### How much does it cost to use?

**Free options**:
- ✅ Ollama (local, completely free)
- ✅ Training (uses your hardware)
- ✅ Storage (local files)

**Paid options**:
- Claude API: ~$0.50-$2.00 per 500 examples
- OpenAI API: ~$0.30-$1.50 per 500 examples
- Cloud GPU: $0.50-$3.00/hour (if no local GPU)

**Budget recommendations**:
- **$0/month**: Use Ollama for generation, train on your GPU
- **~$10/month**: Claude for high-quality generation, local training
- **~$50/month**: Cloud GPUs if no local hardware

### What hardware do I need?

**Minimum (CPU only)**:
- 16GB RAM
- 50GB free disk space
- Quad-core processor
- ⚠️ Training will be VERY slow (10-50x slower)

**Recommended (GPU)**:
- NVIDIA GPU with 8GB+ VRAM (GTX 1070, RTX 3060, etc.)
- 16GB system RAM
- 100GB free disk space
- ✅ Good training speed

**Optimal**:
- NVIDIA GPU with 16-24GB VRAM (RTX 3090, 4090, A5000)
- 32GB+ system RAM
- 200GB+ SSD storage
- ✅ Fast training, can use larger models

**Mac M1/M2/M3**:
- 16GB+ unified memory
- ✅ Good performance with MPS (Metal)
- Limited to smaller models (7B-13B)

### Can I use this on a CPU-only machine?

**Yes, but**:
- ✅ Data generation works fine
- ✅ All interfaces work
- ⚠️ Training is 10-50x slower
- ⚠️ Limited to smaller models
- ⚠️ May take days instead of hours

**Tips for CPU training**:
1. Use smallest model (Phi-2, 2.7B)
2. Reduce batch size to 1
3. Train overnight/over weekend
4. Consider cloud GPU for final training
5. Start with very small datasets (100 examples)

---

## Setup & Installation

### Installation fails with package errors

**Error**: `ERROR: Could not find a version that satisfies the requirement...`

**Solutions**:

1. **Update pip**:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Use Python 3.10 or 3.11** (not 3.12+):
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install PyTorch first** (for GPU):
   ```bash
   # For CUDA 12.1
   pip install torch --index-url https://download.pytorch.org/whl/cu121

   # Then install other requirements
   pip install -r requirements.txt
   ```

4. **System dependencies** (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install python3-dev build-essential
   ```

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions**:

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Reinstall dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Python version**:
   ```bash
   python --version  # Should be 3.10+
   ```

4. **Run with module syntax**:
   ```bash
   python -m backend.main
   ```

**Error**: `Address already in use`

**Solutions**:
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Or use different port
API_PORT=8001 python -m backend.main
```

### Frontend shows connection error

**Error**: `Network Error` or `Cannot connect to backend`

**Solutions**:

1. **Verify backend is running**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

2. **Check CORS settings** in `backend/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],  # Frontend URL
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Update API URL** in frontend (`frontend/src/services/api.js`):
   ```javascript
   const API_URL = "http://localhost:8000/api/v1";
   ```

4. **Clear browser cache** and restart dev server

### Ollama connection refused

**Error**: `Connection refused at http://localhost:11434`

**Solutions**:

1. **Start Ollama**:
   ```bash
   ollama serve
   ```

2. **Check if running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **Pull a model**:
   ```bash
   ollama pull llama2
   ```

4. **Update Ollama URL** if using remote:
   ```bash
   export OLLAMA_BASE_URL=http://192.168.1.100:11434
   ```

### HuggingFace token issues

**Error**: `401 Unauthorized` when downloading models

**Solutions**:

1. **Create token** at https://huggingface.co/settings/tokens
   - Select "Read" access
   - Copy token

2. **Add to `.env`**:
   ```bash
   HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx
   ```

3. **Login via CLI**:
   ```bash
   huggingface-cli login
   ```

4. **Test access**:
   ```python
   from huggingface_hub import HfApi
   api = HfApi(token="your_token")
   api.whoami()
   ```

---

## Data Generation

### Generation is very slow

**Problem**: Takes hours to generate 100 examples

**Causes & Solutions**:

1. **Using Ollama** (slower but free):
   - Expected: 20-40 examples/hour
   - Solution: Switch to Claude/GPT for faster generation
   - Or: Run overnight with larger batch

2. **Low temperature** causing retries:
   - Increase temperature: 0.5 → 0.7 → 0.8
   - Reduces validation failures

3. **Network issues** (for cloud APIs):
   - Check internet connection
   - Use smaller batch size
   - Add retry logic

4. **Complex XML patterns**:
   - Simplify patterns for initial generation
   - Add complexity gradually

**Speed comparison**:
- Ollama (local): 20-40 examples/hour
- Claude: 100-200 examples/hour
- GPT-4: 80-150 examples/hour

### Generated data doesn't have XML tags

**Problem**: Examples are missing required XML tags

**Solutions**:

1. **Lower temperature**:
   ```bash
   model-train generate my-project --temperature 0.5
   ```

2. **Simplify XML patterns**:
   - Start with 1-2 tags
   - Add more tags gradually
   - Avoid overly complex nesting

3. **Better AI provider**:
   - Ollama → Claude/GPT
   - Claude better at following XML structure

4. **Add examples to patterns**:
   ```bash
   model-train xml add-tag my-project thinking \
     --description "Internal reasoning" \
     --example "<thinking>I should analyze this carefully...</thinking>"
   ```

5. **Review and filter**:
   ```python
   # Manually filter out bad examples before training
   import json
   with open('dataset.json') as f:
       data = json.load(f)

   # Keep only examples with all required tags
   filtered = [ex for ex in data if all(
       f"<{tag}>" in ex['conversations'][1]['value']
       for tag in ['thinking', 'response']
   )]
   ```

### How many examples do I need?

**Short answer**: 300-500 for most tasks

**Detailed guide**:

| Task Complexity | Examples Needed |
|-----------------|-----------------|
| Simple (1-2 XML tags, basic chat) | 100-300 |
| Medium (3-4 tags, domain-specific) | 300-500 |
| Complex (5+ tags, reasoning, code) | 500-1000 |
| Very complex (multi-domain, creative) | 1000-2000 |

**Quality matters more than quantity**:
- ✅ 200 diverse, high-quality examples > 1000 repetitive ones
- ✅ Cover edge cases and variations
- ✅ Include different difficulty levels

**How to tell if you need more**:
- Model forgets XML tags → Add 100-200 examples
- Generic responses → Add more diverse examples
- Poor on edge cases → Add 50-100 edge case examples

### Can I mix different AI providers?

**Yes!** Generate different parts with different providers:

```bash
# Use Ollama for bulk generation (free)
model-train generate my-project --count 300 --provider ollama

# Use Claude for complex examples (paid, higher quality)
model-train generate my-project --count 100 --provider anthropic

# Manually merge datasets
cat datasets/my-project/*.json > datasets/combined.json
```

**Benefits**:
- Save money (Ollama for simple, Claude for complex)
- Diverse outputs (different "voices")
- Best of both worlds

### Examples are too repetitive

**Problem**: Generated examples are very similar

**Solutions**:

1. **Increase temperature**:
   ```bash
   model-train generate my-project --temperature 0.9
   ```

2. **Vary prompts** in objective:
   - Instead of: "Generate a chatbot response"
   - Use: "Generate varied chatbot responses including casual, formal, technical, and empathetic styles"

3. **Use different AI models**:
   - Mix Ollama, Claude, and GPT outputs
   - Each has different "style"

4. **Generate in multiple batches**:
   ```bash
   # Batch 1: Casual tone
   model-train generate my-project --count 100 --mode casual

   # Batch 2: Formal tone
   model-train generate my-project --count 100 --mode formal

   # Batch 3: Technical
   model-train generate my-project --count 100 --mode technical
   ```

---

## Training

### CUDA out of memory error

**Error**: `RuntimeError: CUDA out of memory. Tried to allocate X.XX GiB`

**Immediate fixes**:

1. **Reduce batch size**:
   ```json
   {
     "batch_size": 1  // Smallest possible
   }
   ```

2. **Reduce sequence length**:
   ```json
   {
     "max_seq_length": 1024  // Down from 2048
   }
   ```

3. **Enable gradient checkpointing** (should be default):
   ```json
   {
     "use_gradient_checkpointing": true
   }
   ```

4. **Use gradient accumulation**:
   ```json
   {
     "batch_size": 1,
     "gradient_accumulation_steps": 8
     // Effective batch size = 1 × 8 = 8
   }
   ```

5. **Close other GPU applications**:
   ```bash
   # Check GPU usage
   nvidia-smi

   # Kill processes if needed
   kill -9 <PID>
   ```

6. **Restart to clear memory**:
   ```bash
   # Restart backend to clear any lingering GPU memory
   pkill -f "python -m backend.main"
   python -m backend.main
   ```

**Long-term solutions**:
- Use smaller model (13B → 7B)
- Ensure 4-bit quantization is enabled
- Upgrade GPU (if budget allows)

### Training is extremely slow

**Problem**: Training takes days instead of hours

**Diagnostics**:

1. **Check GPU is being used**:
   ```bash
   nvidia-smi
   # Should show python process using GPU
   ```

   ```python
   import torch
   print(torch.cuda.is_available())  # Should be True
   print(torch.cuda.get_device_name(0))  # Shows GPU name
   ```

2. **Check CPU usage** (should be <50% if GPU working):
   ```bash
   htop  # Linux
   top   # Mac
   ```

**Solutions**:

1. **Reduce max_seq_length**:
   - 2048 → 1024 = 2-4x faster
   - 1024 → 512 = 2-4x faster

2. **Increase batch size** (if memory allows):
   - batch_size 1 → 2 = 2x faster
   - batch_size 2 → 4 = 2x faster

3. **Use better GPU**:
   - Cloud GPU (Vast.ai, RunPod, Lambda Labs)
   - ~$0.50-$2/hour for RTX 3090/4090

4. **Enable bf16** (on newer GPUs):
   ```json
   {
     "bf16": true  // Better than fp16 on A100/H100
   }
   ```

5. **Reduce logging**:
   ```json
   {
     "logging_steps": 10  // Log less frequently
   }
   ```

**Expected speeds**:
- GTX 1070 (8GB): ~5-10 examples/minute
- RTX 3060 (12GB): ~10-20 examples/minute
- RTX 3090 (24GB): ~20-40 examples/minute
- RTX 4090 (24GB): ~30-50 examples/minute
- A100 (80GB): ~50-100 examples/minute

### Loss is not decreasing

**Problem**: Training loss stays high or increases

**Causes & Solutions**:

1. **Learning rate too high**:
   ```json
   {
     "learning_rate": 1e-4  // Reduce from 2e-4
   }
   ```

2. **Learning rate too low**:
   ```json
   {
     "learning_rate": 3e-4  // Increase from 2e-4
   }
   ```

3. **Bad training data**:
   - Review dataset quality
   - Remove duplicates
   - Ensure XML tags are consistent

4. **Need more epochs**:
   ```json
   {
     "num_train_epochs": 5  // Increase from 3
   }
   ```

5. **Model capacity too low**:
   ```json
   {
     "lora_r": 32  // Increase from 16
   }
   ```

6. **Check for NaN/Inf**:
   - If loss shows as `nan`, learning rate is definitely too high
   - Restart training with lower learning rate

**Good loss values**:
- Initial: 1.5-3.0
- After epoch 1: 0.8-1.5
- After epoch 3: 0.3-0.8
- Final: 0.2-0.6

### Training crashes mid-process

**Problem**: Training stops unexpectedly

**Common causes**:

1. **Out of memory**:
   - Reduce batch size
   - Reduce sequence length

2. **System killed process** (OOM killer):
   ```bash
   # Check system logs
   dmesg | grep -i kill  # Linux
   ```
   - Solution: Reduce overall memory usage

3. **Power/thermal issues**:
   - Check GPU temperature
   - Ensure adequate cooling
   - Check power supply

4. **Dataset corruption**:
   - Validate dataset format
   - Re-generate if needed

5. **Disk full**:
   ```bash
   df -h  # Check disk space
   ```
   - Clean up old models/datasets

**Prevention**:
- Save more frequently (reduce `save_steps`)
- Use smaller batch sizes
- Monitor system resources
- Run in tmux/screen for SSH sessions

### How long does training take?

**Varies greatly** by:
- Dataset size
- Model size
- Hardware
- Training parameters

**Estimates for 300 examples, 3 epochs**:

| Hardware | 7B Model | 13B Model |
|----------|----------|-----------|
| RTX 3060 (12GB) | 1-2 hours | 2-4 hours |
| RTX 3090 (24GB) | 30-60 min | 1-2 hours |
| RTX 4090 (24GB) | 20-40 min | 45-90 min |
| A100 (80GB) | 15-30 min | 30-60 min |
| CPU (16GB) | 24-48 hours | 48-96 hours |
| Mac M1 (16GB) | 3-6 hours | 6-12 hours |

**For 1000 examples, 5 epochs**: Multiply by 5-6x

---

## Model Quality

### Model doesn't follow XML patterns

**Problem**: Trained model forgets XML tags or uses them inconsistently

**Solutions**:

1. **Check training data**:
   ```python
   # Verify 100% of examples have XML tags
   import json
   with open('dataset.json') as f:
       data = json.load(f)

   missing_tags = 0
   for ex in data:
       response = ex['conversations'][1]['value']
       if '<thinking>' not in response or '</thinking>' not in response:
           missing_tags += 1

   print(f"Missing tags: {missing_tags}/{len(data)}")
   ```

2. **Generate more data** (100-200 more examples)

3. **Train for more epochs** (3 → 5 → 7)

4. **Increase LoRA rank** (16 → 32)

5. **Lower temperature during generation** (0.8 → 0.6)

6. **Use better base model**:
   - Llama-2 → Mistral → Qwen2.5

7. **Add XML examples** to every training example:
   - Ensure consistency
   - No exceptions

### Responses are generic/repetitive

**Problem**: Model gives the same answer for different inputs

**Solutions**:

1. **More diverse training data**:
   - Vary input types
   - Include edge cases
   - Different difficulty levels

2. **Higher generation temperature** (0.7 → 0.9)

3. **More training examples** (300 → 500 → 800)

4. **Less training** (might be overfitting):
   - Reduce epochs: 5 → 3
   - Check if validation loss increases while training loss decreases

5. **Better prompting at inference**:
   ```python
   # Add variation to prompts
   prompt = f"<context>Different each time</context>\n{user_input}"
   ```

### Model outputs nonsense

**Problem**: Model generates gibberish or off-topic responses

**Causes**:

1. **Overtrained** (too many epochs):
   - Model memorized and collapsed
   - Solution: Reduce epochs or learning rate

2. **Learning rate too high**:
   - Model failed to converge
   - Solution: Start over with lower LR (2e-4 → 1e-4)

3. **Corrupted training data**:
   - Bad examples in dataset
   - Solution: Review and clean data

4. **Wrong model architecture**:
   - Base model incompatible
   - Solution: Use official Unsloth models

5. **Insufficient training**:
   - Model didn't learn
   - Solution: Train longer or with more data

**Recovery**:
- Start fresh with cleaned data
- Use lower learning rate
- Reduce epochs to 3-5
- Verify training loss decreases smoothly

### How do I improve model quality?

**Systematic approach**:

1. **Evaluate current quality**:
   - Test on 20-50 diverse inputs
   - Identify specific weaknesses
   - Categorize errors

2. **Target weak areas**:
   - Generate 50-100 examples addressing weaknesses
   - Add to dataset
   - Retrain

3. **Increase data quality**:
   - Use better AI provider (Ollama → Claude)
   - Lower generation temperature
   - Manually review and filter

4. **Optimize parameters**:
   - Increase LoRA rank if complex
   - Adjust learning rate if not converging
   - Add more epochs if undertrained

5. **Iterate**:
   - Train → Test → Identify issues → Generate targeted data → Repeat

### Can I continue training an existing model?

**Currently**: Not directly supported

**Workarounds**:

1. **Generate new data** and retrain from scratch:
   - Merge old and new datasets
   - Train fresh model

2. **Manual adapter merging** (advanced):
   ```python
   from peft import PeftModel

   # Load base model
   model = AutoModelForCausalLM.from_pretrained("base_model")

   # Load first adapter
   model = PeftModel.from_pretrained(model, "adapter1")

   # Merge
   model = model.merge_and_unload()

   # Continue training
   ```

3. **Planned for future version**:
   - Resume training from checkpoint
   - Incremental training support

---

## Performance & Optimization

### How to speed up training?

**Immediate optimizations**:

1. **Use faster GPU** (if available/affordable)

2. **Optimize batch size**:
   ```json
   {
     "batch_size": 4,  // Max your GPU can handle
     "gradient_accumulation_steps": 1  // Reduce if batch_size high
   }
   ```

3. **Reduce sequence length**:
   ```json
   {
     "max_seq_length": 1024  // If examples are typically short
   }
   ```

4. **Enable bf16** (newer GPUs):
   ```json
   {
     "bf16": true  // Faster than fp16
   }
   ```

5. **Reduce logging**:
   ```json
   {
     "logging_steps": 10  // Log less frequently
   }
   ```

6. **Disable unused features**:
   ```json
   {
     "eval_steps": null,  // Skip evaluation
     "save_steps": 500    // Save less frequently
   }
   ```

**Expected speedup**:
- Batch size 1 → 4: 2-3x faster
- Sequence 2048 → 1024: 2-3x faster
- fp16 → bf16: 10-20% faster
- Combined: 5-8x faster

### How to reduce memory usage?

**GPU memory reduction**:

1. **Smallest batch size**:
   ```json
   {"batch_size": 1}
   ```

2. **Smaller sequence length**:
   ```json
   {"max_seq_length": 512}  // Or even 256
   ```

3. **Gradient accumulation**:
   ```json
   {
     "batch_size": 1,
     "gradient_accumulation_steps": 8
   }
   ```

4. **4-bit quantization** (should be default):
   ```json
   {"load_in_4bit": true}
   ```

5. **Gradient checkpointing** (should be default):
   ```json
   {"use_gradient_checkpointing": true}
   ```

6. **Smaller LoRA rank**:
   ```json
   {"lora_r": 8}  // Minimal but works
   ```

**System memory**:
- Close other applications
- Increase swap space (Linux)
- Use smaller dataset for testing

### Best model for limited hardware?

**For 4GB VRAM**:
- Phi-2 (2.7B)
- TinyLlama (1.1B)
- Settings: batch_size=1, max_seq_length=512

**For 8GB VRAM**:
- Llama-2-7B-4bit
- Mistral-7B-4bit
- Settings: batch_size=2, max_seq_length=1024

**For 12GB VRAM**:
- Llama-2-7B-4bit
- Mistral-7B-4bit
- Qwen2.5-7B-4bit
- Settings: batch_size=4, max_seq_length=2048

**For 16GB+ VRAM**:
- Llama-2-13B-4bit
- Qwen2.5-14B-4bit
- Settings: batch_size=4, max_seq_length=2048

**For CPU only**:
- Phi-2 (2.7B)
- TinyLlama (1.1B)
- Be patient (very slow)

### Hardware requirements breakdown

**Component breakdown**:

| Component | Minimum | Recommended | Optimal |
|-----------|---------|-------------|---------|
| **GPU VRAM** | 4GB | 8-12GB | 16-24GB |
| **System RAM** | 16GB | 16-32GB | 32-64GB |
| **Storage** | 50GB | 100-200GB | 500GB+ SSD |
| **CPU** | 4 cores | 6-8 cores | 12+ cores |
| **Internet** | 10 Mbps | 50 Mbps | 100+ Mbps |

**GPU recommendations**:
- Budget: GTX 1660 Super (6GB), RTX 3060 (12GB)
- Mid-range: RTX 3070 (8GB), RTX 3080 (10-12GB)
- High-end: RTX 3090 (24GB), RTX 4090 (24GB)
- Professional: A5000 (24GB), A100 (40-80GB)

**Cloud GPU options**:
- Vast.ai: $0.20-$1.50/hour
- RunPod: $0.30-$2.00/hour
- Lambda Labs: $0.50-$3.00/hour
- Google Colab: Free tier + $10/month Pro

---

## Advanced Usage

### Can I use custom base models?

**Yes!** Any HuggingFace model supported by Unsloth:

```bash
model-train project create my-project \
  --model "your-org/your-model-name" \
  --objective "Your objective"
```

**Compatible architectures**:
- ✅ Llama 2, Llama 3
- ✅ Mistral, Mixtral
- ✅ Qwen, Qwen2, Qwen2.5
- ✅ Gemma, Gemma 2
- ✅ Phi, Phi-2
- ✅ Yi, DeepSeek

**Check compatibility**:
```python
from unsloth import FastLanguageModel

# This will fail if incompatible
model, tokenizer = FastLanguageModel.from_pretrained(
    "your-org/your-model-name",
    max_seq_length=2048,
    load_in_4bit=True
)
```

### How to export for production?

**Option 1: GGUF for Ollama**:
```bash
# Export to GGUF
model-train model export my-project \
  --format gguf \
  --quantization q4_k_m

# Create Ollama model
cd models/my-project
ollama create my-model -f Modelfile

# Test
ollama run my-model "Hello!"
```

**Option 2: HuggingFace format**:
```python
# Model already saved in HuggingFace format
# Location: models/my-project/

# Load and use
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("models/my-project")
tokenizer = AutoTokenizer.from_pretrained("models/my-project")
```

**Option 3: Merge and quantize**:
```python
from unsloth import FastLanguageModel

# Load with adapters
model, tokenizer = FastLanguageModel.from_pretrained(
    "models/my-project/adapter"
)

# Merge LoRA weights
model.save_pretrained_merged(
    "models/my-project-merged",
    tokenizer,
    save_method="merged_16bit"
)

# Optionally quantize further
```

### Can I run multiple trainings simultaneously?

**Currently**: Not recommended (v0.1.0)

**Reasons**:
- GPU memory conflicts
- Job tracking in-memory only
- May cause crashes

**Workarounds**:

1. **Sequential training**:
   - Queue jobs manually
   - Train one at a time

2. **Multiple GPUs**:
   ```bash
   # Terminal 1 (GPU 0)
   CUDA_VISIBLE_DEVICES=0 python -m backend.main --port 8000

   # Terminal 2 (GPU 1)
   CUDA_VISIBLE_DEVICES=1 python -m backend.main --port 8001
   ```

3. **Separate machines**:
   - Run backend on multiple servers
   - Each handles different projects

**Planned for v0.2.0**:
- Proper job queue (Celery)
- Multi-GPU support
- Concurrent training

### How to version control my models?

**Git LFS for models**:
```bash
# Install Git LFS
git lfs install

# Track model files
git lfs track "models/**/*.bin"
git lfs track "models/**/*.safetensors"

# Add and commit
git add .gitattributes models/
git commit -m "Add trained model v1.0"
```

**DVC for large files**:
```bash
# Install DVC
pip install dvc

# Initialize
dvc init

# Track models
dvc add models/my-project
git add models/my-project.dvc .gitignore
git commit -m "Add model with DVC"

# Push to remote storage
dvc remote add -d myremote s3://mybucket/models
dvc push
```

**Naming convention**:
```
models/
├── my-project-v1.0-2023-11-13/
├── my-project-v1.1-2023-11-20/
├── my-project-v2.0-2023-12-01/
└── my-project-prod/  # Symlink to current production
```

**Model metadata**:
```json
// models/my-project/metadata.json
{
  "version": "1.0.0",
  "created_at": "2023-11-13T10:00:00Z",
  "base_model": "unsloth/llama-2-7b-bnb-4bit",
  "training_data": "dataset_20231113.json",
  "num_examples": 500,
  "epochs": 5,
  "lora_rank": 32,
  "performance_metrics": {
    "validation_loss": 0.42,
    "accuracy": 0.95
  },
  "notes": "Production model for customer support"
}
```

---

## Getting Help

### Still having issues?

1. **Check documentation**:
   - [README.md](README.md) - Quick start
   - [USER_GUIDE.md](USER_GUIDE.md) - Detailed tutorials
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design

2. **Search issues**: Check if someone already had your problem
   - https://github.com/your-repo/issues

3. **Ask community**:
   - GitHub Discussions
   - Discord (if available)

4. **Report bug**:
   - Include: OS, Python version, GPU info
   - Provide: Error message, steps to reproduce
   - Attach: Logs if possible

### Debug mode

Enable verbose logging:
```bash
# Set environment variable
export DEBUG=1
export LOG_LEVEL=DEBUG

# Run backend
python -m backend.main

# Or for specific run
DEBUG=1 model-train generate my-project --count 100
```

---

**Last Updated**: 2023-11-13
**Version**: 0.1.0

Have a question not answered here? [Open an issue](https://github.com/your-repo/issues/new) or [start a discussion](https://github.com/your-repo/discussions/new)!
