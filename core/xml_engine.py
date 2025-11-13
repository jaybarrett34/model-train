"""
Robust XML Pattern Engine for defining, validating, and parsing structured XML patterns.

This module provides a comprehensive framework for creating XML-based patterns with
various constraint types, nested structures, and validation capabilities.
"""

import re
import random
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import xml.etree.ElementTree as ET
from xml.dom import minidom


class ConstraintType(Enum):
    """Enumeration of supported constraint types."""
    REGEX = "regex"
    LIST = "list"
    RANGE = "range"
    RANDOM_LIST = "random_list"
    FREE_FORM = "free_form"


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    message: str = ""
    errors: List[str] = field(default_factory=list)


class ConstraintValidator:
    """
    Validates content against various constraint types.

    Supports regex patterns, list membership, numeric ranges,
    and nested tag validation.
    """

    @staticmethod
    def validate_regex(content: str, pattern: str) -> ValidationResult:
        """
        Validate content against a regex pattern.

        Args:
            content: The content to validate
            pattern: The regex pattern to match against

        Returns:
            ValidationResult indicating success or failure
        """
        try:
            if re.match(pattern, content, re.DOTALL):
                return ValidationResult(
                    is_valid=True,
                    message="Content matches regex pattern"
                )
            else:
                return ValidationResult(
                    is_valid=False,
                    message=f"Content does not match pattern: {pattern}",
                    errors=[f"Expected pattern: {pattern}, got: {content[:100]}..."]
                )
        except re.error as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid regex pattern: {e}",
                errors=[str(e)]
            )

    @staticmethod
    def validate_list(content: str, values: List[str]) -> ValidationResult:
        """
        Validate that content is in a predefined list of values.

        Args:
            content: The content to validate
            values: List of valid values

        Returns:
            ValidationResult indicating success or failure
        """
        if content in values:
            return ValidationResult(
                is_valid=True,
                message="Content is in valid list"
            )
        else:
            return ValidationResult(
                is_valid=False,
                message=f"Content not in valid list",
                errors=[f"Expected one of {values}, got: {content}"]
            )

    @staticmethod
    def validate_range(content: str, min_val: float, max_val: float) -> ValidationResult:
        """
        Validate that content is a number within a specified range.

        Args:
            content: The content to validate (should be numeric)
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            ValidationResult indicating success or failure
        """
        try:
            num_val = float(content)
            if min_val <= num_val <= max_val:
                return ValidationResult(
                    is_valid=True,
                    message=f"Value {num_val} is within range [{min_val}, {max_val}]"
                )
            else:
                return ValidationResult(
                    is_valid=False,
                    message=f"Value out of range",
                    errors=[f"Expected value in [{min_val}, {max_val}], got: {num_val}"]
                )
        except ValueError:
            return ValidationResult(
                is_valid=False,
                message="Content is not a valid number",
                errors=[f"Expected numeric value, got: {content}"]
            )

    @staticmethod
    def validate_free_form(content: str) -> ValidationResult:
        """
        Validate free-form content (always passes).

        Args:
            content: The content to validate

        Returns:
            ValidationResult that always succeeds
        """
        return ValidationResult(
            is_valid=True,
            message="Free-form content accepted"
        )


