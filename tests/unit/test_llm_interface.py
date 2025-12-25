"""Tests for LLM interface and adapters."""
import pytest
from vendingbench.core.llm_interface import LLMInterface, LLMResponse
from vendingbench.adapters.mock_llm import MockLLM


class TestLLMResponse:
    """Test LLMResponse dataclass."""
    
    def test_create_response(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Test response",
            model="test-model",
        )
        assert response.content == "Test response"
        assert response.model == "test-model"
        assert response.metadata == {}
    
    def test_response_to_dict(self):
        """Test converting response to dictionary."""
        response = LLMResponse(
            content="Test",
            model="test-model",
            metadata={"key": "value"}
        )
        result = response.to_dict()
        assert result["content"] == "Test"
        assert result["model"] == "test-model"
        assert result["metadata"]["key"] == "value"
        assert "timestamp" in result


class TestLLMInterface:
    """Test LLM interface base class."""
    
    def test_validate_messages_valid(self):
        """Test message validation with valid messages."""
        llm = MockLLM()
        messages = [
            {"role": "system", "content": "You are a helper"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        assert llm.validate_messages(messages) is True
    
    def test_validate_messages_invalid_role(self):
        """Test message validation with invalid role."""
        llm = MockLLM()
        messages = [
            {"role": "invalid_role", "content": "Test"},
        ]
        assert llm.validate_messages(messages) is False
    
    def test_validate_messages_missing_content(self):
        """Test message validation with missing content."""
        llm = MockLLM()
        messages = [
            {"role": "user"},
        ]
        assert llm.validate_messages(messages) is False
    
    def test_validate_messages_empty(self):
        """Test message validation with empty list."""
        llm = MockLLM()
        assert llm.validate_messages([]) is False
    
    def test_get_model_info(self):
        """Test getting model information."""
        llm = MockLLM(model_name="test-model", extra_param="value")
        info = llm.get_model_info()
        assert info["model_name"] == "test-model"
        assert "config" in info


class TestMockLLM:
    """Test MockLLM adapter."""
    
    def test_mock_with_predefined_responses(self):
        """Test mock LLM with predefined responses."""
        responses = ["Response 1", "Response 2"]
        llm = MockLLM(responses=responses)
        
        messages = [{"role": "user", "content": "Test"}]
        
        response1 = llm.generate(messages)
        assert response1.content == "Response 1"
        
        response2 = llm.generate(messages)
        assert response2.content == "Response 2"
    
    def test_mock_echo_mode(self):
        """Test mock LLM echoing user input."""
        llm = MockLLM()
        messages = [{"role": "user", "content": "Hello world"}]
        
        response = llm.generate(messages)
        assert "Hello world" in response.content
    
    def test_mock_call_count(self):
        """Test that mock LLM tracks call count."""
        llm = MockLLM()
        messages = [{"role": "user", "content": "Test"}]
        
        llm.generate(messages)
        assert llm.call_count == 1
        
        llm.generate(messages)
        assert llm.call_count == 2
    
    def test_mock_reset(self):
        """Test resetting mock LLM state."""
        responses = ["Response 1", "Response 2"]
        llm = MockLLM(responses=responses)
        messages = [{"role": "user", "content": "Test"}]
        
        llm.generate(messages)
        assert llm.call_count == 1
        assert llm.response_index == 1
        
        llm.reset()
        assert llm.call_count == 0
        assert llm.response_index == 0
    
    def test_mock_stream(self):
        """Test mock LLM streaming."""
        llm = MockLLM(responses=["Hello world test"])
        messages = [{"role": "user", "content": "Test"}]
        
        chunks = list(llm.generate_stream(messages))
        assert len(chunks) > 0
        full_response = "".join(chunks).strip()
        assert "Hello world test" in full_response
    
    def test_mock_invalid_messages(self):
        """Test that mock LLM validates messages."""
        llm = MockLLM()
        invalid_messages = [{"role": "invalid"}]
        
        with pytest.raises(ValueError):
            llm.generate(invalid_messages)
