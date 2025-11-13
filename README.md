# Model Fine-Tuning Application

A comprehensive platform for fine-tuning large language models with XML pattern synthesis and AI-powered data generation. Train custom models with structured output patterns using a powerful combination of synthetic data generation, XML validation, and efficient LoRA/QLoRA fine-tuning.

## Features

- **Project Management**: Create and manage multiple fine-tuning projects with different objectives
- **XML Pattern Engine**: Define custom XML patterns with constraints, attributes, and validation rules
- **Synthetic Data Generation**: Generate high-quality training data using Ollama, Anthropic Claude, or OpenAI
- **Unsloth Integration**: Memory-efficient fine-tuning with QLoRA/LoRA using Unsloth's optimized library
- **Multiple Interfaces**: Choose from Web UI (React), TUI (Textual), or CLI (Click)
- **Dataset Formats**: Support for ShareGPT and Alpaca conversation formats
- **Model Export**: Export to GGUF, PyTorch, or HuggingFace formats
- **Real-time Monitoring**: Track training progress with live metrics and logs

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT INTERFACES                         │
├───────────────┬─────────────────────┬──────────────────────────┤
│   Web UI      │        TUI          │          CLI             │
│  (React/Vite) │    (Textual)        │        (Click)           │
│   Port 5173   │   Terminal-based    │    Command-line          │
└───────┬───────┴──────────┬──────────┴────────────┬─────────────┘
        │                  │                        │
        └──────────────────┼────────────────────────┘
                           │ HTTP/REST
                           ▼
        ┌──────────────────────────────────────────┐
        │         FastAPI Backend (Port 8000)       │
        │  ┌────────────────────────────────────┐  │
        │  │         API Routes                 │  │
        │  │  /projects /generate /train /models│  │
        │  └────────────────┬───────────────────┘  │
        │  ┌────────────────▼───────────────────┐  │
        │  │         Services Layer             │  │
        │  │  ProjectService  GenerationService │  │
        │  │  TrainingService ModelService      │  │
        │  └────────────────┬───────────────────┘  │
        └───────────────────┼──────────────────────┘
                            │
        ┌───────────────────▼──────────────────────┐
        │          Core Modules (Python)            │
        ├──────────────┬───────────────┬───────────┤
        │ XML Engine   │  Synthesis    │  Training │
        │ - Validation │  - Ollama     │  - Unsloth│
        │ - Parsing    │  - Claude     │  - QLoRA  │
        │ - Patterns   │  - OpenAI     │  - LoRA   │
        └──────────────┴───────────────┴───────────┘
                            │
        ┌───────────────────▼──────────────────────┐
        │              Storage Layer                │
        ├──────────────┬───────────────┬───────────┤
        │  Projects    │   Datasets    │   Models  │
        │  (JSON)      │   (JSONL)     │  (HF/GGUF)│
        │  ./projects/ │  ./datasets/  │  ./models/│
        └──────────────┴───────────────┴───────────┘
```

## Quick Start

### Prerequisites

- **Python 3.10+** (with pip)
- **Node.js 18+** and npm (for frontend only)
- **CUDA-capable GPU** (recommended for training, optional for CPU/MPS)
- **Ollama** (optional, for local LLM generation)
- **8GB+ RAM** (16GB+ recommended for training)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd model-train
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   # or with pip install
   pip install -e .
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   nano .env  # or your preferred editor
   ```

4. **Install frontend dependencies** (optional, for Web UI):
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

#### Option 1: Web UI (Recommended for beginners)

**Terminal 1 - Start the Backend:**
```bash
python -m backend.main
# Backend runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Terminal 2 - Start the Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs at http://localhost:5173
```

Open your browser to `http://localhost:5173`

#### Option 2: TUI (Terminal User Interface)

```bash
# Make sure backend is running first
python -m backend.main &

# Launch the TUI
python -m cli.tui
# or
./tui.sh
```

Navigate with keyboard shortcuts:
- `P` - Projects
- `X` - XML Editor
- `G` - Generate Data
- `T` - Training
- `Q` - Quit

#### Option 3: CLI (Command-Line Interface)

```bash
# Make sure backend is running first
python -m backend.main &

# Use CLI commands
model-train --help
model-train project list
model-train project create my-project --objective "Train a chatbot"
model-train generate my-project --count 100
model-train train start my-project
```

## Usage Examples

### Example 1: Creating a Minecraft Bot (Web UI)

