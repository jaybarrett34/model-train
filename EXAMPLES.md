# Examples - Real-World Use Cases

This document provides complete, ready-to-use examples for common fine-tuning scenarios. Each example includes the full workflow from project creation to model deployment.

## Table of Contents

1. [Minecraft Assistant Bot](#1-minecraft-assistant-bot)
2. [Code Formatter](#2-code-formatter)
3. [Customer Support Bot](#3-customer-support-bot)
4. [Data Extraction Tool](#4-data-extraction-tool)
5. [Educational Tutor](#5-educational-tutor)
6. [Creative Writing Assistant](#6-creative-writing-assistant)
7. [SQL Query Generator](#7-sql-query-generator)
8. [JSON API Response Generator](#8-json-api-response-generator)

---

## 1. Minecraft Assistant Bot

Train a bot that helps players in Minecraft by providing commands, explanations, and guidance.

### XML Pattern Design

```xml
<observe>Current game state and player situation</observe>
<think>Reasoning about what action to take</think>
<command>Minecraft command to execute (if any)</command>
<speak>Message to say to the player</speak>
```

### Complete Code Example (CLI)

```bash
#!/bin/bash

# 1. Create the project
model-train project create minecraft-bot \
  --objective "Train a Minecraft assistant that helps players with commands and guidance" \
  --model "unsloth/llama-2-7b-bnb-4bit" \
  --format "sharegpt" \
  --provider "ollama"

# 2. Add XML patterns
model-train xml add-tag minecraft-bot observe \
  --description "What the bot observes in the game environment"

model-train xml add-tag minecraft-bot think \
  --description "Internal reasoning about what to do next"

model-train xml add-tag minecraft-bot command \
  --description "Minecraft command to execute (e.g., /tp, /give)"

model-train xml add-tag minecraft-bot speak \
  --description "Message to communicate to the player"

# 3. Generate training data
model-train generate minecraft-bot \
  --count 300 \
  --temperature 0.7 \
  --batch-size 15

# 4. Start training
model-train train start minecraft-bot \
  --epochs 5 \
  --lora-rank 32 \
  --learning-rate 2e-4

# 5. Monitor progress
model-train train status <job-id> --watch
```

### Example Training Data

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "Help me find diamonds! I've been mining for hours."
    },
    {
      "from": "gpt",
      "value": "<observe>Player is mining, hasn't found diamonds yet, likely not at optimal Y-level</observe>\n<think>Diamonds spawn best at Y-levels 5-12. Player needs to check their current level and possibly dig deeper. I should help them navigate to the right level.</think>\n<command>/tp @p ~ 11 ~</command>\n<speak>Diamonds are most common at Y-level 11! I'll teleport you there. Remember to bring iron or diamond pickaxe, and watch out for lava!</speak>"
    }
  ]
}
```

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "How do I make a nether portal?"
    },
    {
      "from": "gpt",
      "value": "<observe>Player needs help building a nether portal, likely new to the game</observe>\n<think>Nether portal requires obsidian blocks arranged in a specific frame. Player needs: obsidian (mined with diamond pickaxe), flint and steel to light it. I should explain the structure clearly.</think>\n<command></command>\n<speak>To make a nether portal, you need 10-14 obsidian blocks. Build a rectangular frame that's 4 blocks wide and 5 blocks tall (you can omit corners). Light it with flint and steel. The purple portal will appear! Want me to give you the materials?</speak>"
    }
  ]
}
```

### Python Code for Integration

```python
import requests

def minecraft_bot_assist(player_message, bot_api_url="http://localhost:11434/api/generate"):
    """
    Send player message to fine-tuned Minecraft bot
    """
    prompt = player_message

    response = requests.post(
        bot_api_url,
        json={
            "model": "minecraft-bot",
            "prompt": prompt,
            "stream": False
        }
    )

    bot_response = response.json()["response"]

    # Parse XML tags
    import re

    observe = re.search(r'<observe>(.*?)</observe>', bot_response, re.DOTALL)
    think = re.search(r'<think>(.*?)</think>', bot_response, re.DOTALL)
    command = re.search(r'<command>(.*?)</command>', bot_response, re.DOTALL)
    speak = re.search(r'<speak>(.*?)</speak>', bot_response, re.DOTALL)

    return {
        "observe": observe.group(1).strip() if observe else "",
        "think": think.group(1).strip() if think else "",
        "command": command.group(1).strip() if command else "",
        "speak": speak.group(1).strip() if speak else ""
    }

# Usage
result = minecraft_bot_assist("I need help building a house")
print(f"Bot says: {result['speak']}")
if result['command']:
    print(f"Executing: {result['command']}")
```

---

## 2. Code Formatter

Train a model to analyze and format code with detailed explanations.

### XML Pattern Design

```xml
<analysis>Code structure and style analysis</analysis>
<issues>List of problems found</issues>
<formatted>Properly formatted code</formatted>
<explanation>What changed and why</explanation>
```

### Complete Code Example (Python)

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 1. Create project
project_data = {
    "name": "code-formatter",
    "objective": "Format code and provide detailed style analysis",
    "xml_patterns": [
        {
            "tag_name": "analysis",
            "description": "Analysis of code structure and style"
        },
        {
            "tag_name": "issues",
            "description": "List of style or syntax issues found"
        },
        {
            "tag_name": "formatted",
            "description": "Properly formatted code"
        },
        {
            "tag_name": "explanation",
            "description": "Explanation of what changed and why"
        }
    ],
    "base_model": "unsloth/qwen2.5-14b-instruct-bnb-4bit",  # Better for code
    "dataset_format": "sharegpt",
    "ai_config": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-5-20250929",
        "temperature": 0.6  # Lower for more consistent code formatting
    }
}

response = requests.post(f"{BASE_URL}/projects", json=project_data)
print(f"Created project: {response.json()['name']}")

# 2. Generate training data
gen_data = {
    "project_name": "code-formatter",
    "num_examples": 500,  # More data for code understanding
    "temperature": 0.6,
    "batch_size": 20
}

response = requests.post(f"{BASE_URL}/generate", json=gen_data)
dataset = response.json()
print(f"Generated: {dataset['dataset_filename']}")

# 3. Train with code-optimized settings
train_data = {
    "project_name": "code-formatter",
    "dataset_filename": dataset['dataset_filename'],
    "training_args": {
        "lora_r": 64,  # Higher rank for code complexity
        "learning_rate": 2e-4,
        "num_train_epochs": 7,
        "batch_size": 2
    }
}

response = requests.post(f"{BASE_URL}/train", json=train_data)
job_id = response.json()['job_id']
print(f"Training started: {job_id}")
```

### Example Training Data

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "Format this Python code:\n\ndef calculate(x,y,z):\n  result=x+y*z\n  return result"
    },
    {
      "from": "gpt",
      "value": "<analysis>Python function with math operations. Issues: missing spacing, no type hints, no docstring, poor variable names</analysis>\n<issues>- No spaces after commas\n- No spaces around operators\n- Missing type hints\n- No docstring\n- Unclear variable names\n- Missing blank lines per PEP 8</issues>\n<formatted>\ndef calculate(x: float, y: float, z: float) -> float:\n    \"\"\"\n    Calculate the result of x + (y * z).\n    \n    Args:\n        x: First operand\n        y: Second operand (to be multiplied)\n        z: Third operand (to be multiplied)\n    \n    Returns:\n        The calculated result\n    \"\"\"\n    result = x + y * z\n    return result\n</formatted>\n<explanation>Added type hints for better code documentation, included a comprehensive docstring explaining the function's purpose and parameters, added proper spacing around operators and after commas following PEP 8 style guide, and improved overall readability.</explanation>"
    }
  ]
}
```

---

## 3. Customer Support Bot

Train an empathetic customer service bot that handles inquiries professionally.

### XML Pattern Design

```xml
<understand>Customer's issue, emotion, and intent</understand>
<action>Required action (search_kb, escalate, resolve, wait)</action>
<response>Customer-facing response</response>
<priority>low, medium, high, urgent</priority>
<internal_notes>Notes for internal tracking</internal_notes>
```

### Web UI Example (React)

```javascript
// CreateCustomerSupportProject.jsx
import { useState } from 'react';
import axios from 'axios';

const CreateCustomerSupportProject = () => {
  const [status, setStatus] = useState('');

  const createProject = async () => {
    setStatus('Creating project...');

    // 1. Create project
    const projectData = {
      name: 'customer-support',
      objective: 'Handle customer inquiries with empathy and professionalism',
      xml_patterns: [
        {
          tag_name: 'understand',
          description: "Analysis of customer's issue and emotional state"
        },
        {
          tag_name: 'action',
          description: 'Required action: search_kb, escalate, resolve, wait'
        },
        {
          tag_name: 'response',
          description: 'Customer-facing response message'
        },
        {
          tag_name: 'priority',
          description: 'Issue priority: low, medium, high, urgent'
        },
        {
          tag_name: 'internal_notes',
          description: 'Internal notes for ticket tracking'
        }
      ],
      base_model: 'unsloth/llama-2-13b-bnb-4bit',
      ai_config: {
        provider: 'anthropic',
        model: 'claude-sonnet-4-5-20250929',
        temperature: 0.8
      }
    };

    try {
      const projectRes = await axios.post(
        'http://localhost:8000/api/v1/projects',
        projectData
      );
      setStatus(`Project created: ${projectRes.data.name}`);

      // 2. Generate data
      setStatus('Generating training data...');
      const genRes = await axios.post(
        'http://localhost:8000/api/v1/generate',
        {
          project_name: 'customer-support',
          num_examples: 400,
          temperature: 0.8,
          batch_size: 20
        }
      );
      setStatus(`Generated ${genRes.data.num_generated} examples`);

      // 3. Start training
      setStatus('Starting training...');
      const trainRes = await axios.post(
        'http://localhost:8000/api/v1/train',
        {
          project_name: 'customer-support',
          dataset_filename: genRes.data.dataset_filename,
          training_args: {
            lora_r: 32,
            num_train_epochs: 5,
            learning_rate: 2e-4
          }
        }
      );
      setStatus(`Training job started: ${trainRes.data.job_id}`);
    } catch (error) {
      setStatus(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div>
      <h2>Create Customer Support Bot</h2>
      <button onClick={createProject}>Create & Train</button>
      <p>Status: {status}</p>
    </div>
  );
};

export default CreateCustomerSupportProject;
```

### Example Training Data

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "I ordered a laptop 5 days ago and still haven't received ANY shipping information! This is ridiculous!"
    },
    {
      "from": "gpt",
      "value": "<understand>Customer is frustrated about delayed shipping information for laptop order placed 5 days ago. Emotion: angry/frustrated. Intent: Get shipping status and explanation.</understand>\n<action>search_kb: order_tracking; escalate: shipping_team_urgent</action>\n<response>I sincerely apologize for the frustration and lack of communication about your laptop order. You're absolutely right to be concerned after 5 days. Let me look into this immediately and get you answers. Can you provide your order number? I'm also escalating this to our shipping team to investigate why you haven't received tracking information.</response>\n<priority>high</priority>\n<internal_notes>Laptop order - 5 days, no shipping info sent. Customer very frustrated. Escalating to shipping team for immediate investigation. Follow-up required within 2 hours.</internal_notes>"
    }
  ]
}
```

---

## 4. Data Extraction Tool

Extract structured information from unstructured text.

### XML Pattern Design

```xml
<input_summary>Brief summary of input text</input_summary>
<entities>Named entities (people, places, organizations, dates)</entities>
<relationships>Relationships between entities</relationships>
<key_facts>Important facts and data points</key_facts>
<structured_data>Extracted data in JSON format</structured_data>
```

### TUI Example (Textual)

```python
# Using the built-in TUI
# 1. Launch TUI
# python -m cli.tui

# 2. Navigate to Projects (Press 'P')
# 3. Create New (Press 'N')
# 4. Fill in form:
#    Name: data-extractor
#    Objective: Extract structured information from unstructured text
#    Model: unsloth/mistral-7b-instruct-bnb-4bit
#    Provider: anthropic

# 5. Navigate to XML Editor (Press 'X')
# 6. Add tags (Press 'A' for each):
#    - input_summary: Brief summary of the text
#    - entities: Named entities found
#    - relationships: Relationships between entities
#    - key_facts: Important facts extracted
#    - structured_data: JSON formatted data

# 7. Navigate to Generation (Press 'G')
# 8. Set:
#    Examples: 400
#    Temperature: 0.5 (lower for extraction)
# 9. Generate (Press Enter)

# 10. Navigate to Training (Press 'T')
# 11. Configure and start training
```

### Example Training Data

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "Extract information from: Sarah Johnson, CEO of TechCorp, announced on March 15, 2024 that the company raised $50 million in Series B funding led by Venture Capital Partners. The funding will be used to expand their AI research team in San Francisco."
    },
    {
      "from": "gpt",
      "value": "<input_summary>Announcement about TechCorp's Series B funding round of $50M led by Venture Capital Partners, announced by CEO Sarah Johnson on March 15, 2024.</input_summary>\n<entities>\n- Person: Sarah Johnson (CEO)\n- Organization: TechCorp\n- Organization: Venture Capital Partners\n- Location: San Francisco\n- Date: March 15, 2024\n- Money: $50 million\n- Round: Series B\n</entities>\n<relationships>\n- Sarah Johnson is CEO of TechCorp\n- Venture Capital Partners led the funding round\n- Funding will support AI research team in San Francisco\n</relationships>\n<key_facts>\n- Funding amount: $50 million\n- Funding type: Series B\n- Announcement date: March 15, 2024\n- Lead investor: Venture Capital Partners\n- Use of funds: Expand AI research team\n- Location of expansion: San Francisco\n</key_facts>\n<structured_data>\n{\n  \"company\": \"TechCorp\",\n  \"ceo\": \"Sarah Johnson\",\n  \"announcement_date\": \"2024-03-15\",\n  \"funding\": {\n    \"amount\": 50000000,\n    \"currency\": \"USD\",\n    \"round\": \"Series B\",\n    \"lead_investor\": \"Venture Capital Partners\"\n  },\n  \"use_of_funds\": \"Expand AI research team\",\n  \"location\": \"San Francisco\"\n}\n</structured_data>"
    }
  ]
}
```

---

## 5. Educational Tutor

Create a patient, adaptive tutor for any subject.

### XML Pattern Design

```xml
<assess>Student's current understanding level</assess>
<explanation>Main concept explanation</explanation>
<example>Concrete example to illustrate</example>
<practice>Practice problem for the student</practice>
<encouragement>Positive reinforcement</encouragement>
```

### Full Workflow Script

```bash
#!/bin/bash
# Complete setup for Math Tutor

PROJECT="math-tutor"
BASE_URL="http://localhost:8000/api/v1"

echo "=== Creating Math Tutor Project ==="

# 1. Create project
curl -X POST "$BASE_URL/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "'$PROJECT'",
    "objective": "Teach math concepts with patience and clear examples",
    "xml_patterns": [
      {"tag_name": "assess", "description": "Assess student understanding level"},
      {"tag_name": "explanation", "description": "Clear explanation of concept"},
      {"tag_name": "example", "description": "Concrete example"},
      {"tag_name": "practice", "description": "Practice problem"},
      {"tag_name": "encouragement", "description": "Positive reinforcement"}
    ],
    "base_model": "unsloth/llama-2-7b-bnb-4bit",
    "ai_config": {
      "provider": "anthropic",
      "model": "claude-sonnet-4-5-20250929",
      "temperature": 0.7
    }
  }'

echo -e "\n\n=== Generating Training Data ==="

# 2. Generate 600 examples across different topics
DATASET=$(curl -s -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "'$PROJECT'",
    "num_examples": 600,
    "temperature": 0.7,
    "batch_size": 30
  }' | jq -r '.dataset_filename')

echo "Dataset: $DATASET"

echo -e "\n\n=== Starting Training ==="

# 3. Train with good settings for educational content
JOB_ID=$(curl -s -X POST "$BASE_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "'$PROJECT'",
    "dataset_filename": "'$DATASET'",
    "training_args": {
      "lora_r": 32,
      "learning_rate": 2e-4,
      "num_train_epochs": 5,
      "batch_size": 2
    }
  }' | jq -r '.job_id')

echo "Training Job: $JOB_ID"

echo -e "\n\n=== Monitoring Training ==="
while true; do
  STATUS=$(curl -s "$BASE_URL/train/status/$JOB_ID" | jq -r '.status')
  PROGRESS=$(curl -s "$BASE_URL/train/status/$JOB_ID" | jq -r '.progress.percentage')

  echo "Status: $STATUS | Progress: $PROGRESS%"

  if [[ "$STATUS" == "completed" || "$STATUS" == "failed" ]]; then
    break
  fi

  sleep 15
done

echo -e "\n\n=== Training Complete ==="
```

### Example Training Data

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "I don't understand fractions. They're so confusing!"
    },
    {
      "from": "gpt",
      "value": "<assess>Student is struggling with basic fraction concept, showing frustration. Needs foundational understanding.</assess>\n<explanation>Don't worry, fractions are actually pretty simple once you get the idea! A fraction is just a way of showing a part of a whole. The top number (numerator) tells you how many parts you have, and the bottom number (denominator) tells you how many equal parts the whole is divided into. Think of it like slicing a pizza!</explanation>\n<example>Imagine you have a pizza cut into 8 equal slices. If you eat 3 slices, you've eaten 3/8 (three-eighths) of the pizza. The 3 is how many slices you ate, and the 8 is how many slices the whole pizza was cut into. Make sense?</example>\n<practice>Try this: If you have a chocolate bar divided into 12 equal pieces and you eat 5 pieces, what fraction of the chocolate bar did you eat? Write it as a fraction!</practice>\n<encouragement>You're doing great by asking questions! That's exactly how we learn. Fractions will feel natural very soon! 🌟</encouragement>"
    }
  ]
}
```

---

## 6. Creative Writing Assistant

Help writers with story development, character building, and plot suggestions.

### XML Pattern Design

```xml
<analysis>Analysis of the writing request</analysis>
<ideas>Creative ideas and suggestions</ideas>
<example>Example text demonstrating the concept</example>
<next_steps>Suggested next steps for the writer</next_steps>
```

### Advanced Pattern Example

```bash
# Create writing assistant with detailed patterns
model-train project create writing-assistant \
  --objective "Help writers develop stories, characters, and plots" \
  --model "unsloth/llama-2-13b-bnb-4bit"

