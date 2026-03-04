# ============================================
# MASI FUTURES - Application Streamlit
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import config
from utils.calculations import (prix_future_theorique, valeur_notionnelle, jours_vers_annees,nombre_contrats_couverture, simulation_couverture,cout_de_portage,prime_future,detecter_arbitrage,calcul_marge_initiale,calcul_marge_maintenance,calcul_appel_marge,simulation_marging_to_market, analyser_risque_marge, calcul_var_parametrique, calcul_var_historique, calcul_cvar, stress_testing, calcul_delta_equivalent, analyser_risque_complet,    calcul_limit_up_down, verifier_limit_up_down,  calcul_position_limit, verifier_conformity_position, calcul_marge_requise_position, analyse_risque_position, rapport_conformite_complet )
from utils.scraping import get_indices_data, get_historical_data, get_cache_info 
from utils.news_scraper import get_all_news, get_latest_market_update

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
  
    # Menu de navigation (mettre à jour)
    # Menu de navigation (mettre à jour - 7 pages maintenant)
    page = st.radio(
    "Pages",
          ["🏠 Accueil", "📊 Indices & Historique", "🧮 Pricing", "🛡️ Couverture", "⚠️ Marges", "📈 Risk Dashboard", "📏 Limites"],  # ← Ajouté
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
# ────────────────────────────────────────
# ACTUALITÉS DU MARCHÉ
# ────────────────────────────────────────
st.divider()
st.markdown("### 📰 Actualités du Marché Marocain")

# Bouton refresh
col1, col2 = st.columns([4, 1])
with col1:
    st.caption("Actualités depuis Ilboursa et Bourse de Casablanca")
with col2:
    if st.button("🔄 Actualiser", key="refresh_news"):
        st.cache_resource.clear()
        st.rerun()

# Récupération des news
with st.spinner("Chargement des actualités..."):
    df_news = get_all_news(force_refresh=False, max_total=10)

if not df_news.empty:
    # Affichage des news
    for idx, row in df_news.iterrows():
        with st.expander(f"📌 {row['titre']} — {row['source']} ({row['date']})"):
            if row['resume']:
                st.markdown(f"*{row['resume']}*")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"Catégorie: {row['categorie']}")
            with col2:
                st.markdown(f"[🔗 Voir plus]({row['url']})")
            
            st.divider()
else:
    st.info("ℹ️ Aucune actualité disponible pour le moment. Réessayez plus tard.")

