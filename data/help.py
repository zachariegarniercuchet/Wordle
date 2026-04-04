"""Helpers for building the word lists and cached opening guesses."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import bon_mot3, dico_mot, esperance, li_mot_to_li_dico, temps, verif


def _load_word_list(word_list_path: Path) -> list[str]:
    """Load a word list file, keeping order and removing duplicates."""

    words: list[str] = []
    seen: set[str] = set()

    with word_list_path.open("r", encoding="utf-8") as handle:
        for raw_word in handle:
            word = raw_word.strip().lower()
            if not word or word in seen:
                continue

            seen.add(word)
            words.append(word)

    return words


def _best_opening_guess(
    words: list[str],
    tolerance: float = 17.0,
    top_n: int = 10,
) -> dict[str, object]:
    """Compute the best initial guess for a vocabulary list."""

    if not words:
        return {"suggestions": [], "scores": {}, "expected_information": 0.0}

    word_length = len(words[0])
    possible_words = words[:]
    possible_dicts = li_mot_to_li_dico(possible_words)

    if temps(len(words), len(possible_words), word_length) > tolerance:
        candidate_words = bon_mot3(words, possible_words, tolerance)
    else:
        candidate_words = words[:]

    candidate_dicts = li_mot_to_li_dico(candidate_words)
    scores: dict[str, float] = {}

    for word, word_dict in zip(candidate_words, candidate_dicts):
        duplicate_letters = verif(word)
        if duplicate_letters:
            score, _ = esperance(possible_dicts, word_dict, True, word_length)
        else:
            score, _ = esperance(possible_words, word, False, word_length)

        scores[word] = score

    ranked_words = sorted(scores, key=lambda word: (-scores[word], word))
    top_words = ranked_words[:top_n]
    top_score = scores[top_words[0]]

    return {
        "suggestions": top_words,
        "scores": scores,
        "expected_information": top_score,
    }


def _format_top_words(best_guess: dict[str, object]) -> list[dict[str, object]]:
    """Format ranked words with their information gain."""

    suggestions = best_guess.get("suggestions", [])
    scores = best_guess.get("scores", {})

    formatted: list[dict[str, object]] = []
    for word in suggestions:
        formatted.append({"word": word, "bits": scores.get(word, 0.0)})

    return formatted


def split_words_alpha(
    source_path: str | Path = "words_alpha.txt",
    output_dir: str | Path | None = None,
    lengths: Iterable[int] = range(5, 10),
    prefix: str = "english",
) -> dict[int, int]:
    """Split ``words_alpha.txt`` into length-specific word list files.

    Args:
        source_path: Path to the source word list.
        output_dir: Directory where the split files should be written.
            Defaults to the directory containing the source file.
        lengths: Word lengths to export.
        prefix: Output file prefix, such as ``english`` or ``french``.

    Returns:
        A mapping of word length to number of words written.
    """

    source_file = Path(source_path)
    base_dir = Path(output_dir) if output_dir is not None else source_file.parent

    buckets: dict[int, list[str]] = {length: [] for length in lengths}
    seen: dict[int, set[str]] = {length: set() for length in buckets}

    with source_file.open("r", encoding="utf-8") as handle:
        for raw_word in handle:
            word = raw_word.strip().lower()
            if not word.isalpha():
                continue

            word_length = len(word)
            if word_length not in buckets:
                continue

            if word in seen[word_length]:
                continue

            seen[word_length].add(word)
            buckets[word_length].append(word)

    written_counts: dict[int, int] = {}
    for word_length, words in buckets.items():
        output_file = base_dir / f"{prefix}_{word_length}.txt"
        with output_file.open("w", encoding="utf-8", newline="\n") as handle:
            for word in words:
                handle.write(f"{word}\n")

        written_counts[word_length] = len(words)

    return written_counts


def precompute_top_examples(
    base_dir: str | Path | None = None,
    prefixes: Iterable[str] = ("english", "french"),
    lengths: Iterable[int] = range(5, 10),
    output_path: str | Path | None = None,
    tolerance: float = 17.0,
) -> dict[str, dict[str, object]]:
    """Precompute the top opening guess for each available vocabulary file."""

    data_dir = Path(base_dir) if base_dir is not None else Path(__file__).resolve().parent
    cache_path = Path(output_path) if output_path is not None else data_dir / "top_examples.json"

    cache: dict[str, dict[str, object]] = {}

    for prefix in prefixes:
        for word_length in lengths:
            word_list_path = data_dir / f"{prefix}_{word_length}.txt"
            if not word_list_path.exists():
                continue

            words = _load_word_list(word_list_path)
            best_guess = _best_opening_guess(words, tolerance=tolerance, top_n=10)
            top_words = _format_top_words(best_guess)

            cache[word_list_path.name] = {
                "top_word": top_words[0]["word"] if top_words else None,
                "top_words": top_words,
                "top_word_bits": top_words[0]["bits"] if top_words else 0.0,
                "expected_information": best_guess["expected_information"],
                "word_count": len(words),
            }

    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return cache


def precompute_top_examples_incremental(
    base_dir: str | Path | None = None,
    prefixes: Iterable[str] = ("english", "french"),
    lengths: Iterable[int] = (5,),
    output_path: str | Path | None = None,
    item_dir: str | Path | None = None,
    tolerance: float = 17.0,
) -> dict[str, dict[str, object]]:
    """Precompute opening guesses and save each result immediately."""

    data_dir = Path(base_dir) if base_dir is not None else Path(__file__).resolve().parent
    cache_path = Path(output_path) if output_path is not None else data_dir / "top_examples_5.json"
    results_dir = Path(item_dir) if item_dir is not None else data_dir / "top_examples"
    results_dir.mkdir(parents=True, exist_ok=True)

    cache: dict[str, dict[str, object]] = {}

    for prefix in prefixes:
        for word_length in lengths:
            word_list_path = data_dir / f"{prefix}_{word_length}.txt"
            if not word_list_path.exists():
                continue

            words = _load_word_list(word_list_path)
            best_guess = _best_opening_guess(words, tolerance=tolerance, top_n=10)
            top_words = _format_top_words(best_guess)

            cache[word_list_path.name] = {
                "top_word": top_words[0]["word"] if top_words else None,
                "top_words": top_words,
                "top_word_bits": top_words[0]["bits"] if top_words else 0.0,
                "expected_information": best_guess["expected_information"],
                "word_count": len(words),
            }

            item_path = results_dir / f"{word_list_path.stem}.json"
            item_path.write_text(
                json.dumps(cache[word_list_path.name], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Saved {item_path.name}")

    return cache


if __name__ == "__main__":
    cache = precompute_top_examples_incremental(prefixes=("english", "french"), lengths=(6,7))
    #print(f"top_examples_5.json: {len(cache)} vocabulary lists cached")