# Add comprehensive XML patterns
model-train xml add-tag writing-assistant analysis \
  --description "Analysis of writer's request and current situation" \
  --example "<analysis>Writer needs help with character motivation for protagonist</analysis>"

model-train xml add-tag writing-assistant ideas \
  --description "Multiple creative suggestions (at least 3)" \
  --constraint "Must provide at least 3 distinct ideas"

model-train xml add-tag writing-assistant example \
  --description "Example paragraph demonstrating the concept"

model-train xml add-tag writing-assistant next_steps \
  --description "Actionable next steps for the writer"

# Generate with high temperature for creativity
model-train generate writing-assistant \
  --count 400 \
  --temperature 0.9 \
  --batch-size 20

# Train
model-train train start writing-assistant \
  --epochs 5 \
  --lora-rank 32
```

---

## 7. SQL Query Generator

Generate SQL queries from natural language descriptions.

### XML Pattern Design

```xml
<understand>Understanding of the data request</understand>
<tables>Relevant tables and columns</tables>
<query>SQL query</query>
<explanation>Explanation of how the query works</explanation>
<example_output>Example of what the query returns</example_output>
```

### Training Data Template

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "Find all customers who made purchases over $1000 in the last month"
    },
    {
      "from": "gpt",
      "value": "<understand>Need to query customers table joined with purchases table, filter by amount > 1000 and date within last 30 days</understand>\n<tables>- customers (id, name, email)\n- purchases (id, customer_id, amount, purchase_date)</tables>\n<query>\nSELECT DISTINCT c.id, c.name, c.email\nFROM customers c\nINNER JOIN purchases p ON c.id = p.customer_id\nWHERE p.amount > 1000\n  AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)\nORDER BY c.name;\n</query>\n<explanation>This query joins the customers and purchases tables, filters for purchases over $1000 in the last month, and returns distinct customers. DISTINCT ensures each customer appears only once even if they made multiple qualifying purchases.</explanation>\n<example_output>\n| id | name | email |\n|----|------|-------|\n| 42 | Alice Smith | alice@email.com |\n| 57 | Bob Jones | bob@email.com |\n</example_output>"
    }
  ]
}
```

