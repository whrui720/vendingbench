"""Tests for scenario management."""
import pytest
from vendingbench.core.scenario import (
    Scenario,
    ScenarioConfig,
    ConversationTurn,
    TurnType,
)


class TestScenarioConfig:
    """Test ScenarioConfig."""
    
    def test_create_config(self):
        """Test creating a scenario config."""
        config = ScenarioConfig(
            name="test_scenario",
            description="Test description",
            system_prompt="Test prompt",
            temperature=0.8,
        )
        assert config.name == "test_scenario"
        assert config.description == "Test description"
        assert config.system_prompt == "Test prompt"
        assert config.temperature == 0.8
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = ScenarioConfig(
            name="test",
            description="desc",
        )
        result = config.to_dict()
        assert result["name"] == "test"
        assert result["description"] == "desc"


class TestConversationTurn:
    """Test ConversationTurn."""
    
    def test_create_turn(self):
        """Test creating a conversation turn."""
        turn = ConversationTurn(
            turn_type=TurnType.USER_INPUT,
            content="Test input",
            expected_patterns=["pattern1", "pattern2"],
        )
        assert turn.turn_type == TurnType.USER_INPUT
        assert turn.content == "Test input"
        assert len(turn.expected_patterns) == 2
    
    def test_turn_to_dict(self):
        """Test converting turn to dictionary."""
        turn = ConversationTurn(
            turn_type=TurnType.USER_INPUT,
            content="Test",
        )
        result = turn.to_dict()
        assert result["turn_type"] == "user_input"
        assert result["content"] == "Test"


class TestScenario:
    """Test Scenario class."""
    
    def test_create_scenario(self):
        """Test creating a scenario."""
        config = ScenarioConfig(
            name="test",
            description="Test scenario",
        )
        scenario = Scenario(config)
        assert scenario.config.name == "test"
        assert len(scenario.turns) == 0
    
    def test_add_turn(self):
        """Test adding a turn to scenario."""
        config = ScenarioConfig(name="test", description="desc")
        scenario = Scenario(config)
        
        turn = ConversationTurn(
            turn_type=TurnType.USER_INPUT,
            content="Test",
        )
        scenario.add_turn(turn)
        
        assert len(scenario.turns) == 1
        assert scenario.turns[0].content == "Test"
    
    def test_add_user_input(self):
        """Test convenience method for adding user input."""
        config = ScenarioConfig(name="test", description="desc")
        scenario = Scenario(config)
        
        scenario.add_user_input(
            "User message",
            expected_patterns=["pattern1"],
        )
        
        assert len(scenario.turns) == 1
        assert scenario.turns[0].turn_type == TurnType.USER_INPUT
        assert scenario.turns[0].content == "User message"
        assert "pattern1" in scenario.turns[0].expected_patterns
    
    def test_add_state_check(self):
        """Test adding a state check."""
        config = ScenarioConfig(name="test", description="desc")
        scenario = Scenario(config)
        
        scenario.add_state_check(
            "Check inventory",
            expected_patterns=["5 items"],
        )
        
        assert len(scenario.turns) == 1
        assert scenario.turns[0].turn_type == TurnType.STATE_CHECK
    
    def test_method_chaining(self):
        """Test that methods return self for chaining."""
        config = ScenarioConfig(name="test", description="desc")
        scenario = Scenario(config)
        
        result = (
            scenario
            .add_user_input("Input 1")
            .add_user_input("Input 2")
            .add_state_check("Check", ["pattern"])
        )
        
        assert result is scenario
        assert len(scenario.turns) == 3
    
    def test_add_validator(self):
        """Test adding a custom validator."""
        config = ScenarioConfig(name="test", description="desc")
        scenario = Scenario(config)
        
        def custom_validator(history, scenario):
            return True
        
        scenario.add_validator(custom_validator)
        assert len(scenario.validators) == 1
    
    def test_get_system_message(self):
        """Test getting system message."""
        config = ScenarioConfig(
            name="test",
            description="desc",
            system_prompt="You are a test assistant",
        )
        scenario = Scenario(config)
        
        msg = scenario.get_system_message()
        assert msg is not None
        assert msg["role"] == "system"
        assert msg["content"] == "You are a test assistant"
    
    def test_get_system_message_none(self):
        """Test getting system message when none exists."""
        config = ScenarioConfig(name="test", description="desc")
        scenario = Scenario(config)
        
        msg = scenario.get_system_message()
        assert msg is None
    
    def test_scenario_len(self):
        """Test scenario length."""
        config = ScenarioConfig(name="test", description="desc")
        scenario = Scenario(config)
        
        assert len(scenario) == 0
        
        scenario.add_user_input("Test")
        assert len(scenario) == 1
    
    def test_scenario_to_dict(self):
        """Test converting scenario to dictionary."""
        config = ScenarioConfig(name="test", description="desc")
        scenario = Scenario(config)
        scenario.add_user_input("Test")
        
        result = scenario.to_dict()
        assert result["config"]["name"] == "test"
        assert len(result["turns"]) == 1
        assert "created_at" in result
    
    def test_scenario_repr(self):
        """Test scenario string representation."""
        config = ScenarioConfig(name="test", description="desc")
        scenario = Scenario(config)
        scenario.add_user_input("Test")
        
        repr_str = repr(scenario)
        assert "test" in repr_str
        assert "turns=1" in repr_str
