"""
Service layer for model training operations.
"""
import uuid
import logging
import threading
from pathlib import Path
from typing import Dict, Optional, Callable
from datetime import datetime

from backend.schemas import Project, TrainRequest, TrainStatus
from core.training import (
    UnslothTrainer,
    LoRAConfig,
    TrainingConfig as CoreTrainingConfig,
    ResourceManager
)

logger = logging.getLogger(__name__)


class TrainingService:
    """Handles model training operations using UnslothTrainer."""

    def __init__(self, models_dir: str = "./models", datasets_dir: str = "./datasets"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True, parents=True)

        self.datasets_dir = Path(datasets_dir)
        self.datasets_dir.mkdir(exist_ok=True, parents=True)

        # In-memory job tracking (in production, use Redis or database)
        self.jobs: Dict[str, TrainStatus] = {}
        self.trainers: Dict[str, UnslothTrainer] = {}

        logger.info(f"TrainingService initialized with models_dir: {self.models_dir}")

    def _create_progress_callback(self, job_id: str) -> Callable:
        """Create a progress callback for tracking training progress."""

        def callback(progress_data: Dict):
            job = self.jobs.get(job_id)
            if job:
                job.current_step = progress_data.get("step", 0)
                job.total_steps = progress_data.get("total_steps")
                if "metrics" in progress_data:
                    # Store latest metrics
                    metrics = progress_data["metrics"]
                    if not hasattr(job, "metrics"):
                        job.metrics = {}
                    job.metrics.update(metrics)

                logger.info(f"Job {job_id}: Step {job.current_step}/{job.total_steps}")

        return callback

    def _run_training_job(
        self,
        job_id: str,
        project: Project,
        request: TrainRequest,
        output_dir: str
    ):
        """Run training job in a separate thread."""
        job = self.jobs[job_id]

        try:
            # Update job status
            job.status = "running"
            job.started_at = datetime.utcnow()

            logger.info(f"Starting training job {job_id}")
            logger.info(f"Base model: {project.base_model}")
            logger.info(f"Dataset: {request.dataset_filename}")
            logger.info(f"Output directory: {output_dir}")

            # Get dataset path
            dataset_path = str(self.datasets_dir / request.dataset_filename)

            if not Path(dataset_path).exists():
                raise FileNotFoundError(f"Dataset not found: {dataset_path}")

            # Create progress callback
            progress_callback = self._create_progress_callback(job_id)

            # Initialize UnslothTrainer
            trainer = UnslothTrainer(
                base_model=project.base_model,
                dataset_path=dataset_path,
                output_dir=output_dir,
                dataset_format=project.dataset_format,
                max_seq_length=project.training_config.max_seq_length,
                load_in_4bit=project.training_config.load_in_4bit,
                progress_callback=progress_callback
            )

            # Store trainer reference
            self.trainers[job_id] = trainer

            # Create LoRA config
            lora_config = LoRAConfig(
                rank=project.training_config.lora_r,
                alpha=project.training_config.lora_alpha,
                dropout=project.training_config.lora_dropout,
                target_modules=project.training_config.target_modules,
                use_gradient_checkpointing=True
            )

            # Create training config
            training_config = CoreTrainingConfig(
                learning_rate=project.training_config.learning_rate,
                batch_size=project.training_config.batch_size,
                gradient_accumulation_steps=project.training_config.gradient_accumulation_steps,
                num_epochs=project.training_config.num_train_epochs,
                warmup_steps=project.training_config.warmup_steps,
                max_seq_length=project.training_config.max_seq_length,
                logging_steps=project.training_config.logging_steps,
                save_steps=project.training_config.save_steps,
                fp16=project.training_config.fp16,
                bf16=project.training_config.bf16,
                optim=project.training_config.optimizer,
                weight_decay=project.training_config.weight_decay
            )

            # Setup and train
            trainer.setup(lora_config=lora_config)

            trainer.train(
                lora_config=lora_config,
                training_config=training_config
            )

            # Save model
            logger.info(f"Saving trained model for job {job_id}")
            trainer.save_model()

            # Export model if requested
            if request.export_format == "gguf":
                gguf_path = str(Path(output_dir) / f"{project.name}.gguf")
                logger.info(f"Exporting to GGUF format: {gguf_path}")
                trainer.export_gguf(gguf_path, quantization_method="q4_k_m")

            elif request.export_format == "ollama":
                logger.info(f"Exporting to Ollama format")
                trainer.export_to_ollama(project.name)

            # Update job status
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            logger.info(f"Training job {job_id} completed successfully")

            # Cleanup
            trainer.cleanup()

        except Exception as e:
            logger.error(f"Training job {job_id} failed: {e}", exc_info=True)
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            if not hasattr(job, "error"):
                job.error = str(e)

    def start_training(
        self, project: Project, request: TrainRequest
    ) -> Dict[str, str]:
        """
        Start a fine-tuning job using UnslothTrainer.

        This implementation:
        1. Loads the base model using Unsloth
        2. Loads and prepares the dataset
        3. Configures LoRA/QLoRA parameters
        4. Starts training in a background thread
        5. Tracks progress and metrics
        """
        job_id = str(uuid.uuid4())

        # Determine output directory
        output_dir = request.output_dir or str(
            self.models_dir / project.name / f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Create job status
        job_status = TrainStatus(
            job_id=job_id,
            status="pending",
            project_name=project.name,
            started_at=None,
            completed_at=None,
            current_epoch=0,
            total_epochs=project.training_config.num_train_epochs,
            current_step=0,
            total_steps=None,  # Will be calculated based on dataset size
            output_dir=output_dir,
        )

        self.jobs[job_id] = job_status

        # Start training in background thread
        training_thread = threading.Thread(
            target=self._run_training_job,
            args=(job_id, project, request, output_dir),
            daemon=True
        )
        training_thread.start()

        logger.info(f"Training job {job_id} started in background")
        logger.info(f"Project: {project.name}")
        logger.info(f"Dataset: {request.dataset_filename}")
        logger.info(f"Output: {output_dir}")

        return {"job_id": job_id}

    def get_training_status(self, job_id: str) -> Optional[TrainStatus]:
        """Get the status of a training job."""
        return self.jobs.get(job_id)

    def cancel_training(self, job_id: str) -> bool:
        """Cancel a running training job."""
        job = self.jobs.get(job_id)
        if not job:
            return False

        if job.status in ["running", "pending"]:
            job.status = "cancelled"
            job.completed_at = datetime.utcnow()

            # Cleanup trainer if exists
            trainer = self.trainers.get(job_id)
            if trainer:
                try:
                    trainer.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up trainer for job {job_id}: {e}")

            logger.info(f"Training job {job_id} cancelled")
            return True

        return False

    def list_jobs(self, project_name: Optional[str] = None) -> list[TrainStatus]:
        """List all training jobs, optionally filtered by project."""
        jobs = list(self.jobs.values())

        if project_name:
            jobs = [j for j in jobs if j.project_name == project_name]

        jobs.sort(
            key=lambda j: j.started_at or datetime.utcnow(), reverse=True
        )
        return jobs
