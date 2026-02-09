"""
Example usage of the WordleSolver API.
This script demonstrates how to use the solver programmatically.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.solver import WordleSolver


def example_basic_usage():
    """Basic usage example."""
    print("="*60)
    print("Example 1: Basic Usage")
    print("="*60)
    
    # Initialize solver for 5-letter words
    solver = WordleSolver(word_length=5, tolerance=17)
    
    print(f"\nDictionary loaded: {len(solver.liste_mot)} words")
    print(f"Starting possibilities: {len(solver.li_poss_mot)}")
    
    # Get first suggestion
    print("\n--- Round 1 ---")
    suggestions, info_gain, elapsed = solver.get_next_guess(n_suggestions=3)
    print(f"Suggested words: {suggestions}")
    print(f"Expected info gain: {info_gain:.3f} bits")
    print(f"Computation time: {elapsed:.2f}s")
    
    # Simulate feedback (example: we guessed "saine" and got "01020")
    word = suggestions[0]
    result = "01020"  # This would come from the actual game
    print(f"\nApplying feedback for '{word}': {result}")
    
    remaining = solver.apply_feedback(word, result)
    print(f"Remaining possibilities: {remaining}")
    
    # Get next suggestion
    if remaining > 1:
        print("\n--- Round 2 ---")
        suggestions, info_gain, elapsed = solver.get_next_guess(n_suggestions=3)
        print(f"Suggested words: {suggestions}")
        print(f"Expected info gain: {info_gain:.3f} bits")


def example_different_lengths():
    """Example with different word lengths."""
    print("\n\n" + "="*60)
    print("Example 2: Different Word Lengths")
    print("="*60)
    
    for length in [5, 6, 7]:
        print(f"\n--- {length}-letter words ---")
        solver = WordleSolver(word_length=length, tolerance=15)
        print(f"Dictionary size: {len(solver.liste_mot)} words")
        
        # Get first suggestion (without verbose output)
        suggestions, info_gain, elapsed = solver.get_next_guess(n_suggestions=1, verbose=False)
        print(f"Best first word: {suggestions[0]}")
        print(f"Info gain: {info_gain:.3f} bits")
        print(f"Time: {elapsed:.2f}s")


def example_interactive():
    """Example of interactive solving."""
    print("\n\n" + "="*60)
    print("Example 3: Interactive Solving")
    print("="*60)
    print("\nThis would start an interactive session where you")
    print("enter feedback from the actual game.")
    print("\nTo try it, uncomment the line below:")
    print("# solver = WordleSolver(word_length=5)")
    print("# solver.solve_interactive()")


def example_with_initial_info():
    """Example with initial constraints."""
    print("\n\n" + "="*60)
    print("Example 4: Starting with Known Information")
    print("="*60)
    
    solver = WordleSolver(word_length=5)
    print(f"\nStarting with {len(solver.li_poss_mot)} words")
    
    # Suppose we know:
    # - Letter 'e' is in position 2 (green)
    # - Letter 'a' is in the word but not position 1 (yellow)
    
    print("\nApplying initial constraint: 'e' in position 2")
    # This would be from actual game feedback
    # For demonstration, we manually filter (in real use, this comes from game)
    
    suggestions, info_gain, elapsed = solver.get_next_guess(n_suggestions=5, verbose=False)
    print(f"\nTop 5 suggestions given constraints:")
    for i, word in enumerate(suggestions, 1):
        print(f"  {i}. {word}")


def example_performance_comparison():
    """Compare performance across word lengths."""
    print("\n\n" + "="*60)
    print("Example 5: Performance Comparison")
    print("="*60)
    
    print("\nEstimated first-guess computation times:")
    print(f"{'Length':<10} {'Words':<10} {'Est. Time':<15}")
    print("-" * 40)
    
    for length in [5, 6, 7, 8, 9]:
        try:
            solver = WordleSolver(word_length=length, tolerance=15)
            from src.utils.heuristics import temps
            est_time = temps(len(solver.liste_mot), len(solver.li_poss_mot), length)
            print(f"{length:<10} {len(solver.liste_mot):<10} {est_time:<.2f}s")
        except FileNotFoundError:
            print(f"{length:<10} {'N/A':<10} {'No data':<15}")


if __name__ == "__main__":
    print("\n" + "🎯 WORDLE SOLVER - API EXAMPLES" + "\n")
    
    # Run examples
    example_basic_usage()
    example_different_lengths()
    example_interactive()
    example_with_initial_info()
    example_performance_comparison()
    
    print("\n\n" + "="*60)
    print("✅ Examples completed!")
    print("="*60)
    print("\nFor more advanced usage, see notebooks/wordle_solver.ipynb")
    print("For interactive solving, run: python Wordle.py")
