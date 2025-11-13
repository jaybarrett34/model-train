# Frontend Project Structure

## Complete File Tree

```
frontend/
├── public/                          # Static assets
│   └── vite.svg                     # Vite logo
├── src/
│   ├── components/                  # Reusable UI components
│   │   ├── ConstraintEditor.jsx     # Modal for editing tag constraints
│   │   ├── Layout.jsx               # Main app layout with sidebar navigation
│   │   ├── TagBlock.jsx             # Individual draggable tag component
│   │   └── TagPalette.jsx           # Left sidebar with draggable tag templates
│   │
│   ├── pages/                       # Page-level components (routes)
│   │   ├── DataGenerator.jsx        # Data generation configuration and monitoring
│   │   ├── DatasetManager.jsx       # Dataset viewing, validation, and export
│   │   ├── ModelExporter.jsx        # Model export interface with format selection
│   │   ├── ProjectList.jsx          # Project management and selection
│   │   ├── TrainingDashboard.jsx    # Training configuration and progress monitoring
│   │   └── XMLEditor.jsx            # Main XML pattern editor with drag-and-drop
│   │
│   ├── services/                    # API and external services
│   │   └── api.js                   # Axios API client with all endpoints
│   │
│   ├── store/                       # State management
│   │   └── useStore.js              # Zustand store for global state
│   │
│   ├── utils/                       # Utility functions
│   │   └── helpers.js               # Helper functions for common operations
│   │
│   ├── App.jsx                      # Main app component with routing
│   ├── index.css                    # Global styles and Tailwind directives
│   └── main.jsx                     # App entry point
│
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── eslint.config.js                 # ESLint configuration
├── index.html                       # HTML entry point
├── package.json                     # NPM dependencies and scripts
├── postcss.config.js                # PostCSS configuration for Tailwind
├── README.md                        # Project documentation
├── tailwind.config.js               # Tailwind CSS configuration
└── vite.config.js                   # Vite build configuration
```

## Component Descriptions

### Core Components

#### `Layout.jsx`
- Main application layout wrapper
- Left sidebar navigation with icons
- Navigation items for all main features
- Responsive design
- Active route highlighting

#### `App.jsx`
- React Router setup
- Route definitions for all pages
- Layout wrapper integration

### XML Editor Components

#### `XMLEditor.jsx`
- Main XML pattern editor page
- Drag-and-drop canvas using @hello-pangea/dnd
- Integration with TagPalette and TagBlock
- Real-time XML preview
- Pattern save/load functionality
- Export to XML file

#### `TagPalette.jsx`
- Left sidebar with draggable tag templates
- Pre-built tag types (text, number, date, url, list, custom)
- Color-coded tag categories
- Drag source for new tags
- Helper tips section

#### `TagBlock.jsx`
- Individual draggable tag component
- Shows tag name, constraints, and attributes
- Inline edit controls (settings, edit, delete)
- Supports nesting and expansion
- Visual feedback during drag

#### `ConstraintEditor.jsx`
- Modal dialog for tag configuration
- Three tabs: Basic, Constraints, Attributes
- Constraint types: regex, list, range, length, format
- Validation of constraint values
- Attribute key-value editor

### Page Components

#### `ProjectList.jsx`
- Grid view of all projects
- Create new project modal
- Project cards with statistics
- Edit and delete actions
- Empty state handling

#### `DataGenerator.jsx`
- Data generation configuration form
- AI provider selection (Ollama, OpenAI, Anthropic, Custom)
- Generation mode selection (pseudorandom, patterned, forced)
- Real-time progress monitoring
- Generated samples preview

#### `DatasetManager.jsx`
- Grid view of generated datasets
- Dataset validation
- Export to multiple formats (JSONL, CSV, Parquet)
- Sample preview modal
- Validation results display
- Dataset statistics

#### `TrainingDashboard.jsx`
- Training configuration form
- Dataset selection
- HuggingFace model search
- QLoRA parameter configuration
- Real-time training progress
- Loss graph visualization (Recharts)
- Training logs viewer

