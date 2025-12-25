"""Tests for evaluation and metrics."""
import pytest
from vendingbench.core.evaluator import Evaluator, EvaluationResult, EvaluationMetric
from vendingbench.core.conversation import ConversationHistory
from vendingbench.core.scenario import Scenario, ScenarioConfig
from vendingbench.core.llm_interface import LLMResponse


class TestEvaluationMetric:
    """Test EvaluationMetric."""
    
    def test_create_metric(self):
        """Test creating an evaluation metric."""
        metric = EvaluationMetric(
            name="test_metric",
            value=0.85,
            passed=True,
        )
        assert metric.name == "test_metric"
        assert metric.value == 0.85
        assert metric.passed is True
    
    def test_metric_to_dict(self):
        """Test converting metric to dictionary."""
        metric = EvaluationMetric(
            name="test",
            value=1.0,
            passed=True,
            details={"key": "value"},
        )
        result = metric.to_dict()
        assert result["name"] == "test"
        assert result["value"] == 1.0
        assert result["passed"] is True
        assert result["details"]["key"] == "value"


class TestEvaluationResult:
    """Test EvaluationResult."""
    
    def test_create_result(self):
        """Test creating an evaluation result."""
        result = EvaluationResult(
            scenario_name="test_scenario",
            model_name="test_model",
        )
        assert result.scenario_name == "test_scenario"
        assert result.model_name == "test_model"
        assert len(result.metrics) == 0
    
    def test_add_metric(self):
        """Test adding a metric to result."""
        result = EvaluationResult(
            scenario_name="test",
            model_name="test",
        )
        metric = EvaluationMetric(name="test", value=1.0, passed=True)
        result.add_metric(metric)
        
        assert len(result.metrics) == 1
    
    def test_get_metric(self):
        """Test getting a metric by name."""
        result = EvaluationResult(
            scenario_name="test",
            model_name="test",
        )
        metric1 = EvaluationMetric(name="metric1", value=1.0, passed=True)
        metric2 = EvaluationMetric(name="metric2", value=0.5, passed=False)
        result.add_metric(metric1)
        result.add_metric(metric2)
        
        found = result.get_metric("metric1")
        assert found is not None
        assert found.name == "metric1"
        
        not_found = result.get_metric("metric3")
        assert not_found is None
    
    def test_calculate_pass_rate(self):
        """Test calculating pass rate."""
        result = EvaluationResult(
            scenario_name="test",
            model_name="test",
        )
        result.add_metric(EvaluationMetric(name="m1", value=1.0, passed=True))
        result.add_metric(EvaluationMetric(name="m2", value=1.0, passed=True))
        result.add_metric(EvaluationMetric(name="m3", value=0.0, passed=False))
        
        assert result.calculate_pass_rate() == pytest.approx(2/3)
    
    def test_calculate_pass_rate_empty(self):
        """Test pass rate with no metrics."""
        result = EvaluationResult(
            scenario_name="test",
            model_name="test",
        )
        assert result.calculate_pass_rate() == 0.0
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = EvaluationResult(
            scenario_name="test",
            model_name="test",
            overall_passed=True,
        )
        result.add_metric(EvaluationMetric(name="test", value=1.0, passed=True))
        
        result_dict = result.to_dict()
        assert result_dict["scenario_name"] == "test"
        assert result_dict["model_name"] == "test"
        assert result_dict["overall_passed"] is True
        assert "pass_rate" in result_dict
        assert len(result_dict["metrics"]) == 1
    
    def test_result_repr(self):
        """Test result string representation."""
        result = EvaluationResult(
            scenario_name="test_scenario",
            model_name="test_model",
        )
        repr_str = repr(result)
        assert "test_scenario" in repr_str
        assert "test_model" in repr_str