class XMLTag:
    """
    Represents a single XML tag with constraints and optional nested children.

    Attributes:
        name: Tag name (e.g., "think", "command", "speak")
        constraint_type: Type of constraint to apply
        required: Whether this tag is required in the pattern
        children: List of nested child tags
        constraint_params: Parameters for the constraint (pattern, values, min, max)
        attributes: Optional XML attributes for the tag
    """

    def __init__(
        self,
        name: str,
        constraint_type: Union[ConstraintType, str] = ConstraintType.FREE_FORM,
        required: bool = True,
        children: Optional[List['XMLTag']] = None,
        **constraint_params
    ):
        """
        Initialize an XMLTag.

        Args:
            name: Tag name
            constraint_type: Type of constraint (enum or string)
            required: Whether tag is required
            children: List of nested child tags
            **constraint_params: Additional constraint parameters:
                - pattern: For regex constraints
                - values: For list/random_list constraints
                - min_val, max_val: For range constraints
                - attributes: Dict of XML attributes
        """
        self.name = name
        self.constraint_type = (
            constraint_type if isinstance(constraint_type, ConstraintType)
            else ConstraintType(constraint_type)
        )
        self.required = required
        self.children = children or []
        self.constraint_params = constraint_params
        self.attributes = constraint_params.get('attributes', {})

        # Validate constraint parameters
        self._validate_constraint_params()

    def _validate_constraint_params(self) -> None:
        """Validate that required constraint parameters are provided."""
        if self.constraint_type == ConstraintType.REGEX:
            if 'pattern' not in self.constraint_params:
                raise ValueError(f"Tag '{self.name}': regex constraint requires 'pattern' parameter")

        elif self.constraint_type in [ConstraintType.LIST, ConstraintType.RANDOM_LIST]:
            if 'values' not in self.constraint_params:
                raise ValueError(f"Tag '{self.name}': list constraint requires 'values' parameter")
            if not isinstance(self.constraint_params['values'], list):
                raise ValueError(f"Tag '{self.name}': 'values' must be a list")

        elif self.constraint_type == ConstraintType.RANGE:
            if 'min_val' not in self.constraint_params or 'max_val' not in self.constraint_params:
                raise ValueError(f"Tag '{self.name}': range constraint requires 'min_val' and 'max_val' parameters")

    def validate_content(self, content: str) -> ValidationResult:
        """
        Validate content against this tag's constraints.

        Args:
            content: The content to validate

        Returns:
            ValidationResult indicating success or failure
        """
        validator = ConstraintValidator()

        if self.constraint_type == ConstraintType.REGEX:
            return validator.validate_regex(content, self.constraint_params['pattern'])

        elif self.constraint_type in [ConstraintType.LIST, ConstraintType.RANDOM_LIST]:
            return validator.validate_list(content.strip(), self.constraint_params['values'])

        elif self.constraint_type == ConstraintType.RANGE:
            return validator.validate_range(
                content.strip(),
                self.constraint_params['min_val'],
                self.constraint_params['max_val']
            )

        elif self.constraint_type == ConstraintType.FREE_FORM:
            return validator.validate_free_form(content)

        return ValidationResult(
            is_valid=False,
            message=f"Unknown constraint type: {self.constraint_type}"
        )

    def generate_example_content(self) -> str:
        """
        Generate example content that satisfies this tag's constraints.

        Returns:
            Example content string
        """
        if self.constraint_type == ConstraintType.REGEX:
            return f"[Content matching: {self.constraint_params['pattern']}]"

        elif self.constraint_type == ConstraintType.LIST:
            values = self.constraint_params['values']
            return values[0] if values else "[empty]"

        elif self.constraint_type == ConstraintType.RANDOM_LIST:
            values = self.constraint_params['values']
            return random.choice(values) if values else "[empty]"

        elif self.constraint_type == ConstraintType.RANGE:
            min_val = self.constraint_params['min_val']
            max_val = self.constraint_params['max_val']
            return str((min_val + max_val) / 2)

        elif self.constraint_type == ConstraintType.FREE_FORM:
            return f"[AI-generated content for {self.name}]"

        return "[content]"

    def generate_template(self, indent_level: int = 0) -> str:
        """
        Generate a template string showing the expected structure.

        Args:
            indent_level: Current indentation level

        Returns:
            Template string with proper indentation
        """
        indent = "  " * indent_level
        attrs = "".join([f' {k}="{v}"' for k, v in self.attributes.items()])

        if self.children:
            lines = [f"{indent}<{self.name}{attrs}>"]
            for child in self.children:
                lines.append(child.generate_template(indent_level + 1))
            lines.append(f"{indent}</{self.name}>")
            return "\n".join(lines)
        else:
            content = self.generate_example_content()
            return f"{indent}<{self.name}{attrs}>{content}</{self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tag to dictionary representation.

        Returns:
            Dictionary with tag configuration
        """
        return {
            'name': self.name,
            'constraint_type': self.constraint_type.value,
            'required': self.required,
            'constraint_params': self.constraint_params,
            'children': [child.to_dict() for child in self.children]
        }

    def __repr__(self) -> str:
        return f"XMLTag(name='{self.name}', type={self.constraint_type.value}, required={self.required})"


class XMLPattern:
    """
    Collection of XML tags forming a complete pattern.

    This class manages a set of tags, generates templates,
    and validates parsed XML against the defined pattern.
    """

    def __init__(
        self,
        tags: List[XMLTag],
        name: str = "UnnamedPattern",
        description: str = ""
    ):
        """
        Initialize an XMLPattern.

        Args:
            tags: List of XMLTag objects defining the pattern
            name: Name of the pattern
            description: Description of the pattern's purpose
        """
        self.tags = tags
        self.name = name
        self.description = description
        self._tag_map = {tag.name: tag for tag in tags}

    def get_tag(self, name: str) -> Optional[XMLTag]:
        """
        Get a tag by name.

        Args:
            name: Tag name to retrieve

        Returns:
            XMLTag if found, None otherwise
        """
        return self._tag_map.get(name)

    def get_required_tags(self) -> List[XMLTag]:
        """
        Get all required tags in the pattern.

        Returns:
            List of required XMLTag objects
        """
        return [tag for tag in self.tags if tag.required]

    def get_optional_tags(self) -> List[XMLTag]:
        """
        Get all optional tags in the pattern.

        Returns:
            List of optional XMLTag objects
        """
        return [tag for tag in self.tags if not tag.required]

    def generate_template(self, include_optional: bool = True) -> str:
        """
        Generate a complete template showing expected structure.

        Args:
            include_optional: Whether to include optional tags

        Returns:
            Template string
        """
        lines = [f"<!-- Pattern: {self.name} -->"]
        if self.description:
            lines.append(f"<!-- {self.description} -->")
        lines.append("")

        for tag in self.tags:
            if tag.required or include_optional:
                lines.append(tag.generate_template())

        return "\n".join(lines)

    def generate_examples(self, count: int = 3) -> List[str]:
        """
        Generate multiple example instances of the pattern.

        Args:
            count: Number of examples to generate

        Returns:
            List of example strings
        """
        examples = []
        for _ in range(count):
            lines = []
            for tag in self.tags:
                if tag.required or random.choice([True, False]):
                    lines.append(tag.generate_template())
            examples.append("\n".join(lines))
        return examples

    def validate(self, xml_string: str) -> ValidationResult:
        """
        Validate an XML string against this pattern.

        Args:
            xml_string: XML string to validate

        Returns:
            ValidationResult with detailed error information
        """
        errors = []

        # Parse XML
        try:
            # Wrap in root element if needed
            if not xml_string.strip().startswith('<?xml'):
                xml_string = f"<root>{xml_string}</root>"

            root = ET.fromstring(xml_string)

            # If we wrapped it, use the children
            elements = list(root) if root.tag == 'root' else [root]

        except ET.ParseError as e:
            return ValidationResult(
                is_valid=False,
                message="XML parsing failed",
                errors=[f"Parse error: {str(e)}"]
            )

        # Check for required tags
        found_tags = {elem.tag for elem in elements}
        required_tags = {tag.name for tag in self.get_required_tags()}
        missing_tags = required_tags - found_tags

        if missing_tags:
            errors.append(f"Missing required tags: {missing_tags}")

        # Validate each element
        for elem in elements:
            tag_def = self.get_tag(elem.tag)
            if tag_def is None:
                errors.append(f"Unknown tag: {elem.tag}")
                continue

            # Validate content
            content = elem.text or ""
            result = tag_def.validate_content(content)

            if not result.is_valid:
                errors.extend([f"Tag '{elem.tag}': {err}" for err in result.errors])

            # Validate children if present
            if tag_def.children:
                child_result = self._validate_children(elem, tag_def)
                if not child_result.is_valid:
                    errors.extend(child_result.errors)

        if errors:
            return ValidationResult(
                is_valid=False,
                message="Validation failed",
                errors=errors
            )

        return ValidationResult(
            is_valid=True,
            message="All validations passed"
        )

    def _validate_children(self, element: ET.Element, tag_def: XMLTag) -> ValidationResult:
        """
        Validate nested children of an element.

        Args:
            element: XML element to validate
            tag_def: Tag definition with children

        Returns:
            ValidationResult for child validation
        """
        errors = []
        found_children = {child.tag for child in element}
        required_children = {child.name for child in tag_def.children if child.required}
        missing_children = required_children - found_children

        if missing_children:
            errors.append(f"Tag '{element.tag}' missing required children: {missing_children}")

        # Validate each child
        for child_elem in element:
            child_def = next((c for c in tag_def.children if c.name == child_elem.tag), None)
            if child_def is None:
                errors.append(f"Unknown child tag '{child_elem.tag}' in '{element.tag}'")
                continue

            content = child_elem.text or ""
            result = child_def.validate_content(content)
            if not result.is_valid:
                errors.extend([f"Child '{child_elem.tag}': {err}" for err in result.errors])

        if errors:
            return ValidationResult(is_valid=False, message="Child validation failed", errors=errors)

        return ValidationResult(is_valid=True, message="Children validated")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pattern to dictionary representation.

        Returns:
            Dictionary with pattern configuration
        """
        return {
            'name': self.name,
            'description': self.description,
            'tags': [tag.to_dict() for tag in self.tags]
        }

    def __repr__(self) -> str:
        return f"XMLPattern(name='{self.name}', tags={len(self.tags)})"


