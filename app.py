# ============================================
# MASI FUTURES - Application Streamlit Simple
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import config
from utils.calculations import prix_future_theorique, valeur_notionnelle, jours_vers_annees

# Configuration de la page
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide"
)

# Style CSS minimal
st.markdown(f"""
    <style>
    .main {{ background-color: {config.BACKGROUND}; }}
    h1, h2, h3 {{ color: {config.PRIMARY}; }}
    .metric {{ background: white; padding: 15px; border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

# Header
st.title(f"📈 {config.APP_NAME}")
st.caption(f"Version {config.APP_VERSION} — Pricing de Futures sur Indices MASI/MASI20")

# ────────────────────────────────────────────
# TABS DE NAVIGATION
# ────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🏠 Accueil", "📊 MASI/MASI20", "🧮 Pricing"])

# ────────────────────────────────────────────
# TAB 1 : ACCUEIL + GUIDE
# ────────────────────────────────────────────
with tab1:
    st.header("🎯 Bienvenue sur MASI Futures")
    
    st.markdown(f"""
    ### Qu'est-ce que cette application ?
    
    **MASI Futures** est un outil simple pour comprendre et calculer le prix 
    théorique des contrats futures sur les indices marocains **MASI** et **MASI20**.
    
    > *« Améliorer l'efficacité du marché en permettant la couverture, 
    > l'optimisation de l'allocation et la découverte des prix. »*
    > 
    > — Document CDG Capital
    
    ### 📋 Ce que vous pouvez faire :
    
    - ✅ Comprendre les caractéristiques des futures MASI/MASI20
    - ✅ Consulter les niveaux actuels des indices (données mockées)
    - ✅ Calculer le prix théorique d'un future avec la formule :  
       **F₀ = S₀ × e^((r−q)T)**
    """)
    
    st.divider()
    
    st.header("📘 Guide d'Utilisation Rapide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **1️⃣ Onglet "MASI/MASI20"**
        - Voir le niveau spot des indices
        - Consulter les caractéristiques des contrats
        - *(News : version mockée pour cette démo)*
        """)
    
    with col2:
        st.markdown("""
        **2️⃣ Onglet "Pricing"**
        - Entrer les paramètres : Spot, r, q, T
        - Obtenir le prix théorique du future
        - Voir la valeur notionnelle du contrat
        """)
    
    with col3:
        st.markdown("""
        **3️⃣ Comprendre les résultats**
        - Comparer prix théorique vs marché
        - Identifier des opportunités d'arbitrage
        - Exporter vos calculs (à venir)
        """)
    
    st.info("💡 **Astuce** : Commencez par l'onglet **Pricing** pour tester la formule avec l'exemple du document (§7.1).")

# ────────────────────────────────────────────
# TAB 2 : MASI / MASI20 INFOS
# ────────────────────────────────────────────
with tab2:
    st.header("📊 Indices MASI & MASI20")
    
    # Sélecteur d'indice
    indice_choisi = st.selectbox("Sélectionnez un indice", config.INDICES)
    
    # Données mockées (à remplacer par scraping plus tard)
    if indice_choisi == "MASI":
        niveau = 12345.67
        variation = "+0.45%"
        haut = 12400.50
        bas = 12280.30
        ouverture = 12300.00
    else:
        niveau = 1876.54
        variation = "+0.32%"
        haut = 1885.20
        bas = 1865.10
        ouverture = 1870.00
    
    # Affichage des métriques
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Niveau", f"{niveau:,.2f} pts")
    col2.metric("Variation", variation)
    col3.metric("Plus Haut", f"{haut:,.2f}")
    col4.metric("Plus Bas", f"{bas:,.2f}")
    
    st.divider()
    
    # Caractéristiques du contrat
    st.subheader("📋 Caractéristiques du Contrat Future")
    
    specs = pd.DataFrame({
        "Paramètre": [
            "Sous-jacent",
            "Règlement",
            "Multiplicateur",
            "Échéances",
            "Devise"
        ],
        "Valeur": [
            f"Indice {indice_choisi}",
            "Cash settlement (en espèces)",
            f"{config.MULTIPLICATEUR} MAD/point",
            "Mensuelles / Trimestrielles",
            config.MULTIPLICATEUR
        ]
    })
    st.dataframe(specs, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # News section (mockée)
    st.subheader("📰 Actualités du Marché")
    
    news_mock = [
        {
            "titre": f"Le {indice_choisi} termine en hausse de 0,45%",
            "source": "Bourse de Casablanca",
            "date": "03/03/2026",
            "resume": "Le marché marocain affiche une progression portée par les valeurs bancaires..."
        },
        {
            "titre": "Introduction des futures sur indices : une étape clé",
            "source": "CDG Capital",
            "date": "01/03/2026",
            "resume": "Lancement officiel des contrats futures MASI/MASI20 pour moderniser le marché..."
        },
        {
            "titre": "Analyse : Impact des dividendes sur le pricing des futures",
            "source": "Ilboursa",
            "date": "28/02/2026",
            "resume": "Les distributions de dividendes influencent directement le coût de portage..."
        }
    ]
    
    for n in news_mock:
        with st.expander(f"📌 {n['titre']} — {n['source']} ({n['date']})"):
            st.markdown(f"*{n['resume']}*")
    
    st.caption("ℹ️ News en version mockée. Scraping Bourse de Casablanca/Investing.com prévu en V2.")

# ────────────────────────────────────────────
# TAB 3 : PRICING CALCULATOR
# ────────────────────────────────────────────
with tab3:
    st.header("🧮 Calculateur de Prix Future")
    
    st.markdown("### Formule : $F_0 = S_0 \\times e^{(r-q)T}$")
    
    # Inputs
    col1, col2 = st.columns(2)
    
    with col1:
        spot = st.number_input(
            "Niveau Spot (S₀) en points",
            min_value=1000.0,
            value=12000.0,
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
    
    # Affichage des résultats
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
    
    # Exemple du document
    with st.expander("📖 Voir l'exemple du document CDG Capital (§6)"):
        st.markdown("""
        **Paramètres de l'exemple :**
        - Spot S₀ = 12 000 pts
        - r = 3%, q = 2.5%, T = 0.25 ans (3 mois)
        
        **Calcul :**
        ```
        F₀ = 12 000 × e^((0.03 - 0.025) × 0.25)
           = 12 000 × e^(0.00125)
           = 12 000 × 1.00125
           ≈ 12 015 pts
        ```
        
        **Valeur notionnelle :** 12 015 × 10 = **120 150 MAD**
        """)

# ────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────
st.divider()
st.caption(f"{config.APP_NAME} v{config.APP_VERSION} | Basé sur le document CDG Capital | Données mockées — Scraping en V2")