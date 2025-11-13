"""
Project schema definitions for the model training application.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class XMLPattern(BaseModel):
    """Definition of an XML tag pattern with constraints."""
    tag_name: str = Field(..., description="Name of the XML tag")
    description: str = Field(..., description="Purpose and usage of this tag")
    attributes: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional attributes and their types"
    )
    constraints: Optional[str] = Field(
        default=None,
        description="Validation rules or constraints for tag content"
    )
    examples: Optional[List[str]] = Field(
        default=None,
        description="Example usages of this tag"
    )


class AIConfig(BaseModel):
    """Configuration for AI service used in synthesis."""
    provider: Literal["ollama", "anthropic", "openai"] = Field(
        default="ollama",
        description="LLM provider for synthetic data generation"
    )
    model: str = Field(
        default="llama2",
        description="Model identifier"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=2048,
        ge=1,
        description="Maximum tokens to generate"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Base URL for the API (used for Ollama)"
    )


class TrainingConfig(BaseModel):
    """Unsloth/QLoRA training configuration."""
    max_seq_length: int = Field(
        default=2048,
        ge=128,
        description="Maximum sequence length"
    )
    load_in_4bit: bool = Field(
        default=True,
        description="Use 4-bit quantization"
    )
    lora_r: int = Field(
        default=16,
        ge=1,
        description="LoRA rank"
    )
    lora_alpha: int = Field(
        default=16,
        ge=1,
        description="LoRA alpha parameter"
    )
    lora_dropout: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="LoRA dropout rate"
    )
    target_modules: List[str] = Field(
        default=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        description="Target modules for LoRA"
    )
    batch_size: int = Field(
        default=2,
        ge=1,
        description="Training batch size per device"
    )
    gradient_accumulation_steps: int = Field(
        default=4,
        ge=1,
        description="Gradient accumulation steps"
    )
    learning_rate: float = Field(
        default=2e-4,
        gt=0.0,
        description="Learning rate"
    )
    num_train_epochs: int = Field(
        default=3,
        ge=1,
        description="Number of training epochs"
    )
    warmup_steps: int = Field(
        default=5,
        ge=0,
        description="Number of warmup steps"
    )
    logging_steps: int = Field(
        default=1,
        ge=1,
        description="Log every N steps"
    )
    save_steps: int = Field(
        default=100,
        ge=1,
        description="Save checkpoint every N steps"
    )
    optimizer: str = Field(
        default="adamw_8bit",
        description="Optimizer type"
    )
    weight_decay: float = Field(
        default=0.01,
        ge=0.0,
        description="Weight decay"
    )
    fp16: bool = Field(
        default=False,
        description="Use FP16 precision"
    )
    bf16: bool = Field(
        default=True,
        description="Use BF16 precision"
    )


class DatasetInfo(BaseModel):
    """Information about a generated dataset."""
    filename: str = Field(..., description="Dataset filename")
    created_at: datetime = Field(..., description="Creation timestamp")
    num_examples: int = Field(..., description="Number of examples in dataset")
    format: Literal["sharegpt", "alpaca"] = Field(..., description="Dataset format")
    size_bytes: Optional[int] = Field(default=None, description="File size in bytes")


class Project(BaseModel):
    """Complete project configuration."""
    name: str = Field(..., description="Unique project name")
    objective: str = Field(..., description="Training objective and purpose")
    xml_patterns: List[XMLPattern] = Field(
        default=[],
        description="XML tag definitions and constraints"
    )
    dataset_format: Literal["sharegpt", "alpaca"] = Field(
        default="sharegpt",
        description="Output dataset format"
    )
    base_model: str = Field(
        default="unsloth/llama-2-7b-bnb-4bit",
        description="HuggingFace model identifier"
    )
    ai_config: AIConfig = Field(
        default_factory=AIConfig,
        description="AI service configuration for synthesis"
    )
    training_config: TrainingConfig = Field(
        default_factory=TrainingConfig,
        description="Unsloth/QLoRA training parameters"
    )
    datasets: List[DatasetInfo] = Field(
        default=[],
        description="Generated datasets for this project"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Project creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "xml-formatter",
                "objective": "Train a model to generate properly formatted XML with specific tag constraints",
                "xml_patterns": [
                    {
                        "tag_name": "thinking",
                        "description": "Internal reasoning before response",
                        "constraints": "Must appear before any output tags"
                    }
                ],
                "dataset_format": "sharegpt",
                "base_model": "unsloth/llama-2-7b-bnb-4bit"
            }
        }


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    objective: str = Field(..., min_length=1, description="Training objective")
    xml_patterns: Optional[List[XMLPattern]] = Field(default=None)
    dataset_format: Optional[Literal["sharegpt", "alpaca"]] = Field(default="sharegpt")
    base_model: Optional[str] = Field(default="unsloth/llama-2-7b-bnb-4bit")
    ai_config: Optional[AIConfig] = Field(default=None)
    training_config: Optional[TrainingConfig] = Field(default=None)


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""
    objective: Optional[str] = Field(default=None)
    xml_patterns: Optional[List[XMLPattern]] = Field(default=None)
    dataset_format: Optional[Literal["sharegpt", "alpaca"]] = Field(default=None)
    base_model: Optional[str] = Field(default=None)
    ai_config: Optional[AIConfig] = Field(default=None)
    training_config: Optional[TrainingConfig] = Field(default=None)


class ProjectList(BaseModel):
    """List of projects."""
    projects: List[Project]
    total: int
