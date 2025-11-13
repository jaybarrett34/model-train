"""
Data Synthesis Module for AI-Powered Training Data Generation

This module provides a flexible framework for generating training data using various AI providers.
It supports multiple generation modes, XML pattern validation, and multiple output formats.
"""

import json
import re
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal, Tuple
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GenerationMode(Enum):
    """Generation modes for data synthesis"""
    PSEUDORANDOM = "pseudorandom"  # AI generates varied content within constraints
    PATTERNED = "patterned"        # Use templates with specific fill-in sections
    FORCED = "forced"              # Lock specific parts, randomize others


@dataclass
class GenerationConfig:
    """Configuration for data generation"""
    mode: GenerationMode = GenerationMode.PSEUDORANDOM
    temperature: float = 0.8
    max_tokens: int = 1024
    retry_attempts: int = 3
    retry_delay: float = 1.0
    batch_size: int = 10
    rate_limit_delay: float = 0.5  # Delay between API calls in seconds


@dataclass
class XMLPattern:
    """XML pattern specification for validation"""
    schema: str  # XML schema or pattern
    required_tags: List[str]  # Required XML tags
    optional_tags: List[str] = None  # Optional XML tags

    def __post_init__(self):
        if self.optional_tags is None:
            self.optional_tags = []


class ValidationError(Exception):
    """Raised when generated data fails validation"""
    pass


class AIProviderError(Exception):
    """Raised when AI provider encounters an error"""
    pass


# ============================================================================
# AI Provider Interface and Implementations
# ============================================================================

class AIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self._request_count = 0
        self._total_tokens = 0

    @abstractmethod
    def generate(self, prompt: str, config: GenerationConfig) -> str:
        """
        Generate text using the AI provider

        Args:
            prompt: The prompt to send to the AI
            config: Generation configuration

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate that the provider is accessible"""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "request_count": self._request_count,
            "total_tokens": self._total_tokens
        }


