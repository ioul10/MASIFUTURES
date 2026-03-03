# ============================================
# SCRAPPING BOURSE DE CASABLANCA
# Récupération des données MASI/MASI20
# ============================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from cachetools import TTLCache

# Cache pour éviter trop de requêtes (5 minutes)
cache = TTLCache(maxsize=100, ttl=300)

# ────────────────────────────────────────────
# CONSTANTES
# ────────────────────────────────────────────
BASE_URL = "https://www.casablanca-bourse.com"
INDICES_URL = f"{BASE_URL}/fr/historique-des-indices"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
}

# ────────────────────────────────────────────
# FONCTIONS DE SCRAPPING
# ────────────────────────────────────────────

def _fetch_page(url):
    """Récupère le contenu HTML d'une page avec gestion d'erreurs"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
        return None

def _parse_indices(html):
    """Extrait les données des indices depuis le HTML"""
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'lxml')
    
    # Recherche les tableaux ou divs contenant les indices
    # Note: Structure à adapter selon le site réel
    indices_data = {}
    
    # Méthode 1: Recherche par class CSS commune
    index_containers = soup.find_all('div', class_=lambda x: x and 'index' in x.lower())
    
    for container in index_containers:
        name = container.find('span', class_='index-name')
        value = container.find('span', class_='index-value')
        variation = container.find('span', class_='index-variation')
        
        if name and value:
            index_name = name.text.strip()
            if 'MASI' in index_name.upper():
                indices_data['MASI'] = {
                    'nom': index_name,
                    'niveau': float(value.text.strip().replace(' ', '').replace(',', '.')),
                    'variation': variation.text.strip() if variation else 'N/A',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            elif 'MASI20' in index_name.upper():
                indices_data['MASI20'] = {
                    'nom': index_name,
                    'niveau': float(value.text.strip().replace(' ', '').replace(',', '.')),
                    'variation': variation.text.strip() if variation else 'N/A',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
    
    return indices_data if indices_data else None

def get_indices_data(force_refresh=False):
    """
    Récupère les données MASI/MASI20 avec cache
    Args:
        force_refresh: Force une nouvelle requête même si cache existe
    Returns:
        dict avec données MASI et MASI20 ou None si échec
    """
    
    # Vérifier le cache
    if not force_refresh and 'indices_data' in cache:
        print("✅ Données récupérées depuis le cache")
        return cache['indices_data']
    
    print("🔄 Récupération des données depuis Bourse de Casablanca...")
    
    # Tenter de scraper
    html = _fetch_page(INDICES_URL)
    data = _parse_indices(html) if html else None
    
    # Si scraping échoue, retourner données mockées
    if not data:
        print("⚠️ Scraping échoué, utilisation des données mockées")
        data = get_mock_indices_data()
    
    # Mettre en cache
    cache['indices_data'] = data
    
    return data

def get_mock_indices_data():
    """Données mockées de secours (réalistes)"""
    import random
    
    base_masi = 12345.67
    base_masi20 = 1876.54
    
    # Variation aléatoire réaliste
    variation_masi = random.uniform(-1.5, 1.5)
    variation_masi20 = random.uniform(-1.5, 1.5)
    
    return {
        'MASI': {
            'nom': 'MASI',
            'niveau': base_masi * (1 + variation_masi/100),
            'variation': f"{variation_masi:+.2f}%",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'MASI20': {
            'nom': 'MASI20',
            'niveau': base_masi20 * (1 + variation_masi20/100),
            'variation': f"{variation_masi20:+.2f}%",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

def get_historical_data(indice='MASI', jours=30):
    """
    Récupère l'historique des cours (mocké pour V1)
    À améliorer avec scraping réel plus tard
    """
    import numpy as np
    
    dates = pd.date_range(end=datetime.now(), periods=jours, freq='B')
    
    # Simulation GBM réaliste
    if indice == 'MASI':
        S0 = 12345.67
        volatilite = 0.015
    else:
        S0 = 1876.54
        volatilite = 0.018
    
    returns = np.random.normal(0.0003, volatilite, jours)
    prices = S0 * np.exp(np.cumsum(returns))
    
    return pd.DataFrame({
        'Date': dates,
        f'{indice}_Close': prices,
        'Variation': np.concatenate([[0], np.diff(prices)/prices[:-1] * 100])
    })

# ────────────────────────────────────────────
# TEST DU SCRAPPING
# ────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DU MODULE DE SCRAPPING")
    print("=" * 60)
    
    # Test 1: Récupération des données
    print("\n1️⃣ Test: Récupération des indices...")
    data = get_indices_data(force_refresh=True)
    
    if data:
        for indice, info in data.items():
            print(f"\n✅ {info['nom']}:")
            print(f"   Niveau: {info['niveau']:,.2f} pts")
            print(f"   Variation: {info['variation']}")
            print(f"   Timestamp: {info['timestamp']}")
    else:
        print("❌ Échec de récupération des données")
    
    # Test 2: Données historiques
    print("\n2️⃣ Test: Données historiques...")
    hist = get_historical_data('MASI', jours=10)
    print(f"   {len(hist)} jours récupérés")
    print(f"   Dernier cours: {hist[f'MASI_Close'].iloc[-1]:,.2f}")
    
    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ")
    print("=" * 60)
