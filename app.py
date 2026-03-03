# ============================================
# MASI FUTURES - Application Streamlit
# Version avec Scraping Bourse de Casablanca
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import config
from utils.calculations import prix_future_theorique, valeur_notionnelle, jours_vers_annees
from utils.scraping import get_indices_data, get_historical_data

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
    .status-ok {{ color: green; font-weight: bold; }}
    .status-error {{ color: red; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

# Header
st.title(f"📈 {config.APP_NAME}")
st.caption(f"Version {config.APP_VERSION} — Données Bourse de Casablanca")

# ────────────────────────────────────────────
# TABS DE NAVIGATION
# ────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Accueil", "📊 Indices Live", "🧮 Pricing", "📈 Historique"])

# ────────────────────────────────────────────
# TAB 1 : ACCUEIL
# ────────────────────────────────────────────
with tab1:
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
        **1️⃣ Onglet "Indices Live"**
        - Voir les niveaux actuels
        - Variations journalières
        - Statut du scraping
        """)
    
    with col2:
        st.info("""
        **2️⃣ Onglet "Pricing"**
        - Calculer le prix théorique
        - Ajuster r, q, T
        - Voir la valeur notionnelle
        """)
    
    with col3:
        st.info("""
        **3️⃣ Onglet "Historique"**
        - Graphique d'évolution
        - Tendances récentes
        - Export des données
        """)

# ────────────────────────────────────────────
# TAB 2 : INDICES LIVE (SCRAPPING)
# ────────────────────────────────────────────
with tab2:
    st.header("📊 Indices MASI & MASI20 - Temps Réel")
    
    # Bouton pour forcer la mise à jour
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("🔄 Données mises à jour automatiquement toutes les 5 minutes")
    with col2:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    
    # Récupération des données
    with st.spinner("Chargement des données..."):
        indices_data = get_indices_data()
    
    # Affichage du statut
    if indices_data:
        st.success("✅ Connexion Bourse de Casablanca : OK")
    else:
        st.error("❌ Connexion échouée - Mode dégradé activé")
    
    st.divider()
    
    # Affichage des indices
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🇲🇦 MASI")
        if indices_data and 'MASI' in indices_data:
            masi = indices_data['MASI']
            st.metric(
                label="Niveau",
                value=f"{masi['niveau']:,.2f} pts",
                delta=masi['variation']
            )
            st.caption(f"Dernière MAJ: {masi['timestamp']}")
        else:
            st.warning("Données non disponibles")
    
    with col2:
        st.subheader("🇲🇦 MASI20")
        if indices_data and 'MASI20' in indices_data:
            masi20 = indices_data['MASI20']
            st.metric(
                label="Niveau",
                value=f"{masi20['niveau']:,.2f} pts",
                delta=masi20['variation']
            )
            st.caption(f"Dernière MAJ: {masi20['timestamp']}")
        else:
            st.warning("Données non disponibles")
    
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
# TAB 3 : PRICING
# ────────────────────────────────────────────
with tab3:
    st.header("🧮 Calculateur de Prix Future")
    
    st.markdown("### Formule : $F_0 = S_0 \\times e^{(r-q)T}$")
    
    # Récupérer le spot depuis le scraping (ou manuel)
    indices_data = get_indices_data()
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
# TAB 4 : HISTORIQUE
# ────────────────────────────────────────────
with tab4:
    st.header("📈 Historique des Indices")
    
    indice_choisi = st.selectbox("Sélectionnez un indice", ["MASI", "MASI20"])
    jours = st.slider("Nombre de jours", 10, 90, 30)
    
    # Récupération des données historiques
    hist_data = get_historical_data(indice_choisi, jours)
    
    # Graphique
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hist_data['Date'],
        y=hist_data[f'{indice_choisi}_Close'],
        name=f'{indice_choisi}',
        line=dict(color=config.PRIMARY, width=2)
    ))
    
    fig.update_layout(
        title=f'Évolution de l\'indice {indice_choisi} sur {jours} jours',
        xaxis_title='Date',
        yaxis_title='Niveau (points)',
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques
    st.subheader("📊 Statistiques")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dernier cours", f"{hist_data[f'{indice_choisi}_Close'].iloc[-1]:,.2f}")
    col2.metric("Plus haut", f"{hist_data[f'{indice_choisi}_Close'].max():,.2f}")
    col3.metric("Plus bas", f"{hist_data[f'{indice_choisi}_Close'].min():,.2f}")
    col4.metric("Variation totale", f"{((hist_data[f'{indice_choisi}_Close'].iloc[-1] / hist_data[f'{indice_choisi}_Close'].iloc[0]) - 1) * 100:+.2f}%")

# ────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────
st.divider()
st.caption(f"{config.APP_NAME} v{config.APP_VERSION} | Basé sur le document CDG Capital | Scraping Bourse de Casablanca")
