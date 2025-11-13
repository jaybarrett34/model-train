"""
API routes for model management.
"""
from fastapi import APIRouter, HTTPException, Depends

from backend.schemas import ModelList, ModelDownloadRequest, ModelDownloadResponse
from backend.services import ModelService

router = APIRouter(prefix="/models", tags=["models"])


def get_model_service() -> ModelService:
    """Dependency to get model service instance."""
    return ModelService()


@router.get("", response_model=ModelList)
async def list_models(
    service: ModelService = Depends(get_model_service),
):
    """List all available models (downloaded locally)."""
    models = service.list_models()
    return ModelList(models=models, total=len(models))


@router.post("/download", response_model=ModelDownloadResponse)
async def download_model(
    request: ModelDownloadRequest,
    service: ModelService = Depends(get_model_service),
):
    """
    Download a model from HuggingFace.

    This endpoint downloads a model and saves it to the local models directory.
    """
    try:
        result = service.download_model(
            model_id=request.model_id,
            revision=request.revision,
            quantization=request.quantization,
        )

        return ModelDownloadResponse(
            success=True,
            message=f"Model '{request.model_id}' downloaded successfully",
            model_path=result["model_path"],
            model_id=result["model_id"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error downloading model: {str(e)}"
        )


@router.delete("/{model_name}", status_code=204)
async def delete_model(
    model_name: str,
    service: ModelService = Depends(get_model_service),
):
    """Delete a model from local storage."""
    success = service.delete_model(model_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")


@router.get("/{model_name}")
async def get_model_info(
    model_name: str,
    service: ModelService = Depends(get_model_service),
):
    """Get detailed information about a specific model."""
    info = service.get_model_info(model_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    return info
