"""
Service layer for synthetic data generation.
"""
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.schemas import Project, GenerateRequest
from core.synthesis import (
    DataSynthesizer,
    GenerationConfig,
    GenerationMode,
    XMLPattern as CoreXMLPattern,
    OllamaProvider,
    ClaudeProvider,
    OpenAIProvider,
    to_sharegpt_format,
    to_alpaca_format,
    save_dataset
)
from core.xml_engine import XMLPattern as EngineXMLPattern, XMLTag, ConstraintType
from core.size_analyzer import DatasetSizeAnalyzer, FinetuningStrength

logger = logging.getLogger(__name__)


class GenerationService:
    """Handles synthetic training data generation using core.synthesis module."""

    def __init__(self, datasets_dir: str = "./datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.datasets_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"GenerationService initialized with datasets_dir: {self.datasets_dir}")

    def _create_xml_pattern_from_project(self, project: Project) -> Optional[CoreXMLPattern]:
        """Convert project XML patterns to core XMLPattern."""
        if not project.xml_patterns:
            return None

        required_tags = [p.tag_name for p in project.xml_patterns]
        optional_tags = []

        return CoreXMLPattern(
            schema="",
            required_tags=required_tags,
            optional_tags=optional_tags
        )

    def _create_ai_provider(self, project: Project):
        """Create AI provider based on project configuration."""
        ai_config = project.ai_config

        if ai_config.provider == "ollama":
            base_url = ai_config.base_url or "http://localhost:11434"
            return OllamaProvider(model=ai_config.model, base_url=base_url)

        elif ai_config.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            return ClaudeProvider(api_key=api_key, model=ai_config.model)

        elif ai_config.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            return OpenAIProvider(api_key=api_key, model=ai_config.model)

        else:
            raise ValueError(f"Unsupported AI provider: {ai_config.provider}")

    def generate_dataset(
        self, project: Project, request: GenerateRequest
    ) -> Dict[str, Any]:
        """
        Generate synthetic training data for a project using DataSynthesizer.

        This implementation:
        1. Uses the core.synthesis module to generate examples
        2. Applies XML patterns and constraints
        3. Formats data according to dataset_format (sharegpt/alpaca)
        4. Saves to datasets directory
        """
        logger.info(f"Starting dataset generation for project: {project.name}")
        logger.info(f"Generating {request.num_examples} examples")

        # Create XML pattern from project
        xml_pattern = self._create_xml_pattern_from_project(project)

        # Create AI provider
        try:
            provider = self._create_ai_provider(project)
        except Exception as e:
            logger.error(f"Failed to create AI provider: {e}")
            raise

        # Validate provider connection
        logger.info("Validating AI provider connection...")
        if not provider.validate_connection():
            raise RuntimeError(f"Failed to connect to {project.ai_config.provider} provider")
        logger.info("AI provider connection validated")

        # Create generation config
        gen_config = GenerationConfig(
            mode=GenerationMode.PSEUDORANDOM,
            temperature=project.ai_config.temperature,
            max_tokens=project.ai_config.max_tokens,
            retry_attempts=3,
            batch_size=10,
            rate_limit_delay=0.5
        )

        # Initialize DataSynthesizer
        synthesizer = DataSynthesizer(
            provider=provider,
            xml_pattern=xml_pattern,
            config=gen_config
        )

        # Generate examples
        logger.info(f"Generating {request.num_examples} examples...")
        objectives = [project.objective for _ in range(request.num_examples)]

        try:
            examples = synthesizer.generate_batch(
                objectives=objectives,
                show_progress=True
            )
        except Exception as e:
            logger.error(f"Failed to generate examples: {e}")
            raise

        logger.info(f"Successfully generated {len(examples)} examples")

        # Generate timestamp-based filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{project.name}_{timestamp}_{len(examples)}ex.json"
        filepath = self.datasets_dir / filename

        # Save dataset in requested format
        try:
            save_dataset(
                data=examples,
                filepath=str(filepath),
                format_type=project.dataset_format
            )
            logger.info(f"Dataset saved to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save dataset: {e}")
            raise

        # Get statistics
        stats = synthesizer.get_stats()

        return {
            "filename": filename,
            "num_generated": len(examples),
            "format": project.dataset_format,
            "provider": project.ai_config.provider,
            "model": project.ai_config.model,
            "stats": stats
        }

    def analyze_dataset_size(
        self, project: Project, dataset_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze dataset size requirements using size_analyzer module.

        Args:
            project: Project configuration
            dataset_filename: Optional existing dataset to analyze

        Returns:
            Dictionary with size analysis results
        """
        logger.info(f"Analyzing dataset size requirements for project: {project.name}")

        # Create XML pattern from project
        xml_pattern = self._create_xml_pattern_from_project(project)

        # Determine finetuning strength from training config
        finetuning_strength = FinetuningStrength.MODERATE  # Default

        # Initialize analyzer
        analyzer = DatasetSizeAnalyzer(
            xml_pattern=xml_pattern,
            base_model=project.base_model,
            objective=project.objective,
            finetuning_strength=finetuning_strength,
            lora_rank=project.training_config.lora_r
        )

        # Get dataset path if provided
        dataset_path = None
        if dataset_filename:
            dataset_path = str(self.datasets_dir / dataset_filename)

        # Perform analysis
        try:
            report = analyzer.analyze(dataset_path=dataset_path)
            logger.info("Dataset size analysis complete")
            return report.to_dict()
        except Exception as e:
            logger.error(f"Failed to analyze dataset size: {e}")
            raise

    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all generated datasets."""
        datasets = []

        for dataset_file in self.datasets_dir.glob("*.json"):
            try:
                stat = dataset_file.stat()
                datasets.append(
                    {
                        "filename": dataset_file.name,
                        "size_bytes": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime),
                    }
                )
            except Exception as e:
                logger.error(f"Error reading dataset {dataset_file}: {e}")
                continue

        datasets.sort(key=lambda d: d["created_at"], reverse=True)
        return datasets
