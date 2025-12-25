"""Advanced example showing custom scenarios and validators.

This example demonstrates:
1. Creating a custom scenario from scratch
2. Adding custom validators
3. Using the evaluation system
"""
from vendingbench.adapters.mock_llm import MockLLM
from vendingbench.core.scenario import Scenario, ScenarioConfig
from vendingbench.core.conversation import ConversationManager
from vendingbench.core.evaluator import Evaluator


def price_consistency_validator(history, scenario):
    """Custom validator to check price consistency across responses."""
    # Check that prices mentioned stay consistent
    for response in history.responses:
        content = response.content.lower()
        # This is a simple example - real validator would be more sophisticated
        if "$1.50" in content or "1.50" in content:
            # Validate that this price is used consistently
            return True
    return True


def inventory_tracking_validator(history, scenario):
    """Custom validator to check if inventory decreases correctly."""
    # In a real implementation, this would parse responses and track inventory
    # For this example, we just check that inventory is mentioned
    inventory_mentioned = 0
    for response in history.responses:
        if "stock" in response.content.lower() or "remaining" in response.content.lower():
            inventory_mentioned += 1
    return inventory_mentioned >= 2


def main():
    """Run an advanced example with custom validators."""
    
    # Create a custom scenario
    config = ScenarioConfig(
        name="custom_test",
        description="Custom vending machine test with validators",
        system_prompt="""You are a vending machine with:
- Soda ($1.50) - 5 in stock
- Juice ($2.00) - 3 in stock
Track inventory and prices consistently.""",
        temperature=0.7,
    )
    
    scenario = Scenario(config)
    
    # Add turns
    scenario.add_user_input(
        "What do you have?",
        expected_patterns=["Soda", "Juice", "$1.50", "$2.00"]
    )
    
    scenario.add_user_input(
        "I'll buy 2 sodas. Here's $5.",
        expected_patterns=["$2.00", "change"]
    )
    
    scenario.add_user_input(
        "How many sodas are left?",
        expected_patterns=["3", "three"]
    )
    
    # Add custom validators
    scenario.add_validator(price_consistency_validator)
    scenario.add_validator(inventory_tracking_validator)
    
    print(f"Created custom scenario: {scenario.config.name}")
    print(f"Turns: {len(scenario)}")
    print(f"Validators: {len(scenario.validators)}\n")
    
    # Create mock LLM with responses
    mock_responses = [
        "I have Soda ($1.50) with 5 in stock and Juice ($2.00) with 3 in stock.",
        "You purchased 2 Sodas for $3.00 total. Here's your $2.00 change. 3 Sodas remaining in stock.",
        "There are 3 Sodas remaining in stock.",
    ]
    
    llm = MockLLM(model_name="custom-test-model", responses=mock_responses)
    
    # Run scenario
    print("Running scenario...\n")
    manager = ConversationManager(llm)
    history = manager.run_scenario(scenario, verbose=True)
    
    # Evaluate
    print("\nEvaluating...\n")
    evaluator = Evaluator()
    result = evaluator.evaluate(history, scenario)
    
    # Print detailed results
    print("="*60)
    print(f"Results for: {result.scenario_name}")
    print(f"Pass Rate: {result.calculate_pass_rate():.2%}")
    print("="*60)
    
    for metric in result.metrics:
        print(f"\n{metric.name}:")
        print(f"  Passed: {metric.passed}")
        print(f"  Value: {metric.value:.2f}")
        if metric.details:
            for key, value in metric.details.items():
                if key != "turn_content":  # Skip verbose details
                    print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print(f"Final Result: {'PASSED' if result.overall_passed else 'FAILED'}")
    print("="*60)


if __name__ == "__main__":
    main()
