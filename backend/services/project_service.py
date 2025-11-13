"""
Service layer for project management operations.
"""
import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from backend.schemas import Project, ProjectCreate, ProjectUpdate


class ProjectService:
    """Handles project CRUD operations."""

    def __init__(self, projects_dir: str = "./projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True, parents=True)

    def _get_project_path(self, name: str) -> Path:
        """Get the file path for a project."""
        return self.projects_dir / f"{name}.json"

    def create_project(self, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        project_path = self._get_project_path(project_data.name)

        if project_path.exists():
            raise ValueError(f"Project '{project_data.name}' already exists")

        # Create project with defaults
        project = Project(
            name=project_data.name,
            objective=project_data.objective,
            xml_patterns=project_data.xml_patterns or [],
            dataset_format=project_data.dataset_format or "sharegpt",
            base_model=project_data.base_model or "unsloth/llama-2-7b-bnb-4bit",
            ai_config=project_data.ai_config or {},
            training_config=project_data.training_config or {},
            datasets=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to disk
        with open(project_path, "w") as f:
            json.dump(project.model_dump(mode="json"), f, indent=2, default=str)

        return project

    def get_project(self, name: str) -> Optional[Project]:
        """Get a project by name."""
        project_path = self._get_project_path(name)

        if not project_path.exists():
            return None

        with open(project_path, "r") as f:
            data = json.load(f)

        return Project(**data)

    def list_projects(self) -> List[Project]:
        """List all projects."""
        projects = []

        for project_file in self.projects_dir.glob("*.json"):
            try:
                with open(project_file, "r") as f:
                    data = json.load(f)
                projects.append(Project(**data))
            except Exception as e:
                print(f"Error loading project {project_file}: {e}")
                continue

        # Sort by updated_at descending
        projects.sort(key=lambda p: p.updated_at, reverse=True)
        return projects

    def update_project(self, name: str, updates: ProjectUpdate) -> Optional[Project]:
        """Update an existing project."""
        project = self.get_project(name)

        if not project:
            return None

        # Apply updates
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)

        project.updated_at = datetime.utcnow()

        # Save to disk
        project_path = self._get_project_path(name)
        with open(project_path, "w") as f:
            json.dump(project.model_dump(mode="json"), f, indent=2, default=str)

        return project

    def delete_project(self, name: str) -> bool:
        """Delete a project."""
        project_path = self._get_project_path(name)

        if not project_path.exists():
            return False

        project_path.unlink()
        return True

    def add_dataset_to_project(
        self, project_name: str, dataset_filename: str, num_examples: int, format: str
    ) -> Optional[Project]:
        """Add a dataset reference to a project."""
        project = self.get_project(project_name)

        if not project:
            return None

        from backend.schemas import DatasetInfo

        # Get file size if exists
        dataset_path = Path("./datasets") / dataset_filename
        size_bytes = dataset_path.stat().st_size if dataset_path.exists() else None

        dataset_info = DatasetInfo(
            filename=dataset_filename,
            created_at=datetime.utcnow(),
            num_examples=num_examples,
            format=format,
            size_bytes=size_bytes,
        )

        project.datasets.append(dataset_info)
        project.updated_at = datetime.utcnow()

        # Save to disk
        project_path = self._get_project_path(project_name)
        with open(project_path, "w") as f:
            json.dump(project.model_dump(mode="json"), f, indent=2, default=str)

        return project
