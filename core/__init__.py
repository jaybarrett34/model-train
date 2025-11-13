"""
Core module for model fine-tuning with Unsloth and AI-powered data synthesis.

This package provides:
- Comprehensive training pipeline for fine-tuning large language models using Unsloth
- AI-powered training data synthesis with multiple providers (Ollama, Claude, OpenAI)
- XML pattern validation and dataset formatting utilities
- Dataset size analysis and quality metrics
"""

# Import synthesis module (always available)
from .synthesis import (
    # Enums and Configs
    GenerationMode,
    GenerationConfig,
    XMLPattern,

    # Exceptions
    ValidationError,
    AIProviderError,

    # Providers
    AIProvider,
    OllamaProvider,
    ClaudeProvider,
    OpenAIProvider,

    # Core Classes
    XMLValidator,
    DataSynthesizer,

    # Utilities
    to_sharegpt_format,
    to_alpaca_format,
    save_dataset,
)

# Import size analyzer module
from .size_analyzer import (
    # Enums
    FinetuningStrength,
    AdequacyStatus,
    ComplexityLevel,

    # Data Classes
    SizeEstimate,
    QualityMetrics,
    ComplexityAnalysis,
    AnalysisReport,

    # Core Class
    DatasetSizeAnalyzer,

    # Utility
    analyze_dataset,
)

# Try to import training module (optional - may not be fully implemented yet)
__all__ = [
    # Synthesis module - Enums and Configs
    "GenerationMode",
    "GenerationConfig",
    "XMLPattern",

    # Synthesis module - Exceptions
    "ValidationError",
    "AIProviderError",

    # Synthesis module - Providers
    "AIProvider",
    "OllamaProvider",
    "ClaudeProvider",
    "OpenAIProvider",

    # Synthesis module - Core Classes
    "XMLValidator",
    "DataSynthesizer",

    # Synthesis module - Utilities
    "to_sharegpt_format",
    "to_alpaca_format",
    "save_dataset",

    # Size Analyzer module - Enums
    "FinetuningStrength",
    "AdequacyStatus",
    "ComplexityLevel",

    # Size Analyzer module - Data Classes
    "SizeEstimate",
    "QualityMetrics",
    "ComplexityAnalysis",
    "AnalysisReport",

    # Size Analyzer module - Core Class
    "DatasetSizeAnalyzer",

    # Size Analyzer module - Utility
    "analyze_dataset",
]

# Note: Training module imports are commented out until the training directory
# structure is resolved. To use training features, import directly:
# from core.training import UnslothTrainer, LoRAConfig, etc.

__version__ = "0.1.0"
