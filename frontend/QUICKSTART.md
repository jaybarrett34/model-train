# Quick Start Guide

Get up and running with the Model Training UI in 5 minutes.

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Backend API running (default: http://localhost:8000)

## Installation

```bash
# Install dependencies
npm install

# This will install:
# - React 19 + React Router
# - Vite build tool
# - TailwindCSS for styling
# - @dnd-kit & @hello-pangea/dnd for drag-and-drop
# - Zustand for state management
# - Axios for API calls
# - Recharts for visualizations
# - Lucide React for icons
```

## Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your API URL
# VITE_API_URL=http://localhost:8000/api
```

## Development

```bash
# Start dev server with hot reload
npm run dev

# Open browser to http://localhost:5173
```

## First Steps

### 1. Create a Project (30 seconds)

- Click "New Project" on the home screen
- Enter a name like "My First Model"
- Add optional description
- Click "Create"

### 2. Build XML Pattern (2 minutes)

- Click "XML Editor" in the sidebar
- Drag tags from the left palette to the canvas
  - Try dragging "text", "number", and "date" tags
- Click the settings icon on a tag to configure constraints
  - Add a regex pattern for validation
  - Set min/max ranges for numbers
- Click "Save Pattern"

### 3. Generate Data (3 minutes)

- Click "Generator" in the sidebar
- Enter an objective like:
  ```
  Generate customer support conversations about product returns
  ```
- Configure AI provider:
  - For local: Select "Ollama" with "llama2"
  - For cloud: Select "OpenAI" and add API key
- Set number of samples (start with 10-20)
- Click "Start Generation"
- Watch progress and preview samples

### 4. Analyze Dataset Size (1 minute)

- Click "Size Analyzer" in the sidebar
- Select your target model (e.g., "llama-2-7b")
- Set task complexity (e.g., "Medium")
- Adjust desired accuracy slider
- View recommendations for:
  - Minimum samples needed
  - Recommended dataset size
  - Optimal size for best quality
  - Training time and cost estimates

### 5. View Dataset (1 minute)

- Click "Datasets" in the sidebar
- Click "Preview" on your dataset
- Browse through generated samples
- Click "Validate" to check quality
- Export to JSONL if needed

### 6. Train Model (10+ minutes)

- Click "Training" in the sidebar
- Select your dataset
- Search for base model or use default "meta-llama/Llama-2-7b-hf"
- Adjust training parameters:
  - Epochs: 3 (default)
  - Batch size: 4 (for 16GB VRAM)
  - Learning rate: 2e-4
- Configure QLoRA parameters (defaults are good)
- Click "Start Training"
- Monitor progress and loss graph

### 7. Export Model (2 minutes)

- Click "Export" in the sidebar
- Select your trained model
- Choose format:
  - HuggingFace for standard deployment
  - GGUF for llama.cpp
  - ONNX for cross-platform
- Configure options:
  - Merge adapters for faster inference
  - Quantization for smaller size
- Click "Export Model"

## Common Workflows

### Quick Prototype Flow

```
Create Project → Build Simple Pattern → Generate 50 Samples → Quick Train (1 epoch)
```

### Production Flow

```
Create Project →
Design Detailed Pattern with Constraints →
Use Size Analyzer →
Generate Recommended Sample Count →
Validate Dataset →
Train with Optimal Settings →
Export with Quantization
```

### Experimentation Flow

```
Create Project →
Generate Data with Different Modes →
Compare Dataset Quality →
Train Multiple Variants →
Export Best Performer
```

## Tips & Tricks

### XML Pattern Design

- Start simple with 2-3 basic tags
- Test generation with small samples first
- Add constraints gradually
- Use preview to verify structure

### Data Generation

- **Pseudorandom**: Fast, diverse, less structured
- **Patterned**: Balanced quality and speed
- **Forced**: Slow but highly structured

### Training

- **Small datasets (<500)**: 5-10 epochs
- **Medium datasets (500-2000)**: 3-5 epochs
- **Large datasets (2000+)**: 1-3 epochs

- **Low VRAM (8-12GB)**: Batch size 1-2, gradient accumulation 8
- **Medium VRAM (16-24GB)**: Batch size 4, gradient accumulation 4
- **High VRAM (40GB+)**: Batch size 8+, gradient accumulation 2

### Size Analyzer

- Use "Recommended" size for most cases
- Use "Minimum" only for rapid prototyping
- Use "Optimal" for production models
- Higher accuracy target = more samples needed
- More complex tasks = more samples needed

### Dataset Quality

- Validate before training to catch errors
- Preview samples to check diversity
- Check quality scores if available
- Remove duplicates or low-quality samples

## Troubleshooting

### Frontend won't start

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Can't connect to backend

1. Check backend is running: `curl http://localhost:8000/api/health`
2. Verify VITE_API_URL in .env
3. Check browser console for CORS errors

### Drag-and-drop not working

1. Clear browser cache
2. Check console for errors
3. Ensure @hello-pangea/dnd is installed

### Generation stuck

1. Check backend logs for errors
2. Verify AI provider is accessible
3. Try smaller batch size
4. Check API key if using cloud provider

### Training fails

1. Verify dataset exists and is valid
2. Check VRAM availability
3. Reduce batch size if OOM
4. Ensure base model is accessible

## Production Deployment

### Build for Production

```bash
# Create optimized build
npm run build

# Output in dist/ directory
```

### Serve Static Files

```bash
# Using Vite preview
npm run preview

# Or use any static file server
npx serve dist
```

### Environment Variables

For production, set:
```
VITE_API_URL=https://api.yourcompany.com/api
```

### Nginx Example

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
    }
}
```

## Performance Tips

### Development

- Use `npm run dev` with hot reload
- Keep browser DevTools open
- Use React DevTools extension

### Production

- Enable gzip/brotli compression
- Use CDN for static assets
- Cache API responses where appropriate
- Lazy load heavy components

## Next Steps

- Read [README.md](README.md) for detailed features
- Check [COMPONENTS.md](COMPONENTS.md) for component reference
- Review API documentation for backend integration
- Join community for support and updates

## Support

- GitHub Issues: Report bugs and request features
- Documentation: Full guides and API reference
- Community: Forums and Discord

---

**Ready to train your first model?** Start with step 1 above!
