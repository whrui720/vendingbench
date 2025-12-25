# VendingBench

A reusable, modular framework for testing Large Language Model (LLM) long-term coherence and consistency using vending machine scenarios and other stateful interactions.

Based on the VendingBench paper ([arXiv:2502.15840](https://arxiv.org/abs/2502.15840)), this framework provides a structured approach to evaluate how well LLMs maintain state, follow constraints, and remain logically consistent over multi-turn conversations.

## Features

- **Model-Agnostic Architecture**: Uniform interface works with any LLM (OpenAI, Anthropic, Cohere, or custom)
- **Scenario-Based Testing**: Define reusable test scenarios with expected behaviors
- **Flexible Evaluation**: Built-in pattern matching and custom validators
- **Conversation Management**: Track and manage multi-turn conversations with state
- **Export & Analysis**: Save results in JSON format for further analysis
- **Extensible Design**: Easy to add new LLM adapters, scenarios, and evaluation metrics

## Installation

### Basic Installation

```bash
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

### With LLM Provider Support

```bash
# For OpenAI
pip install -e ".[openai]"

# For Anthropic
pip install -e ".[anthropic]"

# For Cohere
pip install -e ".[cohere]"

# All providers
pip install -e ".[openai,anthropic,cohere]"
```

## Quick Start

### Basic Example with Mock LLM

```python
from vendingbench.adapters.mock_llm import MockLLM
from vendingbench.core.conversation import ConversationManager
from vendingbench.core.evaluator import Evaluator
from vendingbench.scenarios.vending_machine import create_basic_vending_scenario

# Create a mock LLM for testing
llm = MockLLM(model_name="test-model")

# Load a pre-defined scenario
scenario = create_basic_vending_scenario()

# Run the scenario
manager = ConversationManager(llm)
history = manager.run_scenario(scenario, verbose=True)

# Evaluate the results
evaluator = Evaluator()
result = evaluator.evaluate(history, scenario)

print(f"Pass Rate: {result.calculate_pass_rate():.2%}")
print(f"Overall: {'PASSED' if result.overall_passed else 'FAILED'}")
```

### Using with OpenAI

```python
from vendingbench.adapters.openai_adapter import OpenAIAdapter

# Initialize with your API key
llm = OpenAIAdapter(model_name="gpt-4", api_key="your-key-here")

# Rest is the same as above
manager = ConversationManager(llm)
history = manager.run_scenario(scenario, verbose=True)
```

### Creating Custom Scenarios

```python
from vendingbench.core.scenario import Scenario, ScenarioConfig

# Define scenario configuration
config = ScenarioConfig(
    name="custom_test",
    description="Test LLM's ability to track state",
    system_prompt="You are a vending machine with specific inventory...",
    temperature=0.7,
)

# Build scenario with expected patterns
scenario = Scenario(config)
scenario.add_user_input(
    "What items do you have?",
    expected_patterns=["Chips", "Cookies", "Soda"]
)
scenario.add_user_input(
    "I'll buy the chips. Here's $5.",
    expected_patterns=["change", "$3.50"]
)

# Add custom validators
def check_inventory_tracking(history, scenario):
    # Custom logic to validate state tracking
    return True

scenario.add_validator(check_inventory_tracking)
```

## Architecture

### Core Components

1. **LLMInterface** (`vendingbench/core/llm_interface.py`)
   - Abstract base class for all LLM adapters
   - Provides uniform API for generation and streaming
   - Handles message validation

2. **Scenario** (`vendingbench/core/scenario.py`)
   - Defines test scenarios with conversation turns
   - Supports expected patterns and custom validators
   - Fluent API for building scenarios

3. **ConversationManager** (`vendingbench/core/conversation.py`)
   - Executes scenarios with LLMs
   - Maintains conversation history
   - Tracks metadata and state

4. **Evaluator** (`vendingbench/core/evaluator.py`)
   - Evaluates responses against expectations
   - Pattern matching (substring and regex)
   - Custom validation functions
   - Generates detailed metrics

### Adapters

- **MockLLM**: For testing without API calls
- **OpenAIAdapter**: Integration with OpenAI models
- More adapters can be easily added by implementing `LLMInterface`

### Pre-built Scenarios

Located in `vendingbench/scenarios/`:
- `basic_vending_machine`: Tests basic state management
- `complex_vending_machine`: Tests advanced interactions
- `edge_cases`: Tests error handling

## Project Structure

```
vendingbench/
├── vendingbench/          # Main package
│   ├── core/             # Core framework components
│   │   ├── llm_interface.py    # LLM base interface
│   │   ├── scenario.py         # Scenario definitions
│   │   ├── conversation.py     # Conversation management
│   │   └── evaluator.py        # Evaluation system
│   ├── adapters/         # LLM provider adapters
│   │   ├── mock_llm.py         # Mock adapter for testing
│   │   └── openai_adapter.py   # OpenAI integration
│   ├── scenarios/        # Pre-built test scenarios
│   │   └── vending_machine.py  # Vending machine scenarios
│   └── utils/            # Utility functions
│       ├── logging.py          # Logging utilities
│       └── export.py           # Result export utilities
├── examples/             # Usage examples
│   ├── basic_example.py
│   ├── custom_scenario.py
│   └── openai_example.py
├── tests/               # Test suite
│   └── unit/           # Unit tests
└── config/             # Configuration files
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vendingbench --cov-report=html

# Run specific test file
pytest tests/unit/test_scenario.py
```

## Running Examples

```bash
# Basic example with mock LLM
python examples/basic_example.py

# Custom scenario example
python examples/custom_scenario.py

# OpenAI example (requires API key)
export OPENAI_API_KEY='your-key-here'
python examples/openai_example.py
```

## Creating Custom LLM Adapters

Implement the `LLMInterface` abstract class:

```python
from vendingbench.core.llm_interface import LLMInterface, LLMResponse

class CustomLLMAdapter(LLMInterface):
    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        # Initialize your LLM client
        
    def generate(self, messages, temperature=0.7, max_tokens=None, **kwargs):
        # Call your LLM API
        # Return LLMResponse object
        pass
    
    def generate_stream(self, messages, temperature=0.7, max_tokens=None, **kwargs):
        # Implement streaming if supported
        pass
```

## Contributing

Contributions are welcome! Areas for expansion:
- Additional LLM adapters (Anthropic, Cohere, local models)
- New scenario types beyond vending machines
- Advanced evaluation metrics
- Visualization tools for results
- Performance benchmarking utilities

## License

This project is provided as-is for research and educational purposes.

## Citation

If you use this framework in your research, please cite the VendingBench paper:
```
@article{vendingbench2025,
  title={VendingBench: A Benchmark for Evaluating LLM Long-term Coherence},
  year={2025},
  journal={arXiv preprint arXiv:2502.15840}
}
```

## Contact

For questions, issues, or contributions, please use the GitHub issue tracker.
