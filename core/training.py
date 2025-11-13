"""
Unsloth Fine-tuning Integration for Language Models

This module provides a comprehensive training pipeline for fine-tuning large language models
using Unsloth's optimized FastLanguageModel and QLoRA (Quantized Low-Rank Adaptation).

Key Features:
- Support for multiple model architectures (Llama, Qwen, Mistral, Gemma, etc.)
- 4-bit quantization for memory efficiency
- QLoRA parameter-efficient fine-tuning
- Multiple dataset formats (ShareGPT, Alpaca)
- Progress tracking and monitoring
- Multiple export formats (HuggingFace, GGUF, adapter-only)
- GPU and Mac M4 MPS backend support
"""

import os
import json
import torch
from typing import Optional, Dict, List, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class LoRAConfig:
    """
    Configuration for LoRA (Low-Rank Adaptation) parameters.

    Attributes:
        rank: The rank of the LoRA matrices (default: 16)
        alpha: The scaling parameter for LoRA (default: 16)
        dropout: Dropout probability for LoRA layers (default: 0.0)
        target_modules: List of module names to apply LoRA to
        bias: Bias training strategy ('none', 'all', 'lora_only')
        use_gradient_checkpointing: Enable gradient checkpointing to save memory
        use_rslora: Use Rank-Stabilized LoRA
        use_dora: Use Weight-Decomposed Low-Rank Adaptation
    """
    rank: int = 16
    alpha: int = 16
    dropout: float = 0.0
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])
    bias: str = "none"
    use_gradient_checkpointing: bool = True
    use_rslora: bool = False
    use_dora: bool = False


@dataclass
class TrainingConfig:
    """
    Configuration for the training process.

    Attributes:
        learning_rate: Learning rate for the optimizer (default: 2e-4)
        batch_size: Training batch size per device (default: 2)
        gradient_accumulation_steps: Number of gradient accumulation steps (default: 4)
        max_steps: Maximum number of training steps (default: None for epoch-based)
        num_epochs: Number of training epochs (default: 1)
        warmup_steps: Number of warmup steps for learning rate scheduler (default: 5)
        max_seq_length: Maximum sequence length for training (default: 2048)
        weight_decay: Weight decay for regularization (default: 0.01)
        logging_steps: Log metrics every N steps (default: 1)
        save_steps: Save checkpoint every N steps (default: 100)
        eval_steps: Evaluate every N steps (default: None for no evaluation)
        fp16: Use FP16 mixed precision (default: False)
        bf16: Use BF16 mixed precision (default: False)
        optim: Optimizer name (default: "adamw_8bit")
        lr_scheduler_type: Learning rate scheduler type (default: "linear")
        seed: Random seed for reproducibility (default: 42)
    """
    learning_rate: float = 2e-4
    batch_size: int = 2
    gradient_accumulation_steps: int = 4
    max_steps: Optional[int] = None
    num_epochs: int = 1
    warmup_steps: int = 5
    max_seq_length: int = 2048
    weight_decay: float = 0.01
    logging_steps: int = 1
    save_steps: int = 100
    eval_steps: Optional[int] = None
    fp16: bool = False
    bf16: bool = False
    optim: str = "adamw_8bit"
    lr_scheduler_type: str = "linear"
    seed: int = 42


