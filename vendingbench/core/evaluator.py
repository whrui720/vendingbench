"""Evaluation and metrics for LLM responses."""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import re

from vendingbench.core.conversation import ConversationHistory
from vendingbench.core.scenario import Scenario, ConversationTurn


@dataclass
class EvaluationMetric:
    """Represents a single evaluation metric."""
    
    name: str
    value: float
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "passed": self.passed,
            "details": self.details,
        }


@dataclass
class EvaluationResult:
    """Results from evaluating a conversation."""
    
    scenario_name: str
    model_name: str
    metrics: List[EvaluationMetric] = field(default_factory=list)
    overall_passed: bool = False
    evaluated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_metric(self, metric: EvaluationMetric):
        """Add a metric to the results.
        
        Args:
            metric: Metric to add
        """
        self.metrics.append(metric)
    
    def get_metric(self, name: str) -> Optional[EvaluationMetric]:
        """Get a metric by name.
        
        Args:
            name: Name of the metric
            
        Returns:
            The metric or None if not found
        """
        for metric in self.metrics:
            if metric.name == name:
                return metric
        return None
    
    def calculate_pass_rate(self) -> float:
        """Calculate the percentage of passed metrics.
        
        Returns:
            Pass rate as a float between 0 and 1
        """
        if not self.metrics:
            return 0.0
        passed_count = sum(1 for m in self.metrics if m.passed)
        return passed_count / len(self.metrics)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "scenario_name": self.scenario_name,
            "model_name": self.model_name,
            "metrics": [m.to_dict() for m in self.metrics],
            "overall_passed": self.overall_passed,
            "pass_rate": self.calculate_pass_rate(),
            "evaluated_at": self.evaluated_at.isoformat(),
            "metadata": self.metadata,
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"EvaluationResult(scenario='{self.scenario_name}', "
            f"model='{self.model_name}', "
            f"pass_rate={self.calculate_pass_rate():.2%})"
        )


class Evaluator:
    """Evaluates conversation history against scenario expectations.
    
    This class provides methods for evaluating LLM responses based on
    various criteria such as pattern matching, coherence checks,
    and custom validation functions.
    """
    
    def __init__(self):
        """Initialize the evaluator."""
        self.custom_validators: Dict[str, Callable] = {}
    
    def register_validator(self, name: str, validator: Callable):
        """Register a custom validator function.
        
        Args:
            name: Name of the validator
            validator: Callable that takes (history, scenario) and returns bool
        """
        self.custom_validators[name] = validator
    
    def evaluate(
        self,
        history: ConversationHistory,
        scenario: Scenario,
    ) -> EvaluationResult:
        """Evaluate a conversation history against a scenario.
        
        Args:
            history: The conversation history to evaluate
            scenario: The scenario that was executed
            
        Returns:
            EvaluationResult containing metrics and overall pass/fail
        """
        result = EvaluationResult(
            scenario_name=scenario.config.name,
            model_name=history.metadata.get("model_name", "unknown"),
        )
        
        # Evaluate pattern matching for each turn
        self._evaluate_patterns(history, scenario, result)
        
        # Run custom validators
        self._run_custom_validators(history, scenario, result)
        
        # Calculate overall pass/fail
        result.overall_passed = all(m.passed for m in result.metrics)
        
        return result
    
    def _evaluate_patterns(
        self,
        history: ConversationHistory,
        scenario: Scenario,
        result: EvaluationResult,
    ):
        """Evaluate expected patterns in responses.
        
        Args:
            history: Conversation history
            scenario: Scenario with expected patterns
            result: Result object to add metrics to
        """
        response_idx = 0
        
        for turn in scenario.turns:
            if not turn.expected_patterns:
                continue
            
            if response_idx >= len(history.responses):
                # Not enough responses
                metric = EvaluationMetric(
                    name=f"pattern_match_turn_{response_idx}",
                    value=0.0,
                    passed=False,
                    details={"error": "No response for this turn"},
                )
                result.add_metric(metric)
                continue
            
            response = history.responses[response_idx]
            matched_patterns = []
            missing_patterns = []
            
            for pattern in turn.expected_patterns:
                if self._pattern_matches(pattern, response.content):
                    matched_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            passed = len(missing_patterns) == 0
            value = len(matched_patterns) / len(turn.expected_patterns) if turn.expected_patterns else 1.0
            
            metric = EvaluationMetric(
                name=f"pattern_match_turn_{response_idx}",
                value=value,
                passed=passed,
                details={
                    "matched": matched_patterns,
                    "missing": missing_patterns,
                    "turn_content": turn.content[:100],
                },
            )
            result.add_metric(metric)
            
            response_idx += 1
    
    def _pattern_matches(self, pattern: str, text: str) -> bool:
        """Check if a pattern matches text.
        
        Args:
            pattern: Pattern to match (can be regex or substring)
            text: Text to search in
            
        Returns:
            True if pattern matches
        """
        # Try as regex first
        try:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        except re.error:
            pass
        
        # Fall back to case-insensitive substring match
        return pattern.lower() in text.lower()
    
    def _run_custom_validators(
        self,
        history: ConversationHistory,
        scenario: Scenario,
        result: EvaluationResult,
    ):
        """Run custom validator functions.
        
        Args:
            history: Conversation history
            scenario: Scenario with validators
            result: Result object to add metrics to
        """
        for i, validator in enumerate(scenario.validators):
            try:
                passed = validator(history, scenario)
                metric = EvaluationMetric(
                    name=f"custom_validator_{i}",
                    value=1.0 if passed else 0.0,
                    passed=passed,
                    details={"validator_function": validator.__name__ if hasattr(validator, "__name__") else "lambda"},
                )
                result.add_metric(metric)
            except Exception as e:
                metric = EvaluationMetric(
                    name=f"custom_validator_{i}",
                    value=0.0,
                    passed=False,
                    details={"error": str(e)},
                )
                result.add_metric(metric)
