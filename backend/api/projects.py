"""
API routes for project management.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from backend.schemas import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectList,
)
from backend.services import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service() -> ProjectService:
    """Dependency to get project service instance."""
    return ProjectService()


@router.post("", response_model=Project, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    """Create a new project."""
    try:
        return service.create_project(project_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=ProjectList)
async def list_projects(
    service: ProjectService = Depends(get_project_service),
):
    """List all projects."""
    projects = service.list_projects()
    return ProjectList(projects=projects, total=len(projects))


@router.get("/{name}", response_model=Project)
async def get_project(
    name: str,
    service: ProjectService = Depends(get_project_service),
):
    """Get a specific project by name."""
    project = service.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
    return project


@router.put("/{name}", response_model=Project)
async def update_project(
    name: str,
    updates: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    """Update an existing project."""
    project = service.update_project(name, updates)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
    return project


@router.delete("/{name}", status_code=204)
async def delete_project(
    name: str,
    service: ProjectService = Depends(get_project_service),
):
    """Delete a project."""
    success = service.delete_project(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