class ResourceManager:
    """
    Manages GPU/MPS resources and memory optimization.

    This class detects available compute devices (CUDA, MPS, CPU) and provides
    utilities for memory management and device allocation.
    """

    def __init__(self):
        """Initialize resource manager and detect available devices."""
        self.device = self._detect_device()
        self.device_name = self._get_device_name()
        logger.info(f"Detected device: {self.device_name}")

    @staticmethod
    def _detect_device() -> str:
        """
        Detect the best available compute device.

        Returns:
            Device string: 'cuda', 'mps', or 'cpu'
        """
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def _get_device_name(self) -> str:
        """
        Get the name of the compute device.

        Returns:
            Human-readable device name
        """
        if self.device == "cuda":
            return f"CUDA ({torch.cuda.get_device_name(0)})"
        elif self.device == "mps":
            return "Apple MPS (Metal Performance Shaders)"
        else:
            return "CPU"

    def get_memory_stats(self) -> Dict[str, float]:
        """
        Get current memory usage statistics.

        Returns:
            Dictionary with memory statistics in GB
        """
        stats = {}

        if self.device == "cuda":
            stats["allocated"] = torch.cuda.memory_allocated() / 1024**3
            stats["reserved"] = torch.cuda.memory_reserved() / 1024**3
            stats["max_allocated"] = torch.cuda.max_memory_allocated() / 1024**3
        elif self.device == "mps":
            stats["allocated"] = torch.mps.current_allocated_memory() / 1024**3 if hasattr(torch.mps, "current_allocated_memory") else 0.0
            stats["driver_allocated"] = torch.mps.driver_allocated_memory() / 1024**3 if hasattr(torch.mps, "driver_allocated_memory") else 0.0
        else:
            stats["info"] = "CPU mode - no GPU memory tracking"

        return stats

    def clear_cache(self):
        """Clear GPU memory cache."""
        if self.device == "cuda":
            torch.cuda.empty_cache()
            logger.info("Cleared CUDA cache")
        elif self.device == "mps":
            if hasattr(torch.mps, "empty_cache"):
                torch.mps.empty_cache()
                logger.info("Cleared MPS cache")

    def log_memory_stats(self):
        """Log current memory statistics."""
        stats = self.get_memory_stats()
        logger.info(f"Memory stats: {stats}")


def load_model_with_unsloth(
    model_name: str,
    max_seq_length: int = 2048,
    load_in_4bit: bool = True,
    dtype: Optional[torch.dtype] = None,
    **kwargs
) -> tuple:
    """
    Load a model from HuggingFace using Unsloth's FastLanguageModel.

    This function loads pre-trained language models with optional 4-bit quantization
    for memory efficiency. It supports various model architectures including Llama,
    Qwen, Mistral, Gemma, and more.

    Args:
        model_name: HuggingFace model name or path (e.g., "unsloth/qwen2.5-14b-instruct-bnb-4bit")
        max_seq_length: Maximum sequence length for the model (default: 2048)
        load_in_4bit: Whether to load the model in 4-bit quantization (default: True)
        dtype: Data type for the model (None for auto-detection, torch.float16, torch.bfloat16)
        **kwargs: Additional arguments to pass to FastLanguageModel.from_pretrained

    Returns:
        Tuple of (model, tokenizer)

    Example:
        >>> model, tokenizer = load_model_with_unsloth(
        ...     "unsloth/qwen2.5-14b-instruct-bnb-4bit",
        ...     max_seq_length=2048
        ... )
    """
    try:
        from unsloth import FastLanguageModel
    except ImportError:
        raise ImportError(
            "Unsloth is not installed. Install it with: pip install unsloth"
        )

    logger.info(f"Loading model: {model_name}")
    logger.info(f"Max sequence length: {max_seq_length}")
    logger.info(f"4-bit quantization: {load_in_4bit}")

    # Auto-detect dtype if not specified
    if dtype is None:
        if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
            dtype = torch.bfloat16
        else:
            dtype = torch.float16

    logger.info(f"Using dtype: {dtype}")

    # Load model and tokenizer
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
        dtype=dtype,
        **kwargs
    )

    logger.info(f"Successfully loaded model: {model_name}")
    logger.info(f"Model class: {model.__class__.__name__}")

    return model, tokenizer


