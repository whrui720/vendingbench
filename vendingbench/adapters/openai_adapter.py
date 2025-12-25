"""OpenAI adapter for vendingbench."""
from typing import List, Dict, Optional

from vendingbench.core.llm_interface import LLMInterface, LLMResponse


class OpenAIAdapter(LLMInterface):
    """Adapter for OpenAI models.
    
    This adapter provides integration with OpenAI's API.
    Requires: pip install openai
    """
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None, **kwargs):
        """Initialize the OpenAI adapter.
        
        Args:
            model_name: Name of the OpenAI model (e.g., 'gpt-4', 'gpt-3.5-turbo')
            api_key: OpenAI API key (if not set in environment)
            **kwargs: Additional configuration
        """
        super().__init__(model_name, **kwargs)
        
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        
        self.client = OpenAI(api_key=api_key)
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response using OpenAI API.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters
            
        Returns:
            LLMResponse containing the generated content
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        # Build API parameters
        api_params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens is not None:
            api_params["max_tokens"] = max_tokens
        
        # Add any additional parameters
        api_params.update(kwargs)
        
        # Call OpenAI API
        response = self.client.chat.completions.create(**api_params)
        
        # Extract content
        content = response.choices[0].message.content
        
        return LLMResponse(
            content=content,
            model=self.model_name,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            },
            raw_response=response,
        )
    
    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming response using OpenAI API.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters
            
        Yields:
            Chunks of the response as they are generated
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        # Build API parameters
        api_params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        
        if max_tokens is not None:
            api_params["max_tokens"] = max_tokens
        
        # Add any additional parameters
        api_params.update(kwargs)
        
        # Stream from OpenAI API
        stream = self.client.chat.completions.create(**api_params)
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
