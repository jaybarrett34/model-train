"""
Service layer for configuration management.
"""
import os
from pathlib import Path
from typing import Optional

from backend.schemas import AppConfig


class ConfigService:
    """Handles application configuration."""

    def __init__(self, env_file: str = ".env"):
        self.env_file = Path(env_file)
        self._load_env()

    def _load_env(self):
        """Load environment variables from .env file."""
        if self.env_file.exists():
            from dotenv import load_dotenv

            load_dotenv(self.env_file)

    def get_config(self) -> AppConfig:
        """Get current configuration."""
        return AppConfig(
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "8000")),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama2"),
            huggingface_token=os.getenv("HUGGINGFACE_TOKEN"),
            projects_dir=os.getenv("PROJECTS_DIR", "./projects"),
            models_dir=os.getenv("MODELS_DIR", "./models"),
            datasets_dir=os.getenv("DATASETS_DIR", "./datasets"),
            max_dataset_size_gb=int(os.getenv("MAX_DATASET_SIZE_GB", "10")),
            max_model_size_gb=int(os.getenv("MAX_MODEL_SIZE_GB", "50")),
        )

    def update_config(self, **kwargs) -> AppConfig:
        """
        Update configuration values in .env file.

        Note: Only updates API keys and similar settings, not structural configs.
        """
        lines = []

        # Read existing .env if it exists
        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                lines = f.readlines()

        # Update or add new values
        updated_keys = set()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key = line.split("=")[0]
            if key in kwargs and kwargs[key] is not None:
                lines[i] = f"{key}={kwargs[key]}\n"
                updated_keys.add(key)

        # Add new keys that weren't in the file
        for key, value in kwargs.items():
            if key not in updated_keys and value is not None:
                # Convert to uppercase with underscores
                env_key = key.upper()
                lines.append(f"{env_key}={value}\n")

        # Write back to file
        with open(self.env_file, "w") as f:
            f.writelines(lines)

        # Reload environment
        self._load_env()

        return self.get_config()
