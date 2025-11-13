"""
Command-line and text user interface for the model training application.

This module provides:
- Comprehensive CLI commands for all operations
- Project, XML pattern, and dataset management
- Training job monitoring and control
- Model download and export capabilities
- Progress bars and colorful status displays
"""
__version__ = "0.1.0"

from cli.main import cli, main

__all__ = ["cli", "main", "__version__"]
