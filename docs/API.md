# API Reference

## Core Modules

### LLM Interface (`vendingbench.core.llm_interface`)

#### `LLMResponse`

Dataclass representing a response from an LLM.

**Attributes:**
- `content` (str): The generated text content
- `model` (str): Name of the model that generated the response
- `timestamp` (datetime): When the response was generated
- `metadata` (dict): Additional metadata about the response
- `raw_response` (Any): The raw response object from the provider

**Methods:**
- `to_dict()`: Convert response to dictionary

#### `LLMInterface`

Abstract base class for LLM adapters.

**Methods:**
- `__init__(model_name: str, **kwargs)`: Initialize the interface
- `generate(messages, temperature=0.7, max_tokens=None, **kwargs) -> LLMResponse`: Generate a response
- `generate_stream(messages, temperature=0.7, max_tokens=None, **kwargs)`: Generate a streaming response
- `get_model_info() -> dict`: Get model information
- `validate_messages(messages) -> bool`: Validate message format

### Scenario (`vendingbench.core.scenario`)

#### `TurnType`

Enum defining types of conversation turns:
- `USER_INPUT`: User message
- `SYSTEM_PROMPT`: System prompt
- `ASSERTION`: Assertion to check
- `STATE_CHECK`: State verification

#### `ConversationTurn`

Represents a single turn in a scenario.

**Attributes:**
- `turn_type` (TurnType): Type of turn
- `content` (str): Content of the turn
- `expected_patterns` (List[str]): Patterns expected in response
- `metadata` (dict): Additional metadata

#### `ScenarioConfig`

Configuration for a test scenario.

**Attributes:**
- `name` (str): Scenario name
- `description` (str): Scenario description
- `system_prompt` (str, optional): System prompt
- `temperature` (float): Sampling temperature (default: 0.7)
- `max_tokens` (int, optional): Max tokens to generate
- `stop_sequences` (List[str]): Stop sequences
- `metadata` (dict): Additional metadata

#### `Scenario`

Test scenario for evaluating LLM behavior.

**Methods:**
- `__init__(config: ScenarioConfig)`: Initialize scenario
- `add_turn(turn: ConversationTurn) -> Scenario`: Add a turn
- `add_user_input(content, expected_patterns=None, **metadata) -> Scenario`: Add user input
- `add_state_check(description, expected_patterns, **metadata) -> Scenario`: Add state check
- `add_validator(validator: Callable) -> Scenario`: Add custom validator
- `get_system_message() -> Optional[dict]`: Get system message
- `to_dict() -> dict`: Convert to dictionary
- `__len__() -> int`: Get number of turns

### Conversation (`vendingbench.core.conversation`)

#### `ConversationHistory`

Manages conversation history.

**Attributes:**
- `messages` (List[dict]): All messages
- `responses` (List[LLMResponse]): All LLM responses
- `metadata` (dict): Conversation metadata
- `started_at` (datetime): Start timestamp

**Methods:**
- `add_message(role: str, content: str)`: Add a message
- `add_response(response: LLMResponse)`: Add LLM response
- `get_messages() -> List[dict]`: Get all messages
- `get_last_response() -> Optional[LLMResponse]`: Get last response
- `to_dict() -> dict`: Convert to dictionary

#### `ConversationManager`

Manages scenario execution.

**Methods:**
- `__init__(llm: LLMInterface)`: Initialize manager
- `run_scenario(scenario: Scenario, verbose=False) -> ConversationHistory`: Run a scenario
- `continue_conversation(history, user_input, temperature=0.7, max_tokens=None) -> LLMResponse`: Continue conversation

### Evaluator (`vendingbench.core.evaluator`)

#### `EvaluationMetric`

Represents a single evaluation metric.

**Attributes:**
- `name` (str): Metric name
- `value` (float): Metric value (0.0 to 1.0)
- `passed` (bool): Whether metric passed
- `details` (dict): Additional details

#### `EvaluationResult`

Results from evaluating a conversation.

**Attributes:**
- `scenario_name` (str): Name of scenario
- `model_name` (str): Name of model
- `metrics` (List[EvaluationMetric]): All metrics
- `overall_passed` (bool): Overall pass/fail
- `evaluated_at` (datetime): Evaluation timestamp
- `metadata` (dict): Additional metadata

**Methods:**
- `add_metric(metric: EvaluationMetric)`: Add a metric
- `get_metric(name: str) -> Optional[EvaluationMetric]`: Get metric by name
- `calculate_pass_rate() -> float`: Calculate pass rate (0.0 to 1.0)
- `to_dict() -> dict`: Convert to dictionary

#### `Evaluator`

Evaluates conversations against scenarios.

**Methods:**
- `__init__()`: Initialize evaluator
- `register_validator(name: str, validator: Callable)`: Register custom validator
- `evaluate(history: ConversationHistory, scenario: Scenario) -> EvaluationResult`: Evaluate conversation

## Adapters

### MockLLM (`vendingbench.adapters.mock_llm`)

Mock LLM for testing.

**Methods:**
- `__init__(model_name="mock-model", responses=None, **kwargs)`: Initialize
- `generate(messages, temperature=0.7, max_tokens=None, **kwargs) -> LLMResponse`: Generate response
- `generate_stream(messages, temperature=0.7, max_tokens=None, **kwargs)`: Stream response
- `reset()`: Reset state

### OpenAIAdapter (`vendingbench.adapters.openai_adapter`)

OpenAI API adapter.

**Methods:**
- `__init__(model_name="gpt-4", api_key=None, **kwargs)`: Initialize
- `generate(messages, temperature=0.7, max_tokens=None, **kwargs) -> LLMResponse`: Generate response
- `generate_stream(messages, temperature=0.7, max_tokens=None, **kwargs)`: Stream response

## Utilities

### Export (`vendingbench.utils.export`)

**Functions:**
- `save_evaluation_result(result, output_path)`: Save result to JSON
- `save_conversation_history(history, output_path)`: Save history to JSON
- `save_batch_results(results, output_dir, filename_prefix)`: Save multiple results
- `load_evaluation_result(input_path) -> dict`: Load result from JSON

### Logging (`vendingbench.utils.logging`)

**Functions:**
- `setup_logger(name="vendingbench", level=logging.INFO, log_file=None) -> logging.Logger`: Set up logger

## Scenarios

### Vending Machine (`vendingbench.scenarios.vending_machine`)

**Functions:**
- `create_basic_vending_scenario() -> Scenario`: Create basic scenario
- `create_complex_vending_scenario() -> Scenario`: Create complex scenario
- `create_edge_case_scenario() -> Scenario`: Create edge case scenario
