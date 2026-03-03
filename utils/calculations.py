import numpy as np

def prix_future_theorique(spot, r, q, T):
    """
    Calcule le prix théorique d'un future sur indice
    Formule: F₀ = S₀ × e^((r−q)T)  (Document §7.1)
    """
    return spot * np.exp((r - q) * T)

def valeur_notionnelle(prix_future, multiplicateur=10):
    """Valeur du contrat = Prix × Multiplicateur (§4.3)"""
    return prix_future * multiplicateur

def jours_vers_annees(jours):
    """Conversion jours → années (252 jours de trading)"""
    return jours / 252
