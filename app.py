# ============================================
# MASI FUTURES - Application Streamlit
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import config
from utils.calculations import (
    prix_future_theorique, 
    valeur_notionnelle, 
    jours_vers_annees,
    nombre_contrats_couverture, 
    simulation_couverture,
    cout_de_portage,        # ← NOUVEAU
    prime_future,           # ← NOUVEAU
    detecter_arbitrage      # ← NOUVEAU
)
from utils.scraping import get_indices_data, get_historical_data, get_cache_info  

# Configuration de la page
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide"
)

# Style CSS
st.markdown(f"""
    <style>
    .main {{ background-color: {config.BACKGROUND}; }}
    h1, h2, h3 {{ color: {config.PRIMARY}; }}
    .metric-card {{ 
        background: white; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }}
    .sidebar-metric {{
        background: {config.PRIMARY};
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }}
    .sidebar-metric label {{
        color: #E0E0E0;
        font-size: 0.9em;
    }}
    .sidebar-metric value {{
        color: white;
        font-size: 1.3em;
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────
# SIDEBAR - NIVEAUX DES INDICES
# ────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 📊 {config.APP_NAME}")
    
    st.divider()
    
    # Récupération des données indices
    indices_data = get_indices_data()
    
    # Affichage MASI
    st.markdown("##### 🇲🇦 MASI")
    if indices_data and 'MASI' in indices_data:
        masi = indices_data['MASI']
        st.markdown(f"""
            <div class='sidebar-metric'>
                <label>Niveau</label><br>
                <value>{masi['niveau']:,.2f} pts</value><br>
                <small style='color: {"#4CAF50" if "+" in masi["variation"] else "#F44336"}'>
                    {masi['variation']}
                </small>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Données non disponibles")
    
    # Affichage MASI20
    st.markdown("##### 🇲🇦 MASI20")
    if indices_data and 'MASI20' in indices_data:
        masi20 = indices_data['MASI20']
        st.markdown(f"""
            <div class='sidebar-metric'>
                <label>Niveau</label><br>
                <value>{masi20['niveau']:,.2f} pts</value><br>
                <small style='color: {"#4CAF50" if "+" in masi20["variation"] else "#F44336"}'>
                    {masi20['variation']}
                </small>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Données non disponibles")
    
    st.divider()
    
    # Informations cache
    cache_info = get_cache_info()
    st.caption(f"🔄 Cache: {cache_info['cache_age']} (max {cache_info['duration_minutes']} min)")
    
    # Bouton refresh manuel
    if st.button("🔄 Actualiser les données", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()
    
    st.divider()
    
    # Navigation
    st.markdown("##### 🧭 Navigation")
    
    # Menu de navigation
    page = st.radio(
        "Pages",
        ["🏠 Accueil", "📊 Indices & Historique", "🧮 Pricing", "🛡️ Couverture"],
        label_visibility="collapsed"
    )

# ────────────────────────────────────────────
# HEADER PRINCIPAL
# ────────────────────────────────────────────
st.title(f"📈 {config.APP_NAME}")
st.caption(f"Version {config.APP_VERSION} — Données Bourse de Casablanca")

# ────────────────────────────────────────────
# PAGE 1 : ACCUEIL
# ────────────────────────────────────────────
if page == "🏠 Accueil":
    st.header("🎯 Bienvenue sur MASI Futures")
    
    st.markdown(f"""
    ### Qu'est-ce que cette application ?
    
    **MASI Futures** est un outil pour comprendre et calculer le prix théorique 
    des contrats futures sur les indices marocains **MASI** et **MASI20**.
    
    > *« Améliorer l'efficacité du marché en permettant la couverture, 
    > l'optimisation de l'allocation et la découverte des prix. »*
    > 
    > — Document CDG Capital
    
    ### 📋 Fonctionnalités :
    
    - ✅ **Données en temps réel** : Niveaux MASI/MASI20 depuis la Bourse de Casablanca
    - ✅ **Pricing** : Calcul du prix théorique F₀ = S₀ × e^((r−q)T)
    - ✅ **Historique** : Visualisation de l'évolution des indices
    - ✅ **Couverture** : Calcul du nombre optimal de contrats (à venir)
    """)
    
    st.divider()
    
    st.header("📘 Guide Rapide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **1️⃣ Sidebar**
        - Voir les niveaux MASI/MASI20
        - Actualiser manuellement
        - Statut du cache
        """)
    
    with col2:
        st.info("""
        **2️⃣ Onglet "Indices"**
        - Données complètes des indices
        - Historique et graphiques
        - Caractéristiques contrats
        """)
    
    with col3:
        st.info("""
        **3️⃣ Onglet "Pricing"**
        - Calculer le prix théorique
        - Ajuster r, q, T
        - Voir la valeur notionnelle
        """)
    
    # Statut du scraping
    st.divider()
    st.subheader("🔧 Statut du Système")
    
    if indices_data:
        st.success("✅ Connexion Bourse de Casablanca : OK")
    else:
        st.warning("⚠️ Mode dégradé - Données mockées utilisées")
    
    st.caption(f"Dernière mise à jour: {indices_data['MASI']['timestamp'] if indices_data else 'N/A'}")

# ────────────────────────────────────────────
# PAGE 2 : INDICES & HISTORIQUE (Fusionné)
# ────────────────────────────────────────────
elif page == "📊 Indices & Historique":
    st.header("📊 Indices MASI & MASI20")
    
    # Sélecteur d'indice
    col1, col2 = st.columns([3, 1])
    with col1:
        indice_choisi = st.selectbox("Sélectionnez un indice", ["MASI", "MASI20"])
    with col2:
        jours = st.slider("Jours d'historique", 10, 90, 30)
    
    # Affichage des métriques principales
    st.divider()
    
    if indices_data:
        col1, col2, col3, col4 = st.columns(4)
        
        # MASI
        masi = indices_data.get('MASI', {})
        col1.metric(
            label="🇲🇦 MASI",
            value=f"{masi.get('niveau', 0):,.2f} pts",
            delta=masi.get('variation', 'N/A')
        )
        
        # MASI20
        masi20 = indices_data.get('MASI20', {})
        col2.metric(
            label="🇲🇦 MASI20",
            value=f"{masi20.get('niveau', 0):,.2f} pts",
            delta=masi20.get('variation', 'N/A')
        )
        
        # Timestamp
        col3.metric(
            label="🕐 Dernière MAJ",
            value=masi.get('timestamp', 'N/A').split(' ')[1] if masi else 'N/A',
            delta=None
        )
        
        # Statut cache
        cache_info = get_cache_info()
        col4.metric(
            label="💾 Cache",
            value=f"{cache_info['cache_age']}",
            delta=f"Max {cache_info['duration_minutes']} min"
        )
    else:
        st.warning("Données non disponibles")
    
    st.divider()
    
    # Graphique historique
    st.subheader(f"📈 Évolution de l'indice {indice_choisi}")
    
    hist_data = get_historical_data(indice_choisi, jours)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hist_data['Date'],
        y=hist_data[f'{indice_choisi}_Close'],
        name=indice_choisi,
        line=dict(color=config.PRIMARY, width=2)
    ))
    
    fig.update_layout(
        title=f'Évolution de l\'indice {indice_choisi} sur {jours} jours',
        xaxis_title='Date',
        yaxis_title='Niveau (points)',
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques
    st.subheader("📊 Statistiques")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dernier cours", f"{hist_data[f'{indice_choisi}_Close'].iloc[-1]:,.2f}")
    col2.metric("Plus haut", f"{hist_data[f'{indice_choisi}_Close'].max():,.2f}")
    col3.metric("Plus bas", f"{hist_data[f'{indice_choisi}_Close'].min():,.2f}")
    variation_totale = ((hist_data[f'{indice_choisi}_Close'].iloc[-1] / hist_data[f'{indice_choisi}_Close'].iloc[0]) - 1) * 100
    col4.metric("Variation totale", f"{variation_totale:+.2f}%")
    
    st.divider()
    
    # Caractéristiques des contrats
    st.subheader("📋 Caractéristiques des Contrats Futures")
    
    specs = pd.DataFrame({
        "Paramètre": [
            "Sous-jacent",
            "Règlement",
            "Multiplicateur",
            "Échéances",
            "Devise",
            "Tick Size"
        ],
        "Valeur": [
            "MASI / MASI20",
            "Cash settlement",
            f"{config.MULTIPLICATEUR} MAD/point",
            "Mensuelles / Trimestrielles",
            "MAD",
            "0.01 point"
        ]
    })
    st.dataframe(specs, hide_index=True, use_container_width=True)

# ────────────────────────────────────────────
# PAGE 3 : VALORISATION FUTURES (§7 du document)
# ────────────────────────────────────────────
elif page == "🧮 Pricing":
    st.markdown("## 💰 Valorisation des Contrats Futures")
    
    st.markdown("""
    ### 📐 Formule de Pricing (Absence d'Arbitrage)
    
    $$F_0 = S_0 \\times e^{(r-q)T}$$
    
    **Où :**
    - **S₀** = Niveau spot de l'indice
    - **r** = Taux sans risque annuel
    - **q** = Rendement en dividendes attendu
    - **T** = Maturité en années
    """)
    
    st.divider()
    
    # ────────────────────────────────────────
    # INPUTS
    # ────────────────────────────────────────
    st.markdown("### 🔧 Paramètres de Valorisation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Spot (auto depuis scraping)
        spot_defaut = indices_data['MASI']['niveau'] if indices_data and 'MASI' in indices_data else 12000
        spot = st.number_input(
            "📊 Niveau Spot (S₀) en points",
            min_value=1000.0,
            value=spot_defaut,
            step=50.0,
            help="Niveau actuel de l'indice MASI/MASI20"
        )
        
        r = st.number_input(
            "🏦 Taux sans risque (r) en % annuel",
            min_value=0.0,
            max_value=15.0,
            value=3.0,
            step=0.1,
            help="Taux des bons du Trésor marocain"
        ) / 100
        
    with col2:
        q = st.number_input(
            "💵 Rendement dividendes (q) en % annuel",
            min_value=0.0,
            max_value=10.0,
            value=2.5,
            step=0.1,
            help="Dividendes moyens attendus de l'indice"
        ) / 100
        
        jours = st.number_input(
            "📅 Jours jusqu'à l'échéance",
            min_value=1,
            max_value=365,
            value=90,
            step=1,
            help="Durée restante avant expiration du contrat"
        )
    
    # ────────────────────────────────────────
    # CALCULS
    # ────────────────────────────────────────
    T = jours_vers_annees(jours)
    F0 = prix_future_theorique(spot, r, q, T)
    cout_port = cout_de_portage(r, q, T)
    prime = prime_future(F0, spot)
    valeur_not = valeur_notionnelle(F0)
    
    # ────────────────────────────────────────
    # RÉSULTATS PRINCIPAUX
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📊 Résultats de la Valorisation")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Prix Future Théorique (F₀)</label>
                <value>{F0:,.2f}</value>
                <small style='color: #6B7280;'>points</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Valeur Notionnelle</label>
                <value>{valeur_not:,.0f}</value>
                <small style='color: #6B7280;'>MAD</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        couleur_prime = "#10B981" if prime >= 0 else "#EF4444"
        st.markdown(f"""
            <div class='metric-card'>
                <label>Prime vs Spot</label>
                <value style='color: {couleur_prime};'>{prime*100:+.2f}%</value>
                <small style='color: #6B7280;'>{F0-spot:+,.0f} pts</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Coût de Portage</label>
                <value>{cout_port*100:+.2f}%</value>
                <small style='color: #6B7280;'>(r-q)×T</small>
            </div>
        """, unsafe_allow_html=True)
    
    # ────────────────────────────────────────
    # DÉTECTEUR D'ARBITRAGE (§7.2)
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🎯 Détecteur d'Opportunités d'Arbitrage")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prix_marche = st.number_input(
            "Prix Future Observé sur le Marché (optionnel)",
            min_value=0.0,
            value=float(F0),
            step=10.0,
            help="Prix auquel le future se négocie réellement"
        )
    
    with col2:
        seuil = st.slider(
            "Seuil d'arbitrage (%)",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1
        ) / 100
    
    # Analyse d'arbitrage
    signal, strategie = detecter_arbitrage(prix_marche, F0, seuil)
    ecart_absolu = prix_marche - F0
    ecart_pct = (ecart_absolu / F0) * 100 if F0 != 0 else 0
    
    # Affichage du signal
    if signal == 'Surévalué':
        st.markdown(f"""
            <div class='warning-box'>
                <strong>⚠️ Signal : {signal}</strong><br>
                Le future est <strong>{abs(ecart_pct):.2f}%</strong> au-dessus de sa valeur théorique.<br>
                <strong>Stratégie recommandée :</strong> {strategie}
            </div>
        """, unsafe_allow_html=True)
    elif signal == 'Sous-évalué':
        st.markdown(f"""
            <div class='success-box'>
                <strong>✅ Signal : {signal}</strong><br>
                Le future est <strong>{abs(ecart_pct):.2f}%</strong> en-dessous de sa valeur théorique.<br>
                <strong>Stratégie recommandée :</strong> {strategie}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='info-box'>
                <strong>ℹ️ Signal : {signal}</strong><br>
                L'écart ({ecart_pct:+.2f}%) est dans la zone normale (< {seuil*100:.1f}%).<br>
                <strong>Recommandation :</strong> {strategie}
            </div>
        """, unsafe_allow_html=True)
    
    # ────────────────────────────────────────
    # EXEMPLE DU DOCUMENT (§6 & §7)
    # ────────────────────────────────────────
    with st.expander("📖 Voir l'Exemple du Document CDG Capital"):
        st.markdown("""
        **Paramètres de l'exemple (§6) :**
        - Spot S₀ = 12 000 points
        - Taux sans risque r = 3%
        - Dividendes q = 2.5%
        - Maturité T = 90 jours (0.357 années)
        
        **Calcul :**
        ```
        F₀ = 12 000 × e^((0.03 - 0.025) × 0.357)
           = 12 000 × e^(0.001785)
           = 12 000 × 1.00179
           ≈ 12 021 points
        ```
        
        **Valeur notionnelle :** 12 021 × 10 = **120 210 MAD**
        
        **Prime :** (12 021 - 12 000) / 12 000 = **+0.18%**
        
        **Coût de portage :** (3% - 2.5%) × 0.357 = **0.18%**
        """)
    
    # ────────────────────────────────────────
    # INTERPRÉTATION
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💡 Interprétation des Résultats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **📊 Analyse du Prix Future :**
        - Le future cote à **{F0:,.2f} points**
        - Soit une **prime de {prime*100:+.2f}%** par rapport au spot
        - Valeur notionnelle : **{valeur_not:,.0f} MAD** par contrat
        """)
    
    with col2:
        st.markdown(f"""
        **📈 Coût de Portage :**
        - Taux sans risque : **{r*100:.1f}%**
        - Rendement dividendes : **{q*100:.1f}%**
        - Coût net : **{(r-q)*100:.2f}%** annuel
        - Sur {jours} jours : **{cout_port*100:.2f}%**
        """)
    
    # Info box pédagogique
    st.markdown("""
        <div class='info-box'>
            <strong>💡 Le saviez-vous ?</strong><br>
            La convergence des prix futures vers le spot à l'échéance (T→0) est garantie par l'arbitrage. 
            Si F₀ ≠ S₀ à l'échéance, un arbitragiste pourrait réaliser un profit sans risque, 
            ce qui ramènerait les prix à l'équilibre (Document §4.5 & §7.2).
        </div>
    """, unsafe_allow_html=True)
  
# ────────────────────────────────────────────
# PAGE 4 : COUVERTURE (HEDGING) - §6 du document
# ────────────────────────────────────────────
elif page == "🛡️ Couverture":
    st.header("🛡️ Simulateur de Couverture par Futures")
    
    st.markdown("""
    ### Formule : $N^* = \\beta \\times \\frac{P}{A}$
    
    Où :
    - **P** = Valeur du portefeuille (MAD)
    - **A** = Valeur notionnelle d'un contrat = Spot × Multiplicateur
    - **β** = Bêta du portefeuille (sensibilité au MASI)
    """)
    
    # Inputs
    col1, col2 = st.columns(2)
    
    with col1:
        portefeuille = st.number_input(
            "Valeur du portefeuille (MAD)",
            min_value=100_000,
            value=16_000_000,
            step=100_000
        )
        beta = st.slider(
            "Bêta du portefeuille (β)",
            min_value=0.0,
            max_value=3.0,
            value=1.5,
            step=0.1,
            help="1.0 = suit le marché, >1 = plus volatil, <1 = moins volatil"
        )
        
    with col2:
        # Spot auto depuis scraping ou manuel
        spot_defaut = indices_data['MASI']['niveau'] if indices_data and 'MASI' in indices_data else 12000
        spot = st.number_input(
            "Niveau MASI (points)",
            min_value=1000.0,
            value=spot_defaut,
            step=100.0
        )
        variation = st.slider(
            "Variation marché simulée (%)",
            min_value=-30,
            max_value=30,
            value=-10,
            step=1
        )
    
    # Calculs
    N_contrats = nombre_contrats_couverture(portefeuille, beta, spot, config.MULTIPLICATEUR)
    valeur_contrat = spot * config.MULTIPLICATEUR
    result = simulation_couverture(portefeuille, beta, spot, variation, N_contrats, config.MULTIPLICATEUR)
    
    # Affichage résultats
    st.divider()
    st.subheader("📊 Résultats")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de contrats (N*)", f"{N_contrats:,}")
    col2.metric("Valeur/contrat", f"{valeur_contrat:,.0f} MAD")
    col3.metric("Efficacité", f"{result['efficacite']*100:.1f}%")
    
    st.divider()
    
    # Détails financiers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **📉 Impact sur le portefeuille :**
        - Variation du portefeuille : `{result['variation_pf_pct']:+.1f}%`
        - Perte/gain actions : `{result['perte_portefeuille']:,.0f} MAD`
        - Valeur finale (non couvert) : `{portefeuille + result['perte_portefeuille']:,.0f} MAD`
        """)
    
    with col2:
        st.markdown(f"""
        **📈 Impact sur la position futures :**
        - Position : **Courte** sur {N_contrats:,} contrats
        - Gain/perte futures : `{result['gain_future']:+,.0f} MAD`
        - Valeur finale (couvert) : `{result['valeur_finale']:,.0f} MAD`
        """)
    
    # Graphique : Portefeuille seul vs Couvert
    st.divider()
    st.subheader("📈 Visualisation de l'Effet de Couverture")
    
    variations = np.linspace(-30, 30, 100)
    
    # Sans couverture
    valeurs_brutes = [portefeuille * (1 + beta * v/100) for v in variations]
    
    # Avec couverture
    valeurs_couvertes = []
    for v in variations:
        spot_f = spot * (1 + v/100)
        perte = portefeuille * beta * v/100
        gain = N_contrats * (spot - spot_f) * config.MULTIPLICATEUR
        valeurs_couvertes.append(portefeuille + perte + gain)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=variations, y=valeurs_brutes,
        name='Sans couverture',
        line=dict(color='red', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=variations, y=valeurs_couvertes,
        name='Avec couverture',
        line=dict(color='green', width=2, dash='dash')
    ))
    
    fig.add_hline(y=portefeuille, line_dash='dot', line_color='blue', 
                  annotation_text='Valeur initiale', annotation_position='top right')
    
    fig.update_layout(
        title=f'Impact d\'une variation du MASI sur un portefeuille de {portefeuille:,.0f} MAD (β={beta})',
        xaxis_title='Variation du MASI (%)',
        yaxis_title='Valeur du portefeuille (MAD)',
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Exemple du document
    with st.expander("📖 Voir l'exemple du document CDG Capital (§6)"):
        st.markdown("""
        **Paramètres de l'exemple :**
        - Portefeuille : 16 000 000 MAD
        - Bêta : 1,5
        - MASI : 12 000 points
        - Multiplicateur : 10 MAD/pt
        - Variation marché : -10%
        
        **Calcul :**
        ```
        A = 12 000 × 10 = 120 000 MAD
        N* = 1,5 × 16 000 000 / 120 000 = 200 contrats
        
        Perte portefeuille : 16M × 1,5 × (-10%) = -2 400 000 MAD
        Gain futures : 200 × 1 200 × 10 = +2 400 000 MAD
        Valeur finale : 16 000 000 MAD ✅
        ```
        """)
# ────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────
st.divider()
st.caption(f"{config.APP_NAME} v{config.APP_VERSION} | Basé sur le document CDG Capital | Scraping optimisé avec cache")





