"""
Schemas for model training operations.
"""
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class TrainRequest(BaseModel):
    """Request to start a fine-tuning job."""
    project_name: str = Field(..., description="Name of the project")
    dataset_filename: str = Field(..., description="Dataset file to use for training")
    output_dir: Optional[str] = Field(
        default=None,
        description="Output directory for model (defaults to models/{project_name})"
    )
    resume_from_checkpoint: Optional[str] = Field(
        default=None,
        description="Path to checkpoint to resume from"
    )


class TrainingStatus(str):
    """Training job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainStatus(BaseModel):
    """Training job status response."""
    job_id: str
    status: Literal["pending", "running", "completed", "failed", "cancelled"]
    project_name: str
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    current_epoch: Optional[int] = Field(default=None)
    total_epochs: Optional[int] = Field(default=None)
    current_step: Optional[int] = Field(default=None)
    total_steps: Optional[int] = Field(default=None)
    loss: Optional[float] = Field(default=None)
    learning_rate: Optional[float] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    metrics: Optional[Dict[str, Any]] = Field(default=None)
    output_dir: Optional[str] = Field(default=None)


class TrainResponse(BaseModel):
    """Response from starting a training job."""
    success: bool
    message: str
    job_id: Optional[str] = Field(default=None)
