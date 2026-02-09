"""
Information theory calculations for optimal word selection.
Uses Shannon entropy to measure information gain.
"""

import math


def I(x):
    """
    Calculate information gain using Shannon entropy.
    
    Args:
        x (float): Probability value
        
    Returns:
        float: Information gain in bits
    """
    I = -math.log2(x)
    return I


def esperance(liste, mot, booleen, nbl):
    """
    Calculate expected information gain for a guess word.
    
    This function evaluates how much information we expect to gain
    by guessing a particular word, averaged across all possible answers.
    
    Args:
        liste (list): List of possible answer words
        mot (str or dict): Word to evaluate
        booleen (bool): True if word has duplicate letters (dictionary format)
        nbl (int): Word length
        
    Returns:
        list: [average_info_gain, is_master_word]
            - average_info_gain: Expected information in bits
            - is_master_word: True if this word guarantees optimal information gain
    """
    try:
        from .word_utils import li_dico_to_li_mot
        from .list_operations import new_liste1, new_liste2
        from .game_feedback import re_poss_liste
    except ImportError:
        from word_utils import li_dico_to_li_mot
        from list_operations import new_liste1, new_liste2
        from game_feedback import re_poss_liste
    
    tab = liste[:]
    tab_i = []
    l_t = len(tab)
    i = 0
    
    re = re_poss_liste(liste, mot, booleen, nbl)
    
    for result in re:
        if booleen:
            liste_filtered = new_liste2(liste, mot, result)
            liste_filtered = li_dico_to_li_mot(liste_filtered)
        else:
            liste_filtered = new_liste1(liste, mot, result)
        
        l_p = len(liste_filtered)
        x = l_p / l_t
        
        if x == 0:
            j = 0
            i += j
        else:
            j = I(x)
            i += j
            tab_i.append(j)
        
        liste = tab[:]
    
    average = i / 243  # Average over all possible outcomes
    master = False
    d = True
    mini = tab_i[0] if tab_i else 0
    
    if mini < I(1 / l_t):
        d = False
    
    l_i = len(tab_i)
    j = 1
    
    while j < l_i and d:
        if tab_i[j] < mini:
            mini = tab_i[j]
        if mini < I(1 / l_t):
            d = False
        j += 1
    
    if mini == I(1 / l_t):
        master = True
    
    return [average, master]


def Mmi(liste_dico, li, M, x):
    """
    General function to get max/min values from a list or dictionary.
    
    Args:
        liste_dico: Either a dict (key-value pairs) or a list of values
        li (bool): True if liste_dico is a list, False if it's a dict
        M (bool): True for max, False for min
        x (int): Number of max/min values to return
        
    Returns:
        list or dict: Top x maximum or minimum values
    """
    if li:  # If it's a list
        liste = []
        tab_Mm = []
        l = len(liste_dico)
        i = 0
        
        while len(liste) < x:
            Mm_i = i
            Mm_v = liste_dico[Mm_i]
            
            while Mm_v in tab_Mm:
                i += 1
                Mm_i = i
                Mm_v = liste_dico[Mm_i]
            
            for j in range(l):
                couple = []
                indice = j
                valeur = liste_dico[indice]
                
                if M and valeur > Mm_v and indice not in tab_Mm:
                    Mm_i = indice
                    Mm_v = valeur
                elif not M and valeur < Mm_v and indice not in tab_Mm:
                    Mm_i = indice
                    Mm_v = valeur
            
            tab_Mm.append(indice)
            couple.append(Mm_i)
            couple.append(Mm_v)
            liste.append(couple)
        
        return liste
    
    else:  # If it's a dictionary
        dico = {}
        tab_Mm = []
        cles_valeurs = []
        
        for cle, valeur in liste_dico.items():
            cle_valeur = []
            cle_valeur.append(cle)
            cle_valeur.append(valeur)
            cles_valeurs.append(cle_valeur)
        
        l_c_v = len(cles_valeurs)
        i = 0
        
        while len(tab_Mm) < x:
            Mm_cle = cles_valeurs[i][0]
            Mm_v = cles_valeurs[i][1]
            
            while Mm_v in tab_Mm:
                i += 1
                Mm_cle = cles_valeurs[i][0]
                Mm_v = cles_valeurs[i][1]
            
            for j in range(l_c_v):
                couple = cles_valeurs[j]
                cle = couple[0]
                valeur = couple[1]
                
                if M and valeur > Mm_v and cle not in tab_Mm:
                    Mm_cle = cle
                    Mm_v = valeur
                elif not M and valeur < Mm_v and cle not in tab_Mm:
                    Mm_cle = cle
                    Mm_v = valeur
            
            tab_Mm.append(Mm_cle)
            dico[Mm_cle] = Mm_v
        
        return dico
