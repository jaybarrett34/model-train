# Data Synthesis Module - Quick Reference

## File Locations

- **Main Module**: `/home/user/model-train/core/synthesis.py` (751 lines)
- **Quick Start**: `/home/user/model-train/quickstart_synthesis.py`
- **Full Examples**: `/home/user/model-train/examples_usage.py`
- **Tests**: `/home/user/model-train/test_synthesis.py`
- **Documentation**: `/home/user/model-train/SYNTHESIS_README.md`

## Key Classes

### 1. AI Providers

```python
# Ollama (Local)
from core.synthesis import OllamaProvider
provider = OllamaProvider(model="llama2", base_url="http://localhost:11434")

# Claude (Anthropic)
from core.synthesis import ClaudeProvider
provider = ClaudeProvider(api_key="sk-...", model="claude-sonnet-4-5-20250929")

# OpenAI
from core.synthesis import OpenAIProvider
provider = OpenAIProvider(api_key="sk-...", model="gpt-4")
```

### 2. Configuration

```python
from core.synthesis import GenerationConfig, GenerationMode, XMLPattern

# Generation config
config = GenerationConfig(
    mode=GenerationMode.PSEUDORANDOM,  # or PATTERNED, FORCED
    temperature=0.8,
    max_tokens=1024,
    retry_attempts=3,
    retry_delay=1.0,
    rate_limit_delay=0.5
)

# XML pattern
pattern = XMLPattern(
    schema="",
    required_tags=["think", "command", "speak"],
    optional_tags=["action"]
)
```

### 3. Data Synthesizer

```python
from core.synthesis import DataSynthesizer

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

# Generate batch
examples = synthesizer.generate_batch(
    objectives=["obj1", "obj2", "obj3"],
    inputs=["input1", "input2", "input3"],
    show_progress=True
)
```

### 4. Format Converters

```python
from core.synthesis import save_dataset, to_sharegpt_format, to_alpaca_format

# Save in different formats
save_dataset(examples, "data_sharegpt.json", format_type="sharegpt")
save_dataset(examples, "data_alpaca.json", format_type="alpaca")
save_dataset(examples, "data_raw.json", format_type="raw")

# Convert manually
sharegpt_data = to_sharegpt_format(examples)
alpaca_data = to_alpaca_format(examples, instruction_prefix="You are a helper. ")
```

## Generation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **PSEUDORANDOM** | AI generates varied content | Creative, diverse outputs |
| **PATTERNED** | Use templates with [FILL] sections | Structured generation |
| **FORCED** | Lock specific parts, vary others | Controlled variation |

## XML Validation

```python
from core.synthesis import XMLValidator

# Validate structure
is_valid, error = XMLValidator.validate_xml_structure(text, pattern)

# Extract content from tag
content = XMLValidator.extract_xml_content(text, "think")
```

## Output Formats

### ShareGPT Format
```json
{
  "conversations": [
    {"from": "human", "value": "input text"},
    {"from": "gpt", "value": "output text"}
  ]
}
```

### Alpaca Format
```json
{
  "instruction": "instruction text",
  "input": "input text",
  "output": "output text"
}
```

### Raw Format
```json
{
  "input": "input text",
  "output": "output text",
  "metadata": {
    "mode": "pseudorandom",
    "attempt": 1,
    "timestamp": 1234567890.123
  }
}
```

## Example: Minecraft Assistant

```python
from core.synthesis import *

# 1. Setup
pattern = XMLPattern(schema="", required_tags=["think", "command", "speak"])
provider = OllamaProvider(model="llama2")
config = GenerationConfig(temperature=0.8)
synthesizer = DataSynthesizer(provider, pattern, config)

# 2. Generate
example = synthesizer.generate_single(
    objective="Help player find diamonds",
    input_text="What should I do to get diamonds?"
)

# 3. Output
print(example['output'])
# <think>I need to help them mine diamonds at y-level -59</think>
# <command>/tp ~ ~-60 ~</command>
# <speak>Let me take you to diamond level</speak>
```

## Quick Commands

```bash
# Run tests
python test_synthesis.py

# Run quick start
python quickstart_synthesis.py

# Run examples (interactive menu)
python examples_usage.py

# Install dependencies
pip install -r requirements.txt

# Start Ollama (for local generation)
ollama serve
ollama pull llama2
```

## Error Handling

```python
from core.synthesis import AIProviderError, ValidationError

try:
    example = synthesizer.generate_single(objective, input_text)
except ValidationError as e:
    print(f"Validation failed: {e}")
except AIProviderError as e:
    print(f"AI provider error: {e}")
```

## Statistics

```python
stats = synthesizer.get_stats()
print(f"Generated: {stats['total_generated']}")
print(f"Requests: {stats['provider_stats']['request_count']}")
print(f"Tokens: {stats['provider_stats']['total_tokens']}")
```

## Advanced Features

### Pattern Variations
```python
variations = synthesizer.generate_from_pattern_examples(
    examples=[{"input": "...", "output": "..."}],
    num_variations=5
)
```

### Connection Validation
```python
if provider.validate_connection():
    print("✓ Connected")
else:
    print("❌ Connection failed")
```

### Batch with Custom Mode
```python
examples = synthesizer.generate_batch(
    objectives=objectives,
    inputs=inputs,
    mode=GenerationMode.PATTERNED,
    show_progress=True
)
```

## Environment Variables

```bash
# For Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# For OpenAI
export OPENAI_API_KEY="sk-..."
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Can't connect to Ollama | Run `ollama serve` |
| Model not found | Run `ollama pull llama2` |
| Import errors | Run `pip install -r requirements.txt` |
| Validation failures | Lower temperature or increase retry_attempts |
| Rate limiting | Increase rate_limit_delay in config |

## Performance Tips

1. **Use batching** for multiple examples
2. **Adjust temperature** (0.6-0.9 for most tasks)
3. **Enable rate limiting** to avoid API throttling
4. **Use Ollama locally** for unlimited free generation
5. **Validate selectively** - disable for faster generation

## Next Steps

1. ✓ Module created and tested
2. → Customize XML patterns for your use case
3. → Generate training data
4. → Fine-tune your model with the generated data
5. → Iterate and improve patterns based on results

For detailed documentation, see `SYNTHESIS_README.md`