class XMLParser:
    """
    Parser for extracting and validating XML from generated text.

    Handles various XML formats and extracts structured data.
    """

    def __init__(self, pattern: XMLPattern):
        """
        Initialize parser with a pattern.

        Args:
            pattern: XMLPattern to use for validation
        """
        self.pattern = pattern

    def extract_xml_blocks(self, text: str) -> List[str]:
        """
        Extract XML blocks from text.

        Args:
            text: Text potentially containing XML

        Returns:
            List of extracted XML strings
        """
        blocks = []

        # Try to find XML-like patterns for each tag in the pattern
        for tag in self.pattern.tags:
            pattern = rf'<{tag.name}[^>]*>.*?</{tag.name}>'
            matches = re.findall(pattern, text, re.DOTALL)
            blocks.extend(matches)

        return blocks

    def parse(self, text: str) -> Tuple[Dict[str, str], ValidationResult]:
        """
        Parse text and extract tag contents.

        Args:
            text: Text containing XML tags

        Returns:
            Tuple of (extracted_data, validation_result)
            extracted_data is a dict mapping tag names to their content
        """
        extracted_data = {}

        # Extract each tag
        for tag in self.pattern.tags:
            pattern = rf'<{tag.name}[^>]*>(.*?)</{tag.name}>'
            match = re.search(pattern, text, re.DOTALL)

            if match:
                content = match.group(1).strip()
                extracted_data[tag.name] = content
            elif tag.required:
                extracted_data[tag.name] = None

        # Build XML string for validation
        xml_parts = []
        for tag_name, content in extracted_data.items():
            if content is not None:
                xml_parts.append(f"<{tag_name}>{content}</{tag_name}>")

        xml_string = "\n".join(xml_parts)

        # Validate
        validation_result = self.pattern.validate(xml_string)

        return extracted_data, validation_result

    def parse_to_dict(self, text: str, strict: bool = True) -> Dict[str, Any]:
        """
        Parse text and return structured dictionary.

        Args:
            text: Text containing XML tags
            strict: If True, raise exception on validation failure

        Returns:
            Dictionary with parsed data and validation info

        Raises:
            ValueError: If strict=True and validation fails
        """
        extracted_data, validation_result = self.parse(text)

        result = {
            'data': extracted_data,
            'is_valid': validation_result.is_valid,
            'message': validation_result.message,
            'errors': validation_result.errors
        }

        if strict and not validation_result.is_valid:
            raise ValueError(f"Validation failed: {validation_result.errors}")

        return result

    def pretty_print(self, text: str) -> str:
        """
        Extract and pretty-print XML from text.

        Args:
            text: Text containing XML

        Returns:
            Pretty-printed XML string
        """
        blocks = self.extract_xml_blocks(text)

        if not blocks:
            return "No XML found"

        xml_string = "\n".join(blocks)

        try:
            # Parse and pretty print
            root = ET.fromstring(f"<root>{xml_string}</root>")
            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")
        except Exception as e:
            return f"Error pretty-printing: {e}\n\nRaw XML:\n{xml_string}"


