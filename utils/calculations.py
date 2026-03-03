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

def nombre_contrats_couverture(portefeuille, beta, spot, multiplicateur=10):
    """
    Calcule le nombre optimal de contrats pour couvrir un portefeuille
    Formule: N* = β × P / A  (Document §6.2)
    """
    A = spot * multiplicateur  # Valeur notionnelle d'un contrat
    return round(beta * portefeuille / A)

def simulation_couverture(portefeuille, beta, spot_initial, variation_marche_pct, 
                          n_contrats, multiplicateur=10):
    """
    Simule l'impact d'une variation de marché avec/sans couverture
    """
    # Variation du portefeuille (amplifiée par le bêta)
    variation_pf_pct = beta * variation_marche_pct
    perte_portefeuille = portefeuille * variation_pf_pct / 100
    
    # Gain sur la position future courte
    spot_final = spot_initial * (1 + variation_marche_pct/100)
    gain_future = n_contrats * (spot_initial - spot_final) * multiplicateur
    
    # Valeur finale
    valeur_finale = portefeuille + perte_portefeuille + gain_future
    
    return {
        'variation_pf_pct': variation_pf_pct,
        'perte_portefeuille': perte_portefeuille,
        'spot_final': spot_final,
        'gain_future': gain_future,
        'valeur_finale': valeur_finale,
        'efficacite': 1 - abs(valeur_finale - portefeuille)/portefeuille if portefeuille != 0 else 0
    }

