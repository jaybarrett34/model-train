#!/usr/bin/env python3
"""
Integration Test Script for Model Training Pipeline

This script tests the full pipeline:
1. Project Creation → XML Pattern Definition
2. Dataset Generation → Training Data Synthesis
3. Training → Model Fine-tuning
4. Export → Model Export (optional)

Usage:
    python test_integration.py [--skip-generation] [--skip-training] [--provider ollama|anthropic|openai]
"""

import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.schemas import (
    Project,
    ProjectCreate,
    XMLPattern,
    AIConfig,
    TrainingConfig,
    GenerateRequest,
    TrainRequest
)
from backend.services.generation_service import GenerationService
from backend.services.training_service import TrainingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTest:
    """Integration test runner for the model training pipeline."""

    def __init__(self, test_dir: str = "./test_output"):
        self.test_dir = Path(test_dir)
        self.test_dir.mkdir(exist_ok=True)

        self.datasets_dir = self.test_dir / "datasets"
        self.datasets_dir.mkdir(exist_ok=True)

        self.models_dir = self.test_dir / "models"
        self.models_dir.mkdir(exist_ok=True)

        self.generation_service = GenerationService(datasets_dir=str(self.datasets_dir))
        self.training_service = TrainingService(
            models_dir=str(self.models_dir),
            datasets_dir=str(self.datasets_dir)
        )

        self.results = {
            "test_start": datetime.utcnow().isoformat(),
            "phases": {}
        }

    def create_test_project(self, provider: str = "ollama") -> Project:
        """Create a test project for Minecraft assistant."""
        logger.info("=" * 80)
        logger.info("PHASE 1: Creating Test Project")
        logger.info("=" * 80)

        # Define XML patterns for Minecraft assistant
        xml_patterns = [
            XMLPattern(
                tag_name="think",
                description="Internal reasoning and analysis before taking action",
                constraints="Should describe the reasoning process and goal understanding",
                examples=["I need to help the player find diamonds at Y-level -59"]
            ),
            XMLPattern(
                tag_name="command",
                description="Minecraft command to execute",
                constraints="Must be valid Minecraft command syntax",
                examples=["/tp @p ~ -59 ~", "/give @p minecraft:diamond 1"]
            ),
            XMLPattern(
                tag_name="speak",
                description="Message to speak to the player",
                constraints="Should be helpful and friendly",
                examples=["I'll teleport you to diamond mining level!", "Here's a diamond for you!"]
            )
        ]

        # AI configuration
        ai_config = AIConfig(
            provider=provider,
            model="llama2" if provider == "ollama" else "claude-sonnet-4-5-20250929" if provider == "anthropic" else "gpt-4",
            temperature=0.8,
            max_tokens=1024,
            base_url="http://localhost:11434" if provider == "ollama" else None
        )

        # Training configuration (lightweight for testing)
        training_config = TrainingConfig(
            max_seq_length=512,  # Shorter for faster testing
            load_in_4bit=True,
            lora_r=8,  # Smaller rank for faster testing
            lora_alpha=16,
            batch_size=1,  # Minimal batch size
            gradient_accumulation_steps=2,
            learning_rate=2e-4,
            num_train_epochs=1,  # Just 1 epoch for testing
            warmup_steps=2,
            logging_steps=1,
            save_steps=50
        )

        # Create project
        project = Project(
            name="minecraft-assistant-test",
            objective="Train a Minecraft assistant that responds with thinking, commands, and speech in XML format",
            xml_patterns=xml_patterns,
            dataset_format="sharegpt",
            base_model="unsloth/llama-2-7b-bnb-4bit",  # Lightweight model for testing
            ai_config=ai_config,
            training_config=training_config
        )

        logger.info(f"Project created: {project.name}")
        logger.info(f"Objective: {project.objective}")
        logger.info(f"XML Patterns: {len(project.xml_patterns)}")
        logger.info(f"Provider: {provider}")

        self.results["phases"]["project_creation"] = {
            "status": "success",
            "project_name": project.name,
            "provider": provider
        }

        return project

    def test_dataset_generation(self, project: Project, num_examples: int = 5) -> str:
        """Test dataset generation."""
        logger.info("")
        logger.info("=" * 80)
        logger.info("PHASE 2: Testing Dataset Generation")
        logger.info("=" * 80)

        start_time = time.time()

        try:
            request = GenerateRequest(num_examples=num_examples)

            logger.info(f"Generating {num_examples} examples...")
            result = self.generation_service.generate_dataset(project, request)

            elapsed = time.time() - start_time

            logger.info(f"Dataset generation completed in {elapsed:.2f}s")
            logger.info(f"Filename: {result['filename']}")
            logger.info(f"Examples generated: {result['num_generated']}")
            logger.info(f"Format: {result['format']}")
            logger.info(f"Provider stats: {result.get('stats', {})}")

            self.results["phases"]["dataset_generation"] = {
                "status": "success",
                "filename": result['filename'],
                "num_examples": result['num_generated'],
                "elapsed_time": elapsed,
                "stats": result.get('stats', {})
            }

            return result['filename']

        except Exception as e:
            logger.error(f"Dataset generation failed: {e}", exc_info=True)
            self.results["phases"]["dataset_generation"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    def test_dataset_analysis(self, project: Project, dataset_filename: str):
        """Test dataset size analysis."""
        logger.info("")
        logger.info("=" * 80)
        logger.info("PHASE 3: Testing Dataset Size Analysis")
        logger.info("=" * 80)

        try:
            analysis = self.generation_service.analyze_dataset_size(
                project, dataset_filename
            )

            logger.info("Dataset Size Analysis Results:")
            logger.info(f"  Current Size: {analysis['current_size']}")
            logger.info(f"  Recommended Minimum: {analysis['size_estimates']['minimum']}")
            logger.info(f"  Optimal Size: {analysis['size_estimates']['optimal']}")
            logger.info(f"  Adequacy Status: {analysis['adequacy_status']}")
            logger.info(f"  Complexity Level: {analysis['complexity_analysis']['complexity_level']}")

            self.results["phases"]["dataset_analysis"] = {
                "status": "success",
                "analysis": analysis
            }

        except Exception as e:
            logger.error(f"Dataset analysis failed: {e}", exc_info=True)
            self.results["phases"]["dataset_analysis"] = {
                "status": "failed",
                "error": str(e)
            }

    def test_training(self, project: Project, dataset_filename: str) -> str:
        """Test model training."""
        logger.info("")
        logger.info("=" * 80)
        logger.info("PHASE 4: Testing Model Training")
        logger.info("=" * 80)

        start_time = time.time()

        try:
            request = TrainRequest(
                dataset_filename=dataset_filename,
                export_format=None  # Skip export for faster testing
            )

            logger.info("Starting training job...")
            result = self.training_service.start_training(project, request)
            job_id = result["job_id"]

            logger.info(f"Training job started: {job_id}")

            # Monitor training progress
            logger.info("Monitoring training progress...")
            last_status = None

            while True:
                status = self.training_service.get_training_status(job_id)

                if status and status.status != last_status:
                    logger.info(f"Status: {status.status}")
                    if status.status == "running":
                        logger.info(f"  Step: {status.current_step}/{status.total_steps}")
                    last_status = status.status

                if status and status.status in ["completed", "failed", "cancelled"]:
                    break

                time.sleep(5)  # Check every 5 seconds

            elapsed = time.time() - start_time

            if status.status == "completed":
                logger.info(f"Training completed successfully in {elapsed:.2f}s")
                logger.info(f"Output directory: {status.output_dir}")

                self.results["phases"]["training"] = {
                    "status": "success",
                    "job_id": job_id,
                    "output_dir": status.output_dir,
                    "elapsed_time": elapsed
                }

                return job_id

            else:
                error = getattr(status, "error", "Unknown error")
                logger.error(f"Training failed: {error}")
                self.results["phases"]["training"] = {
                    "status": "failed",
                    "job_id": job_id,
                    "error": error
                }
                raise RuntimeError(f"Training failed: {error}")

        except Exception as e:
            logger.error(f"Training test failed: {e}", exc_info=True)
            self.results["phases"]["training"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    def save_results(self):
        """Save test results to JSON file."""
        self.results["test_end"] = datetime.utcnow().isoformat()

        results_file = self.test_dir / f"integration_test_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        logger.info("")
        logger.info(f"Test results saved to: {results_file}")

    def run_full_pipeline(
        self,
        provider: str = "ollama",
        skip_generation: bool = False,
        skip_training: bool = False,
        num_examples: int = 5
    ):
        """Run the full integration test pipeline."""
        logger.info("=" * 80)
        logger.info("STARTING FULL PIPELINE INTEGRATION TEST")
        logger.info("=" * 80)
        logger.info(f"Test Directory: {self.test_dir}")
        logger.info(f"Provider: {provider}")
        logger.info(f"Skip Generation: {skip_generation}")
        logger.info(f"Skip Training: {skip_training}")
        logger.info("")

        try:
            # Phase 1: Create project
            project = self.create_test_project(provider=provider)

            # Phase 2: Generate dataset
            dataset_filename = None
            if not skip_generation:
                dataset_filename = self.test_dataset_generation(project, num_examples=num_examples)

                # Phase 3: Analyze dataset
                self.test_dataset_analysis(project, dataset_filename)
            else:
                logger.info("Skipping dataset generation (using existing dataset)")
                # Use the most recent dataset
                datasets = self.generation_service.list_datasets()
                if datasets:
                    dataset_filename = datasets[0]["filename"]
                    logger.info(f"Using existing dataset: {dataset_filename}")
                else:
                    raise RuntimeError("No existing dataset found and generation was skipped")

            # Phase 4: Train model
            if not skip_training:
                self.test_training(project, dataset_filename)
            else:
                logger.info("Skipping training phase")

            # Save results
            self.save_results()

            logger.info("")
            logger.info("=" * 80)
            logger.info("INTEGRATION TEST COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Integration test failed: {e}", exc_info=True)
            self.save_results()
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run integration tests for model training pipeline")
    parser.add_argument(
        "--provider",
        choices=["ollama", "anthropic", "openai"],
        default="ollama",
        help="AI provider to use for data generation"
    )
    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Skip dataset generation (use existing dataset)"
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip training phase"
    )
    parser.add_argument(
        "--num-examples",
        type=int,
        default=5,
        help="Number of examples to generate (default: 5)"
    )
    parser.add_argument(
        "--test-dir",
        default="./test_output",
        help="Directory for test outputs (default: ./test_output)"
    )

    args = parser.parse_args()

    # Check for required API keys
    if args.provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    if args.provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    # Run integration test
    test = IntegrationTest(test_dir=args.test_dir)
    test.run_full_pipeline(
        provider=args.provider,
        skip_generation=args.skip_generation,
        skip_training=args.skip_training,
        num_examples=args.num_examples
    )


if __name__ == "__main__":
    main()
