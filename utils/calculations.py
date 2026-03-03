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

# ────────────────────────────────────────────
# 6. GESTION DES MARGES (§5 du document)
# ────────────────────────────────────────────

def calcul_marge_initiale(valeur_notionnelle, pourcentage=10):
    """
    Calcule la marge initiale requise (§5.1)
    Typique: 10% de la valeur notionnelle
    
    Args:
        valeur_notionnelle: Valeur totale du contrat (MAD)
        pourcentage: Pourcentage de marge initiale (défaut: 10%)
    
    Returns:
        Marge initiale en MAD
    """
    return valeur_notionnelle * (pourcentage / 100)

def calcul_marge_maintenance(marge_initiale, pourcentage=75):
    """
    Calcule le seuil de marge de maintenance (§5.1)
    Typique: 75% de la marge initiale
    
    Args:
        marge_initiale: Marge initiale déposée (MAD)
        pourcentage: Pourcentage de maintenance (défaut: 75%)
    
    Returns:
        Seuil de maintenance en MAD
    """
    return marge_initiale * (pourcentage / 100)

def calcul_appel_marge(solde_actuel, marge_maintenance, marge_initiale):
    """
    Calcule le montant d'appel de marge si nécessaire (§5.1)
    
    Args:
        solde_actuel: Solde actuel du compte (MAD)
        marge_maintenance: Seuil de maintenance (MAD)
        marge_initiale: Marge initiale requise (MAD)
    
    Returns:
        Montant d'appel de marge (0 si aucun appel nécessaire)
    """
    if solde_actuel < marge_maintenance:
        return marge_initiale - solde_actuel
    return 0

def simulation_marging_to_market(
    prix_initial, 
    n_contrats, 
    multiplicateur, 
    n_jours, 
    volatilite_journaliere=0.015,
    marge_initiale_pct=10,
    marge_maintenance_pct=75,
    seed=None
):
    """
    Simule le marking-to-market sur N jours (§5.1)
    
    Args:
        prix_initial: Prix d'entrée sur le future (points)
        n_contrats: Nombre de contrats
        multiplicateur: Valeur par point (MAD)
        n_jours: Nombre de jours de simulation
        volatilite_journaliere: Volatilité quotidienne (défaut: 1.5%)
        marge_initiale_pct: Pourcentage marge initiale
        marge_maintenance_pct: Pourcentage marge maintenance
        seed: Seed pour reproductibilité
    
    Returns:
        DataFrame avec l'historique jour par jour
    """
    import numpy as np
    import pandas as pd
    
    if seed:
        np.random.seed(seed)
    
    # Calcul des marges
    valeur_notionnelle = prix_initial * n_contrats * multiplicateur
    marge_initiale = calcul_marge_initiale(valeur_notionnelle, marge_initiale_pct)
    marge_maintenance = calcul_marge_maintenance(marge_initiale, marge_maintenance_pct)
    
    # Génération des prix simulés
    prix = [prix_initial]
    for _ in range(n_jours):
        variation = np.random.normal(0, volatilite_journaliere)
        prix.append(prix[-1] * (1 + variation))
    prix = prix[1:]  # Enlever la valeur initiale dupliquée
    
    # Calcul du solde jour par jour
    solde = [marge_initiale]
    appels_marge = []
    total_depose = marge_initiale
    total_retire = 0
    
    for i in range(n_jours):
        # P&L du jour (position longue)
        pnl = n_contrats * (prix[i] - (prix[i-1] if i>0 else prix_initial)) * multiplicateur
        nouveau_solde = solde[-1] + pnl
        
        # Vérification appel de marge
        appel = 0
        if nouveau_solde < marge_maintenance:
            appel = marge_initiale - nouveau_solde
            nouveau_solde = marge_initiale  # Reconstitution
            total_depose += appel
            appels_marge.append({
                'jour': i+1,
                'montant': appel,
                'solde_avant': solde[-1],
                'prix': prix[i]
            })
        
        # Possibilité de retirer l'excédent (optionnel)
        retrait = 0
        if nouveau_solde > marge_initiale * 1.5:
            retrait = nouveau_solde - marge_initiale
            nouveau_solde = marge_initiale
            total_retire += retrait
        
        solde.append(nouveau_solde)
    
    # Création du DataFrame
    df = pd.DataFrame({
        'Jour': range(n_jours + 1),
        'Prix_MASI': [prix_initial] + prix,
        'Solde_Compte': solde,
        'Marge_Initiale': [marge_initiale] * (n_jours + 1),
        'Marge_Maintenance': [marge_maintenance] * (n_jours + 1)
    })
    
    return {
        'df': df,
        'marge_initiale': marge_initiale,
        'marge_maintenance': marge_maintenance,
        'appels_marge': appels_marge,
        'total_depose': total_depose,
        'total_retire': total_retire,
        'pnl_total': solde[-1] - marge_initiale
    }

