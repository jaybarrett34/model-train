"""
Schemas for application configuration.
"""
from typing import Optional
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Application configuration."""
    # API Settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    # LLM API Keys
    anthropic_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)

    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama2")

    # HuggingFace
    huggingface_token: Optional[str] = Field(default=None)

    # Paths
    projects_dir: str = Field(default="./projects")
    models_dir: str = Field(default="./models")
    datasets_dir: str = Field(default="./datasets")

    # Storage limits
    max_dataset_size_gb: int = Field(default=10)
    max_model_size_gb: int = Field(default=50)


class ConfigUpdate(BaseModel):
    """Update configuration values."""
    anthropic_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)
    ollama_base_url: Optional[str] = Field(default=None)
    ollama_model: Optional[str] = Field(default=None)
    huggingface_token: Optional[str] = Field(default=None)
