# Model Training Frontend

A modern React web UI for building XML patterns, generating synthetic training data, and fine-tuning language models with QLoRA.

## Features

### 1. Project Management
- Create and manage multiple training projects
- Track datasets, samples, and trained models per project
- Project metadata and statistics

### 2. XML Pattern Editor
- **Scratch-like drag-and-drop interface** for building XML patterns
- Visual tag palette with pre-built tag templates
- Configure constraints (regex, list, range, length, format)
- Nest tags via drag-and-drop
- Real-time XML preview
- Export patterns

### 3. Data Generation
- Generate synthetic training data using AI
- Multiple AI provider support (Ollama, OpenAI, Anthropic, Custom)
- Three generation modes:
  - **Pseudorandom**: Random variations
  - **Patterned**: Follow XML pattern with flexibility
  - **Forced**: Strict pattern adherence
- Real-time progress monitoring
- Sample preview

### 4. Dataset Management
- View and manage generated datasets
- Validate datasets against patterns
- Export in multiple formats (JSONL, CSV, Parquet)
- Dataset statistics and metadata
- Interactive dataset viewer with pagination
- Quality scoring and token counting

### 5. Dataset Size Analyzer (NEW)
- Calculate optimal dataset size for your task
- Smart recommendations based on:
  - Target model size
  - Task complexity
  - Desired accuracy
  - Available VRAM
- Training time and cost estimates
- Quality metrics and overfitting risk analysis
- Interactive configuration and visualization

### 6. Training Dashboard
- Configure QLoRA fine-tuning parameters
- Search and select HuggingFace base models
- Monitor training progress in real-time
- Live loss graph visualization
- Training logs viewer

### 7. Model Export
- Export trained models in various formats:
  - HuggingFace (standard format)
  - GGUF (for llama.cpp)
  - ONNX (cross-platform)
  - SafeTensors
- Quantization options (INT8, INT4, NF4, FP16)
- Merge LoRA adapters option

## Tech Stack

- **React 19** - UI framework
- **Vite** - Fast development build tool
- **TailwindCSS** - Utility-first CSS framework
- **@dnd-kit/core**, **@dnd-kit/sortable** - Modern drag-and-drop toolkit
- **@hello-pangea/dnd** - Alternative drag-and-drop library (maintained fork of react-beautiful-dnd)
- **React Router** - Client-side routing
- **Zustand** - Lightweight state management
- **Axios** - HTTP client for API communication
- **Recharts** - Data visualization and charts
- **Lucide React** - Beautiful icon library
- **clsx** - Utility for constructing className strings

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see main project README)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your API URL:
```
VITE_API_URL=http://localhost:8000/api
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/               # Reusable UI components
│   │   ├── Layout.jsx            # Main layout with sidebar navigation
│   │   ├── TagBlock.jsx          # Draggable tag component for XML editor
│   │   ├── TagPalette.jsx        # Tag palette sidebar with templates
│   │   ├── ConstraintEditor.jsx  # Tag configuration modal with tabs
│   │   └── DatasetViewer.jsx     # Interactive dataset sample viewer
│   ├── pages/                    # Page components (routes)
│   │   ├── ProjectList.jsx       # Project CRUD and management
│   │   ├── XMLEditor.jsx         # Drag-and-drop XML pattern builder
│   │   ├── DataGenerator.jsx     # AI-powered data generation interface
│   │   ├── DatasetManager.jsx    # Dataset validation and export
│   │   ├── SizeAnalyzer.jsx      # Dataset size calculator (NEW)
│   │   ├── TrainingDashboard.jsx # QLoRA training config & monitoring
│   │   └── ModelExporter.jsx     # Model export with quantization
│   ├── services/                 # API services
│   │   └── api.js                # Axios client with all API endpoints
│   ├── store/                    # State management
│   │   └── useStore.js           # Zustand global store
│   ├── utils/                    # Utility functions
│   │   └── helpers.js            # Date, validation, XML helpers
│   ├── App.jsx                   # Main app with routing
│   ├── main.jsx                  # App entry point
│   └── index.css                 # TailwindCSS + custom styles
├── public/                       # Static assets
├── .env.example                  # Environment variables template
├── package.json                  # Dependencies and scripts
├── vite.config.js                # Vite configuration
├── tailwind.config.js            # TailwindCSS theme customization
├── postcss.config.js             # PostCSS configuration
├── eslint.config.js              # ESLint configuration
└── README.md                     # This file
```

## Usage

### Creating a Project

1. Navigate to the Projects page
2. Click "New Project"
3. Enter project name and description
4. Click "Create"

### Building XML Patterns

1. Select a project
2. Navigate to "XML Editor"
3. Drag tags from the left palette to the canvas
4. Click the gear icon on a tag to configure constraints
5. Arrange tags by dragging
6. Use the preview panel to see the XML structure
7. Save the pattern

### Generating Data

1. Navigate to "Generator"
2. Enter your objective/task description
3. Configure AI provider settings
4. Select generation mode
5. Set number of samples
6. Click "Start Generation"
7. Monitor progress and preview samples

### Training Models

1. Navigate to "Training"
2. Select a dataset
3. Search and select a base model from HuggingFace
4. Configure QLoRA parameters
5. Click "Start Training"
6. Monitor progress and loss graph

### Analyzing Dataset Size Requirements

1. Navigate to "Size Analyzer"
2. Select your target model
3. Set task complexity level
4. Adjust desired accuracy
5. Configure available VRAM
6. View recommendations for minimum, recommended, and optimal dataset sizes
7. Review training time and cost estimates

### Exporting Models

1. Navigate to "Export"
2. Select a trained model
3. Choose export format (HuggingFace, GGUF, ONNX, SafeTensors)
4. Configure export options (quantization, merge adapters, etc.)
5. Click "Export Model"

## API Integration

The frontend communicates with the backend API using Axios. All API endpoints are defined in `src/services/api.js`:

- **Projects API**: CRUD operations for projects
- **Patterns API**: Save and retrieve XML patterns
- **Generation API**: Start and monitor data generation
- **Datasets API**: Manage and export datasets
- **Training API**: Configure and monitor training
- **Models API**: Manage and export models
- **HuggingFace API**: Search for base models

## State Management

Global state is managed using Zustand (`src/store/useStore.js`):

- Current project
- XML pattern state
- Training status and progress
- Generation status and progress
- Projects, datasets, and models lists

## Styling

TailwindCSS is used for styling with custom utility classes defined in `src/index.css`:

- `.btn-primary`, `.btn-secondary`, `.btn-danger` - Button styles
- `.input-field` - Input and textarea styles
- `.card` - Card container style
- `.tag-block` - Tag component style
- `.drop-zone` - Drag-and-drop zone style
