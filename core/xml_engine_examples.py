"""
Practical usage examples for the XML Pattern Engine.

This file demonstrates real-world scenarios and common use cases.
"""

import importlib.util

# Import the xml_engine module directly
spec = importlib.util.spec_from_file_location("xml_engine", "/home/user/model-train/core/xml_engine.py")
xml_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xml_engine)

XMLTag = xml_engine.XMLTag
XMLPattern = xml_engine.XMLPattern
XMLParser = xml_engine.XMLParser
ConstraintType = xml_engine.ConstraintType


def example_chatbot_pattern():
    """Example: Chatbot response with thinking and speaking."""
    print("EXAMPLE 1: Chatbot Response Pattern")
    print("=" * 70)

    pattern = XMLPattern([
        XMLTag("think", constraint_type="free_form", required=True),
        XMLTag("speak", constraint_type="free_form", required=True),
        XMLTag("emotion", constraint_type="list",
               values=["happy", "sad", "neutral", "excited", "confused"],
               required=False)
    ], name="ChatbotPattern", description="Structured chatbot responses")

    # Generate template
    print("\nTemplate:")
    print(pattern.generate_template())

    # Simulate chatbot response
    bot_response = """
    <think>The user is asking about the weather. I should provide a helpful response
    and check if I have access to current weather data.</think>
    <speak>I'd be happy to help you with the weather! However, I don't have access
    to real-time weather data. You might want to check a weather website or app
    for the most current information.</speak>
    <emotion>neutral</emotion>
    """

    parser = XMLParser(pattern)
    data, validation = parser.parse(bot_response)

    print("\n\nParsed Response:")
    print(f"Validation: {validation.is_valid}")
    for key, value in data.items():
        print(f"\n{key.upper()}:")
        print(f"  {value}")

    print("\n" + "=" * 70 + "\n")


def example_game_agent_pattern():
    """Example: Game agent with actions and parameters."""
    print("EXAMPLE 2: Game Agent Pattern")
    print("=" * 70)

    pattern = XMLPattern([
        XMLTag("analyze", constraint_type="free_form", required=True),
        XMLTag("action", constraint_type="list",
               values=["move", "attack", "defend", "use_item", "interact", "wait"],
               required=True),
        XMLTag("target", constraint_type="free_form", required=False),
        XMLTag("priority", constraint_type="range", min_val=1, max_val=10, required=False)
    ], name="GameAgentPattern")

    print("\nTemplate:")
    print(pattern.generate_template())

    # Simulate game agent decision
    agent_decision = """
    <analyze>Enemy zombie detected at distance 5 blocks. Health at 80%.
    I have a diamond sword equipped. No other threats nearby.</analyze>
    <action>attack</action>
    <target>zombie_01</target>
    <priority>7</priority>
    """

    parser = XMLParser(pattern)
    data, validation = parser.parse(agent_decision)

    print("\n\nParsed Decision:")
    print(f"Validation: {validation.is_valid}")
    for key, value in data.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70 + "\n")


def example_code_generation_pattern():
    """Example: Code generation with language and explanation."""
    print("EXAMPLE 3: Code Generation Pattern")
    print("=" * 70)

    pattern = XMLPattern([
        XMLTag("plan", constraint_type="free_form", required=True),
        XMLTag("language", constraint_type="list",
               values=["python", "javascript", "java", "cpp", "rust", "go"],
               required=True),
        XMLTag("code", constraint_type="free_form", required=True),
        XMLTag("explanation", constraint_type="free_form", required=False),
        XMLTag("complexity", constraint_type="list",
               values=["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)"],
               required=False)
    ], name="CodeGenerationPattern")

    print("\nTemplate:")
    print(pattern.generate_template())

    # Simulate code generation
    generated_code = """
    <plan>Create a function to find the maximum element in a list.
    Use a simple iteration approach to maintain O(n) complexity.</plan>

    <language>python</language>

    <code>
def find_max(numbers):
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val
    </code>

    <explanation>This function iterates through the list once, keeping track
    of the maximum value seen so far. It handles empty lists by returning None.</explanation>

    <complexity>O(n)</complexity>
    """

    parser = XMLParser(pattern)
    data, validation = parser.parse(generated_code)

    print("\n\nParsed Code Generation:")
    print(f"Validation: {validation.is_valid}")
    print(f"\nPlan: {data['plan']}")
    print(f"Language: {data['language']}")
    print(f"Complexity: {data['complexity']}")
    print(f"\nCode:")
    print(data['code'])

    print("\n" + "=" * 70 + "\n")


