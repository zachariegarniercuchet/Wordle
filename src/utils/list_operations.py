"""
List filtering operations for narrowing down possible words based on feedback.
"""

def remove_0(liste, lettre, position):
    """
    Remove words containing a specific letter (gray feedback).
    
    Args:
        liste (list): List of words
        lettre (str): Letter to exclude
        position (int): Position of the letter in the guess
        
    Returns:
        list: Filtered list of words
    """
    listefinale = []
    for i in liste:
        c = True
        for j in i:
            if j == lettre:
                c = False
        if c:
            listefinale.append(i)
    return listefinale


def remove_1(liste, lettre, position):
    """
    Keep words with letter present but not at the specified position (yellow feedback).
    
    Args:
        liste (list): List of words
        lettre (str): Letter that exists but is misplaced
        position (int): Position where letter should NOT be
        
    Returns:
        list: Filtered list of words
    """
    listefinale = []
    for i in liste:
        c = False
        for j in i:
            if j == lettre and i[position] != lettre:
                c = True
        if c:
            listefinale.append(i)
    return listefinale


def remove_2(liste, lettre, position):
    """
    Keep words with letter at the exact position (green feedback).
    
    Args:
        liste (list): List of words
        lettre (str): Letter that is correctly placed
        position (int): Position where letter must be
        
    Returns:
        list: Filtered list of words
    """
    listefinale = []
    for i in liste:
        c = False
        j = i[position]
        if j == lettre:
            c = True
        if c:
            listefinale.append(i)
    return listefinale


def new_liste1(liste, mot, result):
    """
    Filter word list based on guess result (for words without duplicate letters).
    
    Args:
        liste (list): Current list of possible words
        mot (str): Guessed word
        result (str): Result string (e.g., "01200")
        
    Returns:
        list: Filtered list of possible words
    """
    pos = 0
    for i in result:
        if i == "0":
            liste = remove_0(liste, mot[pos], pos)
        if i == "1":
            liste = remove_1(liste, mot[pos], pos)
        elif i == "2":
            liste = remove_2(liste, mot[pos], pos)
        pos += 1
    
    return liste


def new_liste2(liste, mot, result):
    """
    Filter word list based on guess result (for words with duplicate letters).
    Handles complex cases where duplicate letters have different feedback.
    
    Args:
        liste (list): Current list of possible words (as dictionaries)
        mot (dict): Guessed word as dictionary
        result (str): Result string (e.g., "01200")
        
    Returns:
        list: Filtered list of possible words (as dictionaries)
    """
    li_possible = liste
    
    for lettre_test, t_pos in mot.items():
        t_result = []
        longueur = len(t_pos)
        
        for i in range(longueur):
            t_result.append(int(result[t_pos[i]]))
        
        liste1 = []
        
        compteur = 0
        t_pos_0 = []  # Positions with gray feedback
        t_pos_1 = []  # Positions with yellow feedback
        t_pos_2 = []  # Positions with green feedback
        
        for i in range(longueur):
            if t_result[i] == 2:
                t_pos_2.append(t_pos[i])
                compteur += 1
            elif t_result[i] == 1:
                compteur += 1
                t_pos_1.append(t_pos[i])
            else:
                t_pos_0.append(t_pos[i])
        
        for mot in li_possible:  # mot is a dictionary
            l = False  # Is letter in the word?
            c = True  # Should we keep this word?
            d = True
            
            for lettre_mot, position in mot.items():
                if lettre_mot == lettre_test:
                    l = True
                    posi = position
            
            if not l and compteur > 0:
                c = False
            elif l and compteur == 0:  # If counter = 0 and letter exists
                c = False  # Don't keep the word
            
            if l and c:
                for i in posi:
                    if i in t_pos_1 or i in t_pos_0:
                        d = False
                        c = False
                    
                    if d:
                        if compteur < longueur:
                            if compteur != len(posi):
                                c = False
                        else:
                            if compteur > len(posi):
                                c = False
            
            if c:
                liste1.append(mot)
        
        liste2 = []
        
        for mot in liste1:  # mot is a dictionary
            c = True
            for lettre_mot, position in mot.items():
                for posi in position:
                    if posi in t_pos_2:
                        if lettre_mot != lettre_test:
                            c = False
            if c:
                liste2.append(mot)
        
        li_possible = liste2
    
    return liste2