1. **Start the application** (backend + frontend)
2. **Create a new project**:
   - Name: `minecraft-bot`
   - Objective: "Train a Minecraft assistant that uses XML tags for thinking, commands, and speech"
   - Base Model: `unsloth/llama-2-7b-bnb-4bit`

3. **Add XML patterns**:
   - Tag `<thinking>`: "Internal reasoning before taking action"
   - Tag `<command>`: "Minecraft commands to execute"
   - Tag `<speak>`: "Text to say to the player"

4. **Generate dataset**: 200 examples with temperature 0.8
5. **Start training**: 3 epochs, LoRA rank 16
6. **Export model**: GGUF format for Ollama

### Example 2: Code Formatter (CLI)

```bash
# Create project
model-train project create code-formatter \
  --objective "Format code with XML structure analysis" \
  --model "unsloth/qwen2.5-14b-instruct-bnb-4bit"

# Add XML tags
model-train xml add-tag code-formatter analysis \
  --description "Code structure analysis" \
  --constraint "Must identify language and issues"

model-train xml add-tag code-formatter formatted \
  --description "Formatted code output"

# Generate training data
model-train generate code-formatter --count 500

# Start training
model-train train start code-formatter --epochs 5 --lora-rank 32

# Monitor progress
model-train train status <job-id> --watch
```

### Example 3: Customer Support Bot (TUI)

1. Launch TUI: `python -m cli.tui`
2. Press `P` for Projects → `N` for New
3. Configure:
   - Name: `support-bot`
   - Provider: `anthropic`
   - Model: `claude-sonnet-4-5-20250929`
4. Press `X` for XML Editor → `A` to add tags:
   - `<understand>`: Customer intent analysis
   - `<action>`: Required actions (search, escalate, resolve)
   - `<response>`: Customer-facing response
5. Press `G` to generate 300 examples
6. Press `T` to start training
7. Monitor real-time progress with metrics

## API Endpoints

### Projects API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/projects` | Create a new project |
| `GET` | `/api/v1/projects` | List all projects |
| `GET` | `/api/v1/projects/{name}` | Get project details |
| `PUT` | `/api/v1/projects/{name}` | Update project |
| `DELETE` | `/api/v1/projects/{name}` | Delete project |

### Data Generation API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/generate` | Generate synthetic training data |

### Training API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/train` | Start fine-tuning job |
| `GET` | `/api/v1/train/status/{job_id}` | Check training status |
| `DELETE` | `/api/v1/train/cancel/{job_id}` | Cancel training job |

### Models API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/models` | List available models |
| `POST` | `/api/v1/models/download` | Download model from HuggingFace |
| `DELETE` | `/api/v1/models/{model_name}` | Delete model |

### Configuration API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/config` | Get current configuration |
| `POST` | `/api/v1/config` | Update configuration |

Full API documentation available at `http://localhost:8000/docs`

## Interface Comparison

| Feature | Web UI | TUI | CLI |
|---------|--------|-----|-----|
| **Best For** | Beginners, visual users | Power users, SSH sessions | Automation, scripts |
| **Project Management** | ✓ Full GUI | ✓ Interactive forms | ✓ Commands |
| **XML Editor** | ✓ Visual editor | ✓ Table-based | ✓ CLI commands |
| **Data Generation** | ✓ Progress bars | ✓ Live logs | ✓ Progress bar |
| **Training Monitor** | ✓ Charts & graphs | ✓ Real-time metrics | ✓ Status polling |
| **Remote Access** | ✓ Browser-based | ✓ SSH-friendly | ✓ SSH-friendly |
| **Resource Usage** | Medium (React) | Low (terminal) | Very low |
| **Learning Curve** | Easy | Medium | Medium |

## Configuration

The application uses environment variables defined in `.env`:

### API Settings
```bash
API_HOST=0.0.0.0          # API host
API_PORT=8000              # API port
API_RELOAD=true            # Auto-reload on changes
```

### AI Provider Keys
```bash
ANTHROPIC_API_KEY=sk-ant-...      # For Claude
OPENAI_API_KEY=sk-...             # For GPT models
OLLAMA_BASE_URL=http://localhost:11434  # Ollama endpoint
OLLAMA_MODEL=llama2                     # Default Ollama model
HUGGINGFACE_TOKEN=hf_...          # For model downloads
```

### Storage Paths
```bash
PROJECTS_DIR=./projects    # Project JSON files
MODELS_DIR=./models        # Downloaded/trained models
DATASETS_DIR=./datasets    # Generated datasets
```

### Training Defaults
```bash
DEFAULT_MAX_SEQ_LENGTH=2048
DEFAULT_BATCH_SIZE=2
DEFAULT_LEARNING_RATE=2e-4
DEFAULT_NUM_TRAIN_EPOCHS=3
```

