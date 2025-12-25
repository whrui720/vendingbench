"""Export utilities for saving results."""
import json
from pathlib import Path
from typing import Union, List
from datetime import datetime

from vendingbench.core.evaluator import EvaluationResult
from vendingbench.core.conversation import ConversationHistory


def save_evaluation_result(
    result: EvaluationResult,
    output_path: Union[str, Path],
):
    """Save an evaluation result to a JSON file.
    
    Args:
        result: EvaluationResult to save
        output_path: Path to save the result
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, indent=2)


def save_conversation_history(
    history: ConversationHistory,
    output_path: Union[str, Path],
):
    """Save conversation history to a JSON file.
    
    Args:
        history: ConversationHistory to save
        output_path: Path to save the history
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(history.to_dict(), f, indent=2)


def save_batch_results(
    results: List[EvaluationResult],
    output_dir: Union[str, Path],
    filename_prefix: str = "batch_results",
):
    """Save multiple evaluation results to a directory.
    
    Args:
        results: List of EvaluationResult objects
        output_dir: Directory to save results
        filename_prefix: Prefix for result filenames
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save individual results
    for i, result in enumerate(results):
        filename = f"{filename_prefix}_{i}_{timestamp}.json"
        save_evaluation_result(result, output_dir / filename)
    
    # Save summary
    summary = {
        "timestamp": timestamp,
        "num_results": len(results),
        "results": [r.to_dict() for r in results],
        "aggregate_pass_rate": sum(r.calculate_pass_rate() for r in results) / len(results) if results else 0.0,
    }
    
    summary_path = output_dir / f"{filename_prefix}_summary_{timestamp}.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)


def load_evaluation_result(input_path: Union[str, Path]) -> dict:
    """Load an evaluation result from a JSON file.
    
    Args:
        input_path: Path to the result file
        
    Returns:
        Dictionary containing the result data
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)