# Info box
st.markdown("""
    <div class='info-box'>
        <strong>💡 Sources d'actualités :</strong><br>
        • Ilboursa.com - Actualités boursières marocaines<br>
        • Casablanca-bourse.com - Communiqués officiels<br>
        Les actualités sont mises à jour automatiquement toutes les 30 minutes.
    </div>
""", unsafe_allow_html=True)

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
# PAGE 5 : GESTION DES MARGES (§5 du document)
# ────────────────────────────────────────────
elif page == "⚠️ Marges":
    st.markdown("## ⚠️ Gestion des Marges et Appels de Marge")
    
    st.markdown("""
    ### 📋 Mécanisme des Appels de Marge (Document §5.1)
    
    ```
    Marge Initiale (10%) → Position ouverte
             ↓
    Chaque jour : Ajustement gains/pertes (marking-to-market)
             ↓
    Si Solde < Marge Maintenance (75%) → APPEL DE MARGE
             ↓
    Si non honoré → Clôture automatique de la position
    ```
    
    **Objectif :** Réduire le risque de contrepartie en réglant les pertes progressivement.
    """)
    
    st.divider()
    
    # ────────────────────────────────────────
    # INPUTS
    # ────────────────────────────────────────
    st.markdown("### 🔧 Paramètres de la Position")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        prix_entree = st.number_input(
            "Prix d'entrée (points)",
            min_value=1000.0,
            value=12000.0,
            step=100.0
        )
        n_contrats = st.number_input(
            "Nombre de contrats",
            min_value=1,
            max_value=1000,
            value=10,
            step=1
        )
        
    with col2:
        multiplicateur = st.number_input(
            "Multiplicateur (MAD/point)",
            min_value=1,
            value=config.MULTIPLICATEUR,
            step=1
        )
        volatilite = st.slider(
            "Volatilité journalière (%)",
            min_value=0.5,
            max_value=5.0,
            value=1.5,
            step=0.1
        ) / 100
        
    with col3:
        n_jours = st.slider(
            "Nombre de jours",
            min_value=5,
            max_value=60,
            value=20,
            step=1
        )
        marge_init_pct = st.slider(
            "Marge initiale (%)",
            min_value=5,
            max_value=20,
            value=10,
            step=1
        )
    
    # ────────────────────────────────────────
    # CALCULS
    # ────────────────────────────────────────
    valeur_notionnelle = prix_entree * n_contrats * multiplicateur
    marge_initiale = calcul_marge_initiale(valeur_notionnelle, marge_init_pct)
    marge_maintenance = calcul_marge_maintenance(marge_initiale, 75)
    
    # Simulation
    with st.spinner("Simulation en cours..."):
        simulation = simulation_marging_to_market(
            prix_initial=prix_entree,
            n_contrats=n_contrats,
            multiplicateur=multiplicateur,
            n_jours=n_jours,
            volatilite_journaliere=volatilite,
            marge_initiale_pct=marge_init_pct,
            seed=42  # Pour reproductibilité
        )
    
    # Analyse de risque
    risque = analyser_risque_marge(simulation)
    
    # ────────────────────────────────────────
    # RÉSUMÉ EXÉCUTIF
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📊 Résumé de la Position")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Valeur Notionnelle</label>
                <value>{valeur_notionnelle:,.0f}</value>
                <small style='color: #6B7280;'>MAD</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Marge Initiale</label>
                <value>{marge_initiale:,.0f}</value>
                <small style='color: #6B7280;'>{marge_init_pct}%</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Marge Maintenance</label>
                <value>{marge_maintenance:,.0f}</value>
                <small style='color: #6B7280;'>75% initiale</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        couleur_risque = "#10B981" if risque['risque'] == 'Faible' else "#F59E0B" if risque['risque'] == 'Moyen' else "#EF4444"
        st.markdown(f"""
            <div class='metric-card'>
                <label>Risque d'Appel</label>
                <value style='color: {couleur_risque};'>{risque['risque']}</value>
                <small style='color: #6B7280;'>{risque['nombre_appels']} appels</small>
            </div>
        """, unsafe_allow_html=True)
    
    # ────────────────────────────────────────
    # GRAPHIQUE PRINCIPAL
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📈 Simulation du Marking-to-Market")
    
    df = simulation['df']
    
    fig = go.Figure()
    
    # Solde du compte
    fig.add_trace(go.Scatter(
        x=df['Jour'],
        y=df['Solde_Compte'],
        name='Solde du Compte',
        line=dict(color='#1E3A5F', width=3),
        fill='tozeroy',
        fillcolor='rgba(30, 58, 95, 0.1)'
    ))
    
    # Lignes de seuil
    fig.add_hline(
        y=marge_initiale,
        line_dash='dash',
        line_color='#10B981',
        annotation_text='Marge Initiale',
        annotation_position='top right'
    )
    
    fig.add_hline(
        y=marge_maintenance,
        line_dash='dash',
        line_color='#EF4444',
        annotation_text='Marge Maintenance',
        annotation_position='top right'
    )
    
    # Annotations des appels de marge
    for appel in simulation['appels_marge']:
        fig.add_vline(
            x=appel['jour'],
            line_dash='dot',
            line_color='#F59E0B',
            annotation_text=f'Appel: {appel["montant"]:,.0f} MAD',
            annotation_position='bottom'
        )
    
    fig.update_layout(
        title='Évolution du Solde de Marge sur la Période',
        xaxis_title='Jour',
        yaxis_title='Solde (MAD)',
        hovermode='x unified',
        height=500,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ────────────────────────────────────────
    # DÉTAILS DES APPELS DE MARGE
    # ────────────────────────────────────────
    st.divider()
    
    if simulation['appels_marge']:
        st.markdown(f"### ⚠️ Appels de Marge Détectés ({len(simulation['appels_marge'])})")
        
        for appel in simulation['appels_marge']:
            st.markdown(f"""
                <div class='warning-box'>
                    <strong>Jour {appel['jour']}</strong><br>
                    Montant d'appel : <strong>{appel['montant']:,.0f} MAD</strong><br>
                    Solde avant appel : {appel['solde_avant']:,.0f} MAD<br>
                    Prix MASI : {appel['prix']:,.0f} pts
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class='info-box'>
                <strong>💡 Total déposé :</strong> {simulation['total_depose']:,.0f} MAD<br>
                <strong>💡 P&L total :</strong> {simulation['pnl_total']:+,.0f} MAD
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='success-box'>
                <strong>✅ Aucun appel de marge</strong> sur la période simulée.<br>
                Le solde est resté au-dessus du seuil de maintenance ({marge_maintenance:,.0f} MAD).
            </div>
        """, unsafe_allow_html=True)
    
    # ────────────────────────────────────────
    # TABLEAU DÉTAILLÉ
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 Historique Jour par Jour")
    
    with st.expander("Voir le tableau détaillé"):
        df_affichage = df.copy()
        df_affichage['Variation'] = df_affichage['Solde_Compte'].diff()
        df_affichage['Statut'] = df_affichage['Solde_Compte'].apply(
            lambda x: '⚠️ Appel' if x < marge_maintenance else '✅ OK'
        )
        st.dataframe(
            df_affichage.style.format({
                'Prix_MASI': '{:,.0f}',
                'Solde_Compte': '{:,.0f}',
                'Marge_Initiale': '{:,.0f}',
                'Marge_Maintenance': '{:,.0f}',
                'Variation': '{:+,.0f}'
            }),
            use_container_width=True
        )
    
    # ────────────────────────────────────────
    # RECOMMANDATIONS
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💡 Recommandations de Gestion")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **📊 Analyse de Risque :**
        - Risque d'appel de marge : **{risque['risque']}**
        - Probabilité estimée : **{risque['proba_appel']*100:.1f}%**
        - Distance au seuil critique : **{risque['distance_seuil']:+.1f}%**
        - Solde minimum atteint : **{risque['solde_min']:,.0f} MAD**
        """)
    
    with col2:
        st.markdown(f"""
        **💰 Gestion de Trésorerie :**
        - Capital initial requis : **{marge_initiale:,.0f} MAD**
        - Total déposé (avec appels) : **{simulation['total_depose']:,.0f} MAD**
        - P&L total de la position : **{simulation['pnl_total']:+,.0f} MAD**
        - Marge maintenance : **{marge_maintenance:,.0f} MAD**
        """)
    
    # Info box pédagogique
    st.markdown("""
        <div class='info-box'>
            <strong>💡 Le saviez-vous ?</strong><br>
            Le système de marges (marking-to-market) assure le bon fonctionnement du marché des futures 
            en garantissant que les engagements financiers puissent être honorés en permanence. 
            Si un investisseur ne répond pas à un appel de marge, sa position est automatiquement clôturée 
            par l'intermédiaire afin de limiter les pertes potentielles (Document §5.1).
        </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────
# PAGE 6 : RISK DASHBOARD (§1.2 du document)
# ────────────────────────────────────────────
elif page == "📈 Risk Dashboard":
    st.markdown("## 📈 Risk Dashboard — Gestion du Risque de Marché")
    
    st.markdown("""
    ### 🎯 Objectif (Document §1.2)
    
    Les contrats futures permettent d'**ajuster rapidement le niveau de risque actions** 
    sans modifier la composition du portefeuille, et contribuent à améliorer la 
    mesure des risques via :
    
    - ✅ Le **delta équivalent indice**
    - ✅ La **VaR consolidée**
    - ✅ Les analyses de **stress testing**
    """)
    
    st.divider()
    
    # ────────────────────────────────────────
    # INPUTS
    # ────────────────────────────────────────
    st.markdown("### 🔧 Paramètres du Portefeuille")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        portefeuille_value = st.number_input(
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
            help="Sensibilité aux variations du MASI"
        )
        
    with col2:
        volatilite = st.slider(
            "Volatilité annuelle estimée (%)",
            min_value=5.0,
            max_value=40.0,
            value=18.0,
            step=1.0,
            help="Volatilité historique typique du MASI: ~18%"
        ) / 100
        niveau_confiance = st.selectbox(
            "Niveau de confiance VaR",
            [0.95, 0.99],
            format_func=lambda x: f"{x*100:.0f}%"
        )
        
    with col3:
        horizon = st.selectbox(
            "Horizon de calcul",
            [1, 5, 10, 21],
            format_func=lambda x: f"{x} jour(s)"
        )
        niveau_indice = st.number_input(
            "Niveau MASI actuel (points)",
            min_value=1000.0,
            value=12000.0,
            step=100.0
        )
    
    # ────────────────────────────────────────
    # CALCULS
    # ────────────────────────────────────────
    # Génération de rendements historiques simulés pour la VaR historique
    np.random.seed(42)
    n_observations = 252  # 1 an de données journalières
    returns_simules = np.random.normal(0.0003, volatilite/np.sqrt(252), n_observations)
    
    # Analyse complète
    with st.spinner("Calcul des métriques de risque..."):
        risk_analysis = analyser_risque_complet(
            portefeuille_value=portefeuille_value,
            beta=beta,
            volatilite_annuelle=volatilite,
            returns_historiques=returns_simules,
            niveau_indice=niveau_indice
        )
    
    # ────────────────────────────────────────
    # SYNTHÈSE DU RISQUE
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🎯 Synthèse du Risque")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Risque Global</label>
                <value style='font-size: 1.4em;'>{risk_analysis['risque_global']}</value>
                <small style='color: #6B7280;'>Évaluation globale</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <label>VaR 95% ({horizon}j)</label>
                <value>{risk_analysis['var_95_10j' if horizon==10 else 'var_95_1j']:,.0f}</value>
                <small style='color: #6B7280;'>MAD</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <label>CVaR 95%</label>
                <value>{risk_analysis['cvar_95']:,.0f}</value>
                <small style='color: #6B7280;'>MAD</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Delta Équivalent</label>
                <value>{risk_analysis['delta_equivalent']:,.0f}</value>
                <small style='color: #6B7280;'>points MASI</small>
            </div>
        """, unsafe_allow_html=True)
    
    # ────────────────────────────────────────
    # VAŘ PARAMÉTRIQUE vs HISTORIQUE
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📊 Value at Risk (VaR) — Comparaison des Méthodes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class='info-box'>
                <strong>📐 VaR Paramétrique ({niveau_confiance*100:.0f}%, {horizon}j)</strong><br>
                Hypothèse: distribution normale des rendements<br><br>
                • Volatilité annuelle: {volatilite*100:.1f}%<br>
                • Z-score: {1.645 if niveau_confiance==0.95 else 2.326:.3f}<br>
                • <strong>VaR estimée: {risk_analysis[f'var_{int(niveau_confiance*100)}_{horizon}j' if horizon in [1,10] else 'var_95_1j']:,.0f} MAD</strong><br>
                • Soit {risk_analysis[f'var_{int(niveau_confiance*100)}_{horizon}j' if horizon in [1,10] else 'var_95_1j']/portefeuille_value*100:.2f}% du portefeuille
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='info-box'>
                <strong>📈 VaR Historique ({niveau_confiance*100:.0f}%)</strong><br>
                Basée sur {n_observations} observations simulées<br><br>
                • Méthode: percentile des rendements passés<br>
                • <strong>VaR historique: {risk_analysis['var_hist_95']:,.0f} MAD</strong><br>
                • CVaR (Expected Shortfall): {risk_analysis['cvar_95']:,.0f} MAD<br>
                • Perte moyenne au-delà de la VaR
            </div>
        """, unsafe_allow_html=True)
    
    # Graphique de distribution des rendements
    st.markdown("#### 📉 Distribution des Rendements Simulés")
    
    fig_dist = go.Figure()
    
    fig_dist.add_trace(go.Histogram(
        x=returns_simules * 100,  # Conversion en %
        nbinsx=50,
        name='Rendements journaliers',
        marker_color='#1E3A5F',
        opacity=0.7
    ))
    
    # Lignes VaR
    var_95_pct = np.percentile(returns_simules, 5) * 100
    fig_dist.add_vline(
        x=var_95_pct,
        line_dash='dash',
        line_color='#EF4444',
        annotation_text=f'VaR 95%: {var_95_pct:.2f}%',
        annotation_position='top'
    )
    
    fig_dist.update_layout(
        title='Distribution des Rendements Journaliers Simulés',
        xaxis_title='Rendement (%)',
        yaxis_title='Fréquence',
        height=400,
        template='plotly_white',
        bargap=0.1
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # ────────────────────────────────────────
    # STRESS TESTING
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🌪️ Stress Testing — Scénarios de Crise")
    
    stress_df = risk_analysis['stress']
    
    # Affichage sous forme de cards
    for _, row in stress_df.iterrows():
        couleur = "#EF4444" if "Élevé" in row['Niveau de Risque'] else "#F59E0B" if "Moyen" in row['Niveau de Risque'] else "#10B981"
        st.markdown(f"""
            <div class='metric-card' style='border-left-color: {couleur};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <label style='color: {couleur}; font-weight: 600;'>{row['Scénario']}</label><br>
                        <small>Variation indice: <strong>{row['Variation Indice (%)']:+.0f}%</strong> | 
                        Portefeuille: <strong>{row['Variation Portefeuille (%)']:+.1f}%</strong></small>
                    </div>
                    <div style='text-align: right;'>
                        <value style='color: {couleur}; font-size: 1.3em;'>{row['Perte Estimée (MAD)']:,.0f} MAD</value><br>
                        <small style='color: #6B7280;'>{row['Niveau de Risque']}</small>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Graphique des scénarios
    fig_stress = go.Figure()
    
    fig_stress.add_trace(go.Bar(
        x=stress_df['Scénario'],
        y=stress_df['Perte Estimée (MAD)'] / 1_000_000,  # En millions
        name='Perte Estimée',
        marker_color=stress_df['Niveau de Risque'].map({
            '🔴 Élevé': '#EF4444',
            '🟡 Moyen': '#F59E0B',
            '🟢 Faible': '#10B981'
        }),
        text=stress_df['Perte Estimée (MAD)'].apply(lambda x: f'{x/1_000_000:.1f}M'),
        textposition='auto'
    ))
    
    fig_stress.update_layout(
        title='Impact des Scénarios de Stress sur le Portefeuille',
        xaxis_title='Scénario',
        yaxis_title='Perte Estimée (Millions MAD)',
        height=400,
        template='plotly_white',
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig_stress, use_container_width=True)
    
    # ────────────────────────────────────────
    # DELTA ÉQUIVALENT INDICE
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📐 Delta Équivalent Indice (§1.2)")
    
    delta_equiv = risk_analysis['delta_equivalent']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class='info-box'>
                <strong>🎯 Définition</strong><br>
                Le delta équivalent représente l'exposition de votre portefeuille 
                en termes de <strong>points d'indice MASI</strong>.
                
                **Formule :**
                ```
                Δ = (Valeur Portefeuille × β) / Niveau Indice
                   = ({portefeuille_value:,.0f} × {beta}) / {niveau_indice:,.0f}
                   = {delta_equiv:,.0f} points
                ```
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='info-box'>
                <strong>💡 Interprétation</strong><br>
                Votre portefeuille réagit comme si vous déteniez 
                <strong>{delta_equiv:,.0f} points de MASI</strong>.
                
                **Implications :**
                • Pour couvrir ce delta: vendre {round(delta_equiv / 10):,} contrats futures*<br>
                • *Multiplicateur = 10 MAD/point
                
                **Utilisation :**
                • Ajustement dynamique de l'exposition<br>
                • Calcul du ratio de couverture optimal<br>
                • Intégration dans les systèmes de risque
            </div>
        """, unsafe_allow_html=True)
    
    # ────────────────────────────────────────
    # RECOMMANDATIONS
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💡 Recommandations de Gestion du Risque")
    
    var_pct = risk_analysis['var_95_1j'] / portefeuille_value * 100
    
    if var_pct > 3:
        st.markdown(f"""
            <div class='warning-box'>
                <strong>⚠️ Niveau de risque élevé détecté</strong><br>
                VaR 95% (1 jour): {risk_analysis['var_95_1j']:,.0f} MAD ({var_pct:.2f}% du portefeuille)<br><br>
                <strong>Recommandations :</strong>
                • Envisager une couverture partielle avec des futures MASI<br>
                • Réduire le bêta du portefeuille via diversification<br>
                • Surveiller attentivement les indicateurs de marché
            </div>
        """, unsafe_allow_html=True)
    elif var_pct > 1.5:
        st.markdown(f"""
            <div class='info-box'>
                <strong>ℹ️ Niveau de risque modéré</strong><br>
                VaR 95% (1 jour): {risk_analysis['var_95_1j']:,.0f} MAD ({var_pct:.2f}% du portefeuille)<br><br>
                <strong>Recommandations :</strong>
                • Maintenir une surveillance régulière des métriques de risque<br>
                • Prévoir des scénarios de couverture pour les périodes de volatilité<br>
                • Documenter les limites de risque internes
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='success-box'>
                <strong>✅ Niveau de risque acceptable</strong><br>
                VaR 95% (1 jour): {risk_analysis['var_95_1j']:,.0f} MAD ({var_pct:.2f}% du portefeuille)<br><br>
                <strong>Recommandations :</strong>
                • Continuer le monitoring régulier<br>
                • Profiter de la flexibilité pour ajuster l'exposition si opportunité<br>
                • Documenter les hypothèses de calcul pour audit
            </div>
        """, unsafe_allow_html=True)
    
    # Info box pédagogique
    st.markdown("""
        <div class='info-box'>
            <strong>💡 Le saviez-vous ?</strong><br>
            L'intégration des futures dans les dispositifs internes de gestion du risque 
            permet une mesure plus précise de l'exposition globale du portefeuille. 
            Le delta équivalent indice facilite l'agrégation des risques et le calcul 
            de la VaR consolidée, conformément aux meilleures pratiques institutionnelles 
            (Document §1.2).
        </div>
    """, unsafe_allow_html=True)
# ────────────────────────────────────────────
# PAGE 7 : LIMITES DE POSITION (§4.4 du document)
# ────────────────────────────────────────────
elif page == "📏 Limites":
    st.markdown("## 📏 Limites de Position et Régulation du Marché")
    
    st.markdown("""
    ### 🎯 Objectif (Document §4.4)
    
    Les limites de position et les mécanismes de régulation assurent :
    
    - ✅ **L'intégrité du marché** : Éviter la manipulation des prix
    - ✅ **La liquidité** : Empêcher la concentration excessive
    - ✅ **La stabilité** : Limiter les variations excessives (Limit Up/Down)
    - ✅ **La transparence** : Surveillance des positions par la CCP
    """)
    
    st.divider()
    
    # ────────────────────────────────────────
    # INPUTS
    # ────────────────────────────────────────
    st.markdown("### 🔧 Paramètres de Conformité")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        type_intervenant = st.selectbox(
            "Type d'Intervenant",
            ["Investisseur Institutionnel", "Investisseur Particulier", 
             "Trader Propriétaire", "Market Maker", "Compensateur"],
            help="Détermine les limites de position applicables"
        )
        indice = st.selectbox(
            "Indice Concerné",
            ["MASI", "MASI20"]
        )
        
    with col2:
        position_actuelle = st.number_input(
            "Position Actuelle (contrats)",
            min_value=-100000,
            max_value=100000,
            value=500,
            step=100,
            help="Positive = Long, Négative = Short"
        )
        prix_actuel = st.number_input(
            "Prix Actuel (points)",
            min_value=1000.0,
            value=12000.0,
            step=50.0
        )
        
    with col3:
        prix_reference = st.number_input(
            "Prix de Référence J-1 (points)",
            min_value=1000.0,
            value=11900.0,
            step=50.0,
            help="Cours de clôture de la veille"
        )
        limit_pct = st.slider(
            "Limit Up/Down (%)",
            min_value=5,
            max_value=15,
            value=10,
            step=1
        )
    
    # ────────────────────────────────────────
    # CALCULS
    # ────────────────────────────────────────
    # Rapport de conformité complet
    rapport = rapport_conformite_complet(
        position=position_actuelle,
        type_intervenant=type_intervenant,
        prix_actuel=prix_actuel,
        prix_reference=prix_reference,
        indice=indice
    )
    
    # Analyse de risque position
    risque_position = analyse_risque_position(
        position=position_actuelle,
        prix_entree=prix_reference,
        prix_actuel=prix_actuel
    )
    
    # ────────────────────────────────────────
    # SYNTHÈSE DE CONFORMITÉ
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🎯 Synthèse de Conformité")
    
    # Statut global
    if rapport['conformite_globale']:
        st.markdown(f"""
            <div class='success-box'>
                <strong>✅ Conformité Globale : RESPECTÉE</strong><br>
                Toutes les limites réglementaires sont respectées. Trading autorisé.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='warning-box'>
                <strong>⚠️ Conformité Globale : NON RESPECTÉE</strong><br>
                Une ou plusieurs limites sont dépassées. Action corrective requise.
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ────────────────────────────────────────
    # LIMIT UP / DOWN
    # ────────────────────────────────────────
    st.markdown("### 📊 Limit Up/Down (§4.4.a)")
    
    limit_info = rapport['limit_up_down']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Prix de Référence</label>
                <value>{prix_reference:,.0f}</value>
                <small style='color: #6B7280;'>points</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        limits = calcul_limit_up_down(prix_reference, limit_pct)
        st.markdown(f"""
            <div class='metric-card'>
                <label>Limit Up</label>
                <value style='color: #10B981;'>{limits['limit_up']:,.0f}</value>
                <small style='color: #6B7280;'>+{limit_pct}%</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Limit Down</label>
                <value style='color: #EF4444;'>{limits['limit_down']:,.0f}</value>
                <small style='color: #6B7280;'>-{limit_pct}%</small>
            </div>
        """, unsafe_allow_html=True)
    
    # Statut Limit Up/Down
    st.markdown(f"""
        <div class='{"success-box" if limit_info["trading_autorise"] else "warning-box"}'>
            <strong>{limit_info['statut']}</strong><br>
            {limit_info['message']}
        </div>
    """, unsafe_allow_html=True)
    
    # Graphique des limites
    fig_limit = go.Figure()
    
    fig_limit.add_trace(go.Indicator(
        mode="gauge+number",
        value=prix_actuel,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Prix Actuel: {prix_actuel:,.0f} pts", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [limits['limit_down'] * 0.95, limits['limit_up'] * 1.05]},
            'bar': {'color': "#1E3A5F"},
            'steps': [
                {'range': [limits['limit_down'] * 0.95, limits['limit_down']], 'color': "#FEE2E2"},
                {'range': [limits['limit_down'], limits['limit_up']], 'color': "#D1FAE5"},
                {'range': [limits['limit_up'], limits['limit_up'] * 1.05], 'color': "#FEE2E2"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': prix_actuel
            }
        }
    ))
    
    fig_limit.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_limit, use_container_width=True)
    
    # ────────────────────────────────────────
    # POSITION LIMITS
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 Limites de Position (§4.4.c)")
    
    position_info = rapport['position_limits']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Limite Maximale</label>
                <value>{position_info['limite']:,}</value>
                <small style='color: #6B7280;'>contrats</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <label>Position Actuelle</label>
                <value>{position_actuelle:,}</value>
                <small style='color: #6B7280;'>contrats</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        couleur = "#10B981" if position_info['pourcentage_utilise'] < 50 else "#F59E0B" if position_info['pourcentage_utilise'] < 80 else "#EF4444"
        st.markdown(f"""
            <div class='metric-card'>
                <label>% de la Limite</label>
                <value style='color: {couleur};'>{position_info['pourcentage_utilise']:.1f}%</value>
                <small style='color: #6B7280;'>utilisé</small>
            </div>
        """, unsafe_allow_html=True)
    
    # Statut position
    st.markdown(f"""
        <div class='{"success-box" if position_info["conformite"] and position_info["pourcentage_utilise"] < 80 else "warning-box" if position_info["conformite"] else "warning-box"}'>
            <strong>{position_info['statut']}</strong><br>
            {position_info['action_requise']}
        </div>
    """, unsafe_allow_html=True)
    
    # Barre de progression
    st.progress(min(position_info['pourcentage_utilise'] / 100, 1.0))
    st.caption(f"Utilisation de la limite : {position_info['pourcentage_utilise']:.1f}%")
    
    # ────────────────────────────────────────
    # MARGE REQUISE
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💰 Marge Requise pour la Position")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class='info-box'>
                <strong>📊 Calcul de la Marge</strong><br>
                Valeur notionnelle = |{position_actuelle:,}| × {prix_actuel:,.0f} × {config.MULTIPLICATEUR}<br>
                = {abs(position_actuelle) * prix_actuel * config.MULTIPLICATEUR:,.0f} MAD<br><br>
                Marge requise (10%) = <strong>{rapport['marge_requise']:,.0f} MAD</strong>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='info-box'>
                <strong>📈 Risque de Position</strong><br>
                P&L non réalisé : <strong>{risque_position['pnl_non_realise']:+,.0f} MAD</strong><br>
                Variation : <strong>{risque_position['variation_pct']:+.2f}%</strong><br>
                Niveau de risque : <strong>{risque_position['niveau_risque']}</strong><br>
                {risque_position['recommendation']}
            </div>
        """, unsafe_allow_html=True)
    
    # ────────────────────────────────────────
    # TABLEAU RÉCAPITULATIF
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 Récapitulatif de Conformité")
    
    conformite_data = pd.DataFrame({
        "Critère": [
            "📊 Limit Up/Down",
            "📋 Position Limits",
            "💰 Marge Requise",
            "📈 Risque de Position"
        ],
        "Statut": [
            limit_info['statut'],
            position_info['statut'],
            f"{rapport['marge_requise']:,.0f} MAD",
            risque_position['niveau_risque']
        ],
        "Conforme": [
            "✅" if limit_info['trading_autorise'] else "❌",
            "✅" if position_info['conformite'] else "❌",
            "✅",
            "✅" if abs(risque_position['variation_pct']) < 10 else "⚠️"
        ]
    })
    
    st.dataframe(conformite_data, hide_index=True, use_container_width=True)
    
    # ────────────────────────────────────────
    # RECOMMANDATIONS
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💡 Recommandations de Conformité")
    
    if not rapport['conformite_globale']:
        st.markdown(f"""
            <div class='warning-box'>
                <strong>⚠️ Actions Correctives Requises :</strong><br><br>
                {'• ' + limit_info.get('message', '') if not limit_info['trading_autorise'] else ''}<br>
                {'• ' + position_info.get('action_requise', '') if not position_info['conformite'] else ''}<br><br>
                <strong>Recommandation :</strong> Contacter immédiatement le département conformité 
                et réduire les positions si nécessaire.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='success-box'>
                <strong>✅ Position Conforme</strong><br><br>
                Toutes les limites réglementaires sont respectées.<br><br>
                <strong>Recommandations :</strong>
                • Maintenir une surveillance régulière des positions<br>
                • Anticiper les augmentations de volatilité<br>
                • Documenter les dépassements temporaires si applicable
            </div>
        """, unsafe_allow_html=True)
    
    # Info box pédagogique
    st.markdown("""
        <div class='info-box'>
            <strong>💡 Le saviez-vous ?</strong><br>
            Les limites de position et les mécanismes Limit Up/Down sont des outils essentiels 
            de régulation des marchés à terme. Ils permettent de prévenir les manipulations, 
            assurer la liquidité et protéger les investisseurs contre les mouvements de prix 
            excessifs. La Chambre de Compensation (CCP) surveille en permanence le respect 
            de ces limites (Document §4.4).
        </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────
st.divider()
st.caption(f"{config.APP_NAME} v{config.APP_VERSION} | Basé sur le document CDG Capital | Scraping optimisé avec cache")














