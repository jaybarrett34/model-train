# Model Train CLI - Complete Command Reference

## Quick Installation

```bash
pip install -e .
model-train --help
```

## All Commands at a Glance

### Project Commands
```bash
model-train project list                                    # List all projects
model-train project create <name> --objective "..."         # Create project
model-train project show <name>                             # Show project details
model-train project delete <name>                           # Delete project
```

### XML Pattern Commands
```bash
model-train xml add-tag <project> <tag> -d "..."           # Add XML tag
model-train xml remove-tag <project> <tag>                  # Remove XML tag
model-train xml show <project>                              # Show all tags
```

### Data Generation
```bash
model-train generate <project>                              # Generate 100 examples (default)
model-train generate <project> --count 500                  # Generate 500 examples
model-train generate <project> --validate                   # Generate and validate
```

### Training Commands
```bash
model-train train start <project>                           # Start training
model-train train status <job-id>                           # Check status once
model-train train status <job-id> --watch                   # Watch in real-time
model-train train cancel <job-id>                           # Cancel training
```

### Model Commands
```bash
model-train model list                                      # List models
model-train model download <name>                           # Download model
model-train model export <project> --format gguf            # Export model
```

### Analysis Commands
```bash
model-train analyze dataset <project>                       # Analyze dataset
model-train analyze dataset <project> --estimate-size       # With size estimate
```

### Utilities
```bash
model-train tui                                            # Launch TUI (coming soon)
model-train completion                                      # Shell completion setup
model-train --version                                       # Show version
```

## Global Flags (Work with all commands)

```bash
--api-url URL          # Backend API URL (default: http://localhost:8000)
--verbose, -v          # Enable verbose/debug output
--json                 # Output as JSON
--help                 # Show help for any command
```

## Complete Command Details

### `model-train project create`

```bash
model-train project create <name> \
  --objective "Description of what you want to train" \
  --model "unsloth/llama-2-7b-bnb-4bit" \
  --format sharegpt \
  --provider ollama \
  --ai-model llama2
```

**Options:**
- `--objective, -o` (required) - Training objective description
- `--model, -m` - Base model (default: unsloth/llama-2-7b-bnb-4bit)
- `--format, -f` - Dataset format: sharegpt or alpaca (default: sharegpt)
- `--provider` - AI provider: ollama, anthropic, or openai (default: ollama)
- `--ai-model` - AI model for synthesis (default: llama2)

**Example:**
```bash
model-train project create xml-formatter \
  --objective "Train model to format XML properly" \
  --model "unsloth/mistral-7b-bnb-4bit" \
  --provider anthropic \
  --ai-model "claude-3-opus-20240229"
```

---

### `model-train xml add-tag`

```bash
model-train xml add-tag <project> <tag-name> \
  --description "What this tag is for" \
  --constraint "Validation rules" \
  --example "<tag>example</tag>"
```

**Options:**
- `--description, -d` (required) - Tag description
- `--constraint, -c` - Validation constraint
- `--example, -e` - Example usage (can be repeated)

**Example:**
```bash
model-train xml add-tag my-project thinking \
  --description "Internal reasoning process" \
  --constraint "Must appear before output tags" \
  --example "<thinking>Let me analyze...</thinking>" \
  --example "<thinking>I should consider...</thinking>"
```

---

### `model-train generate`

```bash
model-train generate <project> \
  --count 500 \
  --batch-size 25 \
  --temperature 0.8 \
  --mode diverse \
  --validate
```

**Options:**
- `--count, -n` - Number of examples (default: 100)
- `--batch-size, -b` - Examples per batch (default: 10)
- `--temperature, -t` - AI temperature 0.0-2.0
- `--mode` - Generation mode: pseudorandom, diverse, or focused
- `--validate` - Validate generated data

**Example:**
```bash
# Generate 1000 examples with validation
model-train generate my-project \
  --count 1000 \
  --batch-size 50 \
  --temperature 1.0 \
  --validate
```

---

### `model-train train start`

```bash
model-train train start <project> \
  --dataset data.json \
  --steps 1000 \
  --lora-rank 32 \
  --learning-rate 0.0002 \
  --batch-size 4 \
  --epochs 3
```

**Options:**
- `--dataset, -d` - Dataset filename (uses latest if not specified)
- `--steps, -s` - Number of training steps
- `--lora-rank, -r` - LoRA rank (default: 16)
- `--learning-rate, -lr` - Learning rate
- `--batch-size, -b` - Batch size
- `--epochs, -e` - Number of epochs

**Example:**
```bash
# Start training with custom parameters
model-train train start my-project \
  --lora-rank 64 \
  --learning-rate 0.0001 \
  --epochs 5
```

---

### `model-train train status`

```bash
model-train train status <job-id> \
  --watch \
  --interval 5
```

