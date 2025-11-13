# Frontend Component Reference

Complete documentation for all React components in the Model Training frontend.

## Table of Contents

- [Layout Components](#layout-components)
- [Page Components](#page-components)
- [Shared Components](#shared-components)
- [State Management](#state-management)
- [API Services](#api-services)

---

## Layout Components

### Layout.jsx

**Purpose**: Main application layout with sidebar navigation

**Props**:
- `children` - Page content to render

**Features**:
- Fixed sidebar with navigation links
- Active route highlighting
- Responsive layout structure
- Brand header

**Navigation Items**:
1. Projects (/)
2. XML Editor (/xml-editor)
3. Generator (/generator)
4. Datasets (/datasets)
5. Size Analyzer (/size-analyzer)
6. Training (/training)
7. Export (/export)

---

## Page Components

### 1. ProjectList.jsx

**Route**: `/`

**Purpose**: Project management dashboard

**Features**:
- View all projects in grid layout
- Create new projects with modal form
- Delete projects with confirmation
- Display project statistics (datasets, samples, models)
- Loading and empty states

**State**:
- Projects list (from Zustand store)
- Create modal visibility
- New project form data

**API Calls**:
- `projectsApi.list()` - Fetch all projects
- `projectsApi.create()` - Create new project
- `projectsApi.delete()` - Delete project

---

### 2. XMLEditor.jsx

**Route**: `/xml-editor`

**Purpose**: Drag-and-drop XML pattern builder (Scratch-like interface)

**Features**:
- **Tag Palette** (left sidebar): Draggable tag templates
- **Canvas** (center): Drop zone for building patterns
- **Preview Panel** (right sidebar, toggleable): Live XML preview
- Drag tags from palette to canvas
- Reorder tags via drag-and-drop
- Configure tag constraints via modal
- Export XML pattern to file
- Save pattern to project

**Components Used**:
- `TagPalette` - Sidebar with draggable tag templates
- `TagBlock` - Individual draggable tag component
- `ConstraintEditor` - Configuration modal

**Libraries**:
- `@hello-pangea/dnd` - Drag-and-drop functionality

**State**:
- Tags array (local state)
- Selected tag for editing
- Constraint editor modal visibility
- Preview panel visibility

**API Calls**:
- `patternsApi.get()` - Load existing pattern
- `patternsApi.save()` - Save pattern to project

---

### 3. DataGenerator.jsx

**Route**: `/generator`

**Purpose**: Configure and generate synthetic training data using AI

**Features**:
- **Objective Input**: Describe the task/use case
- **AI Provider Config**:
  - Provider selection (Ollama, OpenAI, Anthropic, Custom)
  - Model selection
  - API key input (for non-local providers)
  - API URL configuration
- **Generation Settings**:
  - Number of samples
  - Temperature
  - Generation mode (pseudorandom, patterned, forced)
- **Progress Monitoring**:
  - Real-time progress bar
  - Sample count
  - Live sample preview
- Start/stop generation controls

**State**:
- Generation configuration
- Job ID for tracking
- Generated samples
- Generation status (from Zustand store)

**API Calls**:
- `generationApi.generate()` - Start generation job
- `generationApi.getStatus()` - Poll for status updates
- `generationApi.cancel()` - Cancel running job

---

### 4. DatasetManager.jsx

**Route**: `/datasets`

**Purpose**: View, validate, and export generated datasets

**Features**:
- Grid view of all datasets
- Dataset cards showing:
  - Name and creation date
  - Sample count and size
  - Validation status
  - Metadata (mode, model)
- **Actions**:
  - Preview samples (opens modal)
  - Validate against pattern
  - Export (JSONL, CSV, Parquet)
  - Delete dataset
- **Validation Modal**: Shows validation results, errors, and statistics
- **Preview Modal**: Uses DatasetViewer component

**Components Used**:
- `DatasetViewer` - Interactive sample viewer

**State**:
- Datasets list (from Zustand store)
- Selected dataset
- Validation results
- Preview data

**API Calls**:
- `datasetsApi.list()` - Fetch all datasets
- `datasetsApi.get()` - Get dataset samples
- `datasetsApi.validate()` - Validate dataset
- `datasetsApi.export()` - Export dataset
- `datasetsApi.delete()` - Delete dataset

---

### 5. SizeAnalyzer.jsx (NEW)

**Route**: `/size-analyzer`

**Purpose**: Calculate optimal dataset size requirements

**Features**:
- **Configuration Panel**:
  - Target model selection (Llama-2-7B, Mistral, etc.)
  - Task complexity (simple, medium, complex, expert)
  - Desired accuracy slider (70% - 95%)
  - Available VRAM selection
- **Results Panel**:
  - Three size recommendations (minimum, recommended, optimal)
  - Comparison bar chart
  - Training time estimates
  - Cost estimates
  - Quality metrics (confidence level, overfitting risk)
  - Calculation breakdown
- **Visualization**:
  - Bar charts (samples vs cost)
  - Progress bars for quality metrics
  - Color-coded risk indicators

**Libraries**:
- `recharts` - Bar charts and data visualization

**State**:
- Configuration settings
- Analysis results
- Calculation status

**API Calls**:
- `api.post('/analyze/dataset-size')` - Get size recommendations (falls back to client-side calculation)

**Algorithms**:
- Base requirement from model specs
- Complexity multiplier (1x - 8x)
- Accuracy multiplier (0.5x - 1.5x)
- Training throughput estimation
- Cost calculation

---

### 6. TrainingDashboard.jsx

**Route**: `/training`

**Purpose**: Configure and monitor QLoRA fine-tuning

**Features**:
- **Dataset Selection**: Choose from available datasets
- **Base Model Selection**:
  - Search HuggingFace models
  - Select from search results
  - Custom model input
  - Output name configuration
- **Training Parameters**:
  - Epochs
  - Batch size
  - Learning rate
  - Max sequence length
- **QLoRA Parameters**:
  - LoRA rank (r)
  - LoRA alpha
  - LoRA dropout
  - Target modules (comma-separated)
- **Monitoring**:
  - Real-time progress bar
  - Current loss value
  - Loss graph (line chart)
  - Training logs console
- Start/stop training controls

**Libraries**:
- `recharts` - Line chart for loss visualization

**State**:
- Training configuration
- Job ID for tracking
- Training status (from Zustand store)
- Logs array
- HuggingFace search results

**API Calls**:
- `trainingApi.start()` - Start training job
- `trainingApi.getStatus()` - Poll for status updates
- `trainingApi.getLogs()` - Fetch training logs
- `trainingApi.stop()` - Stop training job
- `huggingfaceApi.searchModels()` - Search HuggingFace models

---

### 7. ModelExporter.jsx

**Route**: `/export`

**Purpose**: Export trained models in various formats

**Features**:
- **Model Selection Panel** (left):
  - List of trained models
  - Model info (name, base model, date, size)
  - Delete model action
- **Export Configuration** (right):
  - Model information display
  - Training configuration metadata
  - **Format Selection** (4 options):
    - HuggingFace (standard format)
    - GGUF (llama.cpp)
    - ONNX (cross-platform)
    - SafeTensors
  - **Export Options**:
    - Merge LoRA adapters checkbox
    - Include tokenizer checkbox
    - Include config files checkbox
    - Quantization dropdown (none, INT8, INT4, NF4, FP16)
- Export button with format/options summary

**State**:
- Models list (from Zustand store)
- Selected model
- Export format
- Export options
- Export status

**API Calls**:
- `modelsApi.list()` - Fetch all models
- `modelsApi.export()` - Export model
- `modelsApi.delete()` - Delete model

---

## Shared Components

### TagPalette.jsx

**Purpose**: Sidebar with draggable tag templates for XML editor

**Props**:
- `onDragStart` - Callback when drag starts

**Features**:
- Predefined tag templates:
  - text (blue)
  - number (green)
  - date (purple)
  - url (orange)
  - list (pink)
  - custom (gray)
- Each template has icon, description, default constraints
- Drag to canvas to create new tags
- Tips section with usage instructions

**Tag Templates**:
```javascript
{
  name: 'text',
  icon: Type,
  description: 'Text content',
  color: 'bg-blue-100 border-blue-300',
  defaultConstraints: { type: 'string' }
}
```

---

### TagBlock.jsx

**Purpose**: Individual draggable tag component

**Props**:
- `tag` - Tag object with id, name, constraints, attributes, children
- `index` - Position in list
- `onEdit` - Callback to open constraint editor
- `onDelete` - Callback to delete tag
- `onToggleExpanded` - Callback to expand/collapse children
- `level` - Nesting level (for indentation)

**Features**:
- Draggable via @hello-pangea/dnd
- Shows tag name, constraints count, attributes count
- Hover menu with actions:
  - Settings (configure constraints)
  - Edit
  - Delete
- Expand/collapse for nested tags
- Visual nesting with indentation

**Libraries**:
- `@hello-pangea/dnd` - Draggable component
- `clsx` - Conditional classes

---

### ConstraintEditor.jsx

**Purpose**: Modal for configuring tag constraints and attributes

**Props**:
- `tag` - Tag to edit
- `onSave` - Callback with updated tag
- `onClose` - Callback to close modal

**Features**:
- **3 Tabs**:
  1. **Basic**: Tag name and description
  2. **Constraints**: Add/remove/configure constraints
  3. **Attributes**: Add/remove XML attributes

- **Constraint Types**:
  - **Regex**: Regular expression pattern
  - **List**: List of allowed values (one per line)
  - **Range**: Numeric min/max
  - **Length**: String length min/max
  - **Format**: Predefined formats (email, URL, UUID, IPv4, date, time)

- **Validation**:
  - Real-time constraint validation
  - Error messages for invalid patterns
  - Prevents saving with errors

**State**:
- Edited tag (local copy)
- Active tab
- Validation errors

---

### DatasetViewer.jsx

**Purpose**: Interactive modal for viewing dataset samples

**Props**:
- `dataset` - Dataset object with name and metadata
- `samples` - Array of sample objects
- `onClose` - Callback to close viewer

**Features**:
- **Pagination**: 10 samples per page
- **Sample Display**:
  - Supports input/output format
  - Supports raw JSON format
  - Syntax highlighting for JSON
  - Copy to clipboard button per sample
  - Quality score bar (if available)
  - Token count (if available)
- **Navigation**:
  - Previous/Next page buttons
  - Page indicator
  - Total sample count

**Sample Formats**:
```javascript
// Input/Output format
{
  input: "question or prompt",
  output: "answer or completion",
  quality_score: 0.95,
  tokens: 123
}

// Raw format
{
  // any structure
}
```

---

## State Management

### useStore.js (Zustand)

**Global State**:

```javascript
{
  // Current project
  currentProject: null,
  setCurrentProject: (project) => {},

  // XML Pattern
  xmlPattern: {
    tags: [],
    rootTag: null
  },
  setXmlPattern: (pattern) => {},
  addTag: (tag) => {},
  updateTag: (tagId, updates) => {},
  removeTag: (tagId) => {},

  // Training Status
  trainingStatus: {
    isTraining: false,
    progress: 0,
    currentStep: 0,
    totalSteps: 0,
    loss: [],
    logs: []
  },
  setTrainingStatus: (status) => {},
  updateTrainingProgress: (progress) => {},

  // Generation Status
  generationStatus: {
    isGenerating: false,
    progress: 0,
    currentSample: 0,
    totalSamples: 0,
    generatedData: []
  },
  setGenerationStatus: (status) => {},
  updateGenerationProgress: (progress) => {},

  // Projects
  projects: [],
  setProjects: (projects) => {},
  addProject: (project) => {},
  deleteProject: (projectId) => {},

  // Datasets
  datasets: [],
  setDatasets: (datasets) => {},
  addDataset: (dataset) => {},

  // Models
  models: [],
  setModels: (models) => {},
  addModel: (model) => {}
}
```

---

## API Services

### api.js

**Base Configuration**:
```javascript
baseURL: VITE_API_URL || 'http://localhost:8000/api'
headers: { 'Content-Type': 'application/json' }
```

**API Endpoints**:

#### Projects API
- `list()` - GET /projects
- `create(data)` - POST /projects
- `get(id)` - GET /projects/:id
- `update(id, data)` - PUT /projects/:id
- `delete(id)` - DELETE /projects/:id

#### Patterns API
- `save(projectId, pattern)` - POST /projects/:projectId/pattern
- `get(projectId)` - GET /projects/:projectId/pattern
- `validate(pattern)` - POST /patterns/validate

#### Generation API
- `generate(projectId, config)` - POST /projects/:projectId/generate
- `getStatus(projectId, jobId)` - GET /projects/:projectId/generation/:jobId
- `cancel(projectId, jobId)` - POST /projects/:projectId/generation/:jobId/cancel

#### Datasets API
- `list(projectId)` - GET /projects/:projectId/datasets
- `get(projectId, datasetId)` - GET /projects/:projectId/datasets/:datasetId
- `validate(projectId, datasetId)` - POST /projects/:projectId/datasets/:datasetId/validate
- `export(projectId, datasetId, format)` - GET /projects/:projectId/datasets/:datasetId/export
- `delete(projectId, datasetId)` - DELETE /projects/:projectId/datasets/:datasetId

#### Training API
- `start(projectId, config)` - POST /projects/:projectId/train
- `getStatus(projectId, jobId)` - GET /projects/:projectId/training/:jobId
- `stop(projectId, jobId)` - POST /projects/:projectId/training/:jobId/stop
- `getLogs(projectId, jobId)` - GET /projects/:projectId/training/:jobId/logs

#### Models API
- `list(projectId)` - GET /projects/:projectId/models
- `get(projectId, modelId)` - GET /projects/:projectId/models/:modelId
- `export(projectId, modelId, format)` - POST /projects/:projectId/models/:modelId/export
- `delete(projectId, modelId)` - DELETE /projects/:projectId/models/:modelId

#### HuggingFace API
- `searchModels(query)` - GET /huggingface/models?query=:query

---

## Utility Functions

### helpers.js

**Functions**:

- `generateId()` - Generate unique ID with timestamp + random string
- `formatBytes(bytes, decimals)` - Convert bytes to human-readable (KB, MB, GB)
- `formatDate(date)` - Convert to locale string
- `isValidTagName(name)` - Validate XML tag name (regex)
- `patternToXml(tags, rootTagId)` - Convert tag tree to XML string
- `cloneDeep(obj)` - Deep clone object via JSON
- `debounce(func, wait)` - Debounce function calls
- `getConstraintTypeName(type)` - Get display name for constraint type
- `validateConstraint(type, value)` - Validate constraint value

**Constraint Validation**:
- Regex: Test pattern compilation
- Range: Check min < max
- List: Ensure array with values
- Returns `{ valid: boolean, error?: string }`

---

## Styling System

### TailwindCSS Custom Classes

Defined in `src/index.css`:

**Buttons**:
- `.btn-primary` - Primary action button (blue)
- `.btn-secondary` - Secondary action button (gray)
- `.btn-danger` - Destructive action button (red)

**Forms**:
- `.input-field` - Text input and textarea

**Containers**:
- `.card` - White card with shadow and padding

**XML Editor**:
- `.tag-block` - Tag component styling
- `.tag-block-dragging` - Dragging state opacity
- `.drop-zone` - Dashed border drop area
- `.drop-zone-active` - Active drop zone highlight

**Color Palette**:
```javascript
primary: {
  50: '#f0f9ff',
  100: '#e0f2fe',
  // ... up to 900
  600: '#0284c7', // Main brand color
}
```

---

## Routing Structure

```
/ → ProjectList
/xml-editor → XMLEditor
/generator → DataGenerator
/datasets → DatasetManager
/size-analyzer → SizeAnalyzer
/training → TrainingDashboard
/export → ModelExporter
```

All routes are wrapped in `<Layout>` component for consistent navigation.

---

## Key Features Summary

### Drag-and-Drop System
- **Library**: @hello-pangea/dnd (primary), @dnd-kit (available)
- **Components**: TagPalette → Canvas (XMLEditor)
- **Features**: Copy from palette, reorder on canvas, visual feedback

### Real-time Updates
- **Generation**: Poll every 2 seconds
- **Training**: Poll every 3 seconds
- **Progress**: Zustand store updates trigger re-renders

### Modals
- Create Project (ProjectList)
- Constraint Editor (XMLEditor)
- Validation Results (DatasetManager)
- Dataset Preview (DatasetManager)

### Data Visualization
- **Library**: Recharts
- **Charts**:
  - Line chart (training loss)
  - Bar chart (dataset size comparison)
  - Pie chart potential (not yet used)

### Responsive Design
- Grid layouts (1 col → 2 col → 3 col)
- Mobile-friendly navigation
- Scrollable content areas

---

## Development Tips

### Adding a New Page

1. Create component in `src/pages/`
2. Import in `App.jsx`
3. Add route in `<Routes>`
4. Add nav item in `Layout.jsx`
5. Add API methods in `services/api.js` if needed
6. Add state in `useStore.js` if needed

### Adding a New API Endpoint

```javascript
// In src/services/api.js
export const myApi = {
  action: (params) => api.method('/endpoint', params),
};
```

### Debugging State

```javascript
// In any component
import useStore from '../store/useStore';

const MyComponent = () => {
  const store = useStore();
  console.log(store); // View entire state
};
```

### Testing Drag-and-Drop

1. Open XML Editor
2. Check console for drag events
3. Use React DevTools to inspect DragDropContext
4. Verify `onDragEnd` callback updates state

---

## Performance Considerations

### Polling Optimization
- Clear intervals on unmount
- Only poll when job is active
- Use conditional rendering to prevent unnecessary API calls

### State Updates
- Zustand is lightweight and fast
- Updates only trigger re-renders in subscribed components
- Use selectors for partial state access

### Large Datasets
- Pagination in DatasetViewer (10 samples/page)
- Limit preview samples in modals
- Virtualization potential for very large lists

---

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ features required
- No IE11 support

---

## Accessibility

- Semantic HTML elements
- Button labels and titles
- Keyboard navigation (partial)
- Screen reader considerations (basic)

**Improvements Needed**:
- ARIA labels
- Focus management
- Keyboard shortcuts
- Better contrast ratios

---

This documentation covers all components and their interactions in the Model Training frontend application.