## Project Structure

```
model-train/
├── backend/              # FastAPI REST API
│   ├── api/             # API route handlers
│   │   ├── projects.py  # Project management
│   │   ├── generation.py # Data generation
│   │   ├── training.py  # Training jobs
│   │   ├── models.py    # Model operations
│   │   └── config.py    # Configuration
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic layer
├── frontend/            # React web interface
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── services/    # API client
│   └── package.json
├── core/                # Core Python modules
│   ├── synthesis.py     # Data generation with AI
│   ├── training.py      # Unsloth training pipeline
│   └── xml_engine.py    # XML pattern validation
├── cli/                 # Command-line interfaces
│   ├── main.py         # Click CLI
│   └── tui.py          # Textual TUI
├── projects/            # User projects (gitignored)
├── models/              # Downloaded/trained models (gitignored)
├── datasets/            # Generated datasets (gitignored)
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Troubleshooting

### Common Issues

#### CUDA Out of Memory
```
Error: CUDA out of memory
```
**Solutions:**
- Reduce `batch_size` to 1 in training config
- Enable 4-bit quantization: `load_in_4bit: true`
- Reduce `max_seq_length` to 1024 or 512
- Use gradient checkpointing (enabled by default)

#### API Connection Failed
```
Error: Cannot connect to API at http://localhost:8000
```
**Solutions:**
- Ensure backend is running: `python -m backend.main`
- Check port availability: `lsof -i :8000`
- Verify `API_URL` in environment

#### Training Not Starting
```
Error: Dataset file not found
```
**Solutions:**
- Verify dataset exists: `ls datasets/`
- Check dataset path in project JSON
- Regenerate dataset if needed

#### Model Download Fails
```
Error: Failed to download model
```
**Solutions:**
- Check HuggingFace token is valid
- Verify internet connection
- Try smaller model first
- Check disk space

### Performance Optimization

**For faster training:**
- Use 4-bit quantized models (bnb-4bit)
- Increase `gradient_accumulation_steps`
- Use `bf16` precision on A100/H100 GPUs
- Reduce `max_seq_length` if possible

**For better quality:**
- Increase `num_examples` for generation
- Use higher temperature (0.8-1.0) for diversity
- Increase LoRA rank (32 or 64)
- Train for more epochs (5-10)

**For lower memory usage:**
- Use smaller base models (7B instead of 14B)
- Reduce batch size to 1
- Enable gradient checkpointing
- Use QLoRA instead of LoRA

## Development

### Running Tests
```bash
python test_api.py          # Test API endpoints
python test_synthesis.py    # Test data generation
```

### Adding New Features

1. **Backend API**: Add routes in `backend/api/`, services in `backend/services/`
2. **Core Logic**: Implement in `core/synthesis.py`, `core/training.py`, or `core/xml_engine.py`
3. **Frontend**: Add components in `frontend/src/components/`
4. **CLI**: Add commands in `cli/main.py`
5. **TUI**: Add screens in `cli/tui.py`

### Project Data Schema

Projects are stored as JSON in `projects/`:

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
  "dataset_format": "sharegpt",
  "base_model": "unsloth/llama-2-7b-bnb-4bit",
  "ai_config": {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.7
  },
  "training_config": {
    "max_seq_length": 2048,
    "lora_r": 16,
    "batch_size": 2,
    "learning_rate": 0.0002
  },
  "datasets": [
    {
      "filename": "dataset_20231101.json",
      "num_examples": 100,
      "created_at": "2023-11-01T12:00:00"
    }
  ]
}
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

**Areas needing contributions:**
- Additional model architectures
- More dataset formats
- Enhanced XML validation
- UI/UX improvements
- Documentation examples

## Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Step-by-step tutorials for beginners
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete REST API reference
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world use cases and patterns
- **[FAQ.md](FAQ.md)** - Frequently asked questions
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates

## License

MIT License - See LICENSE file for details

## Acknowledgments

- **[Unsloth](https://github.com/unslothai/unsloth)** - Fast and memory-efficient fine-tuning
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Transformers](https://huggingface.co/docs/transformers/)** - HuggingFace model library
- **[Textual](https://textual.textualize.io/)** - Modern TUI framework
- **[Click](https://click.palletsprojects.com/)** - Python CLI framework
- **[React](https://react.dev/)** - Frontend UI library

## Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Wiki](https://github.com/your-repo/wiki)

---

**Made with ❤️ for the ML community**
