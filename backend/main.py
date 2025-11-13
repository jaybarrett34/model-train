"""
Main FastAPI application for the model fine-tuning platform.
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.api import api_router

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown tasks.
    """
    # Startup: Create necessary directories
    directories = [
        os.getenv("PROJECTS_DIR", "./projects"),
        os.getenv("MODELS_DIR", "./models"),
        os.getenv("DATASETS_DIR", "./datasets"),
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True, parents=True)

    print("=" * 60)
    print("Model Fine-Tuning Application Started")
    print("=" * 60)
    print(f"Projects directory: {directories[0]}")
    print(f"Models directory: {directories[1]}")
    print(f"Datasets directory: {directories[2]}")
    print("=" * 60)

    yield

    # Shutdown tasks (if any)
    print("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Model Fine-Tuning API",
    description="API for managing ML model fine-tuning projects with XML pattern synthesis",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Model Fine-Tuning API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
    )
