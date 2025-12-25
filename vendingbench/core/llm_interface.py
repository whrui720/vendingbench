"""Base interface for LLM adapters."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LLMResponse:
    """Response from an LLM."""
    
    content: str
    model: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class LLMInterface(ABC):
    """Abstract base class for LLM adapters.
    
    This interface provides a uniform way to interact with different LLM providers.
    Implement this interface for each LLM provider you want to use with vendingbench.
    """
    
    def __init__(self, model_name: str, **kwargs):
        """Initialize the LLM interface.
        
        Args:
            model_name: Name of the model to use
            **kwargs: Additional provider-specific configuration
        """
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Sampling temperature for generation
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse object containing the generated content and metadata
        """
        pass
    
    @abstractmethod
    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming response from the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Sampling temperature for generation
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Chunks of the response as they are generated
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model_name": self.model_name,
            "config": self.config,
        }
    
    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """Validate message format.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            True if messages are valid, False otherwise
        """
        if not messages:
            return False
        
        for msg in messages:
            if not isinstance(msg, dict):
                return False
            if "role" not in msg or "content" not in msg:
                return False
            if msg["role"] not in ["system", "user", "assistant"]:
                return False
        
        return True