def analyser_risque_marge(simulation_result, niveau_confiance=0.95):
    """
    Analyse le risque d'appel de marge à partir d'une simulation
    
    Args:
        simulation_result: Résultat de simulation_marging_to_market()
        niveau_confiance: Niveau de confiance pour l'analyse
    
    Returns:
        Dict avec les métriques de risque
    """
    df = simulation_result['df']
    solde_min = df['Solde_Compte'].min()
    solde_max = df['Solde_Compte'].max()
    solde_mean = df['Solde_Compte'].mean()
    
    marge_maint = simulation_result['marge_maintenance']
    marge_init = simulation_result['marge_initiale']
    
    # Probabilité d'appel de marge (estimation)
    jours_sous_maintenance = (df['Solde_Compte'] < marge_maint).sum()
    proba_appel = jours_sous_maintenance / len(df)
    
    # Distance au seuil critique
    distance_seuil = (solde_min - marge_maint) / marge_init * 100
    
    return {
        'solde_min': solde_min,
        'solde_max': solde_max,
        'solde_mean': solde_mean,
        'proba_appel': proba_appel,
        'distance_seuil': distance_seuil,
        'nombre_appels': len(simulation_result['appels_marge']),
        'risque': 'Élevé' if proba_appel > 0.3 else 'Moyen' if proba_appel > 0.1 else 'Faible'
    }
# ────────────────────────────────────────────
# 7. RISK DASHBOARD (§1.2 du document)
# ────────────────────────────────────────────

def calcul_var_parametrique(portefeuille_value, volatilite_annuelle, 
                            niveau_confiance=0.95, horizon_jours=1):
    """
    Calcule la Value at Risk (VaR) paramétrique (§1.2)
    Hypothèse: distribution normale des rendements
    
    Formule: VaR = V × z × σ × √T
    
    Args:
        portefeuille_value: Valeur du portefeuille (MAD)
        volatilite_annuelle: Volatilité annuelle en décimal (ex: 0.18 = 18%)
        niveau_confiance: Niveau de confiance (0.95 ou 0.99)
        horizon_jours: Horizon de calcul en jours
    
    Returns:
        VaR en MAD (valeur positive = perte maximale attendue)
    """
    from scipy import stats
    
    # Z-score selon le niveau de confiance
    z_score = stats.norm.ppf(niveau_confiance)
    
    # Volatilité journalière (racine carrée du temps)
    volatilite_journaliere = volatilite_annuelle / np.sqrt(252)
    
    # VaR
    var = portefeuille_value * z_score * volatilite_journaliere * np.sqrt(horizon_jours)
    
    return var

def calcul_var_historique(returns, portefeuille_value, niveau_confiance=0.95):
    """
    Calcule la Value at Risk (VaR) historique (§1.2)
    Basée sur la distribution empirique des rendements passés
    
    Args:
        returns: Série de rendements historiques (array ou list)
        portefeuille_value: Valeur actuelle du portefeuille (MAD)
        niveau_confiance: Niveau de confiance (0.95 ou 0.99)
    
    Returns:
        VaR en MAD (valeur positive = perte maximale attendue)
    """
    import numpy as np
    
    # Percentile correspondant au niveau de confiance
    percentile = (1 - niveau_confiance) * 100
    
    # VaR = percentile des pertes
    var_pct = np.percentile(returns, percentile)
    
    return abs(portefeuille_value * var_pct)

def calcul_cvar(returns, portefeuille_value, niveau_confiance=0.95):
    """
    Calcule la Conditional VaR (CVaR) / Expected Shortfall
    Perte moyenne dans la queue de distribution au-delà de la VaR
    
    Args:
        returns: Série de rendements historiques
        portefeuille_value: Valeur du portefeuille (MAD)
        niveau_confiance: Niveau de confiance
    
    Returns:
        CVaR en MAD (perte moyenne au-delà de la VaR)
    """
    import numpy as np
    
    # Seuil de la VaR
    percentile = (1 - niveau_confiance) * 100
    var_threshold = np.percentile(returns, percentile)
    
    # CVaR = moyenne des rendements en dessous du seuil VaR
    queue_rendements = returns[returns <= var_threshold]
    
    if len(queue_rendements) == 0:
        return calcul_var_historique(returns, portefeuille_value, niveau_confiance)
    
    cvar_pct = np.mean(queue_rendements)
    
    return abs(portefeuille_value * cvar_pct)

