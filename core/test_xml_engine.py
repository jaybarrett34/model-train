"""
Comprehensive test suite for XML Pattern Engine.

Demonstrates advanced features and edge cases.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, '/home/user/model-train')

# Import directly from the module file to avoid __init__.py dependencies
import importlib.util
spec = importlib.util.spec_from_file_location("xml_engine", "/home/user/model-train/core/xml_engine.py")
xml_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xml_engine)

# Import all required classes
XMLTag = xml_engine.XMLTag
XMLPattern = xml_engine.XMLPattern
XMLParser = xml_engine.XMLParser
ConstraintType = xml_engine.ConstraintType
create_simple_pattern = xml_engine.create_simple_pattern
create_nested_pattern = xml_engine.create_nested_pattern
ValidationResult = xml_engine.ValidationResult
ConstraintValidator = xml_engine.ConstraintValidator


def test_constraint_validators():
    """Test all constraint validator types."""
    print("Testing Constraint Validators")
    print("=" * 60)

    validator = ConstraintValidator()

    # Test regex
    result = validator.validate_regex("Hello World", r"^Hello.*")
    print(f"Regex validation (valid): {result.is_valid}")

    result = validator.validate_regex("Goodbye", r"^Hello.*")
    print(f"Regex validation (invalid): {result.is_valid}, errors: {result.errors}")

    # Test list
    result = validator.validate_list("apple", ["apple", "banana", "cherry"])
    print(f"List validation (valid): {result.is_valid}")

    result = validator.validate_list("orange", ["apple", "banana", "cherry"])
    print(f"List validation (invalid): {result.is_valid}, errors: {result.errors}")

    # Test range
    result = validator.validate_range("50", 0, 100)
    print(f"Range validation (valid): {result.is_valid}")

    result = validator.validate_range("150", 0, 100)
    print(f"Range validation (invalid): {result.is_valid}, errors: {result.errors}")

    print()


def test_nested_structures():
    """Test deeply nested tag structures."""
    print("Testing Nested Structures")
    print("=" * 60)

    # Create a complex nested structure
    pattern = XMLPattern([
        XMLTag("game_state", constraint_type="free_form", required=True, children=[
            XMLTag("player", constraint_type="free_form", required=True, children=[
                XMLTag("position", constraint_type="regex",
                       pattern=r"^\(\d+,\s*\d+,\s*\d+\)$", required=True),
                XMLTag("health", constraint_type="range",
                       min_val=0, max_val=100, required=True),
                XMLTag("inventory", constraint_type="free_form", required=False)
            ]),
            XMLTag("enemies", constraint_type="free_form", required=False, children=[
                XMLTag("enemy", constraint_type="list",
                       values=["zombie", "skeleton", "creeper"], required=True)
            ])
        ])
    ], name="GameStatePattern")

    print(pattern.generate_template())

    # Test valid nested XML
    valid_nested = """
    <game_state>
        <player>
            <position>(10, 20, 30)</position>
            <health>75</health>
            <inventory>diamond sword, iron armor</inventory>
        </player>
        <enemies>
            <enemy>zombie</enemy>
        </enemies>
    </game_state>
    """

    result = pattern.validate(valid_nested)
    print(f"\nNested validation result: {result.is_valid}")
    if not result.is_valid:
        print(f"Errors: {result.errors}")

    print()


def test_xml_attributes():
    """Test XML tags with attributes."""
    print("Testing XML Attributes")
    print("=" * 60)

    pattern = XMLPattern([
        XMLTag("message", constraint_type="free_form", required=True,
               attributes={"priority": "high", "timestamp": "2025-11-13"}),
        XMLTag("user", constraint_type="regex", pattern=r"^[a-z]+$",
               attributes={"id": "12345"}, required=True)
    ], name="AttributePattern")

    print(pattern.generate_template())
    print()


def test_multiple_examples():
    """Test generating multiple random examples."""
    print("Testing Multiple Example Generation")
    print("=" * 60)

    pattern = XMLPattern([
        XMLTag("action", constraint_type="random_list",
               values=["move_forward", "turn_left", "turn_right", "jump"], required=True),
        XMLTag("speed", constraint_type="range", min_val=1, max_val=10, required=True),
        XMLTag("comment", constraint_type="free_form", required=False)
    ], name="ActionPattern")

    examples = pattern.generate_examples(count=5)
    for i, example in enumerate(examples, 1):
        print(f"Example {i}:")
        print(example)
        print()


def test_parser_extraction():
    """Test parser's ability to extract XML from mixed content."""
    print("Testing Parser Extraction")
    print("=" * 60)

    pattern = XMLPattern([
        XMLTag("analysis", constraint_type="free_form", required=True),
        XMLTag("decision", constraint_type="list",
               values=["approve", "reject", "pending"], required=True),
        XMLTag("confidence", constraint_type="range",
               min_val=0.0, max_val=1.0, required=False)
    ])

    parser = XMLParser(pattern)

    # Mixed content with XML tags embedded
    mixed_text = """
    After careful consideration, here is my analysis:

    <analysis>
    The proposal shows strong technical merit and addresses key concerns.
    However, the timeline seems aggressive and may need adjustment.
    </analysis>

    Based on this analysis, my decision is:
    <decision>pending</decision>

    I have a confidence level of:
    <confidence>0.75</confidence>

    Additional notes: We should schedule a follow-up meeting.
    """

    extracted_data, validation = parser.parse(mixed_text)

    print("Extracted data from mixed content:")
    for tag_name, content in extracted_data.items():
        print(f"  {tag_name}: {content[:50]}..." if len(str(content)) > 50 else f"  {tag_name}: {content}")

    print(f"\nValidation: {validation.is_valid}")
    if not validation.is_valid:
        print(f"Errors: {validation.errors}")

    print()


