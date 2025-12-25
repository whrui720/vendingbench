"""Tests for conversation management."""
import pytest
from vendingbench.core.conversation import ConversationManager, ConversationHistory
from vendingbench.core.scenario import Scenario, ScenarioConfig
from vendingbench.adapters.mock_llm import MockLLM


class TestConversationHistory:
    """Test ConversationHistory."""
    
    def test_create_history(self):
        """Test creating conversation history."""
        history = ConversationHistory()
        assert len(history.messages) == 0
        assert len(history.responses) == 0
    
    def test_add_message(self):
        """Test adding a message."""
        history = ConversationHistory()
        history.add_message("user", "Hello")
        
        assert len(history.messages) == 1
        assert history.messages[0]["role"] == "user"
        assert history.messages[0]["content"] == "Hello"
    
    def test_add_response(self):
        """Test adding an LLM response."""
        from vendingbench.core.llm_interface import LLMResponse
        
        history = ConversationHistory()
        response = LLMResponse(content="Test response", model="test")
        
        history.add_response(response)
        
        assert len(history.responses) == 1
        assert len(history.messages) == 1
        assert history.messages[0]["role"] == "assistant"
    
    def test_get_messages(self):
        """Test getting messages."""
        history = ConversationHistory()
        history.add_message("user", "Hello")
        
        messages = history.get_messages()
        assert len(messages) == 1
        # Should return a copy
        messages.append({"role": "user", "content": "Test"})
        assert len(history.messages) == 1
    
    def test_get_last_response(self):
        """Test getting last response."""
        from vendingbench.core.llm_interface import LLMResponse
        
        history = ConversationHistory()
        
        # No responses yet
        assert history.get_last_response() is None
        
        response = LLMResponse(content="Test", model="test")
        history.add_response(response)
        
        last = history.get_last_response()
        assert last is not None
        assert last.content == "Test"
    
    def test_history_to_dict(self):
        """Test converting history to dictionary."""
        history = ConversationHistory()
        history.add_message("user", "Hello")
        
        result = history.to_dict()
        assert "messages" in result
        assert "responses" in result
        assert "metadata" in result
        assert "started_at" in result
        assert result["num_turns"] == 0


class TestConversationManager:
    """Test ConversationManager."""
    
    def test_create_manager(self):
        """Test creating a conversation manager."""
        llm = MockLLM()
        manager = ConversationManager(llm)
        assert manager.llm is llm
    
    def test_run_scenario_simple(self):
        """Test running a simple scenario."""
        llm = MockLLM(responses=["Response 1", "Response 2"])
        manager = ConversationManager(llm)
        
        config = ScenarioConfig(
            name="test",
            description="Test scenario",
        )
        scenario = Scenario(config)
        scenario.add_user_input("Input 1")
        scenario.add_user_input("Input 2")
        
        history = manager.run_scenario(scenario)
        
        assert len(history.responses) == 2
        assert history.responses[0].content == "Response 1"
        assert history.responses[1].content == "Response 2"
    
    def test_run_scenario_with_system_prompt(self):
        """Test running scenario with system prompt."""
        llm = MockLLM(responses=["Response"])
        manager = ConversationManager(llm)
        
        config = ScenarioConfig(
            name="test",
            description="Test",
            system_prompt="You are a test assistant",
        )
        scenario = Scenario(config)
        scenario.add_user_input("Hello")
        
        history = manager.run_scenario(scenario)
        
        # Should have system message + user message + assistant response
        assert len(history.messages) == 3
        assert history.messages[0]["role"] == "system"
        assert history.messages[1]["role"] == "user"
        assert history.messages[2]["role"] == "assistant"
    
    def test_run_scenario_metadata(self):
        """Test that scenario metadata is stored."""
        llm = MockLLM(responses=["Response"])
        manager = ConversationManager(llm)
        
        config = ScenarioConfig(name="test_scenario", description="Test")
        scenario = Scenario(config)
        scenario.add_user_input("Hello")
        
        history = manager.run_scenario(scenario)
        
        assert history.metadata["scenario_name"] == "test_scenario"
        assert history.metadata["model_name"] == "mock-model"
    
    def test_continue_conversation(self):
        """Test continuing an existing conversation."""
        llm = MockLLM()
        manager = ConversationManager(llm)
        
        history = ConversationHistory()
        history.add_message("user", "First message")
        
        response = manager.continue_conversation(
            history,
            "Second message",
        )
        
        assert response is not None
        assert len(history.messages) == 3  # user, user, assistant
        assert len(history.responses) == 1
    
    def test_run_scenario_verbose(self, capsys):
        """Test running scenario with verbose output."""
        llm = MockLLM(responses=["Response"])
        manager = ConversationManager(llm)
        
        config = ScenarioConfig(name="test", description="Test")
        scenario = Scenario(config)
        scenario.add_user_input("Hello")
        
        manager.run_scenario(scenario, verbose=True)
        
        captured = capsys.readouterr()
        assert "Turn 1" in captured.out
        assert "user_input" in captured.out
