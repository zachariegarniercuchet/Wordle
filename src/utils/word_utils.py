"""
Word manipulation utilities for Wordle solver.
Handles word-to-dictionary conversions and validations.
"""

def dico_mot(mot):
    """
    Convert a word to a dictionary mapping letters to their positions.
    
    Args:
        mot (str): Input word
        
    Returns:
        dict: Dictionary with letters as keys and lists of positions as values
        
    Example:
        >>> dico_mot("terre")
        {'t': [0], 'e': [1, 4], 'r': [2, 3]}
    """
    nbl = len(mot)
    dico_mot = {}
    i = 0
    compte = []  # Track indices already counted as similar to i
    
    while i < nbl:  # Iterate through all letters
        l1 = mot[i]
        tab_l = [i]
        for j in range(i + 1, nbl):  # Check letters after i
            l2 = mot[j]
            if l1 == l2:
                tab_l.append(j)
                c = j
                compte.append(c)
        dico_mot[mot[i]] = tab_l
        i += 1
        while i in compte:
            i += 1
    
    return dico_mot


def dico_mot_to_mot(dico_mot):
    """
    Convert a dictionary representation back to a word string.
    
    Args:
        dico_mot (dict): Dictionary with letters as keys and positions as values
        
    Returns:
        str: Reconstructed word
    """
    nbl = 0
    mot0 = dico_mot
    for l, pos in mot0.items():
        nbl += len(pos)
    
    mot = ""
    i = 0
    while i < nbl:
        for lettre, position in dico_mot.items():
            for j in position:
                if j == i:
                    mot += lettre
                    i += 1
    return mot


def li_dico_to_li_mot(liste):
    """
    Convert list of dictionary representations to list of word strings.
    
    Args:
        liste (list): List of word dictionaries
        
    Returns:
        list: List of word strings
    """
    new = []
    for mot in liste:
        new.append(dico_mot_to_mot(mot))
    return new


def li_mot_to_li_dico(liste):
    """
    Convert list of word strings to list of dictionary representations.
    
    Args:
        liste (list): List of word strings
        
    Returns:
        list: List of word dictionaries
    """
    new = []
    for mot in liste:
        new.append(dico_mot(mot))
    return new


def verif(mot):
    """
    Check if a word contains duplicate letters.
    
    Args:
        mot (str): Word to check
        
    Returns:
        bool: True if word has duplicate letters, False otherwise
    """
    c = False
    m = len(mot)
    for i in range(m):
        for j in range(i + 1, m):
            if mot[j] == mot[i]:
                c = True
    return c


def erreur_result(result, nbl):
    """
    Validate a result string format.
    
    Args:
        result (str): Result string (e.g., "01200")
        nbl (int): Expected word length
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if len(result) != nbl:
        return False
    for chiffre in result:
        if chiffre not in ['0', '1', '2']:
            return False
    return True


def erreur_mot(mot, nbl, p_l=None):
    """
    Validate a word format.
    
    Args:
        mot (str): Word to validate
        nbl (int): Expected word length
        p_l (str, optional): Required first letter
        
    Returns:
        bool: True if valid word, False otherwise
    """
    if len(mot) != nbl:
        return False
    
    if p_l is not None:
        if mot[0] != p_l:
            return False
    
    tab = []
    for i in range(26):
        tab.append(chr(97 + i))
    
    for lettre in mot:
        if lettre not in tab:
            return False
    
    return True


def addition(liste1, liste2):
    """
    Merge two lists without duplicates, preserving order of liste1.
    
    Args:
        liste1 (list): First list
        liste2 (list): Second list
        
    Returns:
        list: Combined list without duplicates
    """
    liste = liste1[:]
    
    for i in liste2:
        if i not in liste:
            liste.append(i)
    
    return liste
