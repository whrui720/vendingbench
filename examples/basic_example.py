"""Basic example of using vendingbench framework.

This example demonstrates:
1. Creating a scenario
2. Running it with a mock LLM
3. Evaluating the results
"""
from vendingbench.adapters.mock_llm import MockLLM
from vendingbench.core.conversation import ConversationManager
from vendingbench.core.evaluator import Evaluator
from vendingbench.scenarios.vending_machine import create_basic_vending_scenario
from vendingbench.utils.export import save_evaluation_result, save_conversation_history


def main():
    """Run a basic vending machine scenario."""
    
    # Create a mock LLM with predefined responses
    mock_responses = [
        "I have the following items available:\n- A1: Chips ($1.50) - 3 in stock\n- A2: Cookies ($2.00) - 2 in stock\n- A3: Candy ($1.00) - 5 in stock\n- B1: Water ($1.50) - 4 in stock\n- B2: Soda ($2.50) - 1 in stock",
        "Thank you for your purchase! You bought Chips (A1) for $1.50. Your change is $3.50.",
        "A1 (Chips) now has 2 items remaining in stock.",
        "I'm sorry, but I only have 2 cookies in stock. I cannot sell you 3.",
        "Thank you! You bought 1 cookie (A2) for $2.00. Your change is $3.00. A2 now has 1 item in stock.",
    ]
    
    llm = MockLLM(model_name="mock-vending-test", responses=mock_responses)
    
    # Create the scenario
    scenario = create_basic_vending_scenario()
    print(f"Created scenario: {scenario.config.name}")
    print(f"Description: {scenario.config.description}")
    print(f"Number of turns: {len(scenario)}\n")
    
    # Run the scenario
    print("Running scenario...\n")
    manager = ConversationManager(llm)
    history = manager.run_scenario(scenario, verbose=True)
    
    print(f"\nScenario completed with {len(history.responses)} responses\n")
    
    # Evaluate the results
    print("Evaluating results...\n")
    evaluator = Evaluator()
    result = evaluator.evaluate(history, scenario)
    
    # Print results
    print("="*60)
    print(f"Evaluation Results for: {result.scenario_name}")
    print(f"Model: {result.model_name}")
    print(f"Overall Passed: {result.overall_passed}")
    print(f"Pass Rate: {result.calculate_pass_rate():.2%}")
    print("="*60)
    
    for metric in result.metrics:
        status = "✓" if metric.passed else "✗"
        print(f"{status} {metric.name}: {metric.value:.2f}")
        if metric.details.get("missing"):
            print(f"  Missing patterns: {metric.details['missing']}")
    
    print("\n" + "="*60)
    
    # Save results
    save_conversation_history(history, "results/basic_example_history.json")
    save_evaluation_result(result, "results/basic_example_result.json")
    print("\nResults saved to 'results/' directory")


if __name__ == "__main__":
    main()
