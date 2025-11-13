# CLI Examples and Usage

This document provides comprehensive examples of using the `model-train` CLI.

## All Available Commands

### Quick Command Reference

```bash
# PROJECT COMMANDS
model-train project list
model-train project create <name> --objective "..." --model "..."
model-train project show <name>
model-train project delete <name>

# XML PATTERN COMMANDS
model-train xml add-tag <project> <tag-name> --description "..." --constraint "..."
model-train xml remove-tag <project> <tag-name>
model-train xml show <project>

# DATA GENERATION
model-train generate <project> --count 100 --mode pseudorandom
model-train generate <project> --batch-size 10 --validate

# TRAINING COMMANDS
model-train train start <project> --steps 100 --lora-rank 16
model-train train status <job-id>
model-train train status <job-id> --watch
model-train train cancel <job-id>

# MODEL COMMANDS
model-train model list
model-train model download <model-name>
model-train model export <project> --format gguf

# ANALYSIS COMMANDS
model-train analyze dataset <project> --estimate-size
model-train analyze dataset <project> --validate-dataset --stats

# TUI & UTILITIES
model-train tui
model-train completion
model-train --version
```

## Complete Workflow Examples

### Example 1: XML Formatting Model

Train a model to generate properly formatted XML with thinking tags.

```bash
# 1. Create project
model-train project create xml-formatter \
  --objective "Train a model to generate properly formatted XML with thinking and output tags" \
  --model "unsloth/llama-2-7b-bnb-4bit" \
  --format sharegpt

# 2. Add XML patterns
model-train xml add-tag xml-formatter thinking \
  --description "Internal reasoning process before generating output" \
  --constraint "Must appear before any output tags" \
  --example "<thinking>Analyzing the request...</thinking>"

model-train xml add-tag xml-formatter output \
  --description "Final formatted XML response" \
  --constraint "Must be valid XML" \
  --example "<output><result>Success</result></output>"

# 3. Verify XML patterns
model-train xml show xml-formatter

# 4. Generate training data
model-train generate xml-formatter \
  --count 500 \
  --batch-size 25 \
  --temperature 0.8 \
  --validate

# 5. Analyze the dataset
model-train analyze dataset xml-formatter \
  --estimate-size \
  --validate \
  --stats

# 6. Start training
model-train train start xml-formatter \
  --lora-rank 32 \
  --learning-rate 0.0002 \
  --epochs 3

# 7. Monitor training (save job ID from previous command)
model-train train status abc123 --watch --interval 10

# 8. Export the model
model-train model export xml-formatter \
  --format gguf \
  --quantization q4_0
```

### Example 2: Code Generation Model

Train a model for Python code generation with documentation.

```bash
# 1. Create project with Anthropic for generation
model-train project create code-generator \
  --objective "Generate Python code with docstrings and type hints" \
  --model "unsloth/mistral-7b-bnb-4bit" \
  --provider anthropic \
  --ai-model "claude-3-sonnet-20240229"

# 2. Add XML patterns for code structure
model-train xml add-tag code-generator planning \
  --description "Code planning and design thoughts" \
  --constraint "Must outline the approach"

model-train xml add-tag code-generator code \
  --description "Python code implementation" \
  --constraint "Must be syntactically valid Python" \
  --example "<code>def hello(): pass</code>"

model-train xml add-tag code-generator tests \
  --description "Unit tests for the code" \
  --constraint "Must use pytest format"

# 3. Generate diverse examples
model-train generate code-generator \
  --count 1000 \
  --mode diverse \
  --temperature 1.0

# 4. Start training with custom parameters
model-train train start code-generator \
  --lora-rank 64 \
  --batch-size 2 \
  --epochs 5
```

### Example 3: Multi-Project Management

Manage multiple projects simultaneously.

```bash
# Create multiple related projects
for domain in math science history; do
  model-train project create "${domain}-tutor" \
    --objective "Educational tutor for ${domain}" \
    --format alpaca
done

# Add common XML pattern to all
for domain in math science history; do
  model-train xml add-tag "${domain}-tutor" explanation \
    --description "Detailed explanation for students"
done

# List all projects
model-train project list --json | jq '.projects[].name'

# Generate data for each
for domain in math science history; do
  model-train generate "${domain}-tutor" --count 200
done
```

## JSON Output Examples

All commands support `--json` flag for programmatic use.

### Get Project Count

```bash
PROJECT_COUNT=$(model-train project list --json | jq '.total')
echo "Total projects: $PROJECT_COUNT"
```

### Check Training Status Programmatically