def configure_lora_adapters(
    model,
    lora_config: LoRAConfig
):
    """
    Configure LoRA adapters for the model using Unsloth's PEFT implementation.

    This function applies Low-Rank Adaptation (LoRA) to specified modules in the model,
    enabling parameter-efficient fine-tuning. It supports various LoRA variants including
    standard LoRA, RSLoRA, and DoRA.

    Args:
        model: The base language model to add LoRA adapters to
        lora_config: LoRAConfig object with LoRA parameters

    Returns:
        Model with LoRA adapters configured

    Example:
        >>> lora_config = LoRAConfig(rank=16, alpha=16)
        >>> model = configure_lora_adapters(model, lora_config)
    """
    try:
        from unsloth import FastLanguageModel
    except ImportError:
        raise ImportError(
            "Unsloth is not installed. Install it with: pip install unsloth"
        )

    logger.info("Configuring LoRA adapters")
    logger.info(f"LoRA rank: {lora_config.rank}")
    logger.info(f"LoRA alpha: {lora_config.alpha}")
    logger.info(f"Target modules: {lora_config.target_modules}")
    logger.info(f"Dropout: {lora_config.dropout}")
    logger.info(f"Use RSLoRA: {lora_config.use_rslora}")
    logger.info(f"Use DoRA: {lora_config.use_dora}")

    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_config.rank,
        lora_alpha=lora_config.alpha,
        lora_dropout=lora_config.dropout,
        target_modules=lora_config.target_modules,
        bias=lora_config.bias,
        use_gradient_checkpointing=lora_config.use_gradient_checkpointing,
        use_rslora=lora_config.use_rslora,
        use_dora=lora_config.use_dora,
    )

    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_percentage = 100 * trainable_params / total_params

    logger.info(f"Trainable parameters: {trainable_params:,}")
    logger.info(f"Total parameters: {total_params:,}")
    logger.info(f"Trainable: {trainable_percentage:.2f}%")

    return model


def load_dataset(
    dataset_path: str,
    tokenizer,
    format_type: str = "sharegpt",
    max_seq_length: int = 2048
):
    """
    Load and format dataset for training.

    This function loads datasets in various formats (ShareGPT, Alpaca) and prepares
    them for fine-tuning with proper formatting and tokenization.

    Args:
        dataset_path: Path to the dataset file (JSONL or JSON)
        tokenizer: The tokenizer to use for formatting
        format_type: Dataset format ('sharegpt' or 'alpaca')
        max_seq_length: Maximum sequence length for truncation

    Returns:
        Formatted dataset ready for training

    Supported formats:
        - ShareGPT: {"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}
        - Alpaca: {"instruction": "...", "input": "...", "output": "..."}

    Example:
        >>> dataset = load_dataset(
        ...     "datasets/my_data.jsonl",
        ...     tokenizer,
        ...     format_type="sharegpt"
        ... )
    """
    from datasets import load_dataset as hf_load_dataset

    logger.info(f"Loading dataset from: {dataset_path}")
    logger.info(f"Format type: {format_type}")

    # Determine file extension
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    # Load dataset based on file type
    if path.suffix == ".jsonl":
        dataset = hf_load_dataset("json", data_files=dataset_path, split="train")
    elif path.suffix == ".json":
        dataset = hf_load_dataset("json", data_files=dataset_path, split="train")
    else:
        # Try to load as a HuggingFace dataset
        dataset = hf_load_dataset(dataset_path, split="train")

    logger.info(f"Loaded {len(dataset)} examples")

    # Apply formatting based on format type
    if format_type == "sharegpt":
        try:
            from unsloth.chat_templates import get_chat_template

            # Apply chat template
            tokenizer = get_chat_template(
                tokenizer,
                chat_template="chatml",  # Can be customized
            )

            def format_sharegpt(examples):
                texts = []
                for convo in examples["conversations"]:
                    text = tokenizer.apply_chat_template(
                        convo,
                        tokenize=False,
                        add_generation_prompt=False
                    )
                    texts.append(text)
                return {"text": texts}

            dataset = dataset.map(format_sharegpt, batched=True)

        except ImportError:
            logger.warning("Unsloth chat templates not available, using basic formatting")

    elif format_type == "alpaca":
        def format_alpaca(example):
            instruction = example.get("instruction", "")
            input_text = example.get("input", "")
            output = example.get("output", "")

            if input_text:
                text = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
            else:
                text = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"

            return {"text": text}

        dataset = dataset.map(format_alpaca)

    logger.info("Dataset formatting complete")
    return dataset


