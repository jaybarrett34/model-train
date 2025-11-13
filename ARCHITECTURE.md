# Architecture Documentation

Complete system architecture documentation for the Model Fine-Tuning Application. This document explains the design decisions, component relationships, data flow, and technical stack.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Decisions](#design-decisions)
7. [Security Considerations](#security-considerations)
8. [Scalability & Performance](#scalability--performance)
9. [Future Architecture](#future-architecture)

---

## System Overview

The Model Fine-Tuning Application follows a **layered architecture** pattern with clear separation of concerns:

**Presentation Layer** (3 interfaces):
- Web UI (React SPA)
- TUI (Terminal interface)
- CLI (Command-line)

**API Layer** (FastAPI):
- RESTful endpoints
- Request validation
- Business logic orchestration

**Service Layer** (Python):
- Project management
- Data generation coordination
- Training orchestration
- Model operations

**Core Layer** (Python):
- XML pattern engine
- AI-powered synthesis
- Unsloth training pipeline

**Storage Layer**:
- JSON files for projects
- JSONL for datasets
- HuggingFace format for models

### Key Architectural Principles

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **Modularity**: Components can be developed, tested, and deployed independently
3. **Extensibility**: Easy to add new AI providers, model architectures, or interfaces
4. **Configurability**: Environment-based configuration for different deployments
5. **Developer Experience**: Clear APIs, good documentation, and helpful error messages

---

## Architecture Diagram

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐           │
│  │   Web UI    │  │     TUI      │  │       CLI         │           │
│  │  (React)    │  │  (Textual)   │  │     (Click)       │           │
│  │  Port 5173  │  │  Terminal    │  │   Command-line    │           │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬─────────┘           │
└─────────┼────────────────┼──────────────────────┼───────────────────┘
          │                │                      │
          │                │   HTTP/REST          │
          └────────────────┼──────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────────┐
│                      API LAYER (FastAPI)                            │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  API Routes (/api/v1)                                         │ │
│  │  ┌──────────┬──────────┬──────────┬──────────┬───────────┐  │ │
│  │  │Projects  │Generation│ Training │  Models  │   Config  │  │ │
│  │  │  CRUD    │   POST   │CRUD+Mgmt │   CRUD   │ GET/POST  │  │ │
│  │  └──────────┴──────────┴──────────┴──────────┴───────────┘  │ │
│  └──────────────────────────┬────────────────────────────────────┘ │
│                             │                                       │
│  ┌──────────────────────────▼────────────────────────────────────┐ │
│  │  Pydantic Schemas (Validation & Serialization)                │ │
│  │  - Request/Response models                                    │ │
│  │  - Data validation rules                                      │ │
│  │  - Type safety enforcement                                    │ │
│  └──────────────────────────┬────────────────────────────────────┘ │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                      SERVICE LAYER (Business Logic)                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  ProjectService  │  GenerationService  │  TrainingService    │  │
│  │  - Create/Read   │  - Coordinate AI    │  - Job management   │  │
│  │  - Update/Delete │  - Validate data    │  - Progress track   │  │
│  │  - Validation    │  - Save datasets    │  - Status updates   │  │
│  ├──────────────────┴──────────────────────┴────────────────────┤  │
│  │  ModelService    │  ConfigService                            │  │
│  │  - Download      │  - Load/save config                       │  │
│  │  - Management    │  - Env variables                          │  │
│  └──────────────────┴───────────────────────┬──────────────────────┘
└─────────────────────────────────────────────┼──────────────────────┘
                                              │
┌─────────────────────────────────────────────▼──────────────────────┐
│                      CORE LAYER (ML Logic)                          │
│  ┌──────────────────┬──────────────────┬──────────────────────┐   │
│  │   XML Engine     │   Synthesis      │     Training         │   │
│  │                  │                  │                      │   │
│  │ - Pattern parser │ - AIProvider     │ - UnslothTrainer     │   │
│  │ - Validator      │   interface      │ - LoRAConfig         │   │
│  │ - Constraint     │ - OllamaProvider │ - TrainingConfig     │   │
│  │   checker        │ - ClaudeProvider │ - ResourceManager    │   │
│  │ - XML formatter  │ - OpenAIProvider │ - ProgressTracker    │   │
│  │                  │ - DataSynthesizer│ - Model export       │   │
│  │                  │ - Format convert │ - GGUF/HF export     │   │
│  └──────────────────┴──────────────────┴──────────────────────┘   │
└─────────────────────────────────────────────┬──────────────────────┘
                                              │
┌─────────────────────────────────────────────▼──────────────────────┐
│                      STORAGE LAYER                                  │
│  ┌──────────────────┬──────────────────┬──────────────────────┐   │
│  │   Projects       │   Datasets       │     Models           │   │
│  │   (JSON)         │   (JSONL/JSON)   │  (HF/GGUF/PyTorch)   │   │
│  │                  │                  │                      │   │
│  │ ./projects/      │ ./datasets/      │ ./models/            │   │
│  │ - project.json   │ - dataset.jsonl  │ - model files        │   │
│  │ - metadata       │ - sharegpt fmt   │ - adapter files      │   │
│  │                  │ - alpaca fmt     │ - tokenizer files    │   │
│  └──────────────────┴──────────────────┴──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                                 │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐     │
│  │   Ollama     │  Anthropic   │   OpenAI     │ HuggingFace  │     │
│  │   (Local)    │   Claude     │    GPT       │  Hub (Models)│     │
│  └──────────────┴──────────────┴──────────────┴──────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
1. PROJECT CREATION FLOW:
   ┌─────┐     ┌─────┐     ┌─────────┐     ┌─────────┐
   │ UI  │────▶│ API │────▶│ Service │────▶│ Storage │
   └─────┘     └─────┘     └─────────┘     └─────────┘
                              │
                              ▼
                        Validate schema
                        Generate ID
                        Set timestamps

2. DATA GENERATION FLOW:
   ┌─────┐     ┌─────┐     ┌────────────┐     ┌──────────┐
   │ UI  │────▶│ API │────▶│ Generation │────▶│ AI       │
   └─────┘     └─────┘     │ Service    │     │ Provider │
                           └────────────┘     └──────────┘
                                 │                   │
                                 │◀──────────────────┘
                                 │
                                 ▼
                           ┌──────────┐     ┌─────────┐
                           │ XML      │────▶│ Storage │
                           │ Validate │     └─────────┘
                           └──────────┘

3. TRAINING FLOW:
   ┌─────┐     ┌─────┐     ┌──────────┐     ┌──────────┐
   │ UI  │────▶│ API │────▶│ Training │────▶│ Unsloth  │
   └─────┘     └─────┘     │ Service  │     │ Core     │
                           └──────────┘     └──────────┘
                                 │                 │
                                 │                 │
                                 ▼                 ▼
                           ┌──────────┐     ┌──────────┐
                           │ Progress │     │ Storage  │
                           │ Tracker  │     │ (Models) │
                           └──────────┘     └──────────┘
                                 │
                                 ▼
                           ┌──────────┐
                           │ Status   │
                           │ Updates  │
                           └──────────┘
```

---

## Component Breakdown

### 1. Frontend Layer

#### Web UI (React + Vite)

**Location**: `/frontend/src/`

**Components**:
- `App.jsx` - Main application component
- `components/` - Reusable UI components
  - `ProjectCard` - Project list item
  - `XMLEditor` - XML pattern editor
  - `TrainingMonitor` - Real-time training display
  - `DatasetViewer` - Dataset preview
- `pages/` - Full page components
  - `Dashboard` - Main overview
  - `ProjectsPage` - Project management
  - `GenerationPage` - Data generation
  - `TrainingPage` - Training interface
- `services/` - API client
  - `api.js` - HTTP client wrapper
- `store/` - State management (if using Redux/Zustand)

**State Management**:
```javascript
// Current: React Context
// Future: Consider Redux Toolkit for complex state
```

**Build Process**:
```bash
npm run dev    # Development server (Vite)
npm run build  # Production build
npm run preview # Preview production build
```

#### TUI (Textual)

**Location**: `/cli/tui.py`

**Screens**:
- `HomeScreen` - Welcome and navigation
- `ProjectScreen` - Project list and management
- `ProjectCreateScreen` - New project form
- `XMLEditorScreen` - XML pattern editor
- `XMLTagEditorScreen` - Individual tag editor
- `GenerationScreen` - Data generation interface
- `TrainingScreen` - Training monitor
- `ExportScreen` - Model export

**Architecture**:
```python
class ModelTrainTUI(App):
    """Main application"""
    SCREENS = {
        "home": HomeScreen,
        "projects": ProjectScreen,
        # ...
    }

class Screen:
    """Base screen with common functionality"""
    - compose() - Build UI
    - on_mount() - Initialize
    - actions - Keyboard shortcuts
```

**API Integration**:
```python
class APIClient:
    """HTTP client for backend API"""
    def _make_request(method, endpoint, data)
    def list_projects()
    def create_project(data)
    # ...
```

#### CLI (Click)

**Location**: `/cli/main.py`

**Command Structure**:
```
model-train
├── project
│   ├── list
│   ├── create
│   ├── show
│   └── delete
├── xml
│   ├── add-tag
│   ├── remove-tag
│   └── show
├── generate
├── train
│   ├── start
│   ├── status
│   └── cancel
├── model
│   ├── list
│   ├── download
│   └── export
└── analyze
    └── dataset
```

**Design Pattern**: Command pattern with Click decorators

```python
@cli.group()
def project():
    """Manage training projects"""
    pass

@project.command('create')
@click.argument('name')
@click.option('--objective', required=True)
def project_create(name, objective):
    """Create a new project"""
    # Implementation
```

### 2. API Layer (FastAPI)

**Location**: `/backend/`

#### Main Application (`main.py`)

```python
app = FastAPI(
    title="Model Fine-Tuning API",
    version="0.1.0",
    lifespan=lifespan  # Startup/shutdown handlers
)

# Middleware
app.add_middleware(CORSMiddleware, ...)

# Route mounting
app.include_router(api_router, prefix="/api/v1")
```

**Lifespan Management**:
- Startup: Create directories, initialize resources
- Shutdown: Cleanup, save state

#### API Routes (`api/`)

Each route module follows REST conventions:

```python
# api/projects.py
router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=Project, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    service: ProjectService = Depends(get_project_service)
):
    return service.create_project(project_data)

@router.get("", response_model=ProjectList)
async def list_projects(...)

@router.get("/{name}", response_model=Project)
async def get_project(name: str, ...)

@router.put("/{name}", response_model=Project)
async def update_project(name: str, updates: ProjectUpdate, ...)

@router.delete("/{name}", status_code=204)
async def delete_project(name: str, ...)
```

**Dependency Injection**:
```python
def get_project_service() -> ProjectService:
    """Dependency to get project service instance"""
    return ProjectService()

# Usage in routes
async def create_project(
    service: ProjectService = Depends(get_project_service)
):
    # Service is automatically injected
```

#### Schemas (`schemas/`)

Pydantic models for validation and serialization:

```python
class ProjectCreate(BaseModel):
    name: str = Field(..., pattern="^[a-z0-9-]+$")
    objective: str = Field(..., min_length=10)
    xml_patterns: List[XMLPattern] = Field(default_factory=list)
    base_model: str = Field(default="unsloth/llama-2-7b-bnb-4bit")
    # ...

class Project(ProjectCreate):
    created_at: datetime
    updated_at: datetime
    datasets: List[DatasetInfo] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Validation Benefits**:
- Automatic type checking
- Request/response validation
- OpenAPI schema generation
- Serialization/deserialization

### 3. Service Layer

**Location**: `/backend/services/`

#### ProjectService

```python
class ProjectService:
    def __init__(self):
        self.projects_dir = Path(os.getenv("PROJECTS_DIR", "./projects"))

    def create_project(self, project_data: ProjectCreate) -> Project:
        # 1. Validate project name
        # 2. Check for duplicates
        # 3. Set timestamps
        # 4. Save to JSON file
        # 5. Return project object

    def get_project(self, name: str) -> Optional[Project]:
        # 1. Load from JSON
        # 2. Parse and validate
        # 3. Return or None

    def update_project(self, name: str, updates: ProjectUpdate) -> Optional[Project]:
        # 1. Load existing
        # 2. Merge updates
        # 3. Validate
        # 4. Save
        # 5. Return updated

    def delete_project(self, name: str) -> bool:
        # 1. Delete project file
        # 2. Optional: Delete associated datasets
        # 3. Return success
```

**Storage Format** (`projects/{name}.json`):
```json
{
  "name": "my-project",
  "objective": "...",
  "xml_patterns": [...],
  "base_model": "...",
  "ai_config": {...},
  "training_config": {...},
  "datasets": [...],
  "created_at": "2023-11-13T10:00:00Z",
  "updated_at": "2023-11-13T11:00:00Z"
}
```

#### GenerationService

```python
class GenerationService:
    def __init__(self):
        self.datasets_dir = Path(os.getenv("DATASETS_DIR", "./datasets"))

    def generate_dataset(self, request: GenerateRequest) -> GenerateResponse:
        # 1. Load project
        # 2. Initialize AI provider (from core)
        # 3. Create DataSynthesizer
        # 4. Generate examples in batches
        # 5. Validate XML patterns
        # 6. Format dataset (ShareGPT/Alpaca)
        # 7. Save to file
        # 8. Update project with dataset info
        # 9. Return response with stats
```

**Integration with Core**:
```python
from core.synthesis import (
    OllamaProvider,
    ClaudeProvider,
    OpenAIProvider,
    DataSynthesizer,
    GenerationConfig,
    XMLPattern
)

# Select provider based on project config
if ai_config.provider == "ollama":
    provider = OllamaProvider(model=ai_config.model)
elif ai_config.provider == "anthropic":
    provider = ClaudeProvider(api_key=ANTHROPIC_API_KEY, model=ai_config.model)
# ...

# Create synthesizer
synthesizer = DataSynthesizer(
    provider=provider,
    xml_pattern=xml_pattern,
    config=generation_config
)

# Generate
examples = synthesizer.generate_batch(objectives, inputs)
```

#### TrainingService

```python
class TrainingService:
    def __init__(self):
        self.jobs = {}  # In-memory job tracking (TODO: Use Redis/DB)

    def start_training(self, request: TrainRequest) -> TrainResponse:
        # 1. Load project
        # 2. Validate dataset exists
        # 3. Create job ID
        # 4. Initialize UnslothTrainer (from core)
        # 5. Start training in background thread
        # 6. Return job ID

    def get_training_status(self, job_id: str) -> TrainStatus:
        # 1. Lookup job
        # 2. Return current status and metrics

    def cancel_training(self, job_id: str) -> Dict:
        # 1. Lookup job
        # 2. Send cancel signal
        # 3. Update status
```

**Background Job Execution**:
```python
import threading

def _train_background(job_id, project, dataset_path, output_dir, config):
    """Background training function"""
    try:
        # Update status: pending -> running
        job.status = "running"

        # Initialize trainer
        from core.training import UnslothTrainer
        trainer = UnslothTrainer(
            base_model=project.base_model,
            dataset_path=dataset_path,
            output_dir=output_dir,
            progress_callback=lambda progress: update_job_progress(job_id, progress)
        )

        # Train
        trainer.train(**config)

        # Update status: running -> completed
        job.status = "completed"
    except Exception as e:
        job.status = "failed"
        job.error = str(e)

# Start in thread
thread = threading.Thread(target=_train_background, args=(...))
thread.daemon = True
thread.start()
```

### 4. Core Layer

**Location**: `/core/`

#### XML Engine (`xml_engine.py`)

```python
class XMLValidator:
    """Validates generated data against XML patterns"""

    @staticmethod
    def validate_xml_structure(text: str, pattern: XMLPattern) -> Tuple[bool, Optional[str]]:
        # 1. Check for required tags using regex
        # 2. Parse XML fragments
        # 3. Validate structure
        # 4. Return (is_valid, error_message)

    @staticmethod
    def extract_xml_content(text: str, tag: str) -> Optional[str]:
        # Extract content between tags
```

**Pattern Definition**:
```python
@dataclass
class XMLPattern:
    schema: str  # XML schema or pattern
    required_tags: List[str]  # Must be present
    optional_tags: List[str]  # May be present
```

#### Synthesis Module (`synthesis.py`)

**AI Provider Interface**:
```python
class AIProvider(ABC):
    """Abstract base for AI providers"""

    @abstractmethod
    def generate(self, prompt: str, config: GenerationConfig) -> str:
        """Generate text"""
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """Check if provider is accessible"""
        pass
```

**Concrete Implementations**:
```python
class OllamaProvider(AIProvider):
    def generate(self, prompt, config):
        # HTTP request to Ollama API
        # Parse response
        # Return generated text

class ClaudeProvider(AIProvider):
    def generate(self, prompt, config):
        # Use anthropic library
        # Return response.content[0].text

class OpenAIProvider(AIProvider):
    def generate(self, prompt, config):
        # Use openai library
        # Return response.choices[0].message.content
```

**DataSynthesizer**:
```python
class DataSynthesizer:
    def __init__(self, provider, xml_pattern, config):
        self.provider = provider
        self.xml_pattern = xml_pattern
        self.config = config

    def generate_single(self, objective, input_text=None, validate=True):
        # 1. Build prompt from objective
        # 2. Call provider.generate()
        # 3. Validate XML if required
        # 4. Retry on failure (up to config.retry_attempts)
        # 5. Return example dict

    def generate_batch(self, objectives, inputs=None):
        # Generate multiple examples with rate limiting
```

**Format Converters**:
```python
def to_sharegpt_format(examples):
    """Convert to ShareGPT conversation format"""
    return [
        {
            "conversations": [
                {"from": "human", "value": ex["input"]},
                {"from": "gpt", "value": ex["output"]}
            ]
        }
        for ex in examples
    ]

def to_alpaca_format(examples):
    """Convert to Alpaca instruction format"""
    return [
        {
            "instruction": ex["input"],
            "input": "",
            "output": ex["output"]
        }
        for ex in examples
    ]
```

#### Training Module (`training.py`)

**UnslothTrainer**:
```python
class UnslothTrainer:
    def __init__(self, base_model, dataset_path, output_dir, **kwargs):
        self.base_model = base_model
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.resource_manager = ResourceManager()

    def setup(self, lora_config):
        # 1. Load model with Unsloth
        self.model, self.tokenizer = load_model_with_unsloth(...)

        # 2. Configure LoRA adapters
        self.model = configure_lora_adapters(self.model, lora_config)

        # 3. Load and format dataset
        self.dataset = load_dataset(...)

    def train(self, **training_args):
        # 1. Setup if not done
        # 2. Create TrainingArguments
        # 3. Initialize SFTTrainer
        # 4. Add progress callback
        # 5. Start training
        # 6. Monitor and update progress

    def save_model(self, adapter_only=False):
        # Save model/adapters to disk

    def export_gguf(self, output_path, quantization_method="q4_k_m"):
        # Export to GGUF format for Ollama
```

**ResourceManager**:
```python
class ResourceManager:
    def __init__(self):
        self.device = self._detect_device()  # cuda/mps/cpu

    def get_memory_stats(self):
        # Return GPU/MPS memory usage

    def clear_cache(self):
        # Clear GPU memory cache
```

**ProgressTracker**:
```python
class ProgressTracker:
    def __init__(self, total_steps, callback=None):
        self.total_steps = total_steps
        self.callback = callback

    def update(self, step, metrics):
        # Calculate progress percentage
        # Estimate time remaining
        # Call callback with progress info
```

---

## Technology Stack

### Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Core language | 3.10+ |
| **FastAPI** | Web framework | 0.104+ |
| **Pydantic** | Data validation | 2.0+ |
| **Uvicorn** | ASGI server | 0.24+ |
| **Unsloth** | Efficient fine-tuning | Latest |
| **Transformers** | Model library | 4.35+ |
| **PyTorch** | Deep learning | 2.1+ |
| **anthropic** | Claude API client | Latest |
| **openai** | OpenAI API client | 1.0+ |
| **requests** | HTTP client | 2.31+ |

### Frontend

| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | UI library | 18+ |
| **Vite** | Build tool | 5+ |
| **Axios** | HTTP client | 1.6+ |
| **Recharts** | Data visualization | 2.10+ |
| **TailwindCSS** | Styling (optional) | 3.3+ |

### CLI/TUI

| Technology | Purpose | Version |
|------------|---------|---------|
| **Click** | CLI framework | 8.1+ |
| **Textual** | TUI framework | 0.41+ |
| **Rich** | Terminal formatting | 13.6+ |

### Development

| Technology | Purpose | Version |
|------------|---------|---------|
| **pytest** | Testing | 7.4+ |
| **black** | Code formatting | 23.10+ |
| **flake8** | Linting | 6.1+ |
| **mypy** | Type checking | 1.6+ |

---

## Design Decisions

### 1. Why FastAPI over Flask/Django?

**Decision**: Use FastAPI for the backend

**Rationale**:
- ✅ Automatic OpenAPI/Swagger documentation
- ✅ Built-in data validation with Pydantic
- ✅ Modern async/await support
- ✅ Better performance than Flask
- ✅ Type hints and IDE support
- ✅ Easy WebSocket support for future features

**Trade-offs**:
- ❌ Smaller ecosystem than Django
- ❌ Steeper learning curve for beginners

### 2. Why JSON Files over Database?

**Decision**: Use JSON files for project storage

**Rationale**:
- ✅ Simple setup, no database required
- ✅ Human-readable and editable
- ✅ Easy to version control and backup
- ✅ Sufficient for small-medium scale
- ✅ Portable across systems

**Trade-offs**:
- ❌ Not suitable for high concurrency
- ❌ No ACID guarantees
- ❌ Slower for large numbers of projects

**Future Migration Path**: Easy to add PostgreSQL/MongoDB later without changing API

### 3. Why Three Interfaces?

**Decision**: Provide Web UI, TUI, and CLI

**Rationale**:
- **Web UI**: Best for beginners, visual learners, remote access
- **TUI**: Best for SSH sessions, power users, low bandwidth
- **CLI**: Best for automation, scripting, integration

**Alternative Considered**: Web UI only
- ❌ Not accessible in SSH-only environments
- ❌ Can't be scripted or automated easily

### 4. Why Unsloth?

**Decision**: Use Unsloth for training

**Rationale**:
- ✅ 2-5x faster than standard HuggingFace training
- ✅ 50-70% less memory usage
- ✅ Built-in 4-bit quantization support
- ✅ Easy LoRA/QLoRA configuration
- ✅ Export to multiple formats (GGUF, HF, etc.)

**Alternative Considered**: Pure HuggingFace Transformers
- ❌ Slower training
- ❌ More memory usage
- ❌ More complex setup

### 5. Why Separate Generation and Training?

**Decision**: Two-step process (generate → train)

**Rationale**:
- ✅ Users can review/edit generated data
- ✅ Can mix multiple data sources
- ✅ Easier to debug issues
- ✅ Can regenerate without retraining

**Alternative Considered**: Combined single-step
- ❌ Less control over data quality
- ❌ Harder to iterate and improve
- ❌ Wastes time/money if data is bad

### 6. Why Multiple AI Providers?

**Decision**: Support Ollama, Claude, and OpenAI

**Rationale**:
- **Ollama**: Free, local, private, but slower
- **Claude**: High quality, good at reasoning, moderate cost
- **OpenAI**: Fast, widely available, higher cost

Gives users flexibility based on:
- Budget (free → $$$ )
- Quality needs (good → excellent)
- Privacy requirements (local → cloud)
- Speed requirements (slow → fast)

---

## Security Considerations

### Current Security (v0.1.0)

**Authentication**: None (localhost only)
**Authorization**: None
**Data Privacy**: Local storage only
**API Keys**: Stored in `.env` file (gitignored)

### Security Best Practices

1. **Environment Variables**:
   ```bash
   # .env file (never commit)
   ANTHROPIC_API_KEY=sk-ant-...
   OPENAI_API_KEY=sk-...
   ```

2. **File Permissions**:
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

3. **Input Validation**:
   - All API inputs validated with Pydantic
   - Prevents injection attacks
   - Type safety enforced

4. **Path Traversal Protection**:
   ```python
   # Prevent ../../../etc/passwd attacks
   safe_path = Path(base_dir) / sanitize_filename(user_input)
   if not safe_path.is_relative_to(base_dir):
       raise ValueError("Invalid path")
   ```

### Future Security Features (v0.2.0+)

**Planned**:
- API key authentication
- User accounts and projects isolation
- Rate limiting per user/API key
- HTTPS enforcement
- Encrypted storage for API keys
- Audit logging
- RBAC (Role-Based Access Control)

**For Production Deployment**:
```python
# Add authentication middleware
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.get("/api/v1/projects")
async def list_projects(api_key: str = Depends(api_key_header)):
    validate_api_key(api_key)  # Raises 401 if invalid
    # ...
```

---

## Scalability & Performance

### Current Scalability

**Designed for**:
- 1-10 concurrent users
- 100s of projects
- 1000s of datasets
- Single machine deployment

**Bottlenecks**:
- In-memory job tracking (lost on restart)
- JSON file storage (slow with 1000s of projects)
- Single-threaded data generation
- No caching

### Performance Optimizations

**Already Implemented**:
- ✅ 4-bit model quantization (75% memory reduction)
- ✅ Gradient accumulation (lower memory, same quality)
- ✅ Unsloth training (2-5x faster)
- ✅ Batch processing for generation

**Future Optimizations**:
- Caching for frequently accessed projects
- Database for project storage (PostgreSQL)
- Redis for job tracking and caching
- Celery for distributed task queue
- Multi-GPU training support
- Streaming responses for long operations

### Scaling Strategies

**Vertical Scaling** (bigger machine):
- Add more RAM for larger models
- Add more/better GPUs for faster training
- Simple, works up to a point

**Horizontal Scaling** (more machines):
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  API Server │    │  API Server │    │  API Server │
│   (FastAPI) │    │   (FastAPI) │    │   (FastAPI) │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
              ┌───────────▼───────────┐
              │    Load Balancer      │
              │       (nginx)         │
              └───────────┬───────────┘
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
│   Redis     │    │ PostgreSQL  │    │   S3/Minio  │
│  (Cache +   │    │  (Projects) │    │  (Models +  │
│   Jobs)     │    │             │    │  Datasets)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

**Training Worker Pool**:
```
┌─────────────┐
│  API Server │
└──────┬──────┘
       │ Submit job
       ▼
┌─────────────┐
│   Celery    │
│   Queue     │
└──────┬──────┘
       │ Dispatch
       ▼
┌──────────────────────────────────────┐
│         Training Workers             │
├─────────────┬─────────────┬──────────┤
│  Worker 1   │  Worker 2   │ Worker 3 │
│  (GPU 0)    │  (GPU 1)    │  (GPU 2) │
└─────────────┴─────────────┴──────────┘
```

### Monitoring

**Recommended Tools**:
- **Prometheus** + **Grafana** for metrics
- **Sentry** for error tracking
- **ELK Stack** for log aggregation
- **W&B** (Weights & Biases) for training metrics

**Key Metrics**:
- Request rate and latency
- Training job queue length
- GPU utilization
- Memory usage
- Error rates
- Dataset generation throughput

---

## Future Architecture

### v0.2.0 - Enhanced Reliability

**Goals**:
- Persistent job tracking (Redis)
- Database for projects (PostgreSQL)
- WebSocket for real-time updates
- Better error handling and retry logic

### v0.3.0 - Multi-User Support

**Goals**:
- User authentication (OAuth 2.0)
- Project isolation per user
- Team collaboration features
- Role-based permissions

### v0.4.0 - Distributed Training

**Goals**:
- Celery task queue for async jobs
- Multi-GPU training support
- Distributed training (across machines)
- S3-compatible object storage

### v1.0.0 - Production Ready

**Goals**:
- Full test coverage (>80%)
- Comprehensive monitoring
- Auto-scaling support
- Security audit and hardening
- Performance benchmarks
- Documentation completeness

---

## Appendix

### Directory Structure

```
model-train/
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── api/                       # API route handlers
│   │   ├── __init__.py
│   │   ├── projects.py
│   │   ├── generation.py
│   │   ├── training.py
│   │   ├── models.py
│   │   └── config.py
│   ├── schemas/                   # Pydantic models
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── generation.py
│   │   ├── training.py
│   │   ├── models.py
│   │   └── config.py
│   └── services/                  # Business logic
│       ├── __init__.py
│       ├── project_service.py
│       ├── generation_service.py
│       ├── training_service.py
│       ├── model_service.py
│       └── config_service.py
│
├── core/                          # Core ML functionality
│   ├── __init__.py
│   ├── xml_engine.py              # XML validation
│   ├── synthesis.py               # Data generation
│   ├── training.py                # Unsloth training
│   └── size_analyzer.py           # Model size analysis
│
├── cli/                           # Command-line interfaces
│   ├── __init__.py
│   ├── main.py                    # Click CLI
│   └── tui.py                     # Textual TUI
│
├── frontend/                      # React web UI
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── projects/                      # User projects (gitignored)
├── datasets/                      # Generated datasets (gitignored)
├── models/                        # Downloaded/trained models (gitignored)
│
├── .env.example                   # Environment template
├── .gitignore
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
├── pyproject.toml                 # Modern Python config
│
└── docs/                          # Documentation
    ├── README.md
    ├── USER_GUIDE.md
    ├── API_DOCUMENTATION.md
    ├── ARCHITECTURE.md (this file)
    ├── EXAMPLES.md
    ├── FAQ.md
    └── CHANGELOG.md
```

### Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `backend/main.py` | FastAPI app setup | ~100 |
| `backend/api/projects.py` | Project CRUD API | ~80 |
| `backend/services/project_service.py` | Project business logic | ~150 |
| `core/synthesis.py` | AI data generation | ~750 |
| `core/training.py` | Unsloth training pipeline | ~950 |
| `core/xml_engine.py` | XML validation | ~300 |
| `cli/main.py` | Click CLI | ~990 |
| `cli/tui.py` | Textual TUI | ~1325 |

---

**Last Updated**: 2023-11-13
**Version**: 0.1.0
**Author**: Model Train Team