```bash
#!/bin/bash
JOB_ID="abc123"

while true; do
  STATUS=$(model-train train status $JOB_ID --json | jq -r '.status')
  echo "Current status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    echo "Training complete!"
    break
  elif [ "$STATUS" = "failed" ]; then
    ERROR=$(model-train train status $JOB_ID --json | jq -r '.error_message')
    echo "Training failed: $ERROR"
    exit 1
  fi

  sleep 30
done
```

### Export All Project Configurations

```bash
#!/bin/bash
mkdir -p backups

for project in $(model-train project list --json | jq -r '.projects[].name'); do
  model-train project show $project --json > "backups/${project}.json"
  echo "Backed up: $project"
done
```

## Verbose Mode Examples

Enable verbose output for debugging:

```bash
# See detailed API requests
model-train --verbose project list

# Debug project creation
model-train --verbose project create debug-project \
  --objective "Testing verbose mode"

# Monitor API calls during generation
model-train --verbose generate debug-project --count 10
```

## Error Handling Examples

### Graceful Error Handling in Scripts

```bash
#!/bin/bash
set -e  # Exit on error

PROJECT="my-project"

# Check if project exists
if model-train project show $PROJECT --json &>/dev/null; then
  echo "Project exists, using it..."
else
  echo "Creating new project..."
  model-train project create $PROJECT \
    --objective "My training objective"
fi

# Generate data with error handling
if ! model-train generate $PROJECT --count 100 --validate; then
  echo "Data generation failed!"
  exit 1
fi

echo "Success!"
```

### Retry Logic

```bash
#!/bin/bash

retry_command() {
  local max_attempts=3
  local attempt=1

  while [ $attempt -le $max_attempts ]; do
    if "$@"; then
      return 0
    fi
    echo "Attempt $attempt failed, retrying..."
    sleep 5
    ((attempt++))
  done

  return 1
}

# Use retry for potentially flaky operations
retry_command model-train model download unsloth/llama-2-7b-bnb-4bit
```

## Advanced Patterns

### Automated Training Pipeline

```bash
#!/bin/bash
set -euo pipefail

PROJECT="$1"
OBJECTIVE="$2"
NUM_EXAMPLES="${3:-500}"

echo "=== Training Pipeline for $PROJECT ==="

# 1. Create or update project
if model-train project show "$PROJECT" --json &>/dev/null; then
  echo "✓ Project exists"
else
  echo "Creating project..."
  model-train project create "$PROJECT" --objective "$OBJECTIVE"
fi

# 2. Check if we have XML patterns
PATTERN_COUNT=$(model-train project show "$PROJECT" --json | jq '.xml_patterns | length')
if [ "$PATTERN_COUNT" -eq 0 ]; then
  echo "⚠ No XML patterns defined. Add them manually."
  exit 1
fi

# 3. Generate data
echo "Generating $NUM_EXAMPLES examples..."
DATASET=$(model-train generate "$PROJECT" \
  --count "$NUM_EXAMPLES" \
  --validate \
  --json | jq -r '.dataset_filename')
echo "✓ Dataset: $DATASET"

# 4. Analyze dataset
echo "Analyzing dataset..."
model-train analyze dataset "$PROJECT" --estimate-size --stats

# 5. Start training
echo "Starting training..."
JOB_ID=$(model-train train start "$PROJECT" --json | jq -r '.job_id')
echo "✓ Job ID: $JOB_ID"

# 6. Wait for completion
echo "Monitoring training..."
while true; do
  STATUS=$(model-train train status "$JOB_ID" --json | jq -r '.status')

  case $STATUS in
    completed)
      echo "✓ Training completed!"
      break
      ;;
    failed)
      ERROR=$(model-train train status "$JOB_ID" --json | jq -r '.error_message')
      echo "✗ Training failed: $ERROR"
      exit 1
      ;;
    *)
      PROGRESS=$(model-train train status "$JOB_ID" --json | \
        jq -r 'if .current_step and .total_steps then (.current_step / .total_steps * 100 | floor) else 0 end')
      echo "  Status: $STATUS ($PROGRESS%)"
      sleep 30
      ;;
  esac
done

# 7. Export model
echo "Exporting model..."
model-train model export "$PROJECT" --format gguf --quantization q4_0

echo "=== Pipeline Complete ==="
```

### Batch Tag Management

```bash
#!/bin/bash

PROJECT="$1"

# Define all tags in an array
declare -A TAGS=(
  ["thinking"]="Internal reasoning process"
  ["analysis"]="Problem analysis"
  ["solution"]="Solution steps"
  ["code"]="Code implementation"
  ["output"]="Final formatted output"
)

# Add all tags
for tag in "${!TAGS[@]}"; do
  model-train xml add-tag "$PROJECT" "$tag" \
    --description "${TAGS[$tag]}" \
    --constraint "Must be well-formed XML"
  echo "Added tag: $tag"
done

# Show all tags
model-train xml show "$PROJECT"
```