class ProgressTracker:
    """
    Tracks and reports training progress.

    This class monitors training metrics such as loss, steps completed, and estimated
    time remaining. It can emit progress updates via callbacks.
    """

    def __init__(self, total_steps: int, callback: Optional[Callable] = None):
        """
        Initialize progress tracker.

        Args:
            total_steps: Total number of training steps
            callback: Optional callback function for progress updates
        """
        self.total_steps = total_steps
        self.callback = callback
        self.start_time = None
        self.current_step = 0
        self.metrics_history = []

    def start(self):
        """Start tracking progress."""
        self.start_time = datetime.now()
        logger.info(f"Training started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def update(self, step: int, metrics: Dict[str, float]):
        """
        Update progress with current step and metrics.

        Args:
            step: Current training step
            metrics: Dictionary of metrics (e.g., {'loss': 0.5, 'learning_rate': 2e-4})
        """
        self.current_step = step
        self.metrics_history.append({"step": step, **metrics})

        # Calculate progress
        progress_pct = (step / self.total_steps) * 100 if self.total_steps > 0 else 0

        # Estimate time remaining
        eta_str = "N/A"
        if self.start_time and step > 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            steps_per_second = step / elapsed
            remaining_steps = self.total_steps - step
            eta_seconds = remaining_steps / steps_per_second if steps_per_second > 0 else 0
            eta_str = self._format_time(eta_seconds)

        # Build progress message
        metrics_str = ", ".join([f"{k}: {v:.4f}" for k, v in metrics.items()])
        progress_msg = (
            f"Step {step}/{self.total_steps} ({progress_pct:.1f}%) - "
            f"{metrics_str} - ETA: {eta_str}"
        )

        logger.info(progress_msg)

        # Call callback if provided
        if self.callback:
            self.callback({
                "step": step,
                "total_steps": self.total_steps,
                "progress_pct": progress_pct,
                "eta": eta_str,
                "metrics": metrics
            })

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds into human-readable time string."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def finish(self):
        """Mark training as finished and log final statistics."""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"Training completed in {self._format_time(elapsed)}")

            if self.metrics_history:
                final_loss = self.metrics_history[-1].get("loss", "N/A")
                logger.info(f"Final loss: {final_loss}")


