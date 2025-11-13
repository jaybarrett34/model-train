# Model Training TUI Guide

## Overview

The Model Training TUI (Text User Interface) is a comprehensive interactive interface for managing ML model fine-tuning projects, built with [Textual](https://textual.textualize.io/).

## Features

### 🏠 Navigation
- **Screen-based interface** with dedicated views for each workflow
- **Keyboard shortcuts** for fast navigation
- **Mouse support** for clicking buttons and selecting items
- **Footer menu** showing available actions

### 📋 Main Screens

#### 1. Home Screen
- Overview and quick actions
- Navigation hub to all features
- **Shortcuts**: P (Projects), X (XML Editor), G (Generate), T (Training), E (Export), Q (Quit)

#### 2. Project Management
- **List all projects** in a sortable table
- **Create new projects** with interactive forms
- **Load existing projects** for editing
- **Delete projects** with confirmation dialogs
- **View project details** including configurations and datasets
- **Shortcuts**: N (New), L (Load), D (Delete), R (Refresh), ESC (Back)

#### 3. XML Pattern Editor
- **Interactive tag editor** for defining XML patterns
- **Add/remove tags** with constraint configuration
- **Pattern preview** showing expected structure
- **Constraint types**: Free-form, Regex, List, Range
- **Live template generation** for validation
- **Shortcuts**: A (Add Tag), R (Remove), P (Preview), S (Save), ESC (Back)

#### 4. Data Generation Screen
- **Configure generation parameters**:
  - Number of examples
  - Temperature (0.0-2.0)
  - Batch size
- **Real-time progress tracking** with progress bars
- **Generation log viewer** with auto-scroll
- **Preview generated examples**
- **Shortcuts**: G (Generate), ESC (Back)

#### 5. Training Screen
- **Start training jobs** with custom parameters
- **Real-time monitoring**:
  - Training status (pending/running/completed/failed)
  - Progress bars for epochs and steps
  - Current loss and learning rate
  - Visual progress indicators
- **Auto-refresh** every 5 seconds during training
- **Training log viewer** with live updates
- **Job management**: Start, check status, cancel
- **Shortcuts**: T (Train), S (Status), C (Cancel), ESC (Back)

#### 6. Export Screen
- **Export trained models** in multiple formats:
  - GGUF (llama.cpp compatible)
  - PyTorch
  - HuggingFace
- **Quantization options**:
  - 4-bit, 8-bit, 16-bit, or none
- **Export log** for tracking progress
- **Shortcuts**: ESC (Back)

### 🎨 UI Components

#### Interactive Widgets
- **DataTable**: Sortable tables with cursor navigation
- **Input fields**: Text entry with validation
- **TextArea**: Multi-line text editing
- **Select dropdowns**: Choice selection
- **Progress bars**: Visual progress with ETA
- **Log viewers**: Auto-scrolling log output
- **Buttons**: Clickable actions with variants (success/error/primary)
- **Modal dialogs**: Confirmations and messages

#### Visual Features
- **Color-coded status indicators**:
  - 🟢 Green: Success/Completed
  - 🔵 Blue: Running/Active
  - 🟡 Yellow: Warning/Pending
  - 🔴 Red: Error/Failed
- **Syntax highlighting** for XML patterns
- **Rich formatting** with bold, italic, and colors
- **Responsive layout** adapting to terminal size

## Installation

### Prerequisites
```bash
pip install textual rich click requests
```

### From requirements.txt
```bash
pip install -r requirements.txt
```

## Usage

### Quick Launch
```bash
# Using launcher script
./tui.sh

# Using CLI command
python -m cli.main tui

# With custom API URL
python -m cli.main tui --api-url http://localhost:9000
```

### Backend Requirement
The TUI requires the backend API to be running:
```bash
# Start backend (in another terminal)
python -m backend.main
# or
uvicorn backend.main:app --reload
```

## Keyboard Navigation

### Global Shortcuts
- **Q**: Quit application (from any screen)
- **H**: Return to home screen
- **ESC**: Go back to previous screen
- **Tab**: Navigate between inputs
- **Enter**: Activate buttons/submit forms
- **Arrow keys**: Navigate tables and selections

### Screen-Specific Shortcuts
| Screen | Key | Action |
|--------|-----|--------|
| Home | P | Go to Projects |
| Home | X | Go to XML Editor |
| Home | G | Go to Generation |
| Home | T | Go to Training |
| Home | E | Go to Export |
| Projects | N | New Project |
| Projects | L | Load Project |
| Projects | D | Delete Project |
| Projects | R | Refresh List |
| XML Editor | A | Add Tag |
| XML Editor | R | Remove Tag |
| XML Editor | P | Preview Pattern |
| XML Editor | S | Save Changes |
| Generation | G | Start Generation |
| Training | T | Start Training |
| Training | S | Check Status |
| Training | C | Cancel Job |

### Mouse Support
- **Click buttons** to activate actions
- **Click table rows** to select items
- **Scroll** log viewers and lists
- **Click inputs** to focus and edit

## Workflow Examples

### Creating a Project
1. Launch TUI: `./tui.sh`
2. Press **P** to go to Projects
3. Press **N** for New Project
4. Fill in project details:
   - Name: `my-xml-project`
   - Objective: `Train model to generate structured XML`
   - Base Model: `unsloth/llama-2-7b-bnb-4bit`
   - Dataset Format: `sharegpt`
   - AI Provider: `ollama`
5. Click **Create** or press **Ctrl+S**
6. Project created! ✅

### Defining XML Patterns
1. From Projects screen, select a project
2. Press **L** to load it
3. In XML Editor, press **A** to add a tag
4. Configure tag:
   - Tag Name: `thinking`
   - Description: `Internal reasoning process`
   - Constraint Type: `free_form`
   - Required: `Yes`
5. Click **Save** or press **Ctrl+S**
6. Press **P** to preview the pattern
7. Press **S** to save to project

### Generating Training Data
1. Press **G** from home or navigate to Generation screen
2. Enter project name: `my-xml-project`
3. Set parameters:
   - Number of examples: `100`
   - Temperature: `0.7`
   - Batch size: `10`
4. Click **Generate Dataset**
5. Watch progress bar and log output
6. Dataset generated! 🎉

### Training a Model
1. Press **T** from home or navigate to Training screen
2. Enter details:
   - Project name: `my-xml-project`
   - Dataset filename: (from previous generation)
3. Click **Start Training**
4. Monitor real-time progress:
   - Current epoch/step
   - Training loss
   - Progress bar
   - Live logs
5. Auto-refresh updates every 5 seconds
6. Training completes! 🚀

### Exporting a Model
1. Press **E** from home or navigate to Export screen
2. Enter model directory: `models/my-xml-project`
3. Select export format: `GGUF`
4. Select quantization: `4-bit`
5. Click **Export Model**
6. Model exported and ready to use! 📦

## API Integration

The TUI connects to the backend API using the `APIClient` class:

```python
# Default API URL
API_BASE_URL = "http://localhost:8000"

# Override with environment variable
export API_URL="http://localhost:9000"
```

### API Endpoints Used
- **Projects**: `/projects` (GET, POST, PUT, DELETE)
- **Generation**: `/generate` (POST)
- **Training**: `/train` (POST), `/train/status/{job_id}` (GET), `/train/cancel/{job_id}` (DELETE)

### Error Handling
- Connection errors show user-friendly messages
- API errors display detailed error information
- Timeout handling with configurable limits
- Graceful degradation when backend is unavailable

## Customization

### Styling
The TUI uses Textual CSS for styling. Customize in `cli/tui.py`:

```python
CSS = """
Screen {
    background: $surface;
}

Button {
    margin: 0 1;
}

# ... more styles
"""
```

### Colors
- Uses Textual's theme system
- Supports custom color schemes
- Rich markup for text formatting

### Layout
- Responsive containers
- Flexbox-style layout
- Scrollable regions for long content

## Troubleshooting

### TUI won't start
```bash
# Check dependencies
pip list | grep textual

# Reinstall if needed
pip install --upgrade textual rich click
```

### Can't connect to API
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/projects

# Check API URL
echo $API_URL

# Start backend if not running
python -m backend.main
```

### Display issues
```bash
# Try different terminal emulator
# Recommended: iTerm2, Alacritty, Windows Terminal

# Check terminal size
tput cols
tput lines

# Resize terminal if too small (min 80x24)
```

### Keyboard shortcuts not working
- Some terminals capture certain key combinations
- Try mouse navigation instead
- Check terminal settings for key binding conflicts

## Advanced Features

### Vim-Style Navigation
While not fully implemented, you can extend the TUI with vim-style keybindings:
- `j`/`k` for up/down navigation
- `gg`/`G` for top/bottom
- `:q` to quit
- `/` for search

### Real-Time Updates
Training screen auto-refreshes with:
```python
self.set_interval(5.0, self.action_status)
```

Adjust refresh rate as needed.

### Progress Tracking
- Epoch progress bars
- Step progress bars
- ETA calculations
- Loss sparklines (coming soon)

### Log Management
- Auto-scrolling log viewers
- Colored log levels
- Searchable logs
- Export log to file

## Future Enhancements

- [ ] Dataset preview with examples
- [ ] Training metrics visualization (sparklines/charts)
- [ ] Model comparison view
- [ ] Configuration presets
- [ ] Batch operations
- [ ] Search and filter
- [ ] Dark/light theme toggle
- [ ] Vim-style keybindings
- [ ] Plugin system
- [ ] Remote API support with auth
- [ ] Export configurations
- [ ] Import project templates

## Contributing

To add new screens or features:

1. Create a new Screen class
2. Implement `compose()` for layout
3. Add action methods for interactions
4. Register in `SCREENS` dict in `ModelTrainTUI`
5. Add navigation bindings

Example:
```python
class MyNewScreen(Screen):
    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("My New Feature"),
            Button("Action", id="my_button"),
        )
        yield Footer()

    @on(Button.Pressed, "#my_button")
    def handle_action(self) -> None:
        # Your logic here
        pass

    def action_back(self) -> None:
        self.app.pop_screen()
```

## Resources

- [Textual Documentation](https://textual.textualize.io/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Project README](README.md)

## Support

For issues or questions:
1. Check this guide
2. Review API documentation
3. Check backend logs
4. Open an issue on GitHub

---

**Happy Training!** 🚀🤖
