# TUI Quick Start Guide

## Installation
```bash
# Install dependencies
pip install textual rich click requests

# Or install all requirements
pip install -r requirements.txt
```

## Launch TUI
```bash
# Quick launch
./tui.sh

# Via CLI
python -m cli.main tui

# With custom API URL
python -m cli.main tui --api-url http://localhost:9000
```

## Prerequisites
**Backend must be running:**
```bash
# Terminal 1: Start backend
python -m backend.main
# or
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Launch TUI
./tui.sh
```

## Main Navigation

### From Home Screen
| Key | Screen |
|-----|--------|
| **P** | Projects - Manage projects |
| **X** | XML Editor - Define patterns |
| **G** | Generation - Create datasets |
| **T** | Training - Train models |
| **E** | Export - Export models |
| **Q** | Quit application |

### Within Screens
| Key | Action |
|-----|--------|
| **ESC** | Go back / Cancel |
| **Tab** | Navigate between inputs |
| **Enter** | Activate button / Submit |
| **Arrow Keys** | Navigate tables/selections |
| **H** | Return to home (from anywhere) |

## Quick Workflows

### 1️⃣ Create a New Project
```
1. Press P → Projects
2. Press N → New Project
3. Fill in:
   - Name: my-project
   - Objective: Your training goal
   - Base Model: unsloth/llama-2-7b-bnb-4bit
   - Format: sharegpt
   - Provider: ollama
4. Click "Create" or Ctrl+S
```

### 2️⃣ Define XML Patterns
```
1. Press X → XML Editor
2. Enter project name → Click "Load Project"
3. Press A → Add Tag
4. Configure:
   - Tag Name: thinking
   - Description: Internal reasoning
   - Constraint Type: free_form
   - Required: Yes
5. Click "Save"
6. Press P → Preview pattern
7. Press S → Save to project
```

### 3️⃣ Generate Training Data
```
1. Press G → Generation
2. Enter:
   - Project: my-project
   - Examples: 100
   - Temperature: 0.7
   - Batch: 10
3. Click "Generate Dataset"
4. Watch progress bar and logs
5. Success! ✅
```

### 4️⃣ Train Your Model
```
1. Press T → Training
2. Enter:
   - Project: my-project
   - Dataset: (from generation)
3. Click "Start Training"
4. Monitor:
   - Progress bars
   - Current loss
   - Live logs
5. Auto-refreshes every 5 seconds
6. Complete! 🚀
```

### 5️⃣ Export Model
```
1. Press E → Export
2. Enter:
   - Model dir: models/my-project
   - Format: GGUF
   - Quantization: 4-bit
3. Click "Export Model"
4. Done! 📦
```

## Keyboard Shortcuts Cheat Sheet

### Global (Works Everywhere)
- `Q` - Quit
- `H` - Home
- `ESC` - Back
- `Tab` - Next input
- `Shift+Tab` - Previous input
- `Enter` - Activate/Submit

### Projects Screen
- `N` - New project
- `L` - Load project
- `D` - Delete project
- `R` - Refresh list

### XML Editor Screen
- `A` - Add tag
- `R` - Remove tag
- `P` - Preview pattern
- `S` - Save changes

### Generation Screen
- `G` - Start generation

### Training Screen
- `T` - Start training
- `S` - Check status
- `C` - Cancel job

## Tips & Tricks

### Mouse Support
- ✅ Click buttons to activate
- ✅ Click table rows to select
- ✅ Scroll logs and lists
- ✅ Click inputs to edit

### Color Codes
- 🟢 **Green** - Success, Completed
- 🔵 **Blue** - Running, Active
- 🟡 **Yellow** - Warning, Pending
- 🔴 **Red** - Error, Failed

### Status Bar
- Bottom of screen shows available shortcuts
- Updates based on current screen
- Context-sensitive help

### Confirmation Dialogs
- Destructive actions (delete, cancel) require confirmation
- Click "Yes"/"No" or press Enter/ESC

### Real-Time Updates
- Training screen auto-refreshes during jobs
- Progress bars update live
- Logs scroll automatically

## Common Issues

### Can't Connect to API
```
Error: Cannot connect to API

Solution:
1. Check backend is running
2. Verify API URL: echo $API_URL
3. Test with: curl http://localhost:8000/api/v1/projects
```

### TUI Won't Start
```
Error: TUI dependencies not installed

Solution:
pip install textual rich click
```

### Display Glitches
```
Issue: Weird characters or layout

Solution:
1. Use modern terminal (iTerm2, Alacritty, Windows Terminal)
2. Ensure terminal size > 80x24
3. Try: export TERM=xterm-256color
```

### Keyboard Shortcuts Don't Work
```
Issue: Keys captured by terminal

Solution:
1. Check terminal key bindings
2. Use mouse as alternative
3. Try different terminal emulator
```

## Advanced Usage

### Environment Variables
```bash
# Set API URL
export API_URL="http://localhost:9000"

# Set debug mode
export DEBUG=1

# Launch TUI
./tui.sh
```

### Custom Configuration
Edit `/home/user/model-train/cli/tui.py`:
- Change default API URL
- Modify refresh intervals
- Customize colors/themes
- Add new screens

### Batch Operations
From Projects screen:
1. Select multiple rows (future feature)
2. Apply bulk actions
3. Export project configurations

## Resources

- **Full Guide**: [TUI_GUIDE.md](TUI_GUIDE.md)
- **Technical Summary**: [TUI_SUMMARY.md](TUI_SUMMARY.md)
- **API Docs**: Check backend documentation
- **Textual Docs**: https://textual.textualize.io/

## Support

Having issues? Check:
1. Backend is running on port 8000
2. Dependencies are installed
3. Terminal size is adequate (80x24 minimum)
4. Python version ≥ 3.8

## Example Session

```bash
# 1. Start backend
$ python -m backend.main
INFO: Uvicorn running on http://127.0.0.1:8000

# 2. Launch TUI (new terminal)
$ ./tui.sh
✓ Launching TUI interface...

# 3. Use TUI
[Home Screen appears]
Press P → Create project
Press X → Add XML patterns
Press G → Generate 100 examples
Press T → Start training
Watch progress...
Press E → Export model

# 4. Exit
Press Q → Quit
```

## Next Steps

After mastering the TUI:
1. ⚡ Use CLI for scripting: `python -m cli.main --help`
2. 🌐 Try Web UI: Open `http://localhost:8000` in browser
3. 🔧 Customize patterns: Edit XML tags for your use case
4. 📊 Analyze results: Check training metrics
5. 🚀 Deploy: Export and use your trained model

---

**Happy Training!** 🎉

For more help: See [TUI_GUIDE.md](TUI_GUIDE.md)
