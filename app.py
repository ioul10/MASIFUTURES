# ============================================
# MASI FUTURES - Application Streamlit
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import config
from utils.calculations import prix_future_theorique, valeur_notionnelle, jours_vers_annees, nombre_contrats_couverture, simulation_couverture
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
# PAGE 3 : PRICING
# ────────────────────────────────────────────
elif page == "🧮 Pricing":
    st.header("🧮 Calculateur de Prix Future")
    
    st.markdown("### Formule : $F_0 = S_0 \\times e^{(r-q)T}$")
    
    # Récupérer le spot depuis le scraping (ou manuel)
    spot_defaut = 12000.0
    
    if indices_data and 'MASI' in indices_data:
        spot_defaut = indices_data['MASI']['niveau']
    
    # Inputs
    col1, col2 = st.columns(2)
    
    with col1:
        spot = st.number_input(
            "Niveau Spot (S₀) en points",
            min_value=1000.0,
            value=spot_defaut,
            step=100.0
        )
        r = st.number_input(
            "Taux sans risque (r) en % annuel",
            min_value=0.0,
            max_value=20.0,
            value=config.TAUX_SANS_RISQUE_DEF * 100,
            step=0.1
        ) / 100
        
    with col2:
        q = st.number_input(
            "Rendement dividendes (q) en % annuel",
            min_value=0.0,
            max_value=10.0,
            value=config.DIVIDENDE_YIELD_DEF * 100,
            step=0.1
        ) / 100
        jours = st.number_input(
            "Jours jusqu'à l'échéance",
            min_value=1,
            max_value=365,
            value=90,
            step=1
        )
    
    # Calculs
    T = jours_vers_annees(jours)
    F0 = prix_future_theorique(spot, r, q, T)
    valeur_not = valeur_notionnelle(F0)
    ecart = F0 - spot
    ecart_pct = (ecart / spot) * 100
    
    # Résultats
    st.divider()
    st.subheader("📊 Résultats")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Prix Future Théorique (F₀)", f"{F0:,.2f} pts")
    col2.metric("Valeur Notionnelle", f"{valeur_not:,.0f} MAD")
    col3.metric("Écart vs Spot", f"{ecart_pct:+.2f}%")
    
    # Interprétation
    st.info(f"""
    **Interprétation :**
    - Coût de portage : `(r - q) × T = {(r-q)*100:.2f}% × {T:.3f} = {(r-q)*T*100:.2f}%`
    - Le future est **{"au-dessus" if ecart > 0 else "en-dessous"}** du spot de **{abs(ecart):.2f} points**
    - À l'échéance (T=0), F₀ convergera vers S₀ = {spot:,.0f} pts
    """)
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



