"""
Schemas for model management.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ModelInfo(BaseModel):
    """Information about a model."""
    name: str = Field(..., description="Model name/identifier")
    path: str = Field(..., description="Local path to model")
    size_bytes: Optional[int] = Field(default=None, description="Model size in bytes")
    model_type: Optional[str] = Field(default=None, description="Type of model (base/fine-tuned)")
    source: Optional[str] = Field(default=None, description="Source (huggingface, local)")
    created_at: Optional[datetime] = Field(default=None, description="Creation/download time")


class ModelList(BaseModel):
    """List of available models."""
    models: List[ModelInfo]
    total: int


class ModelDownloadRequest(BaseModel):
    """Request to download a model from HuggingFace."""
    model_id: str = Field(..., description="HuggingFace model identifier")
    revision: Optional[str] = Field(
        default="main",
        description="Model revision/branch"
    )
    quantization: Optional[str] = Field(
        default=None,
        description="Quantization method (4bit, 8bit)"
    )


class ModelDownloadResponse(BaseModel):
    """Response from model download."""
    success: bool
    message: str
    model_path: Optional[str] = Field(default=None)
    model_id: Optional[str] = Field(default=None)
