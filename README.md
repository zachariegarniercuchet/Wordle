# Wordle Solver: An Information-Theoretic Approach

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An optimal solver for [Wordle](https://en.wikipedia.org/wiki/Wordle) and its variants, leveraging **information theory** and **Shannon entropy** to maximize information gain at each step. This implementation supports French word dictionaries with 5-9 letter words and employs sophisticated heuristics to maintain computational tractability for longer words.

## Theoretical Foundation

### The Wordle Problem

Wordle is a constraint satisfaction problem where the goal is to identify a hidden word from a finite dictionary through a series of guesses, receiving ternary feedback for each letter position:
- **2 (Green)**: Letter is correct and in the right position
- **1 (Yellow)**: Letter exists in the word but in the wrong position  
- **0 (Gray)**: Letter does not exist in the word

### Information-Theoretic Approach

This solver implements an **optimal strategy** based on maximizing expected information gain, grounded in [Shannon's information theory](https://en.wikipedia.org/wiki/Information_theory).

#### Shannon Entropy

For a discrete random variable *X* with possible outcomes *x₁, x₂, ..., xₙ* and probability mass function *P(X)*, the Shannon entropy *H(X)* quantifies the expected uncertainty:

$$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$

#### Information Gain

The information gained by observing an outcome is:

$$I(x) = -\log_2 P(x) = \log_2 \frac{1}{P(x)}$$

When we guess a word and receive feedback, we partition the remaining possible words into equivalence classes. The **expected information gain** for a guess *g* is:

$$E[I(g)] = \sum_{r \in R} P(r|g) \cdot I(r|g)$$

where *R* is the set of all possible feedback patterns, and *P(r|g)* is the probability of receiving feedback *r* given guess *g*.

#### Optimal Strategy

At each step, we select the word that maximizes expected information gain:

$$g^* = \arg\max_{g \in W} E[I(g)]$$

where *W* is the set of all candidate words.

### Computational Complexity

The naive algorithm has time complexity **O(|W|² × 3ⁿ)** where:
- |*W*| = size of the word dictionary
- *n* = word length
- *3ⁿ* = possible feedback patterns (3 states per position)

For a 5-letter word with ~15,000 words, this requires ~2.4 billion operations per guess.

## Quick Start

### Installation

```bash
# Clone the repository
git clone git@github.com:zachariegarniercuchet/Wordle.git
cd Wordle

# Install optional dependencies (for notebooks and analysis)
pip install -r requirements.txt
```

### Basic Usage

```python
from src.solver import WordleSolver

# Initialize solver
solver = WordleSolver(word_length=5, tolerance=17)

# Get optimal first guess
suggestions, info_gain, time = solver.get_next_guess(n_suggestions=5)
print(f"Optimal guess: {suggestions[0]}")
print(f"Expected information gain: {info_gain:.3f} bits")

# Apply game feedback (format: "01200")
# 0=gray, 1=yellow, 2=green
solver.apply_feedback("saine", "01020")

# Continue until solved
while len(solver.li_poss_mot) > 1:
    suggestions, _, _ = solver.get_next_guess()
    # ... get feedback from game ...
```

### Web App Demo

An `index.html` web app is included in this repository so you can test the solver in a browser.

You can play the game directly in French or English:
- French: https://wordly.org/fr
- English: https://wordly.org/

To test the solver with the bundled web app, open:

https://zachariegarniercuchet.github.io/Wordle/

## Game Variants Supported

### Wordle (Classic)
**Problem Specification**: Given a dictionary *D* of *n*-letter words, identify a target word *w* ∈ *D* through sequential guesses, receiving ternary feedback per letter position.

- **Attempts**: Maximum 6 guesses
- **Feedback alphabet**: {0, 1, 2}
- **Standard word length**: 5 letters

[Play French Wordle](https://wordle.louan.me/)

### Sutom (Variant)
**Modified constraint**: First letter *w[0]* is revealed *a priori*, reducing initial entropy by ~4.7 bits.

- **Attempts**: Maximum 6 guesses  
- **Word lengths**: 5-9 letters
- **Initial constraint**: *g[0] = w[0]* for all guesses *g*

[Play Sutom](https://sutom.nocle.fr/)

## Algorithm Details

### Core Algorithm: Expected Information Maximization

#### 1. Feedback Partition Function

For each guess *g* and possible answer *a*, we compute the feedback pattern *f(g, a)*:

```
f(g, a)[i] = {
  2  if g[i] = a[i]           (correct position)
  1  if g[i] ∈ a and g[i] ≠ a[i]  (wrong position)
  0  otherwise                (not in word)
}
```

This handles duplicate letters correctly by tracking letter counts.

#### 2. Expected Information Gain

For a candidate guess *g* with remaining possible answers *A*:

```
E[I(g)] = Σ_{r∈R} P(r|g,A) · log₂(|A| / |A_r|)
```

where:
- *R* = set of all possible feedback patterns
- *A_r* = subset of *A* consistent with receiving feedback *r*
- *P(r|g,A)* = |*A_r*| / |*A*|

#### 3. Optimal Word Selection

```python
def select_optimal_word(candidates, possible_answers):
    best_word = None
    max_expected_info = 0
    
    for word in candidates:
        expected_info = calculate_expected_information(word, possible_answers)
        if expected_info > max_expected_info:
            max_expected_info = expected_info
            best_word = word
    
    return best_word, max_expected_info
```

### Master Words

A **master word** is a guess that partitions the remaining answer space such that:

$$\min_{r \in R} I(r) = \log_2(|A|)$$

In other words, every possible feedback pattern eliminates at least one word, guaranteeing progress.

### Heuristic Optimization

For dictionaries with *n* > 30,000 words or word lengths > 7, we employ **adaptive heuristics**:

#### Frequency-Based Pruning

1. **Letter Frequency Analysis**: Compute positional letter frequencies:
   ```
   freq[letter][position] = count(letter, position) / |A|
   ```

2. **Word Scoring**: Rank candidates by expected frequency:
   ```
   score(w) = Σ_{i=1}^{n} freq[w[i]][i]
   ```

3. **Candidate Reduction**: Retain top *k* candidates where *k* is chosen to satisfy time constraint *T*:
   ```
   k = floor(T / (c · |A|))
   ```
   where *c* is an empirically-determined constant.

#### Computational Savings

This reduces complexity from **O(|W|² × 3ⁿ)** to approximately **O(k × |A| × 3ⁿ)** where *k* << |*W*|.

For 9-letter words:
- Without heuristics: ~15 minutes per guess
- With heuristics: ~10 seconds per guess
- Information loss: < 2% in most cases

The `bon_mot3()` function implements these heuristics to keep computation time under 17 seconds by default.

### Code Organization

The codebase is now modularized for better maintainability:

- **`src/solver.py`**: Main `WordleSolver` class that orchestrates the solving algorithm
- **`src/utils/`**: Utility modules for specific tasks
  - `word_utils.py`: Word-to-dictionary conversions, validation
  - `info_theory.py`: Shannon entropy calculations, information gain
  - `heuristics.py`: Frequency analysis and search space reduction
  - `list_operations.py`: Word filtering based on feedback
  - `game_feedback.py`: Feedback simulation for testing

### Word Lists

The `data/` directory contains curated French word dictionaries sourced from French language databases. Files are named `french_[n].txt` where `n` is the word length (5-9).

## Advanced Usage

### Option 1: Interactive Jupyter Notebook (Recommended)

For research, experimentation, and visualization:

```bash
cd notebooks
jupyter notebook wordle_solver.ipynb
```

**Features**:
- Step-by-step solving with manual control
- Automatic solving sessions  
- Performance analysis and batch testing
- Information gain visualization
- Custom word list analysis

### Option 2: Python API

Programmatic access for integration:

```python
from src.solver import WordleSolver

# Initialize solver
solver = WordleSolver(word_length=5, tolerance=17)

# Get optimal guess
suggestions, info_gain, _ = solver.get_next_guess(n_suggestions=5)

# Apply feedback
solver.apply_feedback(word="saine", result="01020")

# Check remaining possibilities
print(f"Remaining words: {len(solver.li_poss_mot)}")
```

### Option 3: Command-Line Interface

Legacy interface for quick testing:

```bash
# Interactive solver
python Wordle.py

# Sutom variant (first letter revealed)
python Sutom.py
```



### Related Projects
- [Wordle Wikipedia](https://en.wikipedia.org/wiki/Wordle) - Game overview and history
- [3Blue1Brown Wordle Analysis](https://www.youtube.com/watch?v=v68zYyaEmEA) - Visual explanation of information theory approach
- [Original Wordle](https://www.nytimes.com/games/wordle/) by Josh Wardle

### French Wordle Variants
- [SUTOM](https://sutom.nocle.fr/) - French variant with first letter revealed
- [Wordle (French)](https://wordle.louan.me/) - French word adaptation



### Development Setup

```bash
# Fork and clone
git clone git@github.com:your-username/Wordle.git
cd Wordle

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black src/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

This project is free for academic, educational, and personal use. Commercial use requires attribution.

## Citation

If you use this work in academic research, please cite:

```bibtex
@software{garnier_cuchet_2026_wordle,
  author = {Garnier-Cuchet, Zacharie},
  title = {Wordle Solver: An Information-Theoretic Approach},
  year = {2026},
  url = {https://github.com/zachariegarniercuchet/Wordle},
  note = {Optimal solver using Shannon entropy and information maximization}
}
```

## Author

**Zacharie Garnier-Cuchet**
- GitHub: [@zachariegarniercuchet](https://github.com/zachariegarniercuchet)
- Repository: [github.com/zachariegarniercuchet/Wordle](https://github.com/zachariegarniercuchet/Wordle)

## Acknowledgments

- **Josh Wardle** - Creator of the original Wordle game
- **Claude Shannon** - Foundational work in information theory (1948)
- **Donald Knuth** - Pioneering work on Mastermind optimal strategies (1977)
- **Grant Sanderson (3Blue1Brown)** - Accessible explanations of information theory in Wordle
- **French Language Database Contributors** - Comprehensive word list curation

---

<div align="center">

** Star this repository if you find it useful!**

*For questions, issues, or collaboration inquiries, please [open an issue](https://github.com/zachariegarniercuchet/Wordle/issues) on GitHub.*

</div>

