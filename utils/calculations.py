# ============================================
# CALCULS FINANCIERS - FUTURES MASI/MASI20
# Basé sur le document CDG Capital
# ============================================

import numpy as np

# ────────────────────────────────────────────
# 1. VALORISATION (§7.1 du document)
# ────────────────────────────────────────────

def prix_future_theorique(spot, r, q, T):
    """
    Calcule le prix théorique d'un future sur indice
    Formule: F₀ = S₀ × e^((r−q)T)  (Document §7.1)
    
    Args:
        spot: Niveau spot de l'indice (S₀)
        r: Taux sans risque annuel
        q: Rendement dividendes attendu annuel
        T: Maturité en années
    
    Returns:
        Prix théorique du future (F₀)
    """
    return spot * np.exp((r - q) * T)

def cout_de_portage(r, q, T):
    """
    Calcule le coût de portage (cost of carry)
    Formule: (r - q) × T  (Document §7.1)
    
    Args:
        r: Taux sans risque annuel
        q: Rendement dividendes annuel
        T: Maturité en années
    
    Returns:
        Coût de portage en décimal (ex: 0.0018 = 0.18%)
    """
    return (r - q) * T

def prime_future(future_price, spot_price):
    """
    Calcule la prime du future par rapport au spot
    Formule: (F₀ - S₀) / S₀
    
    Args:
        future_price: Prix du future
        spot_price: Niveau spot de l'indice
    
    Returns:
        Prime en décimal (ex: 0.0018 = 0.18%)
    """
    return (future_price - spot_price) / spot_price if spot_price != 0 else 0

# ────────────────────────────────────────────
# 2. ARBITRAGE (§7.2 du document)
# ────────────────────────────────────────────

def detecter_arbitrage(prix_marche, prix_theorique, seuil=0.01):
    """
    Détecte les opportunités d'arbitrage (Document §7.2)
    
    Si F_market > F_théorique → Vendre Future + Acheter Spot
    Si F_market < F_théorique → Acheter Future + Vendre Spot
    
    Args:
        prix_marche: Prix future observé sur le marché
        prix_theorique: Prix future théorique calculé
        seuil: Seuil d'arbitrage en décimal (ex: 0.01 = 1%)
    
    Returns:
        Tuple (signal, strategie)
        - signal: 'Surévalué', 'Sous-évalué', ou 'Équilibre'
        - strategie: Recommandation de trading
    """
    ecart_pct = abs(prix_marche - prix_theorique) / prix_theorique
    
    if ecart_pct > seuil:
        if prix_marche > prix_theorique:
            return 'Surévalué', 'Vendre Future + Acheter Spot'
        else:
            return 'Sous-évalué', 'Acheter Future + Vendre Spot'
    else:
        return 'Équilibre', 'Aucune opportunité'

# ────────────────────────────────────────────
# 3. CARACTÉRISTIQUES DU CONTRAT (§4.1 & §4.3)
# ────────────────────────────────────────────

def valeur_notionnelle(prix_future, multiplicateur=10):
    """
    Valeur du contrat = Prix × Multiplicateur (§4.3)
    
    Args:
        prix_future: Prix du contrat en points
        multiplicateur: Valeur monétaire par point (10 MAD pour MASI)
    
    Returns:
        Valeur notionnelle en MAD
    """
    return prix_future * multiplicateur

def gain_perte_future(prix_entree, prix_sortie, n_contrats, multiplicateur=10):
    """
    Calcule le gain/perte sur une position future (§4.2)
    Formule: (F_clôture − F_entrée) × Taille × N
    
    Args:
        prix_entree: Prix d'entrée sur le future
        prix_sortie: Prix de sortie/clôture
        n_contrats: Nombre de contrats
        multiplicateur: Valeur monétaire par point
    
    Returns:
        Gain/perte en MAD (positif = gain, négatif = perte)
    """
    return (prix_sortie - prix_entree) * multiplicateur * n_contrats

# ────────────────────────────────────────────
# 4. COUVERTURE (§6 du document)
# ────────────────────────────────────────────

def nombre_contrats_couverture(portefeuille, beta, spot, multiplicateur=10):
    """
    Calcule le nombre optimal de contrats pour couvrir un portefeuille
    Formule: N* = β × P / A  (Document §6.2)
    
    Args:
        portefeuille: Valeur du portefeuille en MAD (P)
        beta: Bêta du portefeuille par rapport à l'indice (β)
        spot: Niveau spot de l'indice
        multiplicateur: Valeur monétaire par point
    
    Returns:
        Nombre optimal de contrats (arrondi)
    """
    A = spot * multiplicateur  # Valeur notionnelle d'un contrat
    return round(beta * portefeuille / A)

def simulation_couverture(portefeuille, beta, spot_initial, variation_marche_pct, 
                          n_contrats, multiplicateur=10):
    """
    Simule l'impact d'une variation de marché avec/sans couverture
    Exemple du document §6: 16M MAD, β=1.5, 200 contrats, -10% marché
    
    Args:
        portefeuille: Valeur initiale du portefeuille (MAD)
        beta: Bêta du portefeuille
        spot_initial: Niveau initial de l'indice
        variation_marche_pct: Variation du marché en % (ex: -10)
        n_contrats: Nombre de contrats futures
        multiplicateur: Valeur monétaire par point
    
    Returns:
        Dict avec tous les résultats de la simulation
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

# ────────────────────────────────────────────
# 5. UTILITAIRES
# ────────────────────────────────────────────

def jours_vers_annees(jours):
    """
    Conversion jours → années (252 jours de trading)
    
    Args:
        jours: Nombre de jours jusqu'à l'échéance
    
    Returns:
        Durée en années
    """
    return jours / 252

def annees_vers_jours(annees):
    """Conversion années → jours (252 jours de trading)"""
    return annees * 252

def points_vers_mad(points, multiplicateur=10):
    """Conversion points d'indice → MAD"""
    return points * multiplicateur

def mad_vers_points(mad, multiplicateur=10):
    """Conversion MAD → points d'indice"""
    return mad / multiplicateur