def example_multi_step_reasoning():
    """Example: Multi-step reasoning with nested structure."""
    print("EXAMPLE 4: Multi-Step Reasoning Pattern")
    print("=" * 70)

    pattern = XMLPattern([
        XMLTag("problem", constraint_type="free_form", required=True),
        XMLTag("reasoning", constraint_type="free_form", required=True, children=[
            XMLTag("step", constraint_type="free_form", required=True),
            XMLTag("step", constraint_type="free_form", required=True),
            XMLTag("step", constraint_type="free_form", required=True)
        ]),
        XMLTag("answer", constraint_type="free_form", required=True),
        XMLTag("confidence", constraint_type="range", min_val=0.0, max_val=1.0, required=True)
    ], name="ReasoningPattern")

    print("\nTemplate:")
    print(pattern.generate_template())

    # Note: Nested step validation is complex; for demonstration
    reasoning_example = """
    <problem>What is 15% of 240?</problem>

    <reasoning>
        <step>Convert 15% to decimal: 15/100 = 0.15</step>
        <step>Multiply: 0.15 × 240 = 36</step>
        <step>Verify: 36/240 = 0.15 = 15%</step>
    </reasoning>

    <answer>36</answer>
    <confidence>0.99</confidence>
    """

    parser = XMLParser(pattern)
    data, validation = parser.parse(reasoning_example)

    print("\n\nParsed Reasoning:")
    print(f"Validation: {validation.is_valid}")
    if validation.errors:
        print(f"Errors: {validation.errors}")

    for key, value in data.items():
        print(f"\n{key.upper()}:")
        print(f"  {value[:100]}..." if value and len(str(value)) > 100 else f"  {value}")

    print("\n" + "=" * 70 + "\n")


def example_sentiment_analysis():
    """Example: Sentiment analysis with scores."""
    print("EXAMPLE 5: Sentiment Analysis Pattern")
    print("=" * 70)

    pattern = XMLPattern([
        XMLTag("text", constraint_type="free_form", required=True),
        XMLTag("sentiment", constraint_type="list",
               values=["positive", "negative", "neutral", "mixed"],
               required=True),
        XMLTag("score", constraint_type="range", min_val=-1.0, max_val=1.0, required=True),
        XMLTag("aspects", constraint_type="free_form", required=False, children=[
            XMLTag("aspect", constraint_type="free_form", required=False)
        ]),
        XMLTag("summary", constraint_type="free_form", required=False)
    ], name="SentimentPattern")

    print("\nTemplate:")
    print(pattern.generate_template())

    analysis = """
    <text>The product quality is excellent, but the shipping was very slow
    and customer service was unhelpful.</text>

    <sentiment>mixed</sentiment>
    <score>0.2</score>

    <aspects>
        <aspect>Quality: positive (excellent)</aspect>
        <aspect>Shipping: negative (very slow)</aspect>
        <aspect>Service: negative (unhelpful)</aspect>
    </aspects>

    <summary>Mixed sentiment with positive product quality offset by
    negative shipping and service experience.</summary>
    """

    parser = XMLParser(pattern)
    data, validation = parser.parse(analysis)

    print("\n\nParsed Analysis:")
    print(f"Validation: {validation.is_valid}")
    for key, value in data.items():
        print(f"  {key}: {value[:80]}..." if value and len(str(value)) > 80 else f"  {key}: {value}")

    print("\n" + "=" * 70 + "\n")


