"""Mock LLM adapter for testing purposes."""
from typing import List, Dict, Optional
from vendingbench.core.llm_interface import LLMInterface, LLMResponse


class MockLLM(LLMInterface):
    """Mock LLM implementation for testing.
    
    This adapter returns predefined responses or echoes the user input.
    Useful for testing the framework without requiring API access.
    """
    
    def __init__(self, model_name: str = "mock-model", responses: Optional[List[str]] = None, **kwargs):
        """Initialize the mock LLM.
        
        Args:
            model_name: Name of the mock model
            responses: Predefined responses to return in sequence
            **kwargs: Additional configuration
        """
        super().__init__(model_name, **kwargs)
        self.responses = responses or []
        self.response_index = 0
        self.call_count = 0
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a mock response.
        
        Args:
            messages: List of messages
            temperature: Ignored for mock
            max_tokens: Ignored for mock
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with mock content
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        self.call_count += 1
        
        # Return predefined response if available
        if self.responses and self.response_index < len(self.responses):
            content = self.responses[self.response_index]
            self.response_index += 1
        else:
            # Echo the last user message
            user_messages = [m for m in messages if m["role"] == "user"]
            if user_messages:
                content = f"Mock response to: {user_messages[-1]['content']}"
            else:
                content = "Mock response with no user input"
        
        return LLMResponse(
            content=content,
            model=self.model_name,
            metadata={
                "call_count": self.call_count,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
    
    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming mock response.
        
        Args:
            messages: List of messages
            temperature: Ignored for mock
            max_tokens: Ignored for mock
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the mock response
        """
        response = self.generate(messages, temperature, max_tokens, **kwargs)
        
        # Simulate streaming by yielding words
        words = response.content.split()
        for word in words:
            yield word + " "
    
    def reset(self):
        """Reset the mock LLM state."""
        self.response_index = 0
        self.call_count = 0