def stress_testing(portefeuille_value, beta, scenarios=None):
    """
    Effectue un stress testing sur le portefeuille (§1.2)
    
    Args:
        portefeuille_value: Valeur du portefeuille (MAD)
        beta: Bêta du portefeuille par rapport à l'indice
        scenarios: Dict de scénarios {nom: variation_pct}
    
    Returns:
        DataFrame avec les résultats par scénario
    """
    import pandas as pd
    
    # Scénarios par défaut si non fournis
    if scenarios is None:
        scenarios = {
            "Correction modérée": -10,
            "Correction sévère": -20,
            "Crise 2008": -40,
            "COVID-19 (mars 2020)": -30,
            "Stress extrême": -50
        }
    
    results = []
    
    for nom, variation_indice in scenarios.items():
        # Impact sur le portefeuille (amplifié par le bêta)
        variation_pf = beta * variation_indice
        perte = portefeuille_value * variation_pf / 100
        valeur_finale = portefeuille_value + perte
        
        results.append({
            'Scénario': nom,
            'Variation Indice (%)': variation_indice,
            'Variation Portefeuille (%)': round(variation_pf, 1),
            'Perte Estimée (MAD)': round(perte, 0),
            'Valeur Finale (MAD)': round(valeur_finale, 0),
            'Niveau de Risque': '🔴 Élevé' if variation_pf < -20 else '🟡 Moyen' if variation_pf < -10 else '🟢 Faible'
        })
    
    return pd.DataFrame(results)

def calcul_delta_equivalent(portefeuille_value, beta, niveau_indice):
    """
    Calcule le delta équivalent indice (§1.2)
    Exposition du portefeuille en termes de points d'indice
    
    Args:
        portefeuille_value: Valeur du portefeuille (MAD)
        beta: Bêta du portefeuille
        niveau_indice: Niveau actuel de l'indice (points)
    
    Returns:
        Delta équivalent en points d'indice
    """
    # Exposition théorique = (Valeur portefeuille × Bêta) / Niveau indice
    return (portefeuille_value * beta) / niveau_indice

def analyser_risque_complet(portefeuille_value, beta, volatilite_annuelle, 
                           returns_historiques=None, niveau_indice=12000):
    """
    Analyse de risque complète combinant toutes les métriques
    
    Args:
        portefeuille_value: Valeur du portefeuille (MAD)
        beta: Bêta du portefeuille
        volatilite_annuelle: Volatilité annuelle estimée
        returns_historiques: Rendements historiques (optionnel)
        niveau_indice: Niveau actuel de l'indice
    
    Returns:
        Dict avec toutes les métriques de risque
    """
    results = {}
    
    # VaR paramétrique (95% et 99%, 1 jour et 10 jours)
    results['var_95_1j'] = calcul_var_parametrique(portefeuille_value, volatilite_annuelle, 0.95, 1)
    results['var_99_1j'] = calcul_var_parametrique(portefeuille_value, volatilite_annuelle, 0.99, 1)
    results['var_95_10j'] = calcul_var_parametrique(portefeuille_value, volatilite_annuelle, 0.95, 10)
    
    # VaR historique si données disponibles
    if returns_historiques is not None and len(returns_historiques) > 0:
        results['var_hist_95'] = calcul_var_historique(returns_historiques, portefeuille_value, 0.95)
        results['cvar_95'] = calcul_cvar(returns_historiques, portefeuille_value, 0.95)
    else:
        results['var_hist_95'] = results['var_95_1j']  # Fallback
        results['cvar_95'] = results['var_99_1j'] * 1.2  # Estimation
    
    # Stress testing
    results['stress'] = stress_testing(portefeuille_value, beta)
    
    # Delta équivalent
    results['delta_equivalent'] = calcul_delta_equivalent(portefeuille_value, beta, niveau_indice)
    
    # Synthèse
    results['risque_global'] = (
        '🔴 Élevé' if results['var_95_1j'] / portefeuille_value > 0.03 
        else '🟡 Moyen' if results['var_95_1j'] / portefeuille_value > 0.015 
        else '🟢 Faible'
    )
    
    return results