def example_dynamic_pattern_creation():
    """Example: Creating patterns dynamically based on requirements."""
    print("EXAMPLE 6: Dynamic Pattern Creation")
    print("=" * 70)

    # Function to create a pattern based on configuration
    def create_custom_pattern(config):
        tags = []
        for tag_config in config['tags']:
            tag = XMLTag(
                name=tag_config['name'],
                constraint_type=tag_config['type'],
                required=tag_config.get('required', True),
                **tag_config.get('params', {})
            )
            tags.append(tag)

        return XMLPattern(tags, name=config['name'], description=config.get('description', ''))

    # Configuration for a product review pattern
    review_config = {
        'name': 'ProductReviewPattern',
        'description': 'Structured product reviews',
        'tags': [
            {
                'name': 'rating',
                'type': 'range',
                'params': {'min_val': 1, 'max_val': 5},
                'required': True
            },
            {
                'name': 'title',
                'type': 'free_form',
                'required': True
            },
            {
                'name': 'pros',
                'type': 'free_form',
                'required': False
            },
            {
                'name': 'cons',
                'type': 'free_form',
                'required': False
            },
            {
                'name': 'recommendation',
                'type': 'list',
                'params': {'values': ['highly_recommended', 'recommended', 'not_recommended']},
                'required': True
            }
        ]
    }

    pattern = create_custom_pattern(review_config)

    print("\nDynamically Created Pattern:")
    print(pattern.generate_template())

    print("\n" + "=" * 70 + "\n")


def example_validation_strictness():
    """Example: Different validation strictness levels."""
    print("EXAMPLE 7: Validation Strictness")
    print("=" * 70)

    pattern = XMLPattern([
        XMLTag("name", constraint_type="regex", pattern=r"^[A-Z][a-z]+$", required=True),
        XMLTag("age", constraint_type="range", min_val=0, max_val=120, required=True),
        XMLTag("email", constraint_type="regex",
               pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
               required=False)
    ], name="UserDataPattern")

    # Valid data
    valid_data = """
    <name>John</name>
    <age>30</age>
    <email>john@example.com</email>
    """

    # Invalid data - age out of range
    invalid_data = """
    <name>Jane</name>
    <age>150</age>
    <email>jane@example.com</email>
    """

    parser = XMLParser(pattern)

    print("\n1. Strict parsing (raises exception on invalid):")
    try:
        result = parser.parse_to_dict(valid_data, strict=True)
        print(f"   Valid data parsed successfully")
        print(f"   Data: {result['data']}")
    except ValueError as e:
        print(f"   Error: {e}")

    print("\n2. Lenient parsing (returns errors without exception):")
    result = parser.parse_to_dict(invalid_data, strict=False)
    print(f"   Valid: {result['is_valid']}")
    print(f"   Errors: {result['errors']}")
    print(f"   Data still extracted: {result['data']}")

    print("\n" + "=" * 70 + "\n")


def example_template_generation():
    """Example: Generating templates for documentation."""
    print("EXAMPLE 8: Template Generation for Documentation")
    print("=" * 70)

    pattern = XMLPattern([
        XMLTag("query", constraint_type="free_form", required=True),
        XMLTag("response_type", constraint_type="list",
               values=["factual", "opinion", "instruction", "creative"],
               required=True),
        XMLTag("response", constraint_type="free_form", required=True),
        XMLTag("sources", constraint_type="free_form", required=False)
    ], name="QAPattern")

    print("\nTemplate with optional tags:")
    print(pattern.generate_template(include_optional=True))

    print("\n\nTemplate without optional tags:")
    print(pattern.generate_template(include_optional=False))

    print("\n\nMultiple example variations:")
    examples = pattern.generate_examples(count=3)
    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print(example)

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("XML PATTERN ENGINE - PRACTICAL USAGE EXAMPLES")
    print("=" * 70 + "\n")

    example_chatbot_pattern()
    example_game_agent_pattern()
    example_code_generation_pattern()
    example_multi_step_reasoning()
    example_sentiment_analysis()
    example_dynamic_pattern_creation()
    example_validation_strictness()
    example_template_generation()

    print("=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)