class UnslothTrainer:
    """
    Main training class for fine-tuning models with Unsloth.

    This class orchestrates the entire training pipeline including model loading,
    LoRA configuration, dataset preparation, training execution, and model export.

    Example:
        >>> trainer = UnslothTrainer(
        ...     base_model="unsloth/qwen2.5-14b-instruct-bnb-4bit",
        ...     dataset_path="datasets/my_data.jsonl",
        ...     output_dir="models/my_model"
        ... )
        >>> trainer.train(lora_rank=16, max_steps=100)
        >>> trainer.save_model()
        >>> trainer.export_gguf("models/my_model.gguf")
    """

    def __init__(
        self,
        base_model: str,
        dataset_path: str,
        output_dir: str,
        dataset_format: str = "sharegpt",
        max_seq_length: int = 2048,
        load_in_4bit: bool = True,
        progress_callback: Optional[Callable] = None
    ):
        """
        Initialize UnslothTrainer.

        Args:
            base_model: HuggingFace model name or path
            dataset_path: Path to training dataset
            output_dir: Directory to save trained model
            dataset_format: Format of dataset ('sharegpt' or 'alpaca')
            max_seq_length: Maximum sequence length
            load_in_4bit: Whether to use 4-bit quantization
            progress_callback: Optional callback for progress updates
        """
        self.base_model = base_model
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.dataset_format = dataset_format
        self.max_seq_length = max_seq_length
        self.load_in_4bit = load_in_4bit
        self.progress_callback = progress_callback

        # Initialize components
        self.resource_manager = ResourceManager()
        self.model = None
        self.tokenizer = None
        self.dataset = None
        self.trainer = None
        self.progress_tracker = None

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

    def setup(self, lora_config: Optional[LoRAConfig] = None):
        """
        Set up the model, tokenizer, and dataset.

        Args:
            lora_config: Optional LoRAConfig (uses defaults if not provided)
        """
        # Use default config if not provided
        if lora_config is None:
            lora_config = LoRAConfig()

        # Load model and tokenizer
        self.model, self.tokenizer = load_model_with_unsloth(
            model_name=self.base_model,
            max_seq_length=self.max_seq_length,
            load_in_4bit=self.load_in_4bit
        )

        # Configure LoRA adapters
        self.model = configure_lora_adapters(self.model, lora_config)

        # Load dataset
        self.dataset = load_dataset(
            dataset_path=self.dataset_path,
            tokenizer=self.tokenizer,
            format_type=self.dataset_format,
            max_seq_length=self.max_seq_length
        )

        logger.info("Setup complete")
        self.resource_manager.log_memory_stats()

    def train(
        self,
        lora_rank: int = 16,
        lora_alpha: int = 16,
        learning_rate: float = 2e-4,
        batch_size: int = 2,
        gradient_accumulation_steps: int = 4,
        max_steps: Optional[int] = None,
        num_epochs: int = 1,
        warmup_steps: int = 5,
        training_config: Optional[TrainingConfig] = None,
        lora_config: Optional[LoRAConfig] = None
    ):
        """
        Execute the training process.

        Args:
            lora_rank: LoRA rank (ignored if lora_config provided)
            lora_alpha: LoRA alpha (ignored if lora_config provided)
            learning_rate: Learning rate (ignored if training_config provided)
            batch_size: Batch size (ignored if training_config provided)
            gradient_accumulation_steps: Gradient accumulation steps
            max_steps: Maximum training steps
            num_epochs: Number of epochs
            warmup_steps: Warmup steps
            training_config: Optional TrainingConfig object
            lora_config: Optional LoRAConfig object
        """
        try:
            from transformers import TrainingArguments
            from trl import SFTTrainer
        except ImportError:
            raise ImportError(
                "Required packages not installed. Install with: "
                "pip install transformers trl"
            )

        # Create configs if not provided
        if lora_config is None:
            lora_config = LoRAConfig(rank=lora_rank, alpha=lora_alpha)

        if training_config is None:
            training_config = TrainingConfig(
                learning_rate=learning_rate,
                batch_size=batch_size,
                gradient_accumulation_steps=gradient_accumulation_steps,
                max_steps=max_steps,
                num_epochs=num_epochs,
                warmup_steps=warmup_steps
            )

        # Setup if not already done
        if self.model is None:
            self.setup(lora_config)

        # Calculate total steps
        if training_config.max_steps:
            total_steps = training_config.max_steps
        else:
            steps_per_epoch = len(self.dataset) // (
                training_config.batch_size * training_config.gradient_accumulation_steps
            )
            total_steps = steps_per_epoch * training_config.num_epochs

        # Initialize progress tracker
        self.progress_tracker = ProgressTracker(
            total_steps=total_steps,
            callback=self.progress_callback
        )

        # Prepare training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            per_device_train_batch_size=training_config.batch_size,
            gradient_accumulation_steps=training_config.gradient_accumulation_steps,
            warmup_steps=training_config.warmup_steps,
            max_steps=training_config.max_steps if training_config.max_steps else -1,
            num_train_epochs=training_config.num_epochs if not training_config.max_steps else 1,
            learning_rate=training_config.learning_rate,
            fp16=training_config.fp16 if self.resource_manager.device == "cuda" else False,
            bf16=training_config.bf16 if self.resource_manager.device == "cuda" else False,
            logging_steps=training_config.logging_steps,
            optim=training_config.optim,
            weight_decay=training_config.weight_decay,
            lr_scheduler_type=training_config.lr_scheduler_type,
            seed=training_config.seed,
            save_steps=training_config.save_steps,
            save_total_limit=3,
            report_to="none",  # Disable default reporting
        )

        # Initialize trainer
        self.trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=self.dataset,
            dataset_text_field="text",
            max_seq_length=self.max_seq_length,
            args=training_args,
        )

        # Start training
        logger.info("Starting training...")
        self.progress_tracker.start()

        # Add callback for progress tracking
        from transformers import TrainerCallback

        class ProgressCallback(TrainerCallback):
            def __init__(self, tracker):
                self.tracker = tracker

            def on_log(self, args, state, control, logs=None, **kwargs):
                if logs:
                    self.tracker.update(state.global_step, logs)

        self.trainer.add_callback(ProgressCallback(self.progress_tracker))

        # Train
        self.trainer.train()

        # Finish tracking
        self.progress_tracker.finish()
        self.resource_manager.log_memory_stats()

        logger.info("Training complete!")

    def save_model(self, adapter_only: bool = False):
        """
        Save the trained model.

        Args:
            adapter_only: If True, save only LoRA adapters (smaller size)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call setup() or train() first.")

        save_path = os.path.join(self.output_dir, "adapter" if adapter_only else "model")

        logger.info(f"Saving {'adapter' if adapter_only else 'model'} to: {save_path}")

        if adapter_only:
            self.model.save_pretrained(save_path)
            self.tokenizer.save_pretrained(save_path)
        else:
            self.model.save_pretrained(save_path)
            self.tokenizer.save_pretrained(save_path)

        logger.info("Model saved successfully")

    def save_merged_model(self, save_path: Optional[str] = None):
        """
        Save the model with LoRA adapters merged into base weights.

        This creates a standalone model that doesn't require LoRA adapters at inference time.

        Args:
            save_path: Path to save merged model (uses output_dir/merged if not provided)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call setup() or train() first.")

        if save_path is None:
            save_path = os.path.join(self.output_dir, "merged")

        logger.info(f"Merging LoRA adapters and saving to: {save_path}")

        try:
            from unsloth import FastLanguageModel

            # Save merged model
            self.model.save_pretrained_merged(
                save_path,
                self.tokenizer,
                save_method="merged_16bit"
            )

            logger.info("Merged model saved successfully")

        except Exception as e:
            logger.error(f"Error saving merged model: {e}")
            # Fallback to regular save
            logger.info("Falling back to regular save...")
            self.model.save_pretrained(save_path)
            self.tokenizer.save_pretrained(save_path)

    def export_gguf(
        self,
        output_path: str,
        quantization_method: str = "q4_k_m",
        merged: bool = True
    ):
        """
        Export the model to GGUF format for Ollama/llama.cpp.

        GGUF is a binary format optimized for CPU and Metal inference, commonly used
        with Ollama and llama.cpp for running models locally.

        Args:
            output_path: Path for the output GGUF file
            quantization_method: Quantization method (e.g., 'q4_k_m', 'q5_k_m', 'q8_0')
            merged: Whether to merge LoRA adapters before export

        Available quantization methods:
            - q4_k_m: 4-bit medium quality (recommended, good balance)
            - q5_k_m: 5-bit medium quality (better quality, larger size)
            - q8_0: 8-bit (high quality, large size)
            - f16: 16-bit float (highest quality, largest size)

        Example:
            >>> trainer.export_gguf("models/my_model.gguf", quantization_method="q4_k_m")
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call setup() or train() first.")

        logger.info(f"Exporting to GGUF format: {output_path}")
        logger.info(f"Quantization method: {quantization_method}")

        try:
            from unsloth import FastLanguageModel

            # Save as GGUF
            self.model.save_pretrained_gguf(
                output_path,
                self.tokenizer,
                quantization_method=quantization_method
            )

            logger.info(f"GGUF export complete: {output_path}")

        except Exception as e:
            logger.error(f"Error exporting to GGUF: {e}")
            logger.info("Make sure llama.cpp is installed for GGUF export")
            raise

    def export_to_ollama(
        self,
        model_name: str,
        quantization_method: str = "q4_k_m",
        modelfile_template: Optional[str] = None
    ):
        """
        Export model to Ollama format and create a Modelfile.

        This function exports the model to GGUF format and creates an Ollama Modelfile
        for easy local deployment.

        Args:
            model_name: Name for the Ollama model (e.g., 'my-assistant')
            quantization_method: Quantization method for GGUF
            modelfile_template: Optional custom Modelfile template

        Example:
            >>> trainer.export_to_ollama("my-assistant")
            >>> # Then run: ollama create my-assistant -f models/Modelfile
        """
        # Export to GGUF
        gguf_path = os.path.join(self.output_dir, f"{model_name}.gguf")
        self.export_gguf(gguf_path, quantization_method=quantization_method)

        # Create Modelfile
        modelfile_path = os.path.join(self.output_dir, "Modelfile")

        if modelfile_template is None:
            modelfile_content = f"""FROM {gguf_path}