**Options:**
- `--watch, -w` - Watch status updates in real-time
- `--interval, -i` - Update interval in seconds (default: 5)

**Example:**
```bash
# Watch training progress with 10-second updates
model-train train status abc123 --watch --interval 10
```

---

### `model-train model download`

```bash
model-train model download <model-name> \
  --revision main \
  --quantization 4bit
```

**Options:**
- `--revision, -r` - Model revision/branch
- `--quantization, -q` - Quantization: 4bit, 8bit, or none

**Example:**
```bash
# Download 4-bit quantized model
model-train model download unsloth/llama-2-7b \
  --quantization 4bit
```

---

### `model-train model export`

```bash
model-train model export <project> \
  --format gguf \
  --quantization q4_0 \
  --output my-model.gguf
```

**Options:**
- `--format, -f` - Export format: gguf, safetensors, or pytorch
- `--quantization, -q` - GGUF quantization: q4_0, q4_1, q5_0, q5_1, q8_0
- `--output, -o` - Output filename

**Example:**
```bash
# Export to GGUF with Q4 quantization
model-train model export my-project \
  --format gguf \
  --quantization q4_0
```

---

### `model-train analyze dataset`

```bash
model-train analyze dataset <project> \
  --estimate-size \
  --validate \
  --stats
```

**Options:**
- `--estimate-size` - Estimate final model size
- `--validate` - Validate dataset quality
- `--stats` - Show detailed statistics

**Example:**
```bash
# Full analysis
model-train analyze dataset my-project \
  --estimate-size \
  --validate \
  --stats
```

## Common Patterns

### Complete Workflow

```bash
# 1. Create project
model-train project create my-project \
  --objective "My training goal"

# 2. Add XML patterns
model-train xml add-tag my-project thinking -d "Reasoning"
model-train xml add-tag my-project output -d "Final answer"

# 3. Generate data
model-train generate my-project --count 500

# 4. Start training
JOB_ID=$(model-train train start my-project --json | jq -r '.job_id')

# 5. Monitor progress
model-train train status $JOB_ID --watch

# 6. Export model
model-train model export my-project --format gguf
```

### JSON Output for Scripting

```bash
# Get all project names
model-train project list --json | jq -r '.projects[].name'

# Check if training is done
STATUS=$(model-train train status job123 --json | jq -r '.status')

# Get latest dataset
DATASET=$(model-train project show my-project --json | \
  jq -r '.datasets | sort_by(.created_at) | .[-1].filename')
```

### Verbose Debugging

```bash
# Debug project creation
model-train --verbose project create test \
  --objective "Debug test"

# See API requests
model-train --verbose project list
```

### Confirmation Skipping

```bash
# Delete without confirmation
model-train project delete old-project --yes

# Remove tag without confirmation
model-train xml remove-tag my-project old-tag --yes

# Cancel training without confirmation
model-train train cancel job123 --yes
```

## Environment Variables

```bash
# Set API URL
export API_URL="http://localhost:8000"

# Enable debug mode
export DEBUG=1

# Use in commands
model-train project list
```

## Shell Completion

### Bash
```bash
# Add to ~/.bashrc
eval "$(_MODEL_TRAIN_COMPLETE=bash_source model-train)"
```

### Zsh
```bash
# Add to ~/.zshrc
eval "$(_MODEL_TRAIN_COMPLETE=zsh_source model-train)"
```

### Fish
```bash
# Add to ~/.config/fish/config.fish
eval (env _MODEL_TRAIN_COMPLETE=fish_source model-train)
```

## Error Messages

The CLI provides helpful error messages:

```bash
# No backend running
✗ Cannot connect to API at http://localhost:8000. Is the backend running?

# Project not found
✗ API Error: Project 'missing' not found

# Missing required option
Error: Missing option '--objective' / '-o'.
```

## Output Colors

- ✓ Green - Success
- ✗ Red - Errors
- ⚠ Yellow - Warnings
- ℹ Blue - Information
- Cyan - Headers

## Tips

1. **Always use `--json` for scripts**: Parseable, stable output
2. **Use `--verbose` when debugging**: See what's happening
3. **Watch long operations**: Use `--watch` with train status
4. **Install completion**: Save typing with tab completion
5. **Check help often**: `model-train <command> --help`

## See Also

- `CLI_GUIDE.md` - Comprehensive usage guide with examples
- `CLI_EXAMPLES.md` - Workflow examples and scripts
- `CLI_IMPLEMENTATION.md` - Technical implementation details
- `README.md` - Project overview

## Support

For issues or questions:
- Run with `--verbose` flag
- Check API is running: `curl http://localhost:8000/health`
- View help: `model-train <command> --help`
- Enable debug: `DEBUG=1 model-train <command>`