def test_error_handling():
    """Test error handling and validation failures."""
    print("Testing Error Handling")
    print("=" * 60)

    pattern = XMLPattern([
        XMLTag("required_field", constraint_type="free_form", required=True),
        XMLTag("email", constraint_type="regex",
               pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", required=True)
    ])

    # Missing required field
    invalid_xml1 = "<email>test@example.com</email>"
    result1 = pattern.validate(invalid_xml1)
    print(f"Missing required field - Valid: {result1.is_valid}")
    print(f"Errors: {result1.errors}")

    # Invalid regex pattern
    invalid_xml2 = """
    <required_field>Some content</required_field>
    <email>not-an-email</email>
    """
    result2 = pattern.validate(invalid_xml2)
    print(f"\nInvalid regex - Valid: {result2.is_valid}")
    print(f"Errors: {result2.errors}")

    # Malformed XML
    malformed_xml = "<required_field>Unclosed tag"
    result3 = pattern.validate(malformed_xml)
    print(f"\nMalformed XML - Valid: {result3.is_valid}")
    print(f"Errors: {result3.errors}")

    print()


def test_convenience_functions():
    """Test convenience functions for pattern creation."""
    print("Testing Convenience Functions")
    print("=" * 60)

    # Simple pattern creation
    simple = create_simple_pattern([
        {'name': 'title', 'constraint_type': 'free_form', 'required': True},
        {'name': 'status', 'constraint_type': 'list',
         'values': ['active', 'inactive'], 'required': True}
    ], name="SimpleConveniencePattern")

    print("Simple pattern created via convenience function:")
    print(simple.generate_template())

    # Nested pattern creation
    nested = create_nested_pattern(
        parent_name='container',
        parent_type='free_form',
        children_configs=[
            {'name': 'item1', 'constraint_type': 'free_form'},
            {'name': 'item2', 'constraint_type': 'free_form'}
        ]
    )

    print("\nNested pattern created via convenience function:")
    print(nested.generate_template())

    print()


def test_pattern_serialization():
    """Test converting patterns to/from dictionaries."""
    print("Testing Pattern Serialization")
    print("=" * 60)

    pattern = XMLPattern([
        XMLTag("field1", constraint_type="list", values=["a", "b", "c"], required=True),
        XMLTag("field2", constraint_type="range", min_val=0, max_val=100, required=False)
    ], name="SerializablePattern", description="A pattern that can be serialized")

    # Convert to dictionary
    pattern_dict = pattern.to_dict()

    print("Pattern as dictionary:")
    import json
    print(json.dumps(pattern_dict, indent=2))

    print()


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("Testing Edge Cases")
    print("=" * 60)

    # Empty content
    pattern = XMLPattern([
        XMLTag("empty", constraint_type="free_form", required=True)
    ])

    empty_xml = "<empty></empty>"
    result = pattern.validate(empty_xml)
    print(f"Empty content validation: {result.is_valid}")

    # Very long content
    long_content = "x" * 10000
    long_xml = f"<empty>{long_content}</empty>"
    result = pattern.validate(long_xml)
    print(f"Long content validation: {result.is_valid}")

    # Special characters
    special_xml = "<empty>&lt;special&gt; chars &amp; entities</empty>"
    result = pattern.validate(special_xml)
    print(f"Special characters validation: {result.is_valid}")

    # Whitespace handling
    whitespace_xml = "<empty>   \n\t   </empty>"
    result = pattern.validate(whitespace_xml)
    print(f"Whitespace validation: {result.is_valid}")

    print()


def test_real_world_scenario():
    """Test a real-world AI agent response pattern."""
    print("Testing Real-World AI Agent Scenario")
    print("=" * 60)

    # Define a comprehensive AI agent pattern
    agent_pattern = XMLPattern([
        XMLTag("observation", constraint_type="free_form", required=True),
        XMLTag("reasoning", constraint_type="free_form", required=True, children=[
            XMLTag("step", constraint_type="free_form", required=True),
            XMLTag("conclusion", constraint_type="free_form", required=True)
        ]),
        XMLTag("action", constraint_type="list",
               values=["move", "pickup", "place", "craft", "attack", "wait"],
               required=True),
        XMLTag("parameters", constraint_type="free_form", required=False),
        XMLTag("expected_outcome", constraint_type="free_form", required=False)
    ], name="AIAgentPattern", description="Pattern for structured AI agent responses")

    print("Agent Pattern Template:")
    print(agent_pattern.generate_template())

    # Simulate an AI agent response
    agent_response = """
    <observation>I see a diamond ore block at coordinates (15, 12, -8).
    I have a diamond pickaxe in my inventory.</observation>

    <reasoning>
        <step>The diamond ore requires a diamond pickaxe to mine</step>
        <step>I have the required tool in my inventory</step>
        <step>Mining the ore will give me diamonds</step>
        <conclusion>I should mine this diamond ore block</conclusion>
    </reasoning>

    <action>pickup</action>

    <parameters>target_block: diamond_ore, coordinates: (15, 12, -8), tool: diamond_pickaxe</parameters>

    <expected_outcome>Successfully mine diamond ore and add diamonds to inventory</expected_outcome>
    """

    parser = XMLParser(agent_pattern)
    result_dict = parser.parse_to_dict(agent_response, strict=False)

    print("\nParsed Agent Response:")
    print(f"Valid: {result_dict['is_valid']}")
    print(f"Message: {result_dict['message']}")
    print("\nExtracted Data:")
    for key, value in result_dict['data'].items():
        print(f"  {key}: {value[:60]}..." if value and len(str(value)) > 60 else f"  {key}: {value}")

    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("XML PATTERN ENGINE - COMPREHENSIVE TEST SUITE")
    print("=" * 60 + "\n")

    test_constraint_validators()
    test_nested_structures()
    test_xml_attributes()
    test_multiple_examples()
    test_parser_extraction()
    test_error_handling()
    test_convenience_functions()
    test_pattern_serialization()
    test_edge_cases()
    test_real_world_scenario()

    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
