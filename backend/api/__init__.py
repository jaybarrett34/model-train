"""
API routes for the FastAPI application.
"""
from fastapi import APIRouter

from . import projects, generation, training, models, config

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(projects.router)
api_router.include_router(generation.router)
api_router.include_router(training.router)
api_router.include_router(models.router)
api_router.include_router(config.router)

__all__ = ["api_router"]