# Convenience functions for common patterns

def create_simple_pattern(
    tag_configs: List[Dict[str, Any]],
    name: str = "SimplePattern"
) -> XMLPattern:
    """
    Create a simple pattern from a list of tag configurations.

    Args:
        tag_configs: List of dicts with tag configuration
        name: Pattern name

    Returns:
        XMLPattern instance

    Example:
        pattern = create_simple_pattern([
            {'name': 'think', 'constraint_type': 'free_form'},
            {'name': 'action', 'constraint_type': 'list', 'values': ['move', 'jump', 'run']}
        ])
    """
    tags = []
    for config in tag_configs:
        tag = XMLTag(**config)
        tags.append(tag)

    return XMLPattern(tags, name=name)


def create_nested_pattern(
    parent_name: str,
    parent_type: Union[ConstraintType, str],
    children_configs: List[Dict[str, Any]],
    **parent_params
) -> XMLPattern:
    """
    Create a pattern with nested tags.

    Args:
        parent_name: Name of parent tag
        parent_type: Constraint type for parent
        children_configs: List of child tag configurations
        **parent_params: Additional parent parameters

    Returns:
        XMLPattern with nested structure
    """
    children = [XMLTag(**config) for config in children_configs]
    parent = XMLTag(parent_name, parent_type, children=children, **parent_params)

    return XMLPattern([parent], name=f"{parent_name}_pattern")


