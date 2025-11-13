"""
API routes for model training.
"""
from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path

from backend.schemas import TrainRequest, TrainResponse, TrainStatus
from backend.services import ProjectService, TrainingService

router = APIRouter(prefix="/train", tags=["training"])


def get_project_service() -> ProjectService:
    """Dependency to get project service instance."""
    return ProjectService()


def get_training_service() -> TrainingService:
    """Dependency to get training service instance."""
    return TrainingService()


@router.post("", response_model=TrainResponse)
async def start_training(
    request: TrainRequest,
    project_service: ProjectService = Depends(get_project_service),
    training_service: TrainingService = Depends(get_training_service),
):
    """
    Start a fine-tuning job.

    This endpoint:
    1. Loads the project configuration
    2. Validates the dataset exists
    3. Initializes the training job
    4. Returns a job ID for status tracking
    """
    # Get project
    project = project_service.get_project(request.project_name)
    if not project:
        raise HTTPException(
            status_code=404, detail=f"Project '{request.project_name}' not found"
        )

    # Validate dataset exists
    dataset_path = Path("./datasets") / request.dataset_filename
    if not dataset_path.exists():
        raise HTTPException(
            status_code=404, detail=f"Dataset '{request.dataset_filename}' not found"
        )

    try:
        # Start training
        result = training_service.start_training(project, request)

        return TrainResponse(
            success=True,
            message=f"Training job started successfully",
            job_id=result["job_id"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting training: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=TrainStatus)
async def get_training_status(
    job_id: str,
    training_service: TrainingService = Depends(get_training_service),
):
    """Get the status of a training job."""
    status = training_service.get_training_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Training job '{job_id}' not found")
    return status


@router.delete("/cancel/{job_id}", status_code=204)
async def cancel_training(
    job_id: str,
    training_service: TrainingService = Depends(get_training_service),
):
    """Cancel a running training job."""
    success = training_service.cancel_training(job_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job '{job_id}' (not found or already completed)",
        )
