"""
Utility package for Wordle solver.
Contains modules for word manipulation, information theory, and heuristics.
"""

from .word_utils import (
    dico_mot, 
    dico_mot_to_mot, 
    li_dico_to_li_mot, 
    li_mot_to_li_dico,
    verif,
    erreur_result,
    erreur_mot,
    addition
)

from .list_operations import (
    remove_0,
    remove_1,
    remove_2,
    new_liste1,
    new_liste2
)

from .info_theory import (
    I,
    esperance,
    Mmi
)

from .game_feedback import (
    resultat,
    re_poss_liste,
    choice
)

from .heuristics import (
    temps,
    frequence1,
    frequence2,
    bon_mot1,
    bon_mot2,
    bon_mot3
)

__all__ = [
    # Word utilities
    'dico_mot', 'dico_mot_to_mot', 'li_dico_to_li_mot', 'li_mot_to_li_dico',
    'verif', 'erreur_result', 'erreur_mot', 'addition',
    # List operations
    'remove_0', 'remove_1', 'remove_2', 'new_liste1', 'new_liste2',
    # Information theory
    'I', 'esperance', 'Mmi',
    # Game feedback
    'resultat', 're_poss_liste', 'choice',
    # Heuristics
    'temps', 'frequence1', 'frequence2', 'bon_mot1', 'bon_mot2', 'bon_mot3'
]
