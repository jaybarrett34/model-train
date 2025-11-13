"""
Dataset Size Analysis Module

This module provides tools for estimating optimal dataset sizes for fine-tuning based on
pattern complexity, model size, and training objectives. It includes research-based heuristics
and quality analysis features to help determine adequate training data requirements.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from enum import Enum

from .synthesis import XMLPattern, ValidationError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinetuningStrength(Enum):
    """Fine-tuning strength levels"""
    LIGHT = "light"        # Minimal behavior adjustment
    MODERATE = "moderate"  # Standard fine-tuning
    HEAVY = "heavy"        # Deep behavior modification


class AdequacyStatus(Enum):
    """Dataset adequacy status"""
    INSUFFICIENT = "insufficient"  # Below minimum threshold
    MINIMAL = "minimal"            # At minimum threshold
    ADEQUATE = "adequate"          # Within recommended range
    OPTIMAL = "optimal"            # At optimal size
    EXCESSIVE = "excessive"        # Beyond diminishing returns


class ComplexityLevel(Enum):
    """Pattern complexity levels"""
    TRIVIAL = "trivial"          # 0-20: Simple format changes
    SIMPLE = "simple"            # 21-40: Basic patterns
    MODERATE = "moderate"        # 41-60: Standard complexity
    COMPLEX = "complex"          # 61-80: Advanced patterns
    VERY_COMPLEX = "very_complex"  # 81-100: Complex reasoning/domain knowledge


@dataclass
class SizeEstimate:
    """Dataset size estimates"""
    minimum: int
    optimal: int
    maximum: int
    diminishing_returns_threshold: int

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary"""
        return {
            'minimum': self.minimum,
            'optimal': self.optimal,
            'maximum': self.maximum,
            'diminishing_returns_threshold': self.diminishing_returns_threshold
        }


@dataclass
class QualityMetrics:
    """Dataset quality metrics"""
    total_examples: int
    unique_examples: int
    duplicate_count: int
    duplicate_percentage: float
    avg_input_length: float
    avg_output_length: float
    unique_input_patterns: int
    unique_output_patterns: int
    diversity_score: float  # 0-100, higher is better
    variance_score: float   # 0-100, higher is better
    overfitting_risk: str   # "low", "moderate", "high"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_examples': self.total_examples,
            'unique_examples': self.unique_examples,
            'duplicate_count': self.duplicate_count,
            'duplicate_percentage': round(self.duplicate_percentage, 2),
            'avg_input_length': round(self.avg_input_length, 2),
            'avg_output_length': round(self.avg_output_length, 2),
            'unique_input_patterns': self.unique_input_patterns,
            'unique_output_patterns': self.unique_output_patterns,
            'diversity_score': round(self.diversity_score, 2),
            'variance_score': round(self.variance_score, 2),
            'overfitting_risk': self.overfitting_risk
        }


@dataclass
class ComplexityAnalysis:
    """Pattern complexity analysis results"""
    complexity_score: float  # 0-100
    complexity_level: ComplexityLevel
    unique_tags: int
    tag_depth: int
    constraint_count: int
    reasoning_required: bool
    domain_specific: bool
    factors: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'complexity_score': round(self.complexity_score, 2),
            'complexity_level': self.complexity_level.value,
            'unique_tags': self.unique_tags,
            'tag_depth': self.tag_depth,
            'constraint_count': self.constraint_count,
            'reasoning_required': self.reasoning_required,
            'domain_specific': self.domain_specific,
            'factors': {k: round(v, 2) for k, v in self.factors.items()}
        }


