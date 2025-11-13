# Data Synthesis Module

A powerful, flexible framework for generating AI-powered training data with multiple providers, XML pattern validation, and multiple output formats.

## Features

- **Multiple AI Providers**: Ollama (local), Claude (Anthropic), OpenAI
- **Flexible Generation Modes**: Pseudorandom, patterned, forced
- **XML Pattern Validation**: Ensure generated data follows specified XML structures
- **Multiple Output Formats**: ShareGPT, Alpaca, raw JSON
- **Batch Generation**: Generate multiple examples efficiently
- **Error Handling**: Automatic retries with validation
- **Rate Limiting**: Built-in delays to respect API limits
- **Progress Tracking**: Monitor generation progress

## Installation

```bash
# Install core dependencies
pip install -r requirements.txt

# For specific providers:
pip install anthropic  # For ClaudeProvider
pip install openai     # For OpenAIProvider
pip install requests   # For OllamaProvider (usually pre-installed)
```

## Quick Start

### 1. Using Ollama (Local)

```python
from core.synthesis import (
    OllamaProvider,
    DataSynthesizer,
    GenerationConfig,
    XMLPattern,
    save_dataset
)

# Define XML pattern
pattern = XMLPattern(
    required_tags=["think", "command", "speak"]
)

# Initialize provider
provider = OllamaProvider(model="llama2")

# Create synthesizer
config = GenerationConfig(temperature=0.8)
synthesizer = DataSynthesizer(
    provider=provider,
    xml_pattern=pattern,
    config=config
)

# Generate single example
example = synthesizer.generate_single(
    objective="Help player mine diamonds",
    input_text="What should I do to get diamonds?"
)

print(example['output'])
# Output: <think>I need to help them mine diamonds at y-level -59</think>
#         <command>/tp ~ ~-60 ~</command>
#         <speak>Let me take you to diamond level</speak>
```

### 2. Using Claude (Cloud)

```python
import os
from core.synthesis import ClaudeProvider, DataSynthesizer

# Set API key
api_key = os.environ.get("ANTHROPIC_API_KEY")

# Initialize
provider = ClaudeProvider(api_key=api_key)
synthesizer = DataSynthesizer(provider=provider)

# Generate
example = synthesizer.generate_single(
    objective="Generate Minecraft assistant response",
    input_text="What should I do to get diamonds?"
)
```

### 3. Batch Generation

```python
# Generate multiple examples at once
objectives = [
    "Help player find diamonds",
    "Build a house",
    "Fight hostile mobs"
]

inputs = [
    "How do I get diamonds?",
    "Can you build me a shelter?",
    "There are zombies!"
]

examples = synthesizer.generate_batch(
    objectives=objectives,
    inputs=inputs,
    show_progress=True
)

# Save in different formats
save_dataset(examples, "data_sharegpt.json", format_type="sharegpt")
save_dataset(examples, "data_alpaca.json", format_type="alpaca")
```

## Generation Modes

### 1. Pseudorandom Mode (Default)

AI generates varied content within constraints. Best for creative, diverse outputs.

```python
from core.synthesis import GenerationMode

config = GenerationConfig(mode=GenerationMode.PSEUDORANDOM)
synthesizer = DataSynthesizer(provider=provider, config=config)

example = synthesizer.generate_single(
    objective="Help player with task",
    input_text="Your input here"
)
```

### 2. Patterned Mode

Use templates with specific fill-in sections.

```python
template = """
<think>[FILL: reasoning]</think>
<command>[FILL: minecraft command]</command>
<speak>[FILL: response]</speak>
"""

example = synthesizer.generate_single(
    objective="Your objective",
    input_text="Your input",
    mode=GenerationMode.PATTERNED,
    template=template
)
```

### 3. Forced Mode

Lock specific parts, randomize others.

```python
locked_parts = {
    "command": "/tp @p ~ ~-60 ~",
    "location": "diamond level"
}

example = synthesizer.generate_single(
    objective="Teleport to diamond level",
    input_text="Take me to diamonds",
    mode=GenerationMode.FORCED,
    locked_parts=locked_parts
)
```

## AI Providers

### Ollama (Local)

```python
from core.synthesis import OllamaProvider

provider = OllamaProvider(
    model="llama2",
    base_url="http://localhost:11434"
)

# Check connection
if provider.validate_connection():
    print("✓ Ollama is running")
```

**Requirements:**
- Ollama installed and running locally
- Model downloaded: `ollama pull llama2`

### Claude (Anthropic)

```python
from core.synthesis import ClaudeProvider

provider = ClaudeProvider(
    api_key="your-api-key",
    model="claude-sonnet-4-5-20250929"
)
```

**Requirements:**
- Anthropic API key
- `anthropic` package installed

### OpenAI

```python
from core.synthesis import OpenAIProvider

provider = OpenAIProvider(
    api_key="your-api-key",
    model="gpt-4"
)
```

**Requirements:**
- OpenAI API key
- `openai` package installed

## XML Pattern Validation

Define expected XML structure:

```python
from core.synthesis import XMLPattern

pattern = XMLPattern(
    schema="",  # Optional XML schema
    required_tags=["think", "command", "speak"],
    optional_tags=["action", "observe"]
)

synthesizer = DataSynthesizer(
    provider=provider,
    xml_pattern=pattern
)
```

Generated outputs will be validated and retried if they don't match the pattern.

## Configuration Options

