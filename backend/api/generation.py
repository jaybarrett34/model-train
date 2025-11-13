"""
API routes for synthetic data generation.
"""
from fastapi import APIRouter, HTTPException, Depends

from backend.schemas import GenerateRequest, GenerateResponse
from backend.services import ProjectService, GenerationService

router = APIRouter(prefix="/generate", tags=["generation"])


def get_project_service() -> ProjectService:
    """Dependency to get project service instance."""
    return ProjectService()


def get_generation_service() -> GenerationService:
    """Dependency to get generation service instance."""
    return GenerationService()


@router.post("", response_model=GenerateResponse)
async def generate_dataset(
    request: GenerateRequest,
    project_service: ProjectService = Depends(get_project_service),
    generation_service: GenerationService = Depends(get_generation_service),
):
    """
    Generate synthetic training data for a project.

    This endpoint:
    1. Loads the project configuration
    2. Uses the AI service to generate examples
    3. Applies XML patterns and constraints
    4. Saves the dataset in the specified format
    5. Updates the project with dataset reference
    """
    # Get project
    project = project_service.get_project(request.project_name)
    if not project:
        raise HTTPException(
            status_code=404, detail=f"Project '{request.project_name}' not found"
        )

    try:
        # Generate dataset
        result = generation_service.generate_dataset(project, request)

        # Add dataset to project
        project_service.add_dataset_to_project(
            project_name=request.project_name,
            dataset_filename=result["filename"],
            num_examples=result["num_generated"],
            format=result["format"],
        )

        return GenerateResponse(
            success=True,
            message=f"Successfully generated {result['num_generated']} examples",
            dataset_filename=result["filename"],
            num_generated=result["num_generated"],
            format=result["format"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating dataset: {str(e)}"
        )