---

## 8. JSON API Response Generator

Generate structured JSON responses for APIs.

### XML Pattern Design

```xml
<request_analysis>Analysis of the API request</request_analysis>
<response_structure>JSON structure to return</response_structure>
<validation>Validation rules applied</validation>
<example>Example JSON response</example>
```

### Complete Python Example with Testing

```python
#!/usr/bin/env python3
"""
Complete example: Create and test JSON API Response Generator
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def create_json_api_project():
    """Create project for JSON API response generation"""

    # 1. Project configuration
    project_data = {
        "name": "json-api-generator",
        "objective": "Generate valid JSON API responses with proper structure and validation",
        "xml_patterns": [
            {
                "tag_name": "request_analysis",
                "description": "Analysis of the API request and requirements"
            },
            {
                "tag_name": "response_structure",
                "description": "Description of JSON response structure"
            },
            {
                "tag_name": "validation",
                "description": "Validation rules and constraints applied"
            },
            {
                "tag_name": "example",
                "description": "Complete example JSON response"
            }
        ],
        "base_model": "unsloth/mistral-7b-instruct-bnb-4bit",
        "dataset_format": "sharegpt",
        "ai_config": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929",
            "temperature": 0.5  # Lower for consistent JSON
        }
    }

    # Create project
    print("Creating project...")
    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    response.raise_for_status()
    print(f"✓ Project created: {response.json()['name']}")

    # 2. Generate training data
    print("\nGenerating training data...")
    gen_data = {
        "project_name": "json-api-generator",
        "num_examples": 500,
        "temperature": 0.5,
        "batch_size": 25
    }

    response = requests.post(f"{BASE_URL}/generate", json=gen_data)
    response.raise_for_status()
    dataset = response.json()
    print(f"✓ Generated {dataset['num_generated']} examples")
    print(f"  Dataset: {dataset['dataset_filename']}")

    # 3. Start training
    print("\nStarting training...")
    train_data = {
        "project_name": "json-api-generator",
        "dataset_filename": dataset['dataset_filename'],
        "training_args": {
            "lora_r": 32,
            "learning_rate": 2e-4,
            "num_train_epochs": 7,
            "batch_size": 2
        }
    }

    response = requests.post(f"{BASE_URL}/train", json=train_data)
    response.raise_for_status()
    job = response.json()
    job_id = job['job_id']
    print(f"✓ Training started: {job_id}")

    # 4. Monitor training
    print("\nMonitoring training progress...")
    while True:
        response = requests.get(f"{BASE_URL}/train/status/{job_id}")
        status = response.json()

        print(f"  Status: {status['status']}, Progress: {status['progress']['percentage']:.1f}%", end='\r')

        if status['status'] in ['completed', 'failed', 'cancelled']:
            print()  # New line
            break

        time.sleep(10)

    if status['status'] == 'completed':
        print("\n✓ Training completed successfully!")
        print(f"  Output: {status['output_dir']}")
        return True
    else:
        print(f"\n✗ Training {status['status']}")
        if 'error_message' in status:
            print(f"  Error: {status['error_message']}")
        return False

if __name__ == "__main__":
    success = create_json_api_project()
    exit(0 if success else 1)
```

