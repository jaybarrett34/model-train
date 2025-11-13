"""
Service layer for model management operations.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class ModelService:
    """Handles model downloading and management."""

    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True, parents=True)

    def list_models(self) -> List[Dict[str, Any]]:
        """List all downloaded models."""
        models = []

        # Scan models directory
        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir():
                try:
                    # Check if it's a valid model directory (has config files)
                    has_config = (model_dir / "config.json").exists()
                    has_adapter = (model_dir / "adapter_config.json").exists()

                    if has_config or has_adapter:
                        # Calculate directory size
                        size_bytes = sum(
                            f.stat().st_size
                            for f in model_dir.rglob("*")
                            if f.is_file()
                        )

                        model_type = "fine-tuned" if has_adapter else "base"

                        models.append(
                            {
                                "name": model_dir.name,
                                "path": str(model_dir),
                                "size_bytes": size_bytes,
                                "model_type": model_type,
                                "source": "local",
                                "created_at": datetime.fromtimestamp(
                                    model_dir.stat().st_ctime
                                ),
                            }
                        )
                except Exception as e:
                    print(f"Error reading model {model_dir}: {e}")
                    continue

        models.sort(key=lambda m: m["created_at"], reverse=True)
        return models

    def download_model(
        self, model_id: str, revision: str = "main", quantization: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download a model from HuggingFace.

        This is a placeholder implementation. The actual implementation will:
        1. Use huggingface_hub to download the model
        2. Handle quantization if specified
        3. Save to models directory
        4. Return model info
        """
        # Sanitize model_id to create directory name
        model_name = model_id.replace("/", "--")
        model_path = self.models_dir / model_name

        # TODO: Implement actual download using huggingface_hub
        # from huggingface_hub import snapshot_download
        # snapshot_download(
        #     repo_id=model_id,
        #     revision=revision,
        #     local_dir=model_path,
        #     local_dir_use_symlinks=False,
        # )

        print(f"Would download model {model_id} to {model_path}")

        return {
            "model_path": str(model_path),
            "model_id": model_id,
        }

    def delete_model(self, model_name: str) -> bool:
        """Delete a model from local storage."""
        model_path = self.models_dir / model_name

        if not model_path.exists():
            return False

        # Delete directory recursively
        import shutil

        shutil.rmtree(model_path)
        return True

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific model."""
        model_path = self.models_dir / model_name

        if not model_path.exists():
            return None

        models = self.list_models()
        return next((m for m in models if m["name"] == model_name), None)