```python
from core.synthesis import GenerationConfig, GenerationMode

config = GenerationConfig(
    mode=GenerationMode.PSEUDORANDOM,  # Generation mode
    temperature=0.8,                    # AI temperature (0-1)
    max_tokens=1024,                    # Max tokens per generation
    retry_attempts=3,                   # Retries on validation failure
    retry_delay=1.0,                    # Delay between retries (seconds)
    batch_size=10,                      # Batch size
    rate_limit_delay=0.5                # Delay between API calls
)
```

## Output Formats

### ShareGPT Format

```python
from core.synthesis import to_sharegpt_format, save_dataset

sharegpt_data = to_sharegpt_format(examples)
# Output: [{"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}]

save_dataset(examples, "data.json", format_type="sharegpt")
```

### Alpaca Format

```python
from core.synthesis import to_alpaca_format, save_dataset

alpaca_data = to_alpaca_format(
    examples,
    instruction_prefix="You are a helpful assistant. "
)
# Output: [{"instruction": "...", "input": "...", "output": "..."}]

save_dataset(examples, "data.json", format_type="alpaca")
```

### Raw Format

```python
save_dataset(examples, "data.json", format_type="raw")
# Output: [{"input": "...", "output": "...", "metadata": {...}}]
```

## Advanced Features

### Generate Variations from Examples

```python
seed_examples = [
    {
        "input": "What should I do to get diamonds?",
        "output": "<think>...</think><command>...</command><speak>...</speak>"
    }
]

variations = synthesizer.generate_from_pattern_examples(
    examples=seed_examples,
    num_variations=5,
    mode=GenerationMode.PSEUDORANDOM
)
```

### Progress Tracking

```python
# Automatic progress logging
examples = synthesizer.generate_batch(
    objectives=objectives,
    inputs=inputs,
    show_progress=True  # Shows "Generating example X/Y"
)

# Get statistics
stats = synthesizer.get_stats()
print(f"Total generated: {stats['total_generated']}")
print(f"API requests: {stats['provider_stats']['request_count']}")
print(f"Tokens used: {stats['provider_stats']['total_tokens']}")
```

### Error Handling

```python
from core.synthesis import AIProviderError, ValidationError

try:
    example = synthesizer.generate_single(
        objective="Your objective",
        input_text="Your input"
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
except AIProviderError as e:
    print(f"AI provider error: {e}")
```

## Complete Example: Minecraft Assistant

```python
#!/usr/bin/env python3
from core.synthesis import (
    OllamaProvider,
    DataSynthesizer,
    GenerationConfig,
    GenerationMode,
    XMLPattern,
    save_dataset
)

# 1. Define pattern
pattern = XMLPattern(
    required_tags=["think", "command", "speak"]
)

# 2. Initialize provider
provider = OllamaProvider(model="llama2")

# 3. Configure generation
config = GenerationConfig(
    mode=GenerationMode.PSEUDORANDOM,
    temperature=0.8,
    rate_limit_delay=0.5
)

# 4. Create synthesizer
synthesizer = DataSynthesizer(
    provider=provider,
    xml_pattern=pattern,
    config=config
)

# 5. Generate batch
objectives = [
    "Help player find diamonds at correct Y-level",
    "Build wooden house for protection",
    "Fight hostile mobs effectively",
    "Gather wood resources",
    "Navigate to coordinates"
]

inputs = [
    "What should I do to get diamonds?",
    "Can you build me a shelter?",
    "There are zombies attacking!",
    "I need wood for crafting",
    "Take me to spawn point"
]

examples = synthesizer.generate_batch(
    objectives=objectives,
    inputs=inputs,
    show_progress=True
)

# 6. Save in multiple formats
save_dataset(examples, "minecraft_sharegpt.json", format_type="sharegpt")
save_dataset(examples, "minecraft_alpaca.json", format_type="alpaca")

# 7. Print statistics
stats = synthesizer.get_stats()
print(f"\n✓ Generated {stats['total_generated']} examples")
print(f"✓ API requests: {stats['provider_stats']['request_count']}")
```

## Example Output

```json
{
  "input": "What should I do to get diamonds?",
  "output": "<think>I need to help them mine diamonds at y-level -59</think><command>/tp ~0 ~-60 ~0</command><speak>Let me take you to diamond level</speak>",
  "metadata": {
    "mode": "pseudorandom",
    "attempt": 1,
    "timestamp": 1234567890.123
  }
}
```

## Running Examples

```bash
# Run the comprehensive examples script
python examples_usage.py

# It will show a menu:
# 1. Minecraft with Ollama (Local)
# 2. Patterned Generation
# 3. Forced Generation with Locked Parts
# 4. Claude Provider (Cloud)
# 5. OpenAI Provider (Cloud)
# 6. Pattern Variations
# 7. Format Conversion
```

## API Reference

### Classes

- **`AIProvider`**: Abstract base class for AI providers
- **`OllamaProvider`**: Local Ollama provider
- **`ClaudeProvider`**: Anthropic Claude provider
- **`OpenAIProvider`**: OpenAI provider
- **`DataSynthesizer`**: Main synthesis engine
- **`XMLValidator`**: XML validation utilities
- **`XMLPattern`**: XML pattern specification
- **`GenerationConfig`**: Generation configuration
- **`GenerationMode`**: Enum for generation modes

### Functions

- **`save_dataset()`**: Save dataset to file
- **`to_sharegpt_format()`**: Convert to ShareGPT format
- **`to_alpaca_format()`**: Convert to Alpaca format

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull a model
ollama pull llama2
```

### API Key Issues

```bash
# Set environment variables
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

### Validation Failures

- Check that required tags are in your prompts
- Increase `retry_attempts` in config
- Lower `temperature` for more consistent output
- Review XML pattern requirements

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
