"""
Schemas for synthetic data generation.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request to generate synthetic training data."""
    project_name: str = Field(..., description="Name of the project")
    num_examples: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Number of examples to generate"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Override AI temperature for generation"
    )
    batch_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of examples to generate per batch"
    )


class GenerateResponse(BaseModel):
    """Response from data generation."""
    success: bool
    message: str
    dataset_filename: Optional[str] = Field(default=None)
    num_generated: Optional[int] = Field(default=None)
    format: Optional[Literal["sharegpt", "alpaca"]] = Field(default=None)