@dataclass
class AnalysisReport:
    """Comprehensive analysis report"""
    # Pattern analysis
    complexity_analysis: ComplexityAnalysis

    # Dataset info
    current_size: int

    # Size estimates
    size_estimates: SizeEstimate

    # Quality metrics
    quality_metrics: Optional[QualityMetrics]

    # Status and recommendations
    adequacy_status: AdequacyStatus
    adequacy_percentage: float  # How close to optimal (0-100+)
    recommendations: List[str]
    warnings: List[str]

    # Model and training info
    base_model: str
    model_parameters: str
    finetuning_strength: FinetuningStrength
    lora_rank: Optional[int]

    # Performance estimates
    expected_performance: str
    training_time_estimate: str
    cost_estimate: Optional[str]

    # Data augmentation suggestions
    augmentation_strategies: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'complexity_analysis': self.complexity_analysis.to_dict(),
            'current_size': self.current_size,
            'size_estimates': self.size_estimates.to_dict(),
            'quality_metrics': self.quality_metrics.to_dict() if self.quality_metrics else None,
            'adequacy_status': self.adequacy_status.value,
            'adequacy_percentage': round(self.adequacy_percentage, 2),
            'recommendations': self.recommendations,
            'warnings': self.warnings,
            'base_model': self.base_model,
            'model_parameters': self.model_parameters,
            'finetuning_strength': self.finetuning_strength.value,
            'lora_rank': self.lora_rank,
            'expected_performance': self.expected_performance,
            'training_time_estimate': self.training_time_estimate,
            'cost_estimate': self.cost_estimate,
            'augmentation_strategies': self.augmentation_strategies
        }

    def __str__(self) -> str:
        """Generate human-readable report"""
        lines = [
            "=" * 80,
            "DATASET SIZE ANALYSIS REPORT",
            "=" * 80,
            "",
            "MODEL CONFIGURATION",
            "-" * 80,
            f"Base Model: {self.base_model}",
            f"Model Size: {self.model_parameters}",
            f"Fine-tuning Strength: {self.finetuning_strength.value}",
            f"LoRA Rank: {self.lora_rank if self.lora_rank else 'N/A'}",
            "",
            "PATTERN COMPLEXITY ANALYSIS",
            "-" * 80,
            f"Complexity Score: {self.complexity_analysis.complexity_score:.1f}/100",
            f"Complexity Level: {self.complexity_analysis.complexity_level.value.upper()}",
            f"Unique XML Tags: {self.complexity_analysis.unique_tags}",
            f"Tag Depth: {self.complexity_analysis.tag_depth}",
            f"Constraint Count: {self.complexity_analysis.constraint_count}",
            f"Reasoning Required: {'Yes' if self.complexity_analysis.reasoning_required else 'No'}",
            f"Domain Specific: {'Yes' if self.complexity_analysis.domain_specific else 'No'}",
            "",
            "Complexity Factors:",
        ]

        for factor, score in self.complexity_analysis.factors.items():
            lines.append(f"  - {factor}: {score:.1f}")

        lines.extend([
            "",
            "DATASET SIZE ANALYSIS",
            "-" * 80,
            f"Current Size: {self.current_size} examples",
            f"Minimum Required: {self.size_estimates.minimum} examples",
            f"Optimal Size: {self.size_estimates.optimal} examples",
            f"Maximum Useful: {self.size_estimates.maximum} examples",
            f"Diminishing Returns: {self.size_estimates.diminishing_returns_threshold} examples",
            "",
            f"Adequacy Status: {self.adequacy_status.value.upper()}",
            f"Progress to Optimal: {self.adequacy_percentage:.1f}%",
        ])

        if self.quality_metrics:
            lines.extend([
                "",
                "QUALITY METRICS",
                "-" * 80,
                f"Total Examples: {self.quality_metrics.total_examples}",
                f"Unique Examples: {self.quality_metrics.unique_examples}",
                f"Duplicates: {self.quality_metrics.duplicate_count} ({self.quality_metrics.duplicate_percentage:.1f}%)",
                f"Avg Input Length: {self.quality_metrics.avg_input_length:.1f} chars",
                f"Avg Output Length: {self.quality_metrics.avg_output_length:.1f} chars",
                f"Unique Input Patterns: {self.quality_metrics.unique_input_patterns}",
                f"Unique Output Patterns: {self.quality_metrics.unique_output_patterns}",
                f"Diversity Score: {self.quality_metrics.diversity_score:.1f}/100",
                f"Variance Score: {self.quality_metrics.variance_score:.1f}/100",
                f"Overfitting Risk: {self.quality_metrics.overfitting_risk.upper()}",
            ])

        lines.extend([
            "",
            "PERFORMANCE ESTIMATES",
            "-" * 80,
            f"Expected Performance: {self.expected_performance}",
            f"Estimated Training Time: {self.training_time_estimate}",
        ])

        if self.cost_estimate:
            lines.append(f"Estimated Cost: {self.cost_estimate}")

        if self.recommendations:
            lines.extend([
                "",
                "RECOMMENDATIONS",
                "-" * 80,
            ])
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")

        if self.warnings:
            lines.extend([
                "",
                "WARNINGS",
                "-" * 80,
            ])
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"{i}. {warning}")

        if self.augmentation_strategies:
            lines.extend([
                "",
                "SUGGESTED DATA AUGMENTATION STRATEGIES",
                "-" * 80,
            ])
            for i, strategy in enumerate(self.augmentation_strategies, 1):
                lines.append(f"{i}. {strategy}")

        lines.extend([
            "",
            "=" * 80,
        ])

        return "\n".join(lines)