#### `ModelExporter.jsx`
- Model selection interface
- Export format selection (HuggingFace, GGUF, ONNX, SafeTensors)
- Export options (merge adapters, quantization, etc.)
- Model information display
- Download functionality

## Services

### `api.js`
API client with organized endpoint groups:

- **projectsApi**: CRUD operations for projects
- **patternsApi**: Save and load XML patterns
- **generationApi**: Data generation jobs
- **datasetsApi**: Dataset management and export
- **trainingApi**: Training job management
- **modelsApi**: Model management and export
- **huggingfaceApi**: HuggingFace model search

Base configuration:
- Axios instance with base URL
- Environment variable support via Vite
- JSON content type headers

## State Management

### `useStore.js` (Zustand)

Global state includes:

**Project State:**
- `currentProject`: Currently selected project
- `projects`: List of all projects

**XML Pattern State:**
- `xmlPattern`: Current pattern definition
- Tag management actions (add, update, remove)

**Training State:**
- `trainingStatus`: Current training job status
- Progress, steps, loss data
- Training logs

**Generation State:**
- `generationStatus`: Current generation job status
- Progress tracking
- Generated data preview

**Datasets & Models:**
- `datasets`: List of datasets
- `models`: List of trained models

## Utilities

### `helpers.js`

Utility functions:
- `generateId()`: Unique ID generation
- `formatBytes()`: Human-readable file sizes
- `formatDate()`: Date formatting
- `isValidTagName()`: XML tag name validation
- `patternToXml()`: Convert pattern to XML string
- `cloneDeep()`: Deep object cloning
- `debounce()`: Function debouncing
- `getConstraintTypeName()`: Constraint type display names
- `validateConstraint()`: Constraint value validation

## Styling

### Tailwind Configuration

Custom theme extension:
- Primary color palette (50-900 shades)
- Custom utility classes in `index.css`

### Custom CSS Classes

Defined in `index.css`:
- `.btn-primary`, `.btn-secondary`, `.btn-danger`: Button styles
- `.input-field`: Form input styles
- `.card`: Card container styles
- `.tag-block`: Tag component styles
- `.drop-zone`: Drag-and-drop zone styles

## Key Features Implementation

### Drag-and-Drop
- Library: `@hello-pangea/dnd`
- Implemented in: XMLEditor, TagPalette, TagBlock
- Features: Drag from palette, reorder in canvas, visual feedback

### Real-time Updates
- WebSocket potential for training/generation progress
- Polling implementation for status updates
- Zustand store updates trigger UI re-renders

### Form Validation
- Constraint validation in ConstraintEditor
- Required field checks
- Format validation (regex, ranges, etc.)

### Data Visualization
- Library: Recharts
- Loss graph in TrainingDashboard
- Responsive charts

### Icons
- Library: Lucide React
- Consistent icon set across application
- Size and color customization

## Development Workflow

1. **Component Development**
   - Create component in appropriate directory
   - Import required dependencies
   - Use Zustand hooks for state
   - Apply Tailwind classes for styling

2. **API Integration**
   - Add endpoint to `api.js`
   - Use async/await with try/catch
   - Update Zustand store with results
   - Handle errors gracefully

3. **Routing**
   - Add route to `App.jsx`
   - Add navigation item to `Layout.jsx`
   - Ensure proper icon and label

4. **State Management**
   - Add state to `useStore.js`
   - Create actions for state updates
   - Use hooks in components

## Build and Deploy

### Development Build
```bash
npm run dev
```
- Fast HMR (Hot Module Replacement)
- Source maps enabled
- Development warnings

### Production Build
```bash
npm run build
```
- Minification enabled
- Tree shaking
- Code splitting
- Optimized assets
- Output: `dist/` directory

### Environment Variables
- Prefix: `VITE_`
- Example: `VITE_API_URL`
- Accessed via: `import.meta.env.VITE_API_URL`

## Future Enhancements

Potential additions:
- TypeScript migration
- Unit tests (Vitest)
- E2E tests (Playwright)
- Storybook for component documentation
- Error boundary components
- Loading skeletons
- Optimistic UI updates
- Offline support with service workers
