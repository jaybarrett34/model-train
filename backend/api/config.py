"""
API routes for configuration management.
"""
from fastapi import APIRouter, Depends

from backend.schemas import AppConfig, ConfigUpdate
from backend.services.config_service import ConfigService

router = APIRouter(prefix="/config", tags=["config"])


def get_config_service() -> ConfigService:
    """Dependency to get config service instance."""
    return ConfigService()


@router.get("", response_model=AppConfig)
async def get_config(
    service: ConfigService = Depends(get_config_service),
):
    """Get current application configuration."""
    return service.get_config()


@router.post("", response_model=AppConfig)
async def update_config(
    updates: ConfigUpdate,
    service: ConfigService = Depends(get_config_service),
):
    """
    Update configuration values.

    Note: This only updates API keys and similar settings stored in .env.
    Structural configurations (paths, limits) require manual .env editing.
    """
    update_dict = updates.model_dump(exclude_unset=True)
    return service.update_config(**update_dict)