if __name__ == "__main__":
    # Example usage demonstrating all features

    print("=" * 60)
    print("XML Pattern Engine - Example Usage")
    print("=" * 60)

    # Example 1: Simple pattern with various constraint types
    print("\n1. Simple Pattern Example:")
    print("-" * 60)

    pattern = XMLPattern([
        XMLTag("think", constraint_type="free_form", required=True),
        XMLTag("command", constraint_type="list",
               values=["/tp ~0 ~1 ~0", "/give @p diamond"], required=True),
        XMLTag("speak", constraint_type="regex",
               pattern=r"^[A-Za-z\s]+$", required=False)
    ], name="MinecraftAgentPattern", description="Pattern for Minecraft agent responses")

    print(pattern.generate_template())

    # Example 2: Nested pattern
    print("\n\n2. Nested Pattern Example:")
    print("-" * 60)

    nested_pattern = XMLPattern([
        XMLTag("response", constraint_type="free_form", required=True, children=[
            XMLTag("reasoning", constraint_type="free_form", required=True),
            XMLTag("action", constraint_type="list",
                   values=["move", "attack", "defend"], required=True),
            XMLTag("confidence", constraint_type="range",
                   min_val=0.0, max_val=1.0, required=False)
        ])
    ], name="NestedResponsePattern")

    print(nested_pattern.generate_template())

    # Example 3: Validation
    print("\n\n3. Validation Example:")
    print("-" * 60)

    valid_xml = """
    <think>I need to teleport the player upward</think>
    <command>/tp ~0 ~1 ~0</command>
    <speak>Teleporting you up</speak>
    """

    result = pattern.validate(valid_xml)
    print(f"Validation result: {result.is_valid}")
    print(f"Message: {result.message}")

    invalid_xml = """
    <think>I need to do something</think>
    <command>/invalid command</command>
    """

    result = pattern.validate(invalid_xml)
    print(f"\nInvalid XML result: {result.is_valid}")
    print(f"Errors: {result.errors}")

    # Example 4: Parsing
    print("\n\n4. Parsing Example:")
    print("-" * 60)

    parser = XMLParser(pattern)
    text = """
    The agent thinks: <think>I should give the player a diamond</think>
    Then executes: <command>/give @p diamond</command>
    And says: <speak>Here is your diamond</speak>
    """

    extracted, validation = parser.parse(text)
    print("Extracted data:")
    for tag_name, content in extracted.items():
        print(f"  {tag_name}: {content}")

    # Example 5: Random list constraint
    print("\n\n5. Random List Example:")
    print("-" * 60)

    random_pattern = XMLPattern([
        XMLTag("greeting", constraint_type="random_list",
               values=["Hello!", "Hi there!", "Greetings!", "Welcome!"], required=True)
    ])

    print("Generated examples with random selection:")
    for i, example in enumerate(random_pattern.generate_examples(5), 1):
        print(f"  Example {i}: {example}")

    print("\n" + "=" * 60)
