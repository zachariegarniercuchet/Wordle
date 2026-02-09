"""
Heuristic optimization functions for faster word candidate selection.
These functions reduce search space for longer words (especially 9-letter words).
"""

try:
    from .info_theory import Mmi
    from .word_utils import li_dico_to_li_mot, li_mot_to_li_dico
except ImportError:
    from info_theory import Mmi
    from word_utils import li_dico_to_li_mot, li_mot_to_li_dico


def temps(l_mot, l_poss, nbl):
    """
    Estimate computation time based on word count and length.
    
    Args:
        l_mot (int): Number of candidate words
        l_poss (int): Number of possible answer words
        nbl (int): Word length
        
    Returns:
        float: Estimated time in seconds
    """
    calibration = {
        5: 3.185782222 * (1 - 0.626),
        6: 9.069933333 * (1 - 0.826),
        7: 37.0251 * (1 - 0.870),
        8: 125.9176 * (1 - 0.926),
        9: 493.03872 * (1 - 0.973)
    }
    
    a = calibration.get(nbl, 1.0)
    temps = a * 10**(-4) * l_mot * l_poss
    return temps


def frequence1(liste):
    """
    Calculate letter frequency across all words in the list.
    
    Args:
        liste (list): List of words
        
    Returns:
        list: Frequency of each letter (a-z) as proportions
    """
    t_freq = [0] * 26
    tot = 0
    
    for mot in liste:
        for lettre in mot:
            code = ord(lettre)
            t_freq[code - 97] += 1
            tot += 1
    
    for i in range(26):
        t_freq[i] = t_freq[i] / tot
    
    return t_freq


def bon_mot1(liste, t_freq):
    """
    Select words with highest frequency letters (heuristic #1).
    
    Args:
        liste (list): List of words
        t_freq (list): Letter frequency distribution
        
    Returns:
        list: Words containing most frequent letters
    """
    nbl = len(liste[0])
    best = []
    dico = {}
    
    for i in range(25):
        dico[chr(97 + i)] = t_freq[i]
    
    j = 0
    while len(best) < nbl + 2:  # Get top frequent letters
        maxi = t_freq[0]
        n = 0
        for i in range(25 - j):
            if t_freq[i] > maxi:
                maxi = t_freq[i]
                n = i
        
        for mot, esp in dico.items():
            if esp == maxi:
                best.append(mot)
        
        t_freq.pop(n)
        j += 1
    
    tab = []
    
    for mot in liste:
        used = []
        compt = 0
        for lettre in mot:
            if lettre in best and (lettre not in used):
                compt += 1
                used.append(lettre)
        
        if compt >= nbl:
            tab.append(mot)
    
    return tab


def frequence2(liste_poss_dico):
    """
    Calculate position-weighted letter frequency (heuristic #2).
    
    Args:
        liste_poss_dico (list): List of word dictionaries
        
    Returns:
        dict: Letter frequencies by position count
    """
    l_p_d = len(liste_poss_dico)
    dictionnaire = {}
    
    for i in range(26):
        clé = chr(97 + i)
        dictionnaire[clé] = [0] * 4
    
    for mot in liste_poss_dico:
        for lettre, position in mot.items():
            compt = len(position)
            while compt > 4:
                compt += -1
            for j in range(compt):
                dictionnaire[lettre][j] += 1
    
    for lettre, nombre in dictionnaire.items():
        for j in range(4):
            dictionnaire[lettre][j] = dictionnaire[lettre][j] * 100 / l_p_d
    
    return dictionnaire


def bon_mot2(liste_dico, tab_bon_mot_1, dict_frequence, nb):
    """
    Select best words using position-weighted frequency scoring.
    
    Args:
        liste_dico (list): List of word dictionaries
        tab_bon_mot_1 (list): Words already selected by bon_mot1
        dict_frequence (dict): Position-weighted frequency data
        nb (int): Number of words to return
        
    Returns:
        list: Top scoring words
    """
    dico = {}
    liste_mot = li_dico_to_li_mot(liste_dico)
    l_m = len(liste_mot)
    
    for i in range(l_m):
        c = True
        mot = liste_mot[i]
        if mot in tab_bon_mot_1:
            c = False
        if c:
            m_o_t = liste_dico[i]
            valeur = 0
            for lettre, position in m_o_t.items():
                compt = len(position)
                while compt > 4:
                    compt += -1
                for j in range(compt):
                    valeur += dict_frequence[lettre][j]
            
            dico[mot] = valeur
    
    liste = []
    dico_Max = Mmi(dico, False, True, nb)
    for cle, valeur in dico_Max.items():
        liste.append(cle)
    
    return liste


def bon_mot3(liste_mot, liste_poss_mot, t):
    """
    Combined heuristic function to reduce search space while staying under time limit.
    
    This is the main optimization function that combines frequence1 and frequence2
    to select the most promising candidate words when the search space is too large.
    
    Args:
        liste_mot (list): Full list of candidate words
        liste_poss_mot (list): List of possible answer words
        t (float): Maximum acceptable time in seconds
        
    Returns:
        list: Reduced list of candidate words
    """
    nb = len(liste_mot)
    l_poss_mot = len(liste_poss_mot)
    nbl = len(liste_mot[0])
    te = temps(nb, l_poss_mot, nbl)
    
    freq1 = frequence1(liste_poss_mot)
    tab1 = bon_mot1(liste_mot, freq1)
    l1 = len(tab1)
    
    c = False
    while te > t:
        nb += -1
        te = temps(nb + l1, l_poss_mot, nbl)
        c = True
    
    if c:
        print("nouveau temps estimé: ", te)
    
    liste_dico = li_mot_to_li_dico(liste_mot)
    liste_poss_dico = li_mot_to_li_dico(liste_poss_mot)
    
    freq2 = frequence2(liste_poss_dico)
    tab2 = bon_mot2(liste_dico, tab1, freq2, nb)
    
    try:
        from .word_utils import addition
    except ImportError:
        from word_utils import addition
    tab = addition(tab2, tab1)
    
    return tab
