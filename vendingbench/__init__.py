"""VendingBench: A reusable framework for testing LLM long-term coherence."""

__version__ = "0.1.0"

from vendingbench.core.llm_interface import LLMInterface, LLMResponse
from vendingbench.core.scenario import Scenario, ScenarioConfig, ConversationTurn
from vendingbench.core.conversation import ConversationManager
from vendingbench.core.evaluator import Evaluator, EvaluationResult

__all__ = [
    "LLMInterface",
    "LLMResponse",
    "Scenario",
    "ScenarioConfig",
    "ConversationTurn",
    "ConversationManager",
    "Evaluator",
    "EvaluationResult",
]
