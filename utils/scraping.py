# ============================================
# SCRAPPING BOURSE DE CASABLANCA - VERSION OPTIMISÉE
# ============================================

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
from cachetools import TTLCache

# ────────────────────────────────────────────
# CONFIGURATION DU CACHE
# ────────────────────────────────────────────
CACHE_DURATION_MINUTES = 5  # Durée du cache (minutes)
CACHE_FILE = "data/indices_cache.json"

# Cache en mémoire + fichier local
memory_cache = TTLCache(maxsize=100, ttl=CACHE_DURATION_MINUTES * 60)

# ────────────────────────────────────────────
# CONSTANTES
# ────────────────────────────────────────────
BASE_URL = "https://www.casablanca-bourse.com"
INDICES_URL = f"{BASE_URL}/fr/historique-des-indices"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'fr-FR,fr;q=0.9',
}

# ────────────────────────────────────────────
# FONCTIONS DE CACHE
# ────────────────────────────────────────────

def _load_cache_from_file():
    """Charge le cache depuis le fichier JSON local"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Vérifier si le cache est encore valide
                timestamp = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                if datetime.now() - timestamp < timedelta(minutes=CACHE_DURATION_MINUTES):
                    return data.get('indices')
        except Exception as e:
            print(f"⚠️ Erreur lecture cache: {e}")
    return None

def _save_cache_to_file(indices_data):
    """Sauvegarde le cache dans un fichier JSON local"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'indices': indices_data
    }
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Erreur écriture cache: {e}")

# ────────────────────────────────────────────
# FONCTIONS DE SCRAPPING
# ────────────────────────────────────────────

def _fetch_page(url):
    """Récupère le contenu HTML avec gestion d'erreurs"""
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
    indices_data = {}
    
    # Méthode 1: Recherche par class CSS (à adapter selon le site)
    index_containers = soup.find_all('div', class_=lambda x: x and 'index' in x.lower())
    
    for container in index_containers:
        name = container.find('span', class_='index-name')
        value = container.find('span', class_='index-value')
        variation = container.find('span', class_='index-variation')
        
        if name and value:
            index_name = name.text.strip().upper()
            try:
                niveau = float(value.text.strip().replace(' ', '').replace(',', '.'))
            except:
                continue
                
            if 'MASI' in index_name and 'MASI20' not in index_name:
                indices_data['MASI'] = {
                    'nom': 'MASI',
                    'niveau': niveau,
                    'variation': variation.text.strip() if variation else 'N/A',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            elif 'MASI20' in index_name:
                indices_data['MASI20'] = {
                    'nom': 'MASI20',
                    'niveau': niveau,
                    'variation': variation.text.strip() if variation else 'N/A',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
    
    return indices_data if indices_data else None

def get_indices_data(force_refresh=False):
    """
    Récupère les données MASI/MASI20 avec cache optimisé
    Priority: 1. Memory Cache → 2. File Cache → 3. Scraping → 4. Mock Data
    """
    
    # 1. Vérifier le cache en mémoire
    if not force_refresh and 'indices_data' in memory_cache:
        print("✅ Cache mémoire utilisé")
        return memory_cache['indices_data']
    
    # 2. Vérifier le cache fichier
    if not force_refresh:
        file_cache = _load_cache_from_file()
        if file_cache:
            print("✅ Cache fichier utilisé")
            memory_cache['indices_data'] = file_cache
            return file_cache
    
    # 3. Scraper le site
    print("🔄 Scraping Bourse de Casablanca...")
    html = _fetch_page(INDICES_URL)
    data = _parse_indices(html) if html else None
    
    # 4. Fallback sur données mockées si scraping échoue
    if not data:
        print("⚠️ Scraping échoué, utilisation des données mockées")
        data = get_mock_indices_data()
    
    # Sauvegarder dans les caches
    memory_cache['indices_data'] = data
    _save_cache_to_file(data)
    
    return data

def get_mock_indices_data():
    """Données mockées de secours (réalistes)"""
    import random
    
    base_masi = 12345.67
    base_masi20 = 1876.54
    
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
    """Récupère l'historique des cours (mocké pour V1)"""
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(end=datetime.now(), periods=jours, freq='B')
    
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

def get_cache_info():
    """Retourne des informations sur le cache"""
    cache_file_exists = os.path.exists(CACHE_FILE)
    cache_age = "N/A"
    
    if cache_file_exists:
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                age = datetime.now() - timestamp
                cache_age = f"{age.seconds // 60} minutes"
        except:
            pass
    
    return {
        'file_exists': cache_file_exists,
        'cache_age': cache_age,
        'duration_minutes': CACHE_DURATION_MINUTES
    }

# ────────────────────────────────────────────
# TEST
# ────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DU MODULE DE SCRAPPING")
    print("=" * 60)
    
    print("\n1️⃣ Test: Récupération des indices...")
    data = get_indices_data(force_refresh=True)
    
    if data:
        for indice, info in data.items():
            print(f"\n✅ {info['nom']}:")
            print(f"   Niveau: {info['niveau']:,.2f} pts")
            print(f"   Variation: {info['variation']}")
            print(f"   Timestamp: {info['timestamp']}")
    
    print("\n2️⃣ Test: Informations cache...")
    cache_info = get_cache_info()
    status = "✅ Existe" if cache_info['file_exists'] else "❌ Inexistant"
    print(f"   Fichier cache: {status}")
    print(f"   Âge du cache: {cache_info['cache_age']}")
    print(f"   Durée: {cache_info['duration_minutes']} minutes")
    
    print("\n" + "=" * 60)
