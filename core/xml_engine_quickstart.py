"""
Quick Start Guide for XML Pattern Engine

This file provides a minimal quick reference for getting started.
"""

import importlib.util

# Import the xml_engine module
spec = importlib.util.spec_from_file_location("xml_engine", "/home/user/model-train/core/xml_engine.py")
xml_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xml_engine)

XMLTag = xml_engine.XMLTag
XMLPattern = xml_engine.XMLPattern
XMLParser = xml_engine.XMLParser


print("=" * 70)
print("XML PATTERN ENGINE - QUICK START GUIDE")
print("=" * 70)

# ============================================================================
# STEP 1: Define Tags with Constraints
# ============================================================================
print("\nSTEP 1: Define Tags")
print("-" * 70)

# Free-form content (no constraints)
tag1 = XMLTag("think", constraint_type="free_form", required=True)

# List constraint (predefined values)
tag2 = XMLTag("action", constraint_type="list",
              values=["move", "attack", "defend"], required=True)

# Regex constraint (pattern matching)
tag3 = XMLTag("name", constraint_type="regex",
              pattern=r"^[A-Z][a-z]+$", required=False)

# Range constraint (numeric values)
tag4 = XMLTag("score", constraint_type="range",
              min_val=0, max_val=100, required=False)

# Random list (picks randomly from list)
tag5 = XMLTag("greeting", constraint_type="random_list",
              values=["Hello", "Hi", "Hey"], required=False)

print("✓ Tags defined with various constraint types")

# ============================================================================
# STEP 2: Create a Pattern
# ============================================================================
print("\nSTEP 2: Create Pattern")
print("-" * 70)

pattern = XMLPattern(
    tags=[tag1, tag2, tag3],
    name="MyPattern",
    description="Example pattern for quick start"
)

print("✓ Pattern created")

# ============================================================================
# STEP 3: Generate Templates
# ============================================================================
print("\nSTEP 3: Generate Template")
print("-" * 70)

template = pattern.generate_template()
print(template)

# ============================================================================
# STEP 4: Parse and Validate XML
# ============================================================================
print("\n\nSTEP 4: Parse and Validate")
print("-" * 70)

sample_xml = """
<think>I need to move to a safer location</think>
<action>move</action>
<name>Alice</name>
"""

parser = XMLParser(pattern)
extracted_data, validation = parser.parse(sample_xml)

print(f"Valid: {validation.is_valid}")
print(f"Message: {validation.message}")
print("\nExtracted Data:")
for tag, content in extracted_data.items():
    print(f"  {tag}: {content}")

# ============================================================================
# STEP 5: Nested Tags (Advanced)
# ============================================================================
print("\n\nSTEP 5: Nested Tags (Advanced)")
print("-" * 70)

nested_pattern = XMLPattern([
    XMLTag("response", constraint_type="free_form", required=True, children=[
        XMLTag("thought", constraint_type="free_form", required=True),
        XMLTag("action", constraint_type="list",
               values=["yes", "no"], required=True)
    ])
])

print(nested_pattern.generate_template())

# ============================================================================
# CONSTRAINT TYPES SUMMARY
# ============================================================================
print("\n\n" + "=" * 70)
print("CONSTRAINT TYPES REFERENCE")
print("=" * 70)

summary = """
1. FREE_FORM
   - No constraints, accepts any content
   - Use: constraint_type="free_form"

2. LIST
   - Content must be in predefined list
   - Use: constraint_type="list", values=["a", "b", "c"]

3. REGEX
   - Content must match regex pattern
   - Use: constraint_type="regex", pattern=r"^[A-Z].*"

4. RANGE
   - Content must be numeric and within range
   - Use: constraint_type="range", min_val=0, max_val=100

5. RANDOM_LIST
   - Picks random value from list for examples
   - Use: constraint_type="random_list", values=["a", "b", "c"]
"""

print(summary)

# ============================================================================
# KEY METHODS SUMMARY
# ============================================================================
print("=" * 70)
print("KEY METHODS REFERENCE")
print("=" * 70)

methods = """
XMLTag Methods:
  - XMLTag(name, constraint_type, required, **params)
  - tag.validate_content(content) -> ValidationResult
  - tag.generate_template() -> str
  - tag.generate_example_content() -> str

XMLPattern Methods:
  - XMLPattern(tags, name, description)
  - pattern.generate_template(include_optional=True) -> str
  - pattern.generate_examples(count=3) -> List[str]
  - pattern.validate(xml_string) -> ValidationResult
  - pattern.get_tag(name) -> XMLTag
  - pattern.get_required_tags() -> List[XMLTag]
  - pattern.get_optional_tags() -> List[XMLTag]

XMLParser Methods:
  - XMLParser(pattern)
  - parser.parse(text) -> (Dict[str, str], ValidationResult)
  - parser.parse_to_dict(text, strict=True) -> Dict
  - parser.extract_xml_blocks(text) -> List[str]
  - parser.pretty_print(text) -> str

Convenience Functions:
  - create_simple_pattern(tag_configs, name) -> XMLPattern
  - create_nested_pattern(parent_name, parent_type, children_configs) -> XMLPattern
"""

print(methods)

print("=" * 70)
print("For more examples, see:")
print("  - /home/user/model-train/core/xml_engine_examples.py")
print("  - /home/user/model-train/core/test_xml_engine.py")
print("=" * 70)
