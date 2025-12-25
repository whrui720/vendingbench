# VendingBench Tutorial

This tutorial will guide you through using the VendingBench framework to test LLM long-term coherence.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Understanding the Core Concepts](#understanding-the-core-concepts)
4. [Creating Your First Scenario](#creating-your-first-scenario)
5. [Running Tests with Different LLMs](#running-tests-with-different-llms)
6. [Evaluating Results](#evaluating-results)
7. [Advanced Topics](#advanced-topics)

## Installation

### Basic Setup

```bash
# Clone the repository
git clone https://github.com/whrui720/vendingbench.git
cd vendingbench

# Install the package
pip install -e .
```

### For Development

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

### For Specific LLM Providers

```bash
# OpenAI
pip install -e ".[openai]"

# All providers
pip install -e ".[openai,anthropic,cohere]"
```

## Quick Start

Let's run a simple test to verify everything is working:

```python
from vendingbench.adapters.mock_llm import MockLLM
from vendingbench.core.conversation import ConversationManager
from vendingbench.core.evaluator import Evaluator
from vendingbench.scenarios.vending_machine import create_basic_vending_scenario

# 1. Create an LLM adapter (using mock for this example)
llm = MockLLM(model_name="test-model")

# 2. Load a pre-built scenario
scenario = create_basic_vending_scenario()

# 3. Run the scenario
manager = ConversationManager(llm)
history = manager.run_scenario(scenario, verbose=True)

# 4. Evaluate the results
evaluator = Evaluator()
result = evaluator.evaluate(history, scenario)

# 5. Print results
print(f"Pass Rate: {result.calculate_pass_rate():.2%}")
print(f"Overall: {'PASSED' if result.overall_passed else 'FAILED'}")
```

Save this as `my_first_test.py` and run it:

```bash
python my_first_test.py
```

## Understanding the Core Concepts

### 1. LLM Interface

The `LLMInterface` is an abstract base class that provides a uniform way to interact with different LLM providers.

**Key methods:**
- `generate()`: Generate a single response
- `generate_stream()`: Generate a streaming response
- `validate_messages()`: Validate message format

### 2. Scenarios

A scenario defines a test case consisting of:
- **Configuration**: Name, description, system prompt, parameters
- **Turns**: Sequence of conversation exchanges
- **Validators**: Functions to check custom conditions

### 3. Conversation Manager

The `ConversationManager` executes scenarios and maintains conversation state.

### 4. Evaluator

The `Evaluator` checks if responses match expected patterns and runs custom validators.

## Creating Your First Scenario

Let's create a custom scenario to test a simple calculator:

```python
from vendingbench.core.scenario import Scenario, ScenarioConfig

# Define the scenario configuration
config = ScenarioConfig(
    name="calculator_test",
    description="Test if LLM can perform arithmetic consistently",
    system_prompt="You are a calculator. Perform arithmetic operations accurately.",
    temperature=0.7,
)

# Create the scenario
scenario = Scenario(config)

# Add conversation turns with expected patterns
scenario.add_user_input(
    "What is 5 + 3?",
    expected_patterns=["8", "eight"]
)

scenario.add_user_input(
    "What is 10 - 2?",
    expected_patterns=["8", "eight"]
)

scenario.add_user_input(
    "Are the previous two results the same?",
    expected_patterns=["yes", "same", "equal", "both are 8"]
)

# Add a custom validator
def check_consistency(history, scenario):
    """Check if the LLM correctly identifies the pattern."""
    # This is a simplified example
    last_response = history.get_last_response()
    if last_response:
        content = last_response.content.lower()
        return any(word in content for word in ["yes", "same", "equal"])
    return False

scenario.add_validator(check_consistency)
```

Now run this scenario:

```python
from vendingbench.adapters.mock_llm import MockLLM
from vendingbench.core.conversation import ConversationManager
from vendingbench.core.evaluator import Evaluator

# Create mock responses for testing
mock_responses = [
    "The answer is 8.",
    "10 - 2 = 8",
    "Yes, both results are 8, so they are the same."
]

llm = MockLLM(responses=mock_responses)
manager = ConversationManager(llm)
history = manager.run_scenario(scenario, verbose=True)

evaluator = Evaluator()
result = evaluator.evaluate(history, scenario)

print(f"\nScenario: {result.scenario_name}")
print(f"Pass Rate: {result.calculate_pass_rate():.2%}")
for metric in result.metrics:
    print(f"  {metric.name}: {'✓' if metric.passed else '✗'}")
```

## Running Tests with Different LLMs

### Using OpenAI

```python
from vendingbench.adapters.openai_adapter import OpenAIAdapter
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-key-here"

# Create the adapter
llm = OpenAIAdapter(model_name="gpt-3.5-turbo")

# Run any scenario
manager = ConversationManager(llm)
history = manager.run_scenario(scenario, verbose=True)
```

### Using a Custom LLM

To use your own LLM, implement the `LLMInterface`:

```python
from vendingbench.core.llm_interface import LLMInterface, LLMResponse
from typing import List, Dict, Optional

class MyCustomLLM(LLMInterface):
    def __init__(self, model_name: str = "my-model", **kwargs):
        super().__init__(model_name, **kwargs)
        # Initialize your model here
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        # Call your model's API
        # Extract the response
        # Return LLMResponse
        
        content = "Your model's response here"
        
        return LLMResponse(
            content=content,
            model=self.model_name,
            metadata={"temperature": temperature}
        )
    
    def generate_stream(self, messages, temperature=0.7, max_tokens=None, **kwargs):
        # Implement streaming if your model supports it
        response = self.generate(messages, temperature, max_tokens, **kwargs)
        yield response.content

# Use it
llm = MyCustomLLM()
manager = ConversationManager(llm)
```

## Evaluating Results

### Understanding Metrics

Each metric has:
- **Name**: Identifier for the metric
- **Value**: Score from 0.0 to 1.0
- **Passed**: Boolean indicating pass/fail
- **Details**: Additional information about the metric

### Accessing Results

```python
result = evaluator.evaluate(history, scenario)

# Overall statistics
print(f"Pass Rate: {result.calculate_pass_rate():.2%}")
print(f"Total Metrics: {len(result.metrics)}")

# Individual metrics
for metric in result.metrics:
    print(f"\n{metric.name}:")
    print(f"  Passed: {metric.passed}")
    print(f"  Value: {metric.value:.2f}")
    
    # Pattern matching details
    if "pattern_match" in metric.name:
        if metric.details.get("matched"):
            print(f"  Matched: {metric.details['matched']}")
        if metric.details.get("missing"):
            print(f"  Missing: {metric.details['missing']}")
```

### Saving Results

```python
from vendingbench.utils.export import (
    save_evaluation_result,
    save_conversation_history,
    save_batch_results
)

# Save individual result
save_evaluation_result(result, "results/my_test_result.json")
save_conversation_history(history, "results/my_test_history.json")

# Save multiple results
results = [result1, result2, result3]
save_batch_results(results, "results", "batch_test")
```

## Advanced Topics

### Custom Validators

Validators allow you to check complex conditions:

```python
def check_price_calculation(history, scenario):
    """Verify that price calculations are correct."""
    import re
    
    for response in history.responses:
        # Extract all dollar amounts
        prices = re.findall(r'\$(\d+\.\d{2})', response.content)
        
        # Verify they make sense
        for price in prices:
            if float(price) < 0:
                return False
    
    return True

scenario.add_validator(check_price_calculation)
```

### Pattern Matching Tips

```python
# Use regex for flexible matching
scenario.add_user_input(
    "What's the total?",
    expected_patterns=[
        r"\$\d+\.\d{2}",  # Match currency format
        r"\btotal\b",      # Match word "total"
    ]
)

# Case insensitive by default
scenario.add_user_input(
    "What colors are available?",
    expected_patterns=["red", "blue", "green"]  # Matches RED, Blue, etc.
)
```

### State Checks

Use state checks to verify the model maintains context:

```python
scenario.add_user_input("Buy item A1")
scenario.add_user_input("Buy item A1")

scenario.add_state_check(
    "Verify inventory decreased",
    expected_patterns=["2 remaining", "2 left"]
)
```

### Batch Testing

Run multiple scenarios in batch:

```python
from vendingbench.scenarios.vending_machine import (
    create_basic_vending_scenario,
    create_complex_vending_scenario,
    create_edge_case_scenario
)

scenarios = [
    create_basic_vending_scenario(),
    create_complex_vending_scenario(),
    create_edge_case_scenario(),
]

results = []
for scenario in scenarios:
    print(f"\nRunning: {scenario.config.name}")
    history = manager.run_scenario(scenario)
    result = evaluator.evaluate(history, scenario)
    results.append(result)
    print(f"Pass Rate: {result.calculate_pass_rate():.2%}")

# Save all results
save_batch_results(results, "results/batch_test", "vending_scenarios")
```

### Comparing Models

Test the same scenario with different models:

```python
from vendingbench.adapters.mock_llm import MockLLM
from vendingbench.adapters.openai_adapter import OpenAIAdapter

models = [
    MockLLM(model_name="mock"),
    OpenAIAdapter(model_name="gpt-3.5-turbo"),
    OpenAIAdapter(model_name="gpt-4"),
]

scenario = create_basic_vending_scenario()
results = []

for llm in models:
    manager = ConversationManager(llm)
    history = manager.run_scenario(scenario)
    result = evaluator.evaluate(history, scenario)
    results.append(result)

# Compare results
for result in results:
    print(f"{result.model_name}: {result.calculate_pass_rate():.2%}")
```

## Next Steps

- Explore the [API Reference](API.md) for detailed documentation
- Check out more [examples](../examples/) in the repository
- Read the [Developer Guide](DEVELOPER_GUIDE.md) to extend the framework
- Join the community and contribute new scenarios!

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:
```bash
pip install -e .
```

### API Key Issues

For OpenAI or other providers:
```bash
export OPENAI_API_KEY='your-key-here'
# Or set in Python
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"
```

### Test Failures

Enable verbose mode to see what's happening:
```python
history = manager.run_scenario(scenario, verbose=True)
```

Check individual responses:
```python
for i, response in enumerate(history.responses):
    print(f"Turn {i+1}: {response.content[:100]}...")
```