class OllamaProvider(AIProvider):
    """Provider for local Ollama API"""

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        super().__init__(base_url=base_url)
        self.model = model
        logger.info(f"Initialized OllamaProvider with model: {model}")

    def generate(self, prompt: str, config: GenerationConfig) -> str:
        """Generate text using Ollama API"""
        try:
            import requests
        except ImportError:
            raise AIProviderError("requests library is required for OllamaProvider. Install with: pip install requests")

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()

            self._request_count += 1
            generated_text = result.get("response", "")

            logger.debug(f"Ollama generated {len(generated_text)} characters")
            return generated_text

        except requests.exceptions.RequestException as e:
            raise AIProviderError(f"Ollama API request failed: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate Ollama connection"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection validation failed: {e}")
            return False


class ClaudeProvider(AIProvider):
    """Provider for Anthropic Claude API"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        super().__init__(api_key=api_key)
        self.model = model
        logger.info(f"Initialized ClaudeProvider with model: {model}")

    def generate(self, prompt: str, config: GenerationConfig) -> str:
        """Generate text using Claude API"""
        try:
            import anthropic
        except ImportError:
            raise AIProviderError("anthropic library is required for ClaudeProvider. Install with: pip install anthropic")

        try:
            client = anthropic.Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            self._request_count += 1
            self._total_tokens += response.usage.input_tokens + response.usage.output_tokens

            generated_text = response.content[0].text
            logger.debug(f"Claude generated {len(generated_text)} characters, tokens: {response.usage.output_tokens}")

            return generated_text

        except Exception as e:
            raise AIProviderError(f"Claude API request failed: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate Claude API key"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            # Test with minimal request
            client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            logger.error(f"Claude connection validation failed: {e}")
            return False


class OpenAIProvider(AIProvider):
    """Provider for OpenAI API"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAIProvider with model: {model}")

    def generate(self, prompt: str, config: GenerationConfig) -> str:
        """Generate text using OpenAI API"""
        try:
            import openai
        except ImportError:
            raise AIProviderError("openai library is required for OpenAIProvider. Install with: pip install openai")

        try:
            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )

            self._request_count += 1
            self._total_tokens += response.usage.total_tokens

            generated_text = response.choices[0].message.content
            logger.debug(f"OpenAI generated {len(generated_text)} characters, tokens: {response.usage.completion_tokens}")

            return generated_text

        except Exception as e:
            raise AIProviderError(f"OpenAI API request failed: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate OpenAI API key"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            # Test with minimal request
            client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection validation failed: {e}")
            return False


# ============================================================================
# XML Validation
# ============================================================================

class XMLValidator:
    """Validates generated data against XML patterns"""

    @staticmethod
    def validate_xml_structure(text: str, pattern: XMLPattern) -> Tuple[bool, Optional[str]]:
        """
        Validate that text contains valid XML with required tags

        Args:
            text: Generated text to validate
            pattern: XML pattern specification

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required tags
        for tag in pattern.required_tags:
            tag_pattern = f"<{tag}.*?>.*?</{tag}>"
            if not re.search(tag_pattern, text, re.DOTALL):
                return False, f"Missing required tag: {tag}"

        # Try to parse XML fragments
        for tag in pattern.required_tags + pattern.optional_tags:
            matches = re.findall(f"<{tag}.*?>.*?</{tag}>", text, re.DOTALL)
            for match in matches:
                try:
                    ET.fromstring(match)
                except ParseError as e:
                    return False, f"Invalid XML in tag {tag}: {str(e)}"

        return True, None

    @staticmethod
    def extract_xml_content(text: str, tag: str) -> Optional[str]:
        """Extract content from XML tag"""
        pattern = f"<{tag}.*?>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None


# ============================================================================
# Data Synthesizer
# ============================================================================

class DataSynthesizer:
    """
    Main class for synthesizing training data using AI providers
    """

    def __init__(
        self,
        provider: AIProvider,
        xml_pattern: Optional[XMLPattern] = None,
        config: Optional[GenerationConfig] = None
    ):
        """
        Initialize DataSynthesizer

        Args:
            provider: AI provider instance
            xml_pattern: Optional XML pattern for validation
            config: Generation configuration
        """
        self.provider = provider
        self.xml_pattern = xml_pattern
        self.config = config or GenerationConfig()
        self.generated_examples = []

        logger.info(f"Initialized DataSynthesizer with {provider.__class__.__name__}")

    def _build_generation_prompt(
        self,
        objective: str,
        mode: GenerationMode,
        template: Optional[str] = None,
        locked_parts: Optional[Dict[str, str]] = None
    ) -> str:
        """Build prompt for AI generation based on mode"""

        base_prompt = f"""Generate a training example for the following task:

Task/Objective: {objective}
"""

        if self.xml_pattern:
            base_prompt += f"\nRequired XML tags: {', '.join(self.xml_pattern.required_tags)}"
            if self.xml_pattern.optional_tags:
                base_prompt += f"\nOptional XML tags: {', '.join(self.xml_pattern.optional_tags)}"

        if mode == GenerationMode.PSEUDORANDOM:
            base_prompt += """

Generate varied and creative content within the constraints. The output should be natural and diverse.
"""

        elif mode == GenerationMode.PATTERNED:
            if template:
                base_prompt += f"""

Use this template and fill in the variable sections:
{template}

Fill in the sections marked with [FILL] with appropriate content.
"""

        elif mode == GenerationMode.FORCED:
            if locked_parts:
                base_prompt += "\n\nLocked parts (must include exactly as shown):"
                for key, value in locked_parts.items():
                    base_prompt += f"\n- {key}: {value}"
                base_prompt += "\n\nGenerate the rest of the content with variation."

        base_prompt += "\n\nGenerate ONLY the output in the required format. Do not include explanations."

        return base_prompt

    def generate_single(
        self,
        objective: str,
        input_text: Optional[str] = None,
        mode: Optional[GenerationMode] = None,
        template: Optional[str] = None,
        locked_parts: Optional[Dict[str, str]] = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a single training example

        Args:
            objective: Task description or objective
            input_text: Optional input text for the example
            mode: Generation mode (uses config default if not specified)
            template: Template for patterned mode
            locked_parts: Locked parts for forced mode
            validate: Whether to validate against XML pattern

        Returns:
            Dictionary containing input and output
        """
        mode = mode or self.config.mode

        # Build prompt
        if input_text:
            full_objective = f"{objective}\n\nInput: {input_text}"
        else:
            full_objective = objective

        prompt = self._build_generation_prompt(full_objective, mode, template, locked_parts)

        # Generate with retries
        for attempt in range(self.config.retry_attempts):
            try:
                logger.debug(f"Generation attempt {attempt + 1}/{self.config.retry_attempts}")

                output = self.provider.generate(prompt, self.config)

                # Validate if required
                if validate and self.xml_pattern:
                    is_valid, error_msg = XMLValidator.validate_xml_structure(
                        output, self.xml_pattern
                    )
                    if not is_valid:
                        logger.warning(f"Validation failed: {error_msg}")
                        if attempt < self.config.retry_attempts - 1:
                            time.sleep(self.config.retry_delay)
                            continue
                        else:
                            raise ValidationError(f"Failed validation after {self.config.retry_attempts} attempts: {error_msg}")

                # Success
                example = {
                    "input": input_text or objective,
                    "output": output,
                    "metadata": {
                        "mode": mode.value,
                        "attempt": attempt + 1,
                        "timestamp": time.time()
                    }
                }

                self.generated_examples.append(example)
                logger.info(f"Successfully generated example (attempt {attempt + 1})")

                return example

            except AIProviderError as e:
                logger.error(f"AI provider error on attempt {attempt + 1}: {e}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    raise

        raise AIProviderError("Failed to generate example after all retry attempts")

    def generate_batch(
        self,
        objectives: List[str],
        inputs: Optional[List[str]] = None,
        mode: Optional[GenerationMode] = None,
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple training examples in batch

        Args:
            objectives: List of task objectives
            inputs: Optional list of input texts (must match objectives length)
            mode: Generation mode
            show_progress: Whether to show progress logging

        Returns:
            List of generated examples
        """
        if inputs and len(inputs) != len(objectives):
            raise ValueError("inputs and objectives must have the same length")

        examples = []
        total = len(objectives)

        for i, objective in enumerate(objectives):
            if show_progress:
                logger.info(f"Generating example {i + 1}/{total}")

            input_text = inputs[i] if inputs else None

            try:
                example = self.generate_single(
                    objective=objective,
                    input_text=input_text,
                    mode=mode
                )
                examples.append(example)

                # Rate limiting
                if i < total - 1:  # Don't delay after last item
                    time.sleep(self.config.rate_limit_delay)

            except Exception as e:
                logger.error(f"Failed to generate example {i + 1}: {e}")
                # Continue with next example
                continue

        logger.info(f"Batch generation complete: {len(examples)}/{total} successful")
        return examples

    def generate_from_pattern_examples(
        self,
        examples: List[Dict[str, str]],
        num_variations: int = 5,
        mode: GenerationMode = GenerationMode.PSEUDORANDOM
    ) -> List[Dict[str, Any]]:
        """
        Generate variations based on example patterns

        Args:
            examples: List of example dicts with 'input' and 'output' keys
            num_variations: Number of variations to generate per example
            mode: Generation mode

        Returns:
            List of generated examples
        """
        all_examples = []

        for example in examples:
            logger.info(f"Generating {num_variations} variations of example pattern")

            objective = f"""Generate a similar example following this pattern:
Input: {example['input']}
Output: {example['output']}

Create a NEW example with different content but following the same structure and format.
"""

            for i in range(num_variations):
                try:
                    generated = self.generate_single(
                        objective=objective,
                        mode=mode
                    )
                    all_examples.append(generated)
                    time.sleep(self.config.rate_limit_delay)
                except Exception as e:
                    logger.error(f"Failed to generate variation {i + 1}: {e}")

        return all_examples

    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return {
            "total_generated": len(self.generated_examples),
            "provider_stats": self.provider.get_stats()
        }


# ============================================================================
# Dataset Format Converters
# ============================================================================

def to_sharegpt_format(examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert examples to ShareGPT format

    Args:
        examples: List of examples with 'input' and 'output' keys

    Returns:
        List in ShareGPT format
    """
    sharegpt_data = []

    for example in examples:
        sharegpt_example = {
            "conversations": [
                {
                    "from": "human",
                    "value": example["input"]
                },
                {
                    "from": "gpt",
                    "value": example["output"]
                }
            ]
        }

        # Add metadata if present
        if "metadata" in example:
            sharegpt_example["metadata"] = example["metadata"]

        sharegpt_data.append(sharegpt_example)

    logger.info(f"Converted {len(examples)} examples to ShareGPT format")
    return sharegpt_data


def to_alpaca_format(
    examples: List[Dict[str, Any]],
    instruction_prefix: str = ""
) -> List[Dict[str, Any]]:
    """
    Convert examples to Alpaca format

    Args:
        examples: List of examples with 'input' and 'output' keys
        instruction_prefix: Optional prefix for all instructions

    Returns:
        List in Alpaca format
    """
    alpaca_data = []

    for example in examples:
        # Try to extract instruction and input if they're combined
        input_text = example["input"]
        instruction = instruction_prefix
        inp = ""

        # Check if input contains a clear instruction/input split
        if "\n\n" in input_text:
            parts = input_text.split("\n\n", 1)
            instruction = instruction_prefix + parts[0] if instruction_prefix else parts[0]
            inp = parts[1]
        else:
            instruction = instruction_prefix + input_text if instruction_prefix else input_text

        alpaca_example = {
            "instruction": instruction,
            "input": inp,
            "output": example["output"]
        }

        # Add metadata if present
        if "metadata" in example:
            alpaca_example["metadata"] = example["metadata"]

        alpaca_data.append(alpaca_example)

    logger.info(f"Converted {len(examples)} examples to Alpaca format")
    return alpaca_data


def save_dataset(
    data: List[Dict[str, Any]],
    filepath: str,
    format_type: Literal["sharegpt", "alpaca", "raw"] = "raw"
) -> None:
    """
    Save dataset to JSON file

    Args:
        data: List of examples
        filepath: Output file path
        format_type: Format to save in
    """
    if format_type == "sharegpt":
        formatted_data = to_sharegpt_format(data)
    elif format_type == "alpaca":
        formatted_data = to_alpaca_format(data)
    else:
        formatted_data = data

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(formatted_data)} examples to {filepath} in {format_type} format")


# ============================================================================
# Example Usage and Utilities
# ============================================================================

def create_minecraft_example():
    """Example: Generate Minecraft assistant training data"""

    # Define XML pattern for Minecraft responses
    minecraft_pattern = XMLPattern(
        schema="",
        required_tags=["think", "command", "speak"],
        optional_tags=["action", "observe"]
    )

    # Initialize provider (example with Ollama)
    provider = OllamaProvider(model="llama2")

    # Create synthesizer
    config = GenerationConfig(
        mode=GenerationMode.PSEUDORANDOM,
        temperature=0.8,
        batch_size=10
    )

    synthesizer = DataSynthesizer(
        provider=provider,
        xml_pattern=minecraft_pattern,
        config=config
    )

    # Generate examples
    objectives = [
        "Help the player find diamonds",
        "Build a house for the player",
        "Fight hostile mobs",
        "Gather wood resources",
        "Navigate to coordinates"
    ]

    inputs = [
        "What should I do to get diamonds?",
        "Can you build me a shelter?",
        "There are zombies attacking!",
        "I need wood for crafting",
        "Take me to spawn point"
    ]

    examples = synthesizer.generate_batch(
        objectives=objectives,
        inputs=inputs
    )

    # Save in different formats
    save_dataset(examples, "minecraft_data_sharegpt.json", format_type="sharegpt")
    save_dataset(examples, "minecraft_data_alpaca.json", format_type="alpaca")

    print(f"Generated {len(examples)} examples")
    print(f"Stats: {synthesizer.get_stats()}")


if __name__ == "__main__":
    # Example usage
    print("Data Synthesis Module")
    print("=" * 60)
    print("\nExample providers:")
    print("1. OllamaProvider - Local Ollama API")
    print("2. ClaudeProvider - Anthropic Claude API")
    print("3. OpenAIProvider - OpenAI API")
    print("\nExample usage in create_minecraft_example()")