# Model parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 2048

# System prompt (customize as needed)
SYSTEM You are a helpful AI assistant.
"""
        else:
            modelfile_content = modelfile_template.format(gguf_path=gguf_path)

        with open(modelfile_path, "w") as f:
            f.write(modelfile_content)

        logger.info(f"Modelfile created: {modelfile_path}")
        logger.info(f"To create Ollama model, run:")
        logger.info(f"  ollama create {model_name} -f {modelfile_path}")

    def cleanup(self):
        """Clean up resources and free memory."""
        logger.info("Cleaning up resources...")

        if self.model is not None:
            del self.model
            self.model = None

        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None

        if self.dataset is not None:
            del self.dataset
            self.dataset = None

        if self.trainer is not None:
            del self.trainer
            self.trainer = None

        self.resource_manager.clear_cache()
        logger.info("Cleanup complete")


def create_quick_trainer(
    model_name: str,
    dataset_path: str,
    output_dir: str,
    **kwargs
) -> UnslothTrainer:
    """
    Quick helper function to create a trainer with sensible defaults.

    Args:
        model_name: HuggingFace model name
        dataset_path: Path to dataset
        output_dir: Output directory
        **kwargs: Additional arguments for UnslothTrainer

    Returns:
        Configured UnslothTrainer instance

    Example:
        >>> trainer = create_quick_trainer(
        ...     "unsloth/qwen2.5-14b-instruct-bnb-4bit",
        ...     "data.jsonl",
        ...     "output"
        ... )
        >>> trainer.train(max_steps=100)
    """
    return UnslothTrainer(
        base_model=model_name,
        dataset_path=dataset_path,
        output_dir=output_dir,
        **kwargs
    )


# Example usage
if __name__ == "__main__":
    # Example: Fine-tune a model
    trainer = UnslothTrainer(
        base_model="unsloth/qwen2.5-14b-instruct-bnb-4bit",
        dataset_path="datasets/my_data.jsonl",
        output_dir="models/my_model"
    )

    # Train with custom parameters
    trainer.train(
        lora_rank=16,
        lora_alpha=16,
        learning_rate=2e-4,
        batch_size=2,
        max_steps=100
    )

    # Save the model
    trainer.save_merged_model()

    # Export to GGUF for Ollama
    trainer.export_gguf("models/my_model.gguf")

    # Or export directly to Ollama
    trainer.export_to_ollama("my-assistant")

    # Cleanup
    trainer.cleanup()
