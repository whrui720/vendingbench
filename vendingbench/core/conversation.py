"""Conversation management for running scenarios."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from vendingbench.core.llm_interface import LLMInterface, LLMResponse
from vendingbench.core.scenario import Scenario, TurnType


@dataclass
class ConversationHistory:
    """Manages the history of a conversation."""
    
    messages: List[Dict[str, str]] = field(default_factory=list)
    responses: List[LLMResponse] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str):
        """Add a message to the history.
        
        Args:
            role: Role of the message sender (system/user/assistant)
            content: Content of the message
        """
        self.messages.append({"role": role, "content": content})
    
    def add_response(self, response: LLMResponse):
        """Add an LLM response to the history.
        
        Args:
            response: The LLM response to add
        """
        self.responses.append(response)
        self.add_message("assistant", response.content)
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the conversation.
        
        Returns:
            List of message dictionaries
        """
        return self.messages.copy()
    
    def get_last_response(self) -> Optional[LLMResponse]:
        """Get the last LLM response.
        
        Returns:
            Last LLMResponse or None if no responses yet
        """
        return self.responses[-1] if self.responses else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary.
        
        Returns:
            Dictionary representation of the conversation history
        """
        return {
            "messages": self.messages,
            "responses": [r.to_dict() for r in self.responses],
            "metadata": self.metadata,
            "started_at": self.started_at.isoformat(),
            "num_turns": len(self.responses),
        }


class ConversationManager:
    """Manages the execution of scenarios with an LLM.
    
    This class handles running a scenario, maintaining conversation state,
    and collecting responses for evaluation.
    """
    
    def __init__(self, llm: LLMInterface):
        """Initialize the conversation manager.
        
        Args:
            llm: LLM interface to use for generation
        """
        self.llm = llm
    
    def run_scenario(
        self,
        scenario: Scenario,
        verbose: bool = False
    ) -> ConversationHistory:
        """Run a complete scenario with the LLM.
        
        Args:
            scenario: The scenario to execute
            verbose: Whether to print progress information
            
        Returns:
            ConversationHistory containing the full conversation
        """
        history = ConversationHistory()
        history.metadata["scenario_name"] = scenario.config.name
        history.metadata["model_name"] = self.llm.model_name
        
        # Add system prompt if present
        system_msg = scenario.get_system_message()
        if system_msg:
            history.add_message(system_msg["role"], system_msg["content"])
        
        # Execute each turn
        for i, turn in enumerate(scenario.turns):
            if verbose:
                print(f"Turn {i+1}/{len(scenario.turns)}: {turn.turn_type.value}")
            
            if turn.turn_type == TurnType.USER_INPUT:
                response = self._execute_user_turn(turn, history, scenario)
                history.add_response(response)
                
                if verbose:
                    print(f"  User: {turn.content[:50]}...")
                    print(f"  Assistant: {response.content[:50]}...")
            
            elif turn.turn_type == TurnType.STATE_CHECK:
                # State checks can optionally query the model
                if verbose:
                    print(f"  State check: {turn.content[:50]}...")
        
        return history
    
    def _execute_user_turn(
        self,
        turn,
        history: ConversationHistory,
        scenario: Scenario
    ) -> LLMResponse:
        """Execute a user input turn.
        
        Args:
            turn: The conversation turn to execute
            history: Current conversation history
            scenario: The scenario being executed
            
        Returns:
            LLM response for this turn
        """
        # Add user message
        history.add_message("user", turn.content)
        
        # Generate response
        response = self.llm.generate(
            messages=history.get_messages(),
            temperature=scenario.config.temperature,
            max_tokens=scenario.config.max_tokens,
        )
        
        return response
    
    def continue_conversation(
        self,
        history: ConversationHistory,
        user_input: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Continue an existing conversation with a new user input.
        
        Args:
            history: Existing conversation history
            user_input: New user input
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM response
        """
        history.add_message("user", user_input)
        
        response = self.llm.generate(
            messages=history.get_messages(),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        history.add_response(response)
        return response