class DatasetSizeAnalyzer:
    """
    Analyzes dataset requirements for fine-tuning based on pattern complexity,
    model size, and training objectives.

    This analyzer uses research-based heuristics to estimate optimal dataset sizes
    and provides quality analysis for existing datasets.
    """

    # Model size parameter mapping (in billions)
    MODEL_SIZE_MAP = {
        '1b': 1,
        '3b': 3,
        '7b': 7,
        '8b': 8,
        '14b': 14,
        '32b': 32,
        '70b': 70,
        '405b': 405,
    }

    # Base size multipliers for different complexity levels
    # Format: (min, optimal, max, diminishing_returns)
    BASE_SIZES = {
        ComplexityLevel.TRIVIAL: (30, 100, 300, 200),
        ComplexityLevel.SIMPLE: (50, 250, 600, 400),
        ComplexityLevel.MODERATE: (100, 500, 1500, 1000),
        ComplexityLevel.COMPLEX: (300, 1200, 3500, 2500),
        ComplexityLevel.VERY_COMPLEX: (1000, 5000, 15000, 10000),
    }

    def __init__(
        self,
        xml_pattern: Optional[XMLPattern] = None,
        base_model: str = "qwen2.5:7b",
        objective: str = "",
        finetuning_strength: FinetuningStrength = FinetuningStrength.MODERATE,
        lora_rank: Optional[int] = None,
        pattern_description: Optional[str] = None
    ):
        """
        Initialize DatasetSizeAnalyzer

        Args:
            xml_pattern: XML pattern specification for validation
            base_model: Base model identifier (e.g., "qwen2.5:7b", "llama3:8b")
            objective: Training objective description
            finetuning_strength: Desired fine-tuning strength
            lora_rank: LoRA rank if using LoRA fine-tuning
            pattern_description: Additional pattern description for complexity analysis
        """
        self.xml_pattern = xml_pattern
        self.base_model = base_model
        self.objective = objective
        self.finetuning_strength = finetuning_strength
        self.lora_rank = lora_rank
        self.pattern_description = pattern_description or ""

        # Extract model size
        self.model_parameters = self._extract_model_size(base_model)
        self.model_size_billions = self._parse_model_size(self.model_parameters)

        logger.info(f"Initialized DatasetSizeAnalyzer for {base_model} ({self.model_parameters})")

    def _extract_model_size(self, model_name: str) -> str:
        """Extract model size from model name"""
        # Look for patterns like "7b", "14b", "70b", etc.
        match = re.search(r'(\d+\.?\d*[bB])', model_name)
        if match:
            return match.group(1).lower()

        # Default to medium size if not found
        return "7b"

    def _parse_model_size(self, size_str: str) -> float:
        """Parse model size string to billions of parameters"""
        size_str = size_str.lower().replace('b', '')
        try:
            return float(size_str)
        except ValueError:
            logger.warning(f"Could not parse model size '{size_str}', defaulting to 7B")
            return 7.0

    def analyze_pattern_complexity(self) -> ComplexityAnalysis:
        """
        Analyze XML pattern complexity and return complexity score

        Returns:
            ComplexityAnalysis with detailed complexity metrics
        """
        factors = {}

        # Factor 1: Number of unique tags (0-25 points)
        unique_tags = 0
        if self.xml_pattern:
            unique_tags = len(self.xml_pattern.required_tags) + len(self.xml_pattern.optional_tags or [])

        tag_complexity = min(25, unique_tags * 2.5)
        factors['tag_count'] = tag_complexity

        # Factor 2: Tag depth/nesting (0-20 points)
        tag_depth = self._estimate_tag_depth()
        depth_complexity = min(20, tag_depth * 5)
        factors['tag_depth'] = depth_complexity

        # Factor 3: Constraint complexity (0-25 points)
        constraint_count = self._count_constraints()
        constraint_complexity = min(25, constraint_count * 5)
        factors['constraints'] = constraint_complexity

        # Factor 4: Reasoning requirements (0-15 points)
        reasoning_required = self._requires_reasoning()
        reasoning_complexity = 15 if reasoning_required else 5
        factors['reasoning'] = reasoning_complexity

        # Factor 5: Domain specificity (0-15 points)
        domain_specific = self._is_domain_specific()
        domain_complexity = 15 if domain_specific else 5
        factors['domain_knowledge'] = domain_complexity

        # Calculate total complexity score
        complexity_score = sum(factors.values())

        # Determine complexity level
        if complexity_score <= 20:
            complexity_level = ComplexityLevel.TRIVIAL
        elif complexity_score <= 40:
            complexity_level = ComplexityLevel.SIMPLE
        elif complexity_score <= 60:
            complexity_level = ComplexityLevel.MODERATE
        elif complexity_score <= 80:
            complexity_level = ComplexityLevel.COMPLEX
        else:
            complexity_level = ComplexityLevel.VERY_COMPLEX

        return ComplexityAnalysis(
            complexity_score=complexity_score,
            complexity_level=complexity_level,
            unique_tags=unique_tags,
            tag_depth=tag_depth,
            constraint_count=constraint_count,
            reasoning_required=reasoning_required,
            domain_specific=domain_specific,
            factors=factors
        )

    def _estimate_tag_depth(self) -> int:
        """Estimate maximum nesting depth of XML tags"""
        if not self.xml_pattern or not self.xml_pattern.schema:
            return 1

        # Try to parse schema and find max depth
        try:
            root = ET.fromstring(self.xml_pattern.schema)
            return self._get_element_depth(root)
        except ParseError:
            # Estimate from tag names (tags with dots or underscores suggest nesting)
            all_tags = self.xml_pattern.required_tags + (self.xml_pattern.optional_tags or [])
            max_depth = 1
            for tag in all_tags:
                # Count separators as depth indicators
                depth = tag.count('.') + tag.count('_') + 1
                max_depth = max(max_depth, depth)
            return max_depth

    def _get_element_depth(self, element: ET.Element, current_depth: int = 1) -> int:
        """Recursively calculate XML element depth"""
        if len(element) == 0:
            return current_depth

        max_child_depth = current_depth
        for child in element:
            child_depth = self._get_element_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def _count_constraints(self) -> int:
        """Count number of constraints in the pattern"""
        constraint_count = 0

        # Required tags are constraints
        if self.xml_pattern:
            constraint_count += len(self.xml_pattern.required_tags)

        # Look for constraint keywords in objective and description
        constraint_keywords = [
            'must', 'should', 'required', 'always', 'never',
            'only', 'exactly', 'specific', 'format', 'structure'
        ]

        text = (self.objective + " " + self.pattern_description).lower()
        for keyword in constraint_keywords:
            constraint_count += text.count(keyword)

        return constraint_count

    def _requires_reasoning(self) -> bool:
        """Determine if pattern requires complex reasoning"""
        reasoning_keywords = [
            'reasoning', 'logic', 'understand', 'analyze', 'infer',
            'deduce', 'conclude', 'think', 'complex', 'multi-step'
        ]

        text = (self.objective + " " + self.pattern_description).lower()
        return any(keyword in text for keyword in reasoning_keywords)

    def _is_domain_specific(self) -> bool:
        """Determine if pattern requires domain-specific knowledge"""
        domain_keywords = [
            'medical', 'legal', 'scientific', 'technical', 'specialized',
            'domain', 'expert', 'professional', 'industry', 'academic'
        ]

        text = (self.objective + " " + self.pattern_description).lower()
        return any(keyword in text for keyword in domain_keywords)

    def estimate_dataset_size(
        self,
        complexity_analysis: Optional[ComplexityAnalysis] = None
    ) -> SizeEstimate:
        """
        Estimate optimal dataset size based on complexity and model parameters

        Args:
            complexity_analysis: Pre-computed complexity analysis (computed if not provided)

        Returns:
            SizeEstimate with min/optimal/max sizes
        """
        if complexity_analysis is None:
            complexity_analysis = self.analyze_pattern_complexity()

        # Get base sizes for complexity level
        base_min, base_optimal, base_max, base_diminishing = self.BASE_SIZES[
            complexity_analysis.complexity_level
        ]

        # Apply multipliers

        # 1. Model size multiplier
        # Larger models generally need more data to fine-tune effectively
        model_multiplier = 1.0
        if self.model_size_billions >= 70:
            model_multiplier = 1.5
        elif self.model_size_billions >= 30:
            model_multiplier = 1.3
        elif self.model_size_billions >= 13:
            model_multiplier = 1.15
        elif self.model_size_billions <= 3:
            model_multiplier = 0.85

        # 2. Fine-tuning strength multiplier
        strength_multiplier = {
            FinetuningStrength.LIGHT: 0.7,
            FinetuningStrength.MODERATE: 1.0,
            FinetuningStrength.HEAVY: 1.4
        }[self.finetuning_strength]

        # 3. LoRA rank multiplier
        # Higher rank needs more data to train effectively
        lora_multiplier = 1.0
        if self.lora_rank:
            if self.lora_rank >= 128:
                lora_multiplier = 1.3
            elif self.lora_rank >= 64:
                lora_multiplier = 1.15
            elif self.lora_rank <= 16:
                lora_multiplier = 0.9

        # Combine multipliers
        total_multiplier = model_multiplier * strength_multiplier * lora_multiplier

        # Apply to base sizes
        minimum = int(base_min * total_multiplier)
        optimal = int(base_optimal * total_multiplier)
        maximum = int(base_max * total_multiplier)
        diminishing_returns = int(base_diminishing * total_multiplier)

        return SizeEstimate(
            minimum=minimum,
            optimal=optimal,
            maximum=maximum,
            diminishing_returns_threshold=diminishing_returns
        )

    def analyze_dataset_quality(self, dataset_path: str) -> QualityMetrics:
        """
        Analyze quality metrics of an existing dataset

        Args:
            dataset_path: Path to dataset file (JSONL format)

        Returns:
            QualityMetrics with comprehensive quality analysis
        """
        path = Path(dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        examples = []
        inputs = []
        outputs = []

        # Load dataset
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        examples.append(data)

                        # Extract input/output
                        if 'conversations' in data:
                            # ShareGPT format
                            for msg in data['conversations']:
                                if msg.get('from') == 'human':
                                    inputs.append(msg.get('value', ''))
                                elif msg.get('from') == 'gpt':
                                    outputs.append(msg.get('value', ''))
                        elif 'instruction' in data and 'output' in data:
                            # Alpaca format
                            inputs.append(data['instruction'])
                            outputs.append(data['output'])

                    except json.JSONDecodeError:
                        logger.warning(f"Skipping invalid JSON line")

        total_examples = len(examples)

        # Find duplicates
        example_strings = [json.dumps(ex, sort_keys=True) for ex in examples]
        unique_examples = len(set(example_strings))
        duplicate_count = total_examples - unique_examples
        duplicate_percentage = (duplicate_count / total_examples * 100) if total_examples > 0 else 0

        # Calculate average lengths
        avg_input_length = sum(len(inp) for inp in inputs) / len(inputs) if inputs else 0
        avg_output_length = sum(len(out) for out in outputs) / len(outputs) if outputs else 0

        # Analyze pattern diversity
        unique_input_patterns = self._count_unique_patterns(inputs)
        unique_output_patterns = self._count_unique_patterns(outputs)

        # Calculate diversity score (0-100)
        diversity_score = min(100, (unique_examples / max(1, total_examples)) * 100)

        # Calculate variance score (0-100)
        variance_score = self._calculate_variance_score(inputs, outputs)

        # Assess overfitting risk
        overfitting_risk = self._assess_overfitting_risk(
            total_examples, unique_examples, diversity_score, variance_score
        )

        return QualityMetrics(
            total_examples=total_examples,
            unique_examples=unique_examples,
            duplicate_count=duplicate_count,
            duplicate_percentage=duplicate_percentage,
            avg_input_length=avg_input_length,
            avg_output_length=avg_output_length,
            unique_input_patterns=unique_input_patterns,
            unique_output_patterns=unique_output_patterns,
            diversity_score=diversity_score,
            variance_score=variance_score,
            overfitting_risk=overfitting_risk
        )

    def _count_unique_patterns(self, texts: List[str]) -> int:
        """Count unique structural patterns in texts"""
        if not texts:
            return 0

        patterns = set()
        for text in texts:
            # Extract structural pattern (tags, keywords, etc.)
            # Remove specific content but keep structure
            pattern = re.sub(r'\d+', 'NUM', text)  # Replace numbers
            pattern = re.sub(r'[a-zA-Z]{10,}', 'WORD', pattern)  # Replace long words
            patterns.add(pattern[:200])  # Limit pattern length

        return len(patterns)

    def _calculate_variance_score(self, inputs: List[str], outputs: List[str]) -> float:
        """Calculate variance score based on length and content variation"""
        if not inputs and not outputs:
            return 0.0

        all_texts = inputs + outputs
        if not all_texts:
            return 0.0

        # Calculate length variance
        lengths = [len(text) for text in all_texts]
        avg_length = sum(lengths) / len(lengths)

        if avg_length == 0:
            return 0.0

        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        std_dev = variance ** 0.5
        coefficient_of_variation = (std_dev / avg_length) * 100

        # Normalize to 0-100 scale (30% CV = 100 score)
        variance_score = min(100, coefficient_of_variation / 0.3)

        return variance_score

    def _assess_overfitting_risk(
        self,
        total: int,
        unique: int,
        diversity: float,
        variance: float
    ) -> str:
        """Assess risk of overfitting based on quality metrics"""
        uniqueness = (unique / max(1, total)) * 100

        # High risk: low uniqueness, low diversity, low variance
        if uniqueness < 70 or diversity < 50 or variance < 30:
            return "high"

        # Moderate risk
        if uniqueness < 85 or diversity < 70 or variance < 50:
            return "moderate"

        # Low risk
        return "low"

    def analyze(
        self,
        dataset_path: Optional[str] = None
    ) -> AnalysisReport:
        """
        Perform comprehensive dataset analysis

        Args:
            dataset_path: Optional path to existing dataset for quality analysis

        Returns:
            Comprehensive AnalysisReport
        """
        # Analyze pattern complexity
        complexity = self.analyze_pattern_complexity()
        logger.info(f"Pattern complexity: {complexity.complexity_score:.1f}/100 ({complexity.complexity_level.value})")

        # Estimate optimal sizes
        size_estimates = self.estimate_dataset_size(complexity)
        logger.info(f"Estimated optimal size: {size_estimates.optimal} examples")

        # Analyze dataset quality if provided
        quality_metrics = None
        current_size = 0
        if dataset_path:
            quality_metrics = self.analyze_dataset_quality(dataset_path)
            current_size = quality_metrics.total_examples
            logger.info(f"Current dataset size: {current_size} examples")

        # Determine adequacy status
        adequacy_status, adequacy_percentage = self._determine_adequacy(
            current_size, size_estimates
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            current_size, size_estimates, adequacy_status, complexity, quality_metrics
        )

        # Generate warnings
        warnings = self._generate_warnings(quality_metrics, adequacy_status)

        # Estimate performance
        expected_performance = self._estimate_performance(
            current_size, size_estimates, adequacy_status, quality_metrics
        )

        # Estimate training time
        training_time = self._estimate_training_time(current_size, self.model_size_billions)

        # Estimate cost (if using cloud resources)
        cost_estimate = self._estimate_cost(current_size, self.model_size_billions)

        # Suggest augmentation strategies
        augmentation_strategies = self._suggest_augmentation_strategies(
            complexity, current_size, size_estimates, quality_metrics
        )

        return AnalysisReport(
            complexity_analysis=complexity,
            current_size=current_size,
            size_estimates=size_estimates,
            quality_metrics=quality_metrics,
            adequacy_status=adequacy_status,
            adequacy_percentage=adequacy_percentage,
            recommendations=recommendations,
            warnings=warnings,
            base_model=self.base_model,
            model_parameters=self.model_parameters,
            finetuning_strength=self.finetuning_strength,
            lora_rank=self.lora_rank,
            expected_performance=expected_performance,
            training_time_estimate=training_time,
            cost_estimate=cost_estimate,
            augmentation_strategies=augmentation_strategies
        )

    def _determine_adequacy(
        self,
        current_size: int,
        estimates: SizeEstimate
    ) -> Tuple[AdequacyStatus, float]:
        """Determine dataset adequacy status"""
        if current_size == 0:
            return AdequacyStatus.INSUFFICIENT, 0.0

        percentage = (current_size / estimates.optimal) * 100

        if current_size < estimates.minimum:
            status = AdequacyStatus.INSUFFICIENT
        elif current_size < estimates.minimum * 1.2:
            status = AdequacyStatus.MINIMAL
        elif current_size < estimates.optimal * 0.8:
            status = AdequacyStatus.ADEQUATE
        elif current_size <= estimates.diminishing_returns_threshold:
            status = AdequacyStatus.OPTIMAL
        else:
            status = AdequacyStatus.EXCESSIVE

        return status, percentage

    def _generate_recommendations(
        self,
        current_size: int,
        estimates: SizeEstimate,
        adequacy: AdequacyStatus,
        complexity: ComplexityAnalysis,
        quality: Optional[QualityMetrics]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if adequacy == AdequacyStatus.INSUFFICIENT:
            needed = estimates.minimum - current_size
            recommendations.append(
                f"Generate at least {needed} more examples to reach minimum threshold of {estimates.minimum}"
            )
            recommendations.append(
                f"Target {estimates.optimal} examples for optimal performance"
            )

        elif adequacy == AdequacyStatus.MINIMAL:
            needed = estimates.optimal - current_size
            recommendations.append(
                f"Consider generating {needed} more examples to reach optimal size of {estimates.optimal}"
            )

        elif adequacy == AdequacyStatus.ADEQUATE:
            needed = estimates.optimal - current_size
            recommendations.append(
                f"Dataset is adequate. Adding {needed} more examples would reach optimal size"
            )

        elif adequacy == AdequacyStatus.OPTIMAL:
            recommendations.append(
                "Dataset size is optimal. Focus on quality and diversity rather than quantity"
            )

        elif adequacy == AdequacyStatus.EXCESSIVE:
            recommendations.append(
                f"Dataset exceeds diminishing returns threshold ({estimates.diminishing_returns_threshold}). "
                "Additional examples may provide minimal benefit"
            )

        # Quality-based recommendations
        if quality:
            if quality.duplicate_percentage > 10:
                recommendations.append(
                    f"Remove {quality.duplicate_count} duplicate examples ({quality.duplicate_percentage:.1f}%) "
                    "to improve dataset quality"
                )

            if quality.diversity_score < 60:
                recommendations.append(
                    f"Diversity score is low ({quality.diversity_score:.1f}/100). "
                    "Generate more varied examples"
                )

            if quality.variance_score < 40:
                recommendations.append(
                    f"Variance score is low ({quality.variance_score:.1f}/100). "
                    "Increase variation in example lengths and complexity"
                )

            if quality.overfitting_risk == "high":
                recommendations.append(
                    "High overfitting risk detected. Increase diversity and remove duplicates"
                )

        # Complexity-based recommendations
        if complexity.complexity_level in [ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX]:
            recommendations.append(
                "Pattern is complex. Ensure examples cover all edge cases and variations"
            )

            if complexity.reasoning_required:
                recommendations.append(
                    "Pattern requires reasoning. Include examples with clear logical progressions"
                )

            if complexity.domain_specific:
                recommendations.append(
                    "Pattern is domain-specific. Ensure examples cover domain terminology and concepts"
                )

        return recommendations

    def _generate_warnings(
        self,
        quality: Optional[QualityMetrics],
        adequacy: AdequacyStatus
    ) -> List[str]:
        """Generate warnings about potential issues"""
        warnings = []

        if adequacy == AdequacyStatus.INSUFFICIENT:
            warnings.append(
                "Dataset size is below minimum threshold. Training may not converge properly"
            )

        if quality:
            if quality.duplicate_percentage > 20:
                warnings.append(
                    f"High duplicate rate ({quality.duplicate_percentage:.1f}%). "
                    "This may cause overfitting"
                )

            if quality.diversity_score < 40:
                warnings.append(
                    "Very low diversity score. Model may not generalize well"
                )

            if quality.overfitting_risk == "high":
                warnings.append(
                    "High overfitting risk. Model may memorize examples instead of learning patterns"
                )

            if quality.avg_output_length < 50:
                warnings.append(
                    f"Average output length is very short ({quality.avg_output_length:.0f} chars). "
                    "Ensure this matches your use case"
                )

        return warnings

    def _estimate_performance(
        self,
        current_size: int,
        estimates: SizeEstimate,
        adequacy: AdequacyStatus,
        quality: Optional[QualityMetrics]
    ) -> str:
        """Estimate expected model performance"""
        if adequacy == AdequacyStatus.INSUFFICIENT:
            return "Poor - Dataset too small for reliable learning"

        elif adequacy == AdequacyStatus.MINIMAL:
            return "Fair - Model may learn basic patterns but generalization limited"

        elif adequacy == AdequacyStatus.ADEQUATE:
            performance = "Good - Model should learn patterns effectively"
            if quality and quality.overfitting_risk == "high":
                performance += ", but overfitting risk present"
            return performance

        elif adequacy == AdequacyStatus.OPTIMAL:
            performance = "Excellent - Optimal size for pattern learning"
            if quality:
                if quality.diversity_score > 80:
                    performance += " with high diversity"
                elif quality.overfitting_risk != "low":
                    performance += ", though quality improvements possible"
            return performance

        else:  # EXCESSIVE
            return "Excellent - Large dataset, though additional data may not improve results significantly"

    def _estimate_training_time(self, dataset_size: int, model_size: float) -> str:
        """Estimate training time"""
        # Very rough estimates based on typical fine-tuning scenarios
        # Actual time depends heavily on hardware, batch size, epochs, etc.

        # Base time per example (in seconds)
        base_time_per_example = 0.1

        # Model size multiplier
        if model_size >= 70:
            model_multiplier = 8.0
        elif model_size >= 30:
            model_multiplier = 4.0
        elif model_size >= 13:
            model_multiplier = 2.0
        elif model_size >= 7:
            model_multiplier = 1.0
        else:
            model_multiplier = 0.5

        # Typical epochs
        epochs = 3

        total_seconds = dataset_size * base_time_per_example * model_multiplier * epochs

        if total_seconds < 60:
            return f"~{int(total_seconds)} seconds"
        elif total_seconds < 3600:
            return f"~{int(total_seconds / 60)} minutes"
        else:
            hours = total_seconds / 3600
            return f"~{hours:.1f} hours"

    def _estimate_cost(self, dataset_size: int, model_size: float) -> Optional[str]:
        """Estimate training cost (if using cloud resources)"""
        # This is very approximate and depends on cloud provider
        # Return None for local training

        # Assuming GPU time costs ~$1-3/hour for consumer GPUs
        # and ~$5-10/hour for high-end GPUs

        # For now, return None as costs vary too much
        # In production, this could be parameterized
        return None

    def _suggest_augmentation_strategies(
        self,
        complexity: ComplexityAnalysis,
        current_size: int,
        estimates: SizeEstimate,
        quality: Optional[QualityMetrics]
    ) -> List[str]:
        """Suggest data augmentation strategies"""
        strategies = []

        # If dataset is too small, suggest generation strategies
        if current_size < estimates.optimal:
            strategies.append(
                "Generate additional examples using AI synthesis with varied prompts"
            )

            if complexity.complexity_level in [ComplexityLevel.SIMPLE, ComplexityLevel.TRIVIAL]:
                strategies.append(
                    "Use template-based generation with variable substitution"
                )

            strategies.append(
                "Create variations by modifying existing examples (paraphrasing, reordering)"
            )

        # Quality-based augmentation
        if quality:
            if quality.diversity_score < 70:
                strategies.append(
                    "Increase diversity by generating examples from different perspectives or scenarios"
                )
                strategies.append(
                    "Use multiple AI providers to generate varied responses"
                )

            if quality.variance_score < 50:
                strategies.append(
                    "Generate examples of varying complexity and length"
                )

        # Complexity-based augmentation
        if complexity.reasoning_required:
            strategies.append(
                "Create multi-step reasoning examples with intermediate steps"
            )

        if complexity.domain_specific:
            strategies.append(
                "Include domain-specific edge cases and terminology variations"
            )

        if complexity.unique_tags > 5:
            strategies.append(
                "Ensure all tag combinations are represented in the dataset"
            )

        return strategies


def analyze_dataset(
    dataset_path: str,
    xml_pattern: Optional[XMLPattern] = None,
    base_model: str = "qwen2.5:7b",
    objective: str = "",
    output_format: str = "text"
) -> str:
    """
    Convenience function to analyze a dataset and return a report

    Args:
        dataset_path: Path to dataset file
        xml_pattern: XML pattern specification
        base_model: Base model identifier
        objective: Training objective description
        output_format: Output format ("text" or "json")

    Returns:
        Analysis report as string
    """
    analyzer = DatasetSizeAnalyzer(
        xml_pattern=xml_pattern,
        base_model=base_model,
        objective=objective
    )

    report = analyzer.analyze(dataset_path=dataset_path)

    if output_format == "json":
        return json.dumps(report.to_dict(), indent=2)
    else:
        return str(report)


# Example usage
if __name__ == "__main__":
    # Example 1: Simple format change
    simple_pattern = XMLPattern(
        schema="<thinking>...</thinking><answer>...</answer>",
        required_tags=["thinking", "answer"]
    )

    analyzer = DatasetSizeAnalyzer(
        xml_pattern=simple_pattern,
        base_model="qwen2.5:7b",
        objective="Teach model to show reasoning before answering"
    )

    # Analyze without existing dataset
    report = analyzer.analyze()
    print(report)
    print("\n" + "=" * 80 + "\n")

    # Example 2: Complex Minecraft command formatting
    minecraft_pattern = XMLPattern(
        schema="""
        <thinking>
            <analysis>...</analysis>
            <command_structure>...</command_structure>
        </thinking>
        <minecraft_command>...</minecraft_command>
        """,
        required_tags=["thinking", "analysis", "command_structure", "minecraft_command"]
    )

    analyzer2 = DatasetSizeAnalyzer(
        xml_pattern=minecraft_pattern,
        base_model="qwen2.5:14b",
        objective="Teach Minecraft command formatting with reasoning",
        finetuning_strength=FinetuningStrength.MODERATE,
        lora_rank=64,
        pattern_description="Complex multi-tag structure requiring domain knowledge of Minecraft commands"
    )

    # Analyze with hypothetical dataset
    # report2 = analyzer2.analyze(dataset_path="minecraft_commands.jsonl")
    # print(report2)
