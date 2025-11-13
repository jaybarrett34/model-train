# Model Train CLI Guide

A comprehensive command-line interface for managing ML model fine-tuning with XML pattern synthesis.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/model-train.git
cd model-train

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e ".[full]"
```

### Verify Installation

```bash
model-train --version
model-train --help
```

## Quick Start

```bash
# 1. Start the backend (in a separate terminal)
cd backend
python main.py

# 2. Create a project
model-train project create xml-formatter \
  --objective "Train a model to generate properly formatted XML"

# 3. Add XML patterns
model-train xml add-tag xml-formatter thinking \
  --description "Internal reasoning before response" \
  --constraint "Must appear before output tags"

# 4. Generate training data
model-train generate xml-formatter --count 100

# 5. Start training
model-train train start xml-formatter

# 6. Monitor training
model-train train status <job-id> --watch
```

## Command Reference

### Global Flags

These flags work with all commands:

- `--api-url URL` - Backend API URL (default: http://localhost:8000)
- `--verbose, -v` - Enable verbose output with debug information
- `--json` - Output results as JSON (useful for scripting)

### Project Commands

#### List Projects

```bash
model-train project list
model-train project list --json
```

Shows all projects with their configuration, datasets, and creation dates.

#### Create Project

```bash
model-train project create <name> --objective "Description"

# Options:
#   --objective, -o TEXT          Training objective (required)
#   --model, -m TEXT             Base model (default: unsloth/llama-2-7b-bnb-4bit)
#   --format, -f [sharegpt|alpaca] Dataset format (default: sharegpt)
#   --provider [ollama|anthropic|openai] AI provider (default: ollama)
#   --ai-model TEXT              AI model for synthesis (default: llama2)
```

**Examples:**

```bash
# Basic project
model-train project create my-project \
  --objective "Train model for code generation"

# With custom model and format
model-train project create code-gen \
  --objective "Generate Python code" \
  --model "unsloth/mistral-7b-bnb-4bit" \
  --format alpaca \
  --provider anthropic \
  --ai-model "claude-3-opus-20240229"
```

#### Show Project Details

```bash
model-train project show <name>
model-train project show xml-formatter --json
```

Displays complete project configuration including:
- Project metadata
- AI configuration
- XML patterns
- Generated datasets
- Training history

#### Delete Project

```bash
model-train project delete <name>
model-train project delete old-project --yes  # Skip confirmation
```

### XML Pattern Commands

#### Add XML Tag

```bash
model-train xml add-tag <project> <tag-name> --description "..."

# Options:
#   --description, -d TEXT  Tag description (required)
#   --constraint, -c TEXT   Validation constraint
#   --example, -e TEXT      Example usage (can be repeated)
```

**Examples:**

```bash
# Simple tag
model-train xml add-tag my-project thinking \
  --description "Internal reasoning process"

# Tag with constraints
model-train xml add-tag my-project output \
  --description "Final response to user" \
  --constraint "Must be valid XML" \
  --example "<output>Hello, world!</output>"

# Tag with multiple examples
model-train xml add-tag my-project code \
  --description "Code block" \
  --constraint "Must be syntactically valid" \
  --example "<code>def hello(): pass</code>" \
  --example "<code>print('test')</code>"
```

#### Remove XML Tag

```bash
model-train xml remove-tag <project> <tag-name>
model-train xml remove-tag my-project old-tag --yes  # Skip confirmation
```

#### Show XML Patterns

```bash
model-train xml show <project>
model-train xml show my-project --json
```

Lists all XML patterns defined for a project with their descriptions, constraints, and examples.

### Data Generation Commands

#### Generate Dataset

```bash
model-train generate <project>

# Options:
#   --count, -n INTEGER           Number of examples (default: 100)
#   --batch-size, -b INTEGER      Batch size (default: 10)
#   --temperature, -t FLOAT       AI temperature 0.0-2.0
#   --mode [pseudorandom|diverse|focused] Generation mode (default: pseudorandom)
#   --validate                    Validate generated data
```

**Examples:**

```bash
# Generate 100 examples (default)
model-train generate my-project

# Generate 500 examples with custom batch size
model-train generate my-project --count 500 --batch-size 25

# Generate with higher temperature for more variety
model-train generate my-project \
  --count 200 \
  --temperature 1.2 \
  --mode diverse

# Generate and validate
model-train generate my-project --count 100 --validate
```

### Training Commands

#### Start Training

```bash
model-train train start <project>

# Options:
#   --dataset, -d TEXT         Dataset filename (uses latest if not specified)
#   --steps, -s INTEGER        Number of training steps
#   --lora-rank, -r INTEGER    LoRA rank (default: 16)
#   --learning-rate, -lr FLOAT Learning rate
#   --batch-size, -b INTEGER   Batch size
#   --epochs, -e INTEGER       Number of epochs
```

**Examples:**

```bash
# Start training with defaults
model-train train start my-project

# Start with specific dataset
model-train train start my-project --dataset my-data.json

# Custom training parameters
model-train train start my-project \
  --lora-rank 32 \
  --learning-rate 0.0002 \
  --epochs 5 \
  --batch-size 4
```

#### Check Training Status

```bash
model-train train status <job-id>

# Options:
#   --watch, -w             Watch status in real-time
#   --interval, -i INTEGER  Update interval in seconds (default: 5)
```

**Examples:**

```bash
# Check status once
model-train train status abc123

# Watch status in real-time
model-train train status abc123 --watch

# Watch with custom interval
model-train train status abc123 --watch --interval 10

