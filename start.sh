#!/bin/bash
#
# Startup Script for Model Training Application
#
# This script:
# 1. Checks system dependencies
# 2. Creates and activates virtual environment
# 3. Installs Python dependencies
# 4. Starts backend and frontend services
#
# Usage:
#   ./start.sh              # Start both backend and frontend
#   ./start.sh --backend    # Start backend only
#   ./start.sh --frontend   # Start frontend only
#   ./start.sh --dev        # Start in development mode with auto-reload
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR="venv"
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system dependencies
check_dependencies() {
    print_info "Checking system dependencies..."

    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python ${PYTHON_VERSION} found"

    # Check pip
    if ! command_exists pip3; then
        print_error "pip3 is not installed. Please install pip."
        exit 1
    fi

    # Check Node.js (optional, for frontend)
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js ${NODE_VERSION} found"
    else
        print_warning "Node.js not found. Frontend will not be available."
    fi

    # Check if Ollama is running (optional)
    if command_exists ollama; then
        print_success "Ollama CLI found"
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            print_success "Ollama server is running"
        else
            print_warning "Ollama server is not running. Start it with: ollama serve"
        fi
    else
        print_warning "Ollama not found. Install from https://ollama.ai for local AI generation"
    fi
}

# Create and activate virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."

    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."

    # Upgrade pip
    pip install --upgrade pip >/dev/null 2>&1

    # Install requirements
    if [ -f "requirements.txt" ]; then
        print_info "Installing from requirements.txt..."
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi

    # Install development dependencies if in dev mode
    if [ "$DEV_MODE" = true ] && [ -f "requirements-dev.txt" ]; then
        print_info "Installing development dependencies..."
        pip install -r requirements-dev.txt
        print_success "Development dependencies installed"
    fi
}

# Start backend service
start_backend() {
    print_info "Starting backend service on port ${BACKEND_PORT}..."

    # Create necessary directories
    mkdir -p datasets models logs

    # Set environment variables
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"

    if [ "$DEV_MODE" = true ]; then
        # Development mode with auto-reload
        uvicorn backend.main:app \
            --host 0.0.0.0 \
            --port "$BACKEND_PORT" \
            --reload \
            --log-level info &
    else
        # Production mode
        uvicorn backend.main:app \
            --host 0.0.0.0 \
            --port "$BACKEND_PORT" \
            --workers 4 \
            --log-level info &
    fi

    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid

    print_success "Backend started (PID: $BACKEND_PID)"
    print_info "Backend API: http://localhost:${BACKEND_PORT}"
    print_info "API Docs: http://localhost:${BACKEND_PORT}/docs"
}

# Start frontend service
start_frontend() {
    if [ ! -d "frontend" ]; then
        print_warning "Frontend directory not found. Skipping frontend startup."
        return
    fi

    print_info "Starting frontend service on port ${FRONTEND_PORT}..."

    cd frontend

    # Install npm dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_info "Installing Node.js dependencies..."
        npm install
    fi

    # Start frontend
    if [ "$DEV_MODE" = true ]; then
        npm run dev &
    else
        npm run build
        npm run start &
    fi

    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..

    print_success "Frontend started (PID: $FRONTEND_PID)"
    print_info "Frontend URL: http://localhost:${FRONTEND_PORT}"
}

# Stop services
stop_services() {
    print_info "Stopping services..."

    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            kill "$BACKEND_PID"
            print_success "Backend stopped"
        fi
        rm backend.pid
    fi

    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            kill "$FRONTEND_PID"
            print_success "Frontend stopped"
        fi
        rm frontend.pid
    fi
}

# Cleanup on exit
cleanup() {
    print_info "Cleaning up..."
    stop_services
    deactivate 2>/dev/null || true
}

trap cleanup EXIT INT TERM

# Parse command line arguments
START_BACKEND=true
START_FRONTEND=true
DEV_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            START_FRONTEND=false
            shift
            ;;
        --frontend)
            START_BACKEND=false
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        --stop)
            stop_services
            exit 0
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend    Start backend only"
            echo "  --frontend   Start frontend only"
            echo "  --dev        Start in development mode with auto-reload"
            echo "  --stop       Stop running services"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_info "Starting Model Training Application..."
    echo ""

    # Check dependencies
    check_dependencies
    echo ""

    # Setup virtual environment
    setup_venv
    echo ""

    # Install dependencies
    install_dependencies
    echo ""

    # Start services
    if [ "$START_BACKEND" = true ]; then
        start_backend
        sleep 2  # Give backend time to start
    fi

    if [ "$START_FRONTEND" = true ]; then
        start_frontend
    fi

    echo ""
    print_success "Application started successfully!"
    echo ""
    print_info "Services:"
    if [ "$START_BACKEND" = true ]; then
        echo "  - Backend API: http://localhost:${BACKEND_PORT}"
        echo "  - API Documentation: http://localhost:${BACKEND_PORT}/docs"
    fi
    if [ "$START_FRONTEND" = true ]; then
        echo "  - Frontend: http://localhost:${FRONTEND_PORT}"
    fi
    echo ""
    print_info "Press Ctrl+C to stop all services"
    echo ""

    # Wait for user to stop services
    wait
}

# Run main function
main
