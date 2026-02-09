"""
Game feedback simulation - generates feedback for guesses against answer words.
"""

import random


def resultat(mott, motc, booleen, nbl):
    """
    Calculate the feedback for a guess against the correct word.
    
    Args:
        mott: Tested word (string or dict)
        motc: Correct word (string or dict)
        booleen (bool): True if words have duplicate letters (dict format)
        nbl (int): Word length
        
    Returns:
        str: Result string (e.g., "01200")
            - '0' = letter not in word (gray)
            - '1' = letter in word but wrong position (yellow)
            - '2' = letter in correct position (green)
    """
    result = ''
    
    if booleen:  # If the word is a dictionary
        re = ['0'] * nbl
        
        for lettre, t_pos in mott.items():
            if lettre in motc:
                l_pos = len(t_pos)
                t_posc = motc[lettre]
                compt = len(t_posc)  # Number of times letter appears in correct word
                
                p = 0
                po = []
                
                # First pass: mark exact matches (green)
                for posi in t_pos:
                    if posi in t_posc:
                        re[posi] = '2'
                        p += 1
                    else:
                        po.append(posi)
                
                # Second pass: mark letters in wrong positions (yellow)
                for posi in po:
                    if p == compt or p == l_pos:
                        break
                    else:
                        re[posi] = '1'
                        p += 1
        
        for i in re:
            result += i
    
    else:  # Simple case without duplicate letters
        l_mott = len(mott)
        for i in range(l_mott):
            lettret = mott[i]
            lettrec = motc[i]
            
            if lettret == lettrec:
                result += '2'
            else:
                if lettret in motc:
                    result += '1'
                else:
                    result += '0'
    
    return result


def re_poss_liste(liste_poss, mott, booleen, nbl):
    """
    Generate all possible unique feedback patterns for a guess word.
    
    Args:
        liste_poss (list): List of possible answer words
        mott: Tested word (string or dict)
        booleen (bool): True if word has duplicate letters
        nbl (int): Word length
        
    Returns:
        list: List of unique result strings
    """
    re = []
    for motc in liste_poss:
        result = resultat(mott, motc, booleen, nbl)
        if result not in re:
            re.append(result)
    
    return re


def choice(liste):
    """
    Randomly select a word from a list.
    
    Args:
        liste (list): List of words
        
    Returns:
        str: Randomly selected word
    """
    l_l = len(liste)
    n = random.randrange(l_l)
    mot = liste[n]
    return mot
