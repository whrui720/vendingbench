"""Example showing how to use vendingbench with OpenAI models.

This example demonstrates integration with a real LLM provider.
Requires: pip install openai
Set your OPENAI_API_KEY environment variable before running.
"""
import os
from vendingbench.adapters.openai_adapter import OpenAIAdapter
from vendingbench.core.conversation import ConversationManager
from vendingbench.core.evaluator import Evaluator
from vendingbench.scenarios.vending_machine import (
    create_basic_vending_scenario,
    create_complex_vending_scenario,
)
from vendingbench.utils.export import save_evaluation_result, save_conversation_history


def run_with_openai():
    """Run vending machine scenarios with OpenAI models."""
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    # Initialize OpenAI adapter
    # You can use different models: gpt-4, gpt-3.5-turbo, etc.
    model_name = "gpt-3.5-turbo"  # or "gpt-4" for better results
    
    try:
        llm = OpenAIAdapter(model_name=model_name, api_key=api_key)
        print(f"Initialized OpenAI adapter with model: {model_name}\n")
    except ImportError as e:
        print(f"Error: {e}")
        print("Install OpenAI package with: pip install openai")
        return
    
    # Create and run basic scenario
    print("="*60)
    print("Running Basic Vending Machine Scenario")
    print("="*60 + "\n")
    
    scenario = create_basic_vending_scenario()
    manager = ConversationManager(llm)
    
    print(f"Scenario: {scenario.config.name}")
    print(f"Turns: {len(scenario)}\n")
    
    # Run with verbose output
    history = manager.run_scenario(scenario, verbose=True)
    
    # Evaluate
    evaluator = Evaluator()
    result = evaluator.evaluate(history, scenario)
    
    # Print results
    print("\n" + "="*60)
    print("Evaluation Results")
    print("="*60)
    print(f"Model: {result.model_name}")
    print(f"Pass Rate: {result.calculate_pass_rate():.2%}")
    print(f"Overall: {'PASSED' if result.overall_passed else 'FAILED'}\n")
    
    for metric in result.metrics:
        status = "✓" if metric.passed else "✗"
        print(f"{status} {metric.name}")
        if not metric.passed and metric.details.get("missing"):
            print(f"  Missing: {metric.details['missing']}")
    
    # Save results
    os.makedirs("results", exist_ok=True)
    save_conversation_history(history, "results/openai_basic_history.json")
    save_evaluation_result(result, "results/openai_basic_result.json")
    print("\nResults saved to 'results/' directory")
    
    # Optionally run complex scenario
    run_complex = input("\nRun complex scenario? (y/n): ").lower() == 'y'
    if run_complex:
        print("\n" + "="*60)
        print("Running Complex Vending Machine Scenario")
        print("="*60 + "\n")
        
        complex_scenario = create_complex_vending_scenario()
        complex_history = manager.run_scenario(complex_scenario, verbose=True)
        complex_result = evaluator.evaluate(complex_history, complex_scenario)
        
        print("\n" + "="*60)
        print("Complex Scenario Results")
        print("="*60)
        print(f"Pass Rate: {complex_result.calculate_pass_rate():.2%}")
        print(f"Overall: {'PASSED' if complex_result.overall_passed else 'FAILED'}")
        
        save_conversation_history(complex_history, "results/openai_complex_history.json")
        save_evaluation_result(complex_result, "results/openai_complex_result.json")


if __name__ == "__main__":
    run_with_openai()