class TestEvaluator:
    """Test Evaluator class."""
    
    def test_create_evaluator(self):
        """Test creating an evaluator."""
        evaluator = Evaluator()
        assert len(evaluator.custom_validators) == 0
    
    def test_register_validator(self):
        """Test registering a custom validator."""
        evaluator = Evaluator()
        
        def custom_validator(history, scenario):
            return True
        
        evaluator.register_validator("test", custom_validator)
        assert "test" in evaluator.custom_validators
    
    def test_pattern_matching(self):
        """Test pattern matching logic."""
        evaluator = Evaluator()
        
        # Substring match
        assert evaluator._pattern_matches("hello", "Hello world")
        assert evaluator._pattern_matches("world", "Hello world")
        
        # Regex match
        assert evaluator._pattern_matches(r"\d+", "There are 5 items")
        assert evaluator._pattern_matches(r"[A-Z]+", "ABC123")
        
        # No match
        assert not evaluator._pattern_matches("xyz", "Hello world")
    
    def test_evaluate_simple_scenario(self):
        """Test evaluating a simple scenario."""
        evaluator = Evaluator()
        
        # Create history
        history = ConversationHistory()
        history.metadata["model_name"] = "test-model"
        response = LLMResponse(
            content="I have Chips and Cookies available",
            model="test-model",
        )
        history.add_response(response)
        
        # Create scenario
        config = ScenarioConfig(name="test", description="Test")
        scenario = Scenario(config)
        scenario.add_user_input(
            "What do you have?",
            expected_patterns=["Chips", "Cookies"],
        )
        
        # Evaluate
        result = evaluator.evaluate(history, scenario)
        
        assert result.scenario_name == "test"
        assert result.model_name == "test-model"
        assert len(result.metrics) > 0
    
    def test_evaluate_pattern_match_success(self):
        """Test successful pattern matching."""
        evaluator = Evaluator()
        
        history = ConversationHistory()
        history.metadata["model_name"] = "test"
        response = LLMResponse(content="The price is $5.00", model="test")
        history.add_response(response)
        
        config = ScenarioConfig(name="test", description="Test")
        scenario = Scenario(config)
        scenario.add_user_input("What's the price?", expected_patterns=["$5", "price"])
        
        result = evaluator.evaluate(history, scenario)
        
        # Should have a pattern match metric
        assert len(result.metrics) > 0
        metric = result.metrics[0]
        assert metric.value > 0
    
    def test_evaluate_pattern_match_failure(self):
        """Test failed pattern matching."""
        evaluator = Evaluator()
        
        history = ConversationHistory()
        history.metadata["model_name"] = "test"
        response = LLMResponse(content="No price information", model="test")
        history.add_response(response)
        
        config = ScenarioConfig(name="test", description="Test")
        scenario = Scenario(config)
        scenario.add_user_input("What's the price?", expected_patterns=["$5.00"])
        
        result = evaluator.evaluate(history, scenario)
        
        metric = result.metrics[0]
        assert not metric.passed
        assert len(metric.details.get("missing", [])) > 0
    
    def test_evaluate_with_custom_validator(self):
        """Test evaluation with custom validator."""
        evaluator = Evaluator()
        
        history = ConversationHistory()
        history.metadata["model_name"] = "test"
        response = LLMResponse(content="Test response", model="test")
        history.add_response(response)
        
        config = ScenarioConfig(name="test", description="Test")
        scenario = Scenario(config)
        scenario.add_user_input("Test")
        
        # Add custom validator
        def always_pass(history, scenario):
            return True
        
        scenario.add_validator(always_pass)
        
        result = evaluator.evaluate(history, scenario)
        
        # Should have a custom validator metric
        custom_metrics = [m for m in result.metrics if "custom_validator" in m.name]
        assert len(custom_metrics) > 0
        assert custom_metrics[0].passed
    
    def test_evaluate_custom_validator_failure(self):
        """Test custom validator that fails."""
        evaluator = Evaluator()
        
        history = ConversationHistory()
        history.metadata["model_name"] = "test"
        
        config = ScenarioConfig(name="test", description="Test")
        scenario = Scenario(config)
        
        def always_fail(history, scenario):
            return False
        
        scenario.add_validator(always_fail)
        
        result = evaluator.evaluate(history, scenario)
        
        custom_metrics = [m for m in result.metrics if "custom_validator" in m.name]
        assert len(custom_metrics) > 0
        assert not custom_metrics[0].passed
    
    def test_overall_passed(self):
        """Test that overall_passed is calculated correctly."""
        evaluator = Evaluator()
        
        history = ConversationHistory()
        history.metadata["model_name"] = "test"
        response = LLMResponse(content="Chips and Cookies", model="test")
        history.add_response(response)
        
        config = ScenarioConfig(name="test", description="Test")
        scenario = Scenario(config)
        scenario.add_user_input("Test", expected_patterns=["Chips", "Cookies"])
        
        result = evaluator.evaluate(history, scenario)
        
        # All patterns match, should pass
        assert result.overall_passed