### Parallel Project Training

```bash
#!/bin/bash

PROJECTS=(
  "project-1"
  "project-2"
  "project-3"
)

# Start all training jobs in parallel
declare -A JOB_IDS

for project in "${PROJECTS[@]}"; do
  echo "Starting training for $project..."
  JOB_ID=$(model-train train start "$project" --json | jq -r '.job_id')
  JOB_IDS[$project]=$JOB_ID
  echo "  Job ID: $JOB_ID"
done

# Monitor all jobs
echo "Monitoring all jobs..."
while true; do
  all_done=true

  for project in "${PROJECTS[@]}"; do
    job_id="${JOB_IDS[$project]}"
    status=$(model-train train status "$job_id" --json | jq -r '.status')

    if [[ "$status" != "completed" && "$status" != "failed" ]]; then
      all_done=false
    fi

    echo "  $project: $status"
  done

  if $all_done; then
    break
  fi

  sleep 60
done

echo "All training jobs complete!"
```

## Environment Variables

```bash
# Set API URL
export API_URL="http://api.example.com:8000"

# Enable debug mode
export DEBUG=1

# Use in commands
model-train project list

# Or override per command
API_URL=http://localhost:9000 model-train project list
```

## Shell Completion

### Install Bash Completion

```bash
# Add to ~/.bashrc
eval "$(_MODEL_TRAIN_COMPLETE=bash_source model-train)"

# Reload
source ~/.bashrc

# Test completion
model-train proj<TAB>    # Completes to 'project'
model-train project cr<TAB>  # Completes to 'create'
```

### Install Zsh Completion

```bash
# Add to ~/.zshrc
eval "$(_MODEL_TRAIN_COMPLETE=zsh_source model-train)"

# Reload
source ~/.zshrc
```

### Install Fish Completion

```bash
# Add to ~/.config/fish/config.fish
eval (env _MODEL_TRAIN_COMPLETE=fish_source model-train)
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/train-model.yml
name: Train Model

on:
  push:
    branches: [main]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install CLI
        run: pip install -e .

      - name: Create Project
        run: |
          model-train project create ci-model \
            --objective "CI/CD trained model" \
            --json

      - name: Generate Data
        run: |
          model-train generate ci-model \
            --count 100 \
            --validate

      - name: Start Training
        run: |
          JOB_ID=$(model-train train start ci-model --json | jq -r '.job_id')
          echo "JOB_ID=$JOB_ID" >> $GITHUB_ENV
```

### Docker Integration

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

# Set default API URL
ENV API_URL=http://backend:8000

ENTRYPOINT ["model-train"]
CMD ["--help"]
```

```bash
# Build and run
docker build -t model-train-cli .

# Use the CLI
docker run model-train-cli project list
docker run -e API_URL=http://host:8000 model-train-cli project create test
```

## Tips and Tricks

### 1. Quick Project Status

```bash
# Create an alias
alias mt='model-train'

# Quick status check
mt project show my-project
```

### 2. Watch Multiple Jobs

```bash
# Terminal 1
model-train train status job1 --watch

# Terminal 2
model-train train status job2 --watch
```

### 3. Export Project Summary

```bash
model-train project show my-project --json | \
  jq '{
    name: .name,
    patterns: (.xml_patterns | length),
    datasets: (.datasets | length),
    latest_dataset: (.datasets | sort_by(.created_at) | .[-1].filename)
  }'
```

### 4. Find Projects by Criteria

```bash
# Projects with no datasets
model-train project list --json | \
  jq -r '.projects[] | select(.datasets | length == 0) | .name'

# Projects using specific model
model-train project list --json | \
  jq -r '.projects[] | select(.base_model == "unsloth/llama-2-7b-bnb-4bit") | .name'
```

### 5. Bulk Operations

```bash
# Delete all projects matching pattern
model-train project list --json | \
  jq -r '.projects[] | select(.name | startswith("test-")) | .name' | \
  xargs -I {} model-train project delete {} --yes
```

## Troubleshooting Commands

```bash
# Test API connectivity
curl $(echo $API_URL)/health || echo "API not reachable"

# Verbose mode for debugging
model-train --verbose project create test --objective "Debug test"

# Check CLI version
model-train --version

# Validate JSON output
model-train project list --json | jq empty && echo "Valid JSON"

# Get detailed help
model-train train start --help | less
```
