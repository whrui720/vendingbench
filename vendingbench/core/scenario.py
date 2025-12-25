"""Scenario and test case management."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime


class TurnType(Enum):
    """Type of conversation turn."""
    USER_INPUT = "user_input"
    SYSTEM_PROMPT = "system_prompt"
    ASSERTION = "assertion"
    STATE_CHECK = "state_check"


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation scenario."""
    
    turn_type: TurnType
    content: str
    expected_patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert turn to dictionary."""
        return {
            "turn_type": self.turn_type.value,
            "content": self.content,
            "expected_patterns": self.expected_patterns,
            "metadata": self.metadata,
        }


@dataclass
class ScenarioConfig:
    """Configuration for a test scenario."""
    
    name: str
    description: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop_sequences: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stop_sequences": self.stop_sequences,
            "metadata": self.metadata,
        }


class Scenario:
    """Represents a test scenario for evaluating LLM coherence.
    
    A scenario consists of a sequence of conversation turns that test
    specific aspects of LLM behavior, such as maintaining state,
    following constraints, or logical consistency over time.
    """
    
    def __init__(self, config: ScenarioConfig):
        """Initialize a scenario.
        
        Args:
            config: Configuration for the scenario
        """
        self.config = config
        self.turns: List[ConversationTurn] = []
        self.validators: List[Callable] = []
        self.created_at = datetime.now()
    
    def add_turn(self, turn: ConversationTurn) -> "Scenario":
        """Add a conversation turn to the scenario.
        
        Args:
            turn: ConversationTurn to add
            
        Returns:
            Self for method chaining
        """
        self.turns.append(turn)
        return self
    
    def add_user_input(
        self,
        content: str,
        expected_patterns: Optional[List[str]] = None,
        **metadata
    ) -> "Scenario":
        """Add a user input turn.
        
        Args:
            content: The user's input
            expected_patterns: Optional patterns expected in the response
            **metadata: Additional metadata for this turn
            
        Returns:
            Self for method chaining
        """
        turn = ConversationTurn(
            turn_type=TurnType.USER_INPUT,
            content=content,
            expected_patterns=expected_patterns or [],
            metadata=metadata,
        )
        return self.add_turn(turn)
    
    def add_state_check(
        self,
        description: str,
        expected_patterns: List[str],
        **metadata
    ) -> "Scenario":
        """Add a state check turn.
        
        Args:
            description: Description of what is being checked
            expected_patterns: Patterns that should be present
            **metadata: Additional metadata
            
        Returns:
            Self for method chaining
        """
        turn = ConversationTurn(
            turn_type=TurnType.STATE_CHECK,
            content=description,
            expected_patterns=expected_patterns,
            metadata=metadata,
        )
        return self.add_turn(turn)
    
    def add_validator(self, validator: Callable) -> "Scenario":
        """Add a custom validator function.
        
        Args:
            validator: Callable that takes conversation history and returns bool
            
        Returns:
            Self for method chaining
        """
        self.validators.append(validator)
        return self
    
    def get_system_message(self) -> Optional[Dict[str, str]]:
        """Get the system message for this scenario.
        
        Returns:
            System message dict or None
        """
        if self.config.system_prompt:
            return {
                "role": "system",
                "content": self.config.system_prompt,
            }
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scenario to dictionary.
        
        Returns:
            Dictionary representation of the scenario
        """
        return {
            "config": self.config.to_dict(),
            "turns": [turn.to_dict() for turn in self.turns],
            "created_at": self.created_at.isoformat(),
            "num_validators": len(self.validators),
        }
    
    def __len__(self) -> int:
        """Return the number of turns in the scenario."""
        return len(self.turns)
    
    def __repr__(self) -> str:
        """String representation of the scenario."""
        return f"Scenario(name='{self.config.name}', turns={len(self.turns)})"
