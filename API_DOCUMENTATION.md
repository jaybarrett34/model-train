# API Documentation

Complete REST API reference for the Model Fine-Tuning Application. All endpoints are accessible at `http://localhost:8000/api/v1`.

## Table of Contents

1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Projects API](#projects-api)
7. [Generation API](#generation-api)
8. [Training API](#training-api)
9. [Models API](#models-api)
10. [Configuration API](#configuration-api)
11. [Code Examples](#code-examples)

---

## Authentication

**Current Version**: No authentication required (v0.1.0)

**Future Versions**: Will support:
- API Key authentication
- OAuth 2.0
- JWT tokens

---

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

All endpoints are prefixed with `/api/v1`.

---

## Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

HTTP status codes are used appropriately:
- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Error Handling

### Common Error Codes

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 400 | Bad Request | Invalid JSON, missing required fields |
| 404 | Not Found | Project doesn't exist |
| 409 | Conflict | Project name already exists |
| 422 | Validation Error | Invalid data format |
| 500 | Server Error | Internal server error |

### Error Response Examples

**400 Bad Request**:
```json
{
  "detail": "Field 'objective' is required"
}
```

**404 Not Found**:
```json
{
  "detail": "Project 'my-project' not found"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "num_examples"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

---

## Rate Limiting

**Current Version**: No rate limiting (v0.1.0)

**Best Practices**:
- Limit generation requests to avoid overwhelming AI providers
- Use batch operations when possible
- Implement exponential backoff for retries

**Recommended Limits** (to implement client-side):
- Generation API: 10 requests/minute
- Training API: 5 requests/minute
- All other endpoints: 60 requests/minute

---

## Projects API

### Create Project

Create a new fine-tuning project.

**Endpoint**: `POST /api/v1/projects`

**Request Body**:
```json
{
  "name": "my-project",
  "objective": "Training objective description",
  "xml_patterns": [
    {
      "tag_name": "thinking",
      "description": "Internal reasoning",
      "constraints": "Must appear before output",
      "required": true
    }
  ],
  "base_model": "unsloth/llama-2-7b-bnb-4bit",
  "dataset_format": "sharegpt",
  "ai_config": {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.7,
    "max_tokens": 1024
  },
  "training_config": {
    "max_seq_length": 2048,
    "load_in_4bit": true,
    "lora_r": 16,
    "lora_alpha": 16,
    "batch_size": 2,
    "gradient_accumulation_steps": 4,
    "learning_rate": 0.0002,
    "num_train_epochs": 3,
    "warmup_steps": 5
  }
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique project identifier (lowercase, no spaces) |
| `objective` | string | Yes | Training objective description |
| `xml_patterns` | array | No | Array of XML pattern definitions |
| `base_model` | string | No | HuggingFace model ID (default: "unsloth/llama-2-7b-bnb-4bit") |
| `dataset_format` | string | No | "sharegpt" or "alpaca" (default: "sharegpt") |
| `ai_config` | object | No | AI provider configuration for data generation |
| `training_config` | object | No | Training hyperparameters |

**XML Pattern Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tag_name` | string | Yes | XML tag name (e.g., "thinking") |
| `description` | string | Yes | Description of tag's purpose |
| `constraints` | string | No | Validation constraints |
| `required` | boolean | No | Whether tag is required (default: true) |
| `attributes` | object | No | Allowed XML attributes |
| `examples` | array | No | Example usage strings |

**Response** (201 Created):
```json
{
  "name": "my-project",
  "objective": "Training objective description",
  "xml_patterns": [...],
  "base_model": "unsloth/llama-2-7b-bnb-4bit",
  "dataset_format": "sharegpt",
  "ai_config": {...},
  "training_config": {...},
  "datasets": [],
  "created_at": "2023-11-13T10:00:00Z",
  "updated_at": "2023-11-13T10:00:00Z"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "chatbot",
    "objective": "Train a helpful chatbot",
    "base_model": "unsloth/llama-2-7b-bnb-4bit"
  }'
```

---

### List Projects

Retrieve all projects.

**Endpoint**: `GET /api/v1/projects`

**Query Parameters**: None

**Response** (200 OK):
```json
{
  "projects": [
    {
      "name": "project1",
      "objective": "...",
      "base_model": "...",
      "created_at": "...",
      "updated_at": "..."
    },
    {
      "name": "project2",
      "objective": "...",
      "base_model": "...",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "total": 2
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/projects
```

---

### Get Project

Retrieve a specific project by name.

**Endpoint**: `GET /api/v1/projects/{name}`

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Project name |

**Response** (200 OK):
```json
{
  "name": "my-project",
  "objective": "Training objective",
  "xml_patterns": [...],
  "base_model": "unsloth/llama-2-7b-bnb-4bit",
  "dataset_format": "sharegpt",
  "ai_config": {...},
  "training_config": {...},
  "datasets": [
    {
      "filename": "dataset_20231113.json",
      "created_at": "2023-11-13T11:00:00Z",
      "num_examples": 100,
      "format": "sharegpt"
    }
  ],
  "created_at": "2023-11-13T10:00:00Z",
  "updated_at": "2023-11-13T11:00:00Z"
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/projects/my-project
```

---

### Update Project

Update an existing project.

**Endpoint**: `PUT /api/v1/projects/{name}`

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Project name |

**Request Body** (partial update supported):
```json
{
  "objective": "Updated objective",
  "xml_patterns": [...]
}
```

**Response** (200 OK):
Returns the updated project object.

**Example**:
```bash
curl -X PUT http://localhost:8000/api/v1/projects/my-project \
  -H "Content-Type: application/json" \
  -d '{
    "xml_patterns": [
      {
        "tag_name": "thinking",
        "description": "Reasoning process"
      }
    ]
  }'
```

---

### Delete Project

Delete a project and all associated data.

**Endpoint**: `DELETE /api/v1/projects/{name}`

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Project name |

**Response** (204 No Content):
No response body.

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/v1/projects/my-project
```

---

## Generation API

### Generate Dataset

Generate synthetic training data for a project.

**Endpoint**: `POST /api/v1/generate`

**Request Body**:
```json
{
  "project_name": "my-project",
  "num_examples": 100,
  "batch_size": 10,
  "temperature": 0.8,
  "mode": "pseudorandom",
  "validate": true
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_name` | string | Yes | Name of the project |
| `num_examples` | integer | Yes | Number of examples to generate |
| `batch_size` | integer | No | Batch size for generation (default: 10) |
| `temperature` | float | No | AI temperature 0.0-2.0 (default: 0.7) |
| `mode` | string | No | "pseudorandom", "diverse", or "focused" (default: "pseudorandom") |
| `validate` | boolean | No | Validate XML patterns (default: true) |

**Response** (200 OK):
```json
{
  "dataset_filename": "my-project_20231113_110000_100ex.json",
  "num_generated": 100,
  "num_validated": 100,
  "num_failed": 0,
  "format": "sharegpt",
  "generation_time_seconds": 245.7,
  "metadata": {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.8,
    "total_tokens": 15000
  }
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `dataset_filename` | string | Generated dataset file name |
| `num_generated` | integer | Number of successfully generated examples |
| `num_validated` | integer | Number passing validation |
| `num_failed` | integer | Number that failed generation or validation |
| `format` | string | Dataset format ("sharegpt" or "alpaca") |
| `generation_time_seconds` | float | Total time taken |
| `metadata` | object | Additional generation metadata |

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-project",
    "num_examples": 100,
    "temperature": 0.8
  }'
```

**Long-running Operation**:
This endpoint may take several minutes to complete. Consider implementing:
- Client-side timeout handling (5-10 minutes)
- Progress polling (future feature)
- WebSocket updates (future feature)

---

## Training API

### Start Training

Start a fine-tuning job for a project.

**Endpoint**: `POST /api/v1/train`

**Request Body**:
```json
{
  "project_name": "my-project",
  "dataset_filename": "my-project_20231113_110000_100ex.json",
  "output_dir": "models/my-project",
  "training_args": {
    "lora_r": 16,
    "lora_alpha": 16,
    "learning_rate": 0.0002,
    "batch_size": 2,
    "gradient_accumulation_steps": 4,
    "num_train_epochs": 3,
    "max_seq_length": 2048,
    "warmup_steps": 5,
    "logging_steps": 1,
    "save_steps": 100
  }
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_name` | string | Yes | Name of the project |
| `dataset_filename` | string | Yes | Dataset file to use for training |
| `output_dir` | string | No | Output directory (default: "models/{project_name}") |
| `training_args` | object | No | Training hyperparameters |

**Response** (201 Created):
```json
{
  "job_id": "train_20231113_110500_abc123",
  "project_name": "my-project",
  "dataset_filename": "my-project_20231113_110000_100ex.json",
  "output_dir": "models/my-project",
  "status": "pending",
  "created_at": "2023-11-13T11:05:00Z"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/train \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-project",
    "dataset_filename": "dataset.json"
  }'
```

---

### Get Training Status

Check the status of a training job.

**Endpoint**: `GET /api/v1/train/status/{job_id}`

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | string | Training job ID |

**Response** (200 OK):
```json
{
  "job_id": "train_20231113_110500_abc123",
  "project_name": "my-project",
  "status": "running",
  "progress": {
    "current_epoch": 2,
    "total_epochs": 3,
    "current_step": 150,
    "total_steps": 225,
    "percentage": 66.7
  },
  "metrics": {
    "loss": 0.342,
    "learning_rate": 0.0002,
    "tokens_per_second": 1250,
    "samples_per_second": 2.5
  },
  "started_at": "2023-11-13T11:05:30Z",
  "estimated_completion": "2023-11-13T11:45:00Z",
  "output_dir": "models/my-project"
}
```

**Status Values**:
- `pending` - Job created, not started yet
- `running` - Currently training
- `completed` - Training finished successfully
- `failed` - Training encountered an error
- `cancelled` - Training was cancelled by user

**Example**:
```bash
curl http://localhost:8000/api/v1/train/status/train_20231113_110500_abc123
```

**Polling Recommendation**:
Poll this endpoint every 5-10 seconds while status is "pending" or "running".

---

### Cancel Training

Cancel a running training job.

**Endpoint**: `DELETE /api/v1/train/cancel/{job_id}`

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | string | Training job ID |

**Response** (200 OK):
```json
{
  "job_id": "train_20231113_110500_abc123",
  "status": "cancelled",
  "cancelled_at": "2023-11-13T11:25:00Z",
  "message": "Training job cancelled successfully"
}
```

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/v1/train/cancel/train_20231113_110500_abc123
```

---

## Models API

### List Models

List all downloaded models.

**Endpoint**: `GET /api/v1/models`

**Response** (200 OK):
```json
{
  "models": [
    {
      "model_id": "unsloth/llama-2-7b-bnb-4bit",
      "name": "Llama 2 7B 4-bit",
      "path": "./models/unsloth--llama-2-7b-bnb-4bit",
      "size_gb": 3.8,
      "quantization": "4bit",
      "downloaded_at": "2023-11-10T09:00:00Z"
    },
    {
      "model_id": "unsloth/mistral-7b-bnb-4bit",
      "name": "Mistral 7B 4-bit",
      "path": "./models/unsloth--mistral-7b-bnb-4bit",
      "size_gb": 3.9,
      "quantization": "4bit",
      "downloaded_at": "2023-11-11T14:30:00Z"
    }
  ],
  "total": 2,
  "total_size_gb": 7.7
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/models
```

---

### Download Model

Download a model from HuggingFace.

**Endpoint**: `POST /api/v1/models/download`

**Request Body**:
```json
{
  "model_id": "unsloth/llama-2-7b-bnb-4bit",
  "revision": "main",
  "quantization": "4bit"
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model_id` | string | Yes | HuggingFace model ID |
| `revision` | string | No | Model revision/branch (default: "main") |
| `quantization` | string | No | Quantization type: "4bit", "8bit", or "none" |

**Response** (200 OK):
```json
{
  "model_id": "unsloth/llama-2-7b-bnb-4bit",
  "model_path": "./models/unsloth--llama-2-7b-bnb-4bit",
  "size_gb": 3.8,
  "download_time_seconds": 245,
  "status": "completed"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/models/download \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "unsloth/llama-2-7b-bnb-4bit"
  }'
```

**Note**: This is a long-running operation (5-30 minutes depending on model size and connection speed).

---

### Delete Model

Delete a downloaded model.

**Endpoint**: `DELETE /api/v1/models/{model_name}`

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `model_name` | string | Model name or ID (URL-encoded) |

**Response** (204 No Content):
No response body.

**Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/models/unsloth--llama-2-7b-bnb-4bit"
```

---

## Configuration API

### Get Configuration

Retrieve current application configuration.

**Endpoint**: `GET /api/v1/config`

**Response** (200 OK):
```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": true
  },
  "ai_providers": {
    "anthropic": {
      "enabled": true,
      "model": "claude-sonnet-4-5-20250929"
    },
    "openai": {
      "enabled": true,
      "model": "gpt-4"
    },
    "ollama": {
      "enabled": true,
      "base_url": "http://localhost:11434",
      "model": "llama2"
    }
  },
  "storage": {
    "projects_dir": "./projects",
    "models_dir": "./models",
    "datasets_dir": "./datasets"
  },
  "training_defaults": {
    "max_seq_length": 2048,
    "batch_size": 2,
    "learning_rate": 0.0002,
    "num_train_epochs": 3
  }
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/config
```

---

### Update Configuration

Update application configuration.

**Endpoint**: `POST /api/v1/config`

**Request Body**:
```json
{
  "ai_providers": {
    "ollama": {
      "base_url": "http://192.168.1.100:11434"
    }
  },
  "training_defaults": {
    "batch_size": 4
  }
}
```

**Response** (200 OK):
Returns the updated configuration object.

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "training_defaults": {
      "batch_size": 4
    }
  }'
```

---

## Code Examples

### Python Example

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# Create a project
project_data = {
    "name": "my-chatbot",
    "objective": "Train a helpful chatbot",
    "xml_patterns": [
        {
            "tag_name": "thinking",
            "description": "Internal reasoning"
        },
        {
            "tag_name": "response",
            "description": "User-facing response"
        }
    ]
}

response = requests.post(f"{BASE_URL}/projects", json=project_data)
project = response.json()
print(f"Created project: {project['name']}")

# Generate training data
gen_data = {
    "project_name": "my-chatbot",
    "num_examples": 100,
    "temperature": 0.8
}

response = requests.post(f"{BASE_URL}/generate", json=gen_data)
dataset = response.json()
print(f"Generated dataset: {dataset['dataset_filename']}")

# Start training
train_data = {
    "project_name": "my-chatbot",
    "dataset_filename": dataset['dataset_filename']
}

response = requests.post(f"{BASE_URL}/train", json=train_data)
job = response.json()
job_id = job['job_id']
print(f"Started training job: {job_id}")

# Poll for training status
while True:
    response = requests.get(f"{BASE_URL}/train/status/{job_id}")
    status = response.json()

    print(f"Status: {status['status']}, Progress: {status['progress']['percentage']:.1f}%")

    if status['status'] in ['completed', 'failed', 'cancelled']:
        break

    time.sleep(10)  # Wait 10 seconds before next poll

print(f"Training {status['status']}!")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';

async function createAndTrainModel() {
  try {
    // Create project
    const projectData = {
      name: 'my-chatbot',
      objective: 'Train a helpful chatbot',
      xml_patterns: [
        { tag_name: 'thinking', description: 'Internal reasoning' },
        { tag_name: 'response', description: 'User-facing response' }
      ]
    };

    const project = await axios.post(`${BASE_URL}/projects`, projectData);
    console.log(`Created project: ${project.data.name}`);

    // Generate training data
    const genData = {
      project_name: 'my-chatbot',
      num_examples: 100,
      temperature: 0.8
    };

    const dataset = await axios.post(`${BASE_URL}/generate`, genData);
    console.log(`Generated dataset: ${dataset.data.dataset_filename}`);

    // Start training
    const trainData = {
      project_name: 'my-chatbot',
      dataset_filename: dataset.data.dataset_filename
    };

    const job = await axios.post(`${BASE_URL}/train`, trainData);
    const jobId = job.data.job_id;
    console.log(`Started training job: ${jobId}`);

    // Poll for status
    let status;
    do {
      await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10s

      const statusResponse = await axios.get(`${BASE_URL}/train/status/${jobId}`);
      status = statusResponse.data;

      console.log(`Status: ${status.status}, Progress: ${status.progress.percentage.toFixed(1)}%`);
    } while (!['completed', 'failed', 'cancelled'].includes(status.status));

    console.log(`Training ${status.status}!`);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

createAndTrainModel();
```

### cURL Examples

**Complete workflow**:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"

# 1. Create project
curl -X POST "$BASE_URL/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-chatbot",
    "objective": "Train a helpful chatbot"
  }' | jq

# 2. Add XML patterns
curl -X PUT "$BASE_URL/projects/my-chatbot" \
  -H "Content-Type: application/json" \
  -d '{
    "xml_patterns": [
      {"tag_name": "thinking", "description": "Internal reasoning"},
      {"tag_name": "response", "description": "User response"}
    ]
  }' | jq

# 3. Generate data
DATASET=$(curl -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-chatbot",
    "num_examples": 100
  }' | jq -r '.dataset_filename')

echo "Generated dataset: $DATASET"

# 4. Start training
JOB_ID=$(curl -X POST "$BASE_URL/train" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_name\": \"my-chatbot\",
    \"dataset_filename\": \"$DATASET\"
  }" | jq -r '.job_id')

echo "Training job ID: $JOB_ID"

# 5. Poll status
while true; do
  STATUS=$(curl -s "$BASE_URL/train/status/$JOB_ID" | jq -r '.status')
  PROGRESS=$(curl -s "$BASE_URL/train/status/$JOB_ID" | jq -r '.progress.percentage')

  echo "Status: $STATUS, Progress: $PROGRESS%"

  if [[ "$STATUS" == "completed" || "$STATUS" == "failed" ]]; then
    break
  fi

  sleep 10
done

echo "Training complete!"
```

---

## WebSocket API (Future Feature)

**Planned for v0.2.0**:

```javascript
// Connect to training updates
const ws = new WebSocket('ws://localhost:8000/ws/train/job_id');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`Step ${update.step}/${update.total_steps}, Loss: ${update.loss}`);
};
```

Features:
- Real-time training progress
- Live generation updates
- Model download progress
- Error notifications

---

## API Versioning

**Current Version**: `v1` (0.1.0)

**Version Strategy**:
- Major version in URL path (`/api/v1`, `/api/v2`)
- Breaking changes increment major version
- Backward-compatible changes don't change version
- Old versions supported for 6 months after new version release

**Deprecation Process**:
1. New version released with deprecation notice
2. 3-month warning period
3. 3-month deprecation period
4. Old version removed

---

## OpenAPI/Swagger

**Interactive Documentation**: http://localhost:8000/docs

**ReDoc Documentation**: http://localhost:8000/redoc

**OpenAPI JSON**: http://localhost:8000/openapi.json

Use these for:
- Testing API endpoints interactively
- Generating client libraries
- Viewing all endpoint details
- Trying out requests directly

---

## Support

For API issues:
- Check [FAQ.md](FAQ.md) for common problems
- Report bugs on GitHub Issues
- Request features on GitHub Discussions
- See [EXAMPLES.md](EXAMPLES.md) for more code samples

---

**Last Updated**: 2023-11-13
**API Version**: v1 (0.1.0)
