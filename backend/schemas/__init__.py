"""
Pydantic schemas for API requests and responses.
"""
from .project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectList,
    XMLPattern,
    AIConfig,
    TrainingConfig,
    DatasetInfo,
)
from .generation import GenerateRequest, GenerateResponse
from .training import TrainRequest, TrainResponse, TrainStatus
from .models import (
    ModelInfo,
    ModelList,
    ModelDownloadRequest,
    ModelDownloadResponse,
)
from .config import AppConfig, ConfigUpdate

__all__ = [
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectList",
    "XMLPattern",
    "AIConfig",
    "TrainingConfig",
    "DatasetInfo",
    "GenerateRequest",
    "GenerateResponse",
    "TrainRequest",
    "TrainResponse",
    "TrainStatus",
    "ModelInfo",
    "ModelList",
    "ModelDownloadRequest",
    "ModelDownloadResponse",
    "AppConfig",
    "ConfigUpdate",
]