# Get status as JSON
model-train train status abc123 --json
```

#### Cancel Training

```bash
model-train train cancel <job-id>
model-train train cancel abc123 --yes  # Skip confirmation
```

### Model Commands

#### List Models

```bash
model-train model list
model-train model list --json
```

Shows all downloaded models with their paths, sizes, and quantization info.

#### Download Model

```bash
model-train model download <model-name>

# Options:
#   --revision, -r TEXT              Model revision/branch
#   --quantization, -q [4bit|8bit|none] Quantization type
```

**Examples:**

```bash
# Download default model
model-train model download unsloth/llama-2-7b-bnb-4bit

# Download specific revision
model-train model download unsloth/mistral-7b \
  --revision main \
  --quantization 4bit
```

#### Export Model

```bash
model-train model export <project>

# Options:
#   --format, -f [gguf|safetensors|pytorch] Export format (default: gguf)
#   --quantization, -q [q4_0|q4_1|q5_0|q5_1|q8_0] GGUF quantization
#   --output, -o TEXT                           Output filename
```

**Examples:**

```bash
# Export to GGUF (default)
model-train model export my-project

# Export with specific quantization
model-train model export my-project \
  --format gguf \
  --quantization q4_0 \
  --output my-model.gguf

# Export to safetensors
model-train model export my-project --format safetensors
```

### Analysis Commands

#### Analyze Dataset

```bash
model-train analyze dataset <project>

# Options:
#   --estimate-size  Estimate final model size
#   --validate       Validate dataset quality
#   --stats          Show detailed statistics
```

**Examples:**

```bash
# Basic analysis
model-train analyze dataset my-project

# Full analysis with all options
model-train analyze dataset my-project \
  --estimate-size \
  --validate \
  --stats
```

### TUI Command

Launch the interactive Terminal User Interface:

```bash
model-train tui
```

**Note:** TUI is currently in development. Use CLI commands for now.

### Completion Support

Install shell completion for your shell:

```bash
model-train completion
```

This will show instructions for bash, zsh, or fish.

**Example for bash:**

```bash
# Add to ~/.bashrc
eval "$(_MODEL_TRAIN_COMPLETE=bash_source model-train)"
```

## Configuration

### Environment Variables

- `API_URL` - Backend API URL (default: http://localhost:8000)
- `DEBUG` - Enable debug mode for full error traces

**Example:**

```bash
export API_URL=http://api.example.com:8000
export DEBUG=1
model-train project list
```

### Backend Configuration

The backend should be configured via `.env` file:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Advanced Usage

### Scripting with JSON Output

All commands support `--json` flag for easy parsing:

```bash
# Get project count
model-train project list --json | jq '.total'

# Get latest dataset filename
model-train project show my-project --json | \
  jq -r '.datasets | sort_by(.created_at) | .[-1].filename'

# Check if training is complete
STATUS=$(model-train train status job123 --json | jq -r '.status')
if [ "$STATUS" = "completed" ]; then
  echo "Training complete!"
fi
```

### Batch Operations

```bash
# Create multiple projects
for name in proj1 proj2 proj3; do
  model-train project create $name \
    --objective "Training for $name"
done

# Add same tag to multiple projects
for proj in $(model-train project list --json | jq -r '.projects[].name'); do
  model-train xml add-tag $proj thinking \
    --description "Reasoning process"
done
```

### Pipeline Example

Complete workflow for a new project:

```bash
#!/bin/bash
set -e

PROJECT="my-xml-formatter"
OBJECTIVE="Train model to format XML with thinking tags"

# Create project
echo "Creating project..."
model-train project create $PROJECT --objective "$OBJECTIVE"

# Add XML patterns
echo "Adding XML patterns..."
model-train xml add-tag $PROJECT thinking \
  --description "Internal reasoning" \
  --constraint "Must appear first"

model-train xml add-tag $PROJECT output \
  --description "Final response" \
  --constraint "Must be valid XML"

# Generate training data
echo "Generating training data..."
model-train generate $PROJECT --count 500 --validate

# Start training
echo "Starting training..."
JOB_ID=$(model-train train start $PROJECT --json | jq -r '.job_id')
echo "Training job: $JOB_ID"

# Monitor training
echo "Monitoring training..."
model-train train status $JOB_ID --watch

# Export model when done
echo "Exporting model..."
model-train model export $PROJECT --format gguf

echo "Done!"
```

## Troubleshooting

### Cannot connect to API

```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend if needed
cd backend && python main.py
```

### Verbose output for debugging

```bash
model-train --verbose project list
```

### Enable debug mode

```bash
DEBUG=1 model-train project create test --objective "Test"
```

## Color Output

The CLI uses colorful output by default:

- ✓ Green - Success messages
- ✗ Red - Error messages
- ⚠ Yellow - Warnings
- ℹ Blue - Information
- Cyan - Headers and important data

To disable colors (for logging):

```bash
model-train project list | tee output.log
```

## Best Practices

1. **Always validate generated data** before training:
   ```bash
   model-train generate my-project --validate
   ```

2. **Watch training progress** in real-time:
   ```bash
   model-train train status <job-id> --watch
   ```

3. **Use JSON output** for scripting:
   ```bash
   model-train project list --json | jq '.projects[].name'
   ```

4. **Start small** with data generation:
   ```bash
   # Test with 10 examples first
   model-train generate my-project --count 10
   # Then scale up
   model-train generate my-project --count 1000
   ```

5. **Version control** your project configs:
   ```bash
   model-train project show my-project --json > configs/my-project.json
   ```

## Getting Help

For any command, use `--help`:

```bash
model-train --help
model-train project --help
model-train project create --help
model-train train status --help
```

## Contributing

Found a bug or want to request a feature? Please open an issue on GitHub!

## License

MIT License - see LICENSE file for details.
