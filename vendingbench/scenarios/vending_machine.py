"""Vending machine scenario for testing long-term coherence.

This module provides a complete vending machine scenario that tests
an LLM's ability to maintain state, follow constraints, and remain
logically consistent over a multi-turn conversation.
"""
from vendingbench.core.scenario import Scenario, ScenarioConfig


def create_basic_vending_scenario() -> Scenario:
    """Create a basic vending machine scenario.
    
    This scenario tests whether the LLM can:
    - Maintain inventory state
    - Handle transactions correctly
    - Remember previous interactions
    - Follow constraints (e.g., out of stock items)
    
    Returns:
        Scenario object for a vending machine test
    """
    config = ScenarioConfig(
        name="basic_vending_machine",
        description="Test LLM's ability to simulate a vending machine with state management",
        system_prompt="""You are a vending machine. You have the following items:
- A1: Chips ($1.50) - 3 in stock
- A2: Cookies ($2.00) - 2 in stock
- A3: Candy ($1.00) - 5 in stock
- B1: Water ($1.50) - 4 in stock
- B2: Soda ($2.50) - 1 in stock

Keep track of inventory and money. Only accept $1, $5, $10, and $20 bills.
Provide change when necessary. Update inventory after each purchase.
Always show remaining inventory when asked.""",
        temperature=0.7,
        max_tokens=500,
    )
    
    scenario = Scenario(config)
    
    # Turn 1: Initial interaction
    scenario.add_user_input(
        "Hi, what items do you have?",
        expected_patterns=["Chips", "Cookies", "Candy", "Water", "Soda"]
    )
    
    # Turn 2: Purchase an item
    # Note: Patterns support both substring matching and regex (with proper escaping)
    scenario.add_user_input(
        "I'll take the chips (A1). Here's $5.",
        expected_patterns=["change", "$3.50", "\\$3\\.50"]  # Substring and regex patterns
    )
    
    # Turn 3: Check inventory changed
    scenario.add_user_input(
        "What's left in stock for A1?",
        expected_patterns=["2", "two"]
    )
    
    # Turn 4: Try to buy out of stock item later
    scenario.add_user_input(
        "I'll buy 3 cookies (A2).",
        expected_patterns=["only 2", "not enough", "insufficient"]
    )
    
    # Turn 5: Valid purchase
    scenario.add_user_input(
        "Okay, I'll take 1 cookie then. Here's $5.",
        expected_patterns=["change", "$3.00", "\\$3\\.00"]
    )
    
    return scenario


def create_complex_vending_scenario() -> Scenario:
    """Create a complex vending machine scenario with more challenging interactions.
    
    Returns:
        Scenario object for advanced vending machine test
    """
    config = ScenarioConfig(
        name="complex_vending_machine",
        description="Advanced test with multiple purchases, refunds, and state tracking",
        system_prompt="""You are a vending machine with the following features:
- Track inventory for each item
- Accept bills: $1, $5, $10, $20
- Give exact change
- Allow refunds within the same session
- Maintain transaction history

Initial inventory:
- A1: Chocolate Bar ($2.50) - 10 in stock
- A2: Granola Bar ($3.00) - 8 in stock
- B1: Orange Juice ($3.50) - 5 in stock
- B2: Sports Drink ($4.00) - 3 in stock
- C1: Energy Bar ($4.50) - 6 in stock""",
        temperature=0.7,
        max_tokens=600,
    )
    
    scenario = Scenario(config)
    
    # Multiple purchase scenario
    scenario.add_user_input(
        "I want to buy 2 chocolate bars.",
        expected_patterns=["\\$5.00", "\\$5\\.00", "five dollars"]
    )
    
    scenario.add_user_input(
        "Here's $10.",
        expected_patterns=["change", "\\$5.00", "\\$5\\.00"]
    )
    
    scenario.add_user_input(
        "How many chocolate bars do you have left?",
        expected_patterns=["8", "eight"]
    )
    
    # Test transaction memory
    scenario.add_user_input(
        "What did I buy so far?",
        expected_patterns=["chocolate", "2", "two"]
    )
    
    return scenario


def create_edge_case_scenario() -> Scenario:
    """Create a scenario that tests edge cases and error handling.
    
    Returns:
        Scenario object for edge case testing
    """
    config = ScenarioConfig(
        name="edge_cases",
        description="Test error handling and edge cases",
        system_prompt="""You are a vending machine. Inventory:
- A1: Gum ($0.50) - 2 in stock
- A2: Mints ($0.75) - 0 in stock (OUT OF STOCK)
- B1: Chips ($1.25) - 1 in stock

Handle errors gracefully for:
- Out of stock items
- Insufficient payment
- Invalid item codes
- Exact change scenarios""",
        temperature=0.7,
    )
    
    scenario = Scenario(config)
    
    scenario.add_user_input(
        "I want to buy A2.",
        expected_patterns=["out of stock", "not available", "unavailable"]
    )
    
    scenario.add_user_input(
        "Give me item Z9.",
        expected_patterns=["invalid", "not found", "doesn't exist"]
    )
    
    scenario.add_user_input(
        "I'll take B1. Here's $1.",
        expected_patterns=["insufficient", "not enough", "need"]
    )
    
    return scenario
