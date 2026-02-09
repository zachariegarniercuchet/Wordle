"""
Main WordleSolver class that orchestrates the solving algorithm.
"""

import time
import os
from pathlib import Path

# Handle both package and direct imports
try:
    from .utils import (
        dico_mot, li_dico_to_li_mot, li_mot_to_li_dico, verif,
        new_liste1, new_liste2, esperance, Mmi,
        temps, bon_mot3
    )
except ImportError:
    from utils import (
        dico_mot, li_dico_to_li_mot, li_mot_to_li_dico, verif,
        new_liste1, new_liste2, esperance, Mmi,
        temps, bon_mot3
    )


class WordleSolver:
    """
    Intelligent Wordle solver using information theory.
    
    This solver uses Shannon entropy to calculate the expected information gain
    for each candidate word and selects the optimal guess at each step.
    """
    
    def __init__(self, word_length=5, tolerance=17, data_path=None):
        """
        Initialize the Wordle solver.
        
        Args:
            word_length (int): Length of words to solve (5-9)
            tolerance (float): Maximum acceptable computation time in seconds
            data_path (str, optional): Path to data directory
        """
        self.word_length = word_length
        self.tolerance = tolerance
        
        # Set data path
        if data_path is None:
            self.data_path = Path(__file__).parent.parent / "data"
        else:
            self.data_path = Path(data_path)
        
        # Load word lists
        self.liste_mot = []
        self.liste_dico = []
        self._load_words()
        
        # Initialize possible word lists
        self.li_poss_mot = self.liste_mot[:]
        self.li_poss_dico = self.liste_dico[:]
        
    def _load_words(self):
        """Load word list from data directory."""
        filename = self.data_path / f"french_{self.word_length}.txt"
        
        if not filename.exists():
            raise FileNotFoundError(
                f"Word list not found: {filename}\n"
                f"Please ensure data/french_{self.word_length}.txt exists."
            )
        
        with open(filename, "r", encoding='utf-8') as fichier:
            lignes = fichier.readlines()
        
        for ligne in lignes:
            newline = ligne.strip()
            if newline:
                self.liste_mot.append(newline)
                self.liste_dico.append(dico_mot(newline))
        
        print(f"Loaded {len(self.liste_mot)} words of length {self.word_length}")
    
    def reset(self):
        """Reset the solver to initial state."""
        self.li_poss_mot = self.liste_mot[:]
        self.li_poss_dico = self.liste_dico[:]
    
    def apply_feedback(self, word, result):
        """
        Apply feedback to filter possible words.
        
        Args:
            word (str): The guessed word
            result (str): Feedback string (e.g., "01200")
            
        Returns:
            int: Number of remaining possible words
        """
        booleen = verif(word)
        
        if booleen:
            self.li_poss_dico = new_liste2(self.li_poss_dico, dico_mot(word), result)
            self.li_poss_mot = li_dico_to_li_mot(self.li_poss_dico)
        else:
            self.li_poss_mot = new_liste1(self.li_poss_mot, word, result)
            self.li_poss_dico = li_mot_to_li_dico(self.li_poss_mot)
        
        return len(self.li_poss_mot)
    
    def meilleur_mot(self, liste_mot, liste_dico, li_poss_mot, li_poss_dico, n):
        """
        Find the best word(s) to guess.
        
        Args:
            liste_mot (list): Candidate words
            liste_dico (list): Candidate words as dictionaries
            li_poss_mot (list): Possible answer words
            li_poss_dico (list): Possible answer words as dictionaries
            n (int): Number of top words to return
            
        Returns:
            tuple: (list of best words, expected information gain)
        """
        dico_average = {}
        l_m = len(liste_mot)
        
        master_p = []  # Master words that are possible answers
        master_np = []  # Master words that are not possible answers
        
        for i in range(l_m):
            mot = liste_mot[i]
            booleen = verif(mot)
            possi = False
            
            if booleen:
                m_o_t = liste_dico[i]
                espoir_mot = esperance(li_poss_dico, m_o_t, booleen, self.word_length)
                dico_average[mot] = espoir_mot[0]
                e = espoir_mot[1]
                
                if m_o_t in li_poss_dico:
                    possi = True
            else:
                espoir_mot = esperance(li_poss_mot, mot, booleen, self.word_length)
                dico_average[mot] = espoir_mot[0]
                e = espoir_mot[1]
                
                if mot in li_poss_mot:
                    possi = True
            
            if e and possi:  # Master word that is possible
                master_p.append(mot)
            elif e:  # Master word that is not possible
                master_np.append(mot)
        
        # Prefer master words that are possible answers
        if len(master_p) != 0:
            espoir_best = dico_average[master_p[0]]
            print('Master words (possible): ', master_p)
            return (master_p, espoir_best)
        elif len(master_np) != 0:
            espoir_best = dico_average[master_np[0]]
            print('Master words (not possible): ', master_np)
            return (master_np, espoir_best)
        
        # Otherwise, return top n words by expected information gain
        while n > len(dico_average):
            n += -1
        
        premiers_mots = Mmi(dico_average, False, True, n)
        liste = []
        for mot, nb in premiers_mots.items():
            liste.append(mot)
        
        espoir_best = premiers_mots[liste[0]]
        
        return (liste, espoir_best)
    
    def get_next_guess(self, n_suggestions=5, verbose=True):
        """
        Get the next optimal guess(es).
        
        Args:
            n_suggestions (int): Number of suggestions to return
            verbose (bool): Print timing and progress information
            
        Returns:
            tuple: (list of suggested words, expected information gain, computation time)
        """
        start = time.time()
        
        l_poss_mot = len(self.li_poss_mot)
        l_mot = len(self.liste_mot)
        
        te = temps(l_mot, l_poss_mot, self.word_length)
        
        if verbose:
            print(f"Estimated time: {te:.2f}s")
            print(f"Remaining possible words: {l_poss_mot}")
        
        # Apply heuristics if computation would be too slow
        if te > self.tolerance:
            if verbose:
                print(f"Applying heuristics (tolerance: {self.tolerance}s)...")
            new_liste_mot = bon_mot3(self.liste_mot, self.li_poss_mot, self.tolerance)
            new_liste_dico = li_mot_to_li_dico(new_liste_mot)
        else:
            new_liste_mot = self.liste_mot[:]
            new_liste_dico = self.liste_dico[:]
        
        if len(self.li_poss_mot) == 0 or len(new_liste_mot) == 0:
            return ([], 0, 0)
        
        # Find best words
        premiers_mots, esp_best = self.meilleur_mot(
            new_liste_mot, new_liste_dico,
            self.li_poss_mot, self.li_poss_dico,
            n_suggestions
        )
        
        end = time.time()
        elapsed = end - start
        
        if verbose:
            print(f"Computation time: {elapsed:.2f}s")
        
        return (premiers_mots, esp_best, elapsed)
    
    def get_possible_words(self, limit=10):
        """
        Get the current list of possible words.
        
        Args:
            limit (int): Maximum number of words to return (None for all)
            
        Returns:
            list: Possible words
        """
        if limit is None:
            return self.li_poss_mot
        return self.li_poss_mot[:limit]
    
    def solve_interactive(self):
        """
        Interactive solving session (command-line interface).
        """
        print(f"\n=== Wordle Solver ({self.word_length} letters) ===\n")
        print(f"Loaded {len(self.liste_mot)} words")
        print(f"Current possible words: {len(self.li_poss_mot)}\n")
        
        while len(self.li_poss_mot) > 1:
            # Get suggestion
            suggestions, esp, elapsed = self.get_next_guess()
            
            if not suggestions:
                print("No valid words found!")
                return None
            
            print(f"\nSuggested word: {suggestions[0]}")
            print(f"Expected information gain: {esp:.3f} bits")
            
            if len(suggestions) > 1:
                print(f"Alternative suggestions: {suggestions[1:]}")
            
            # Get feedback
            word = suggestions[0]
            result = input(f"\nEnter result for '{word}' (e.g., 01200): ").strip()
            
            if result == "":
                print("Skipping...")
                continue
            
            # Apply feedback
            remaining = self.apply_feedback(word, result)
            print(f"Remaining possible words: {remaining}")
            
            if remaining <= 5:
                print(f"Possible words: {self.li_poss_mot}")
        
        if len(self.li_poss_mot) == 1:
            print(f"\n🎉 Solution found: {self.li_poss_mot[0]}")
            return self.li_poss_mot[0]
        else:
            print("\n❌ No solution found (word not in database)")
            return None