---

## Advanced Patterns

### Multi-Language Support

```xml
<input_language>Language of input text</input_language>
<translation>Translated to target language</translation>
<cultural_notes>Cultural context and notes</cultural_notes>
<formality>Level of formality (casual, formal, business)</formality>
```

### Debugging Assistant

```xml
<error_analysis>Analysis of the error</error_analysis>
<root_cause>Root cause identification</root_cause>
<solution>Proposed solution</solution>
<code_fix>Corrected code</code_fix>
<prevention>How to prevent in future</prevention>
```

### Content Moderation

```xml
<content_type>Type of content (text, image description, etc.)</content_type>
<safety_analysis>Safety and appropriateness analysis</safety_analysis>
<violations>Any policy violations found</violations>
<action>Recommended action (approve, flag, remove)</action>
<explanation>Explanation of decision</explanation>
```

---

## Tips for All Examples

### Common Best Practices

1. **Start Small**: Begin with 100-200 examples, test, then scale up
2. **Review Data**: Always manually review a sample of generated data
3. **Iterate**: Train, test, identify weaknesses, generate more targeted data
4. **Temperature**: Lower (0.5-0.7) for structured tasks, higher (0.8-1.0) for creative tasks
5. **Model Selection**: Use larger models (13B+) for complex reasoning tasks
6. **LoRA Rank**: Start with 16, increase to 32-64 for complex patterns

### Testing Your Model

```bash
# After training, test with Ollama
ollama run your-model-name "Test input"

# Or via API
curl http://localhost:11434/api/generate \
  -d '{
    "model": "your-model-name",
    "prompt": "Test input",
    "stream": false
  }'
```

### Monitoring Quality

```python
def evaluate_model_quality(model_name, test_cases):
    """Test model on various inputs"""
    import re

    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "xml_valid": 0
    }

    for test in test_cases:
        response = generate(model_name, test['input'])

        # Check for required XML tags
        has_all_tags = all(
            f"<{tag}>" in response and f"</{tag}>" in response
            for tag in test['required_tags']
        )

        if has_all_tags:
            results['xml_valid'] += 1
            results['passed'] += 1
        else:
            results['failed'] += 1

    return results
```

---

## Support

For more examples or help:
- Check [USER_GUIDE.md](USER_GUIDE.md) for detailed tutorials
- See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Visit [FAQ.md](FAQ.md) for troubleshooting
- Ask in GitHub Discussions for community help

---

**Happy Training!** 🚀
