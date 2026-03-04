# ============================================
# NEWS SCRAPER - Actualités Marché Marocain
# MASI Futures Pro Simulator
# ============================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from cachetools import TTLCache
import re

# Cache pour les news (30 minutes)
news_cache = TTLCache(maxsize=100, ttl=1800)

# ────────────────────────────────────────────
# CONSTANTES
# ────────────────────────────────────────────
ILBOURSA_URL = "https://www.ilboursa.com"
ILBOURSA_NEWS_URL = f"{ILBOURSA_URL}/f/marche-de-casablanca"

CASABLANCA_BOURSE_URL = "https://www.casablanca-bourse.com"
CASABLANCA_NEWS_URL = f"{CASABLANCA_BOURSE_URL}/fr/actualites"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'fr-FR,fr;q=0.9',
}

# ────────────────────────────────────────────
# FONCTIONS DE SCRAPPING ILBOURSA
# ────────────────────────────────────────────

def scrape_ilboursa_news(max_news=10):
    """
    Récupère les actualités depuis Ilboursa.com
    
    Args:
        max_news: Nombre maximum d'articles à récupérer
    
    Returns:
        Liste de dicts avec titre, date, résumé, url
    """
    try:
        response = requests.get(ILBOURSA_NEWS_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        news_list = []
        
        # Recherche les articles (structure Ilboursa)
        articles = soup.find_all('div', class_='post-item') or soup.find_all('article')
        
        for article in articles[:max_news]:
            try:
                # Titre
                title_tag = article.find('h2') or article.find('h3')
                if not title_tag:
                    continue
                titre = title_tag.text.strip()
                
                # Lien
                link_tag = title_tag.find('a') or article.find('a', href=True)
                url = link_tag['href'] if link_tag else ''
                if url and not url.startswith('http'):
                    url = ILBOURSA_URL + url
                
                # Date (si disponible)
                date_tag = article.find('time') or article.find('span', class_='date')
                date_str = date_tag.text.strip() if date_tag else datetime.now().strftime('%d/%m/%Y')
                
                # Résumé
                summary_tag = article.find('p', class_='post-excerpt') or article.find('p')
                resume = summary_tag.text.strip()[:200] + '...' if summary_tag else ''
                
                news_list.append({
                    'source': 'Ilboursa',
                    'titre': titre,
                    'resume': resume,
                    'date': date_str,
                    'url': url,
                    'categorie': 'Marché'
                })
            except Exception as e:
                continue
        
        return news_list
    
    except Exception as e:
        print(f"❌ Erreur scraping Ilboursa: {e}")
        return []

# ────────────────────────────────────────────
# FONCTIONS DE SCRAPPING BOURSE DE CASABLANCA
# ────────────────────────────────────────────

def scrape_casablanca_bourse_news(max_news=5):
    """
    Récupère les actualités depuis Bourse de Casablanca
    
    Args:
        max_news: Nombre maximum d'articles
    
    Returns:
        Liste de dicts avec actualités
    """
    try:
        response = requests.get(CASABLANCA_NEWS_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        news_list = []
        
        # Recherche les actualités
        articles = soup.find_all('div', class_='item') or soup.find_all('article')
        
        for article in articles[:max_news]:
            try:
                # Titre
                title_tag = article.find('h3') or article.find('h4')
                if not title_tag:
                    continue
                titre = title_tag.text.strip()
                
                # Lien
                link_tag = title_tag.find('a') or article.find('a', href=True)
                url = link_tag['href'] if link_tag else ''
                if url and not url.startswith('http'):
                    url = CASABLANCA_BOURSE_URL + url
                
                # Date
                date_tag = article.find('span', class_='date') or article.find('time')
                date_str = date_tag.text.strip() if date_tag else datetime.now().strftime('%d/%m/%Y')
                
                # Catégorie
                cat_tag = article.find('span', class_='category')
                categorie = cat_tag.text.strip() if cat_tag else 'Actualité'
                
                news_list.append({
                    'source': 'Bourse de Casablanca',
                    'titre': titre,
                    'resume': '',
                    'date': date_str,
                    'url': url,
                    'categorie': categorie
                })
            except Exception as e:
                continue
        
        return news_list
    
    except Exception as e:
        print(f"❌ Erreur scraping Bourse de Casablanca: {e}")
        return []

# ────────────────────────────────────────────
# FONCTIONS PRINCIPALES
# ────────────────────────────────────────────

def get_all_news(force_refresh=False, max_total=15):
    """
    Récupère toutes les actualités (Ilboursa + Bourse de Casa)
    
    Args:
        force_refresh: Forcer le rafraîchissement
        max_total: Nombre maximum total d'articles
    
    Returns:
        DataFrame avec toutes les actualités
    """
    
    # Vérifier le cache
    if not force_refresh and 'news_data' in news_cache:
        return news_cache['news_data']
    
    # Scraper les deux sources
    ilboursa_news = scrape_ilboursa_news(max_news=10)
    casablanca_news = scrape_casablanca_bourse_news(max_news=5)
    
    # Combiner les news
    all_news = ilboursa_news + casablanca_news
    
    # Trier par date (approximatif)
    # Convertir en DataFrame
    df_news = pd.DataFrame(all_news)
    
    if not df_news.empty:
        df_news = df_news.drop_duplicates(subset=['titre'])
        df_news = df_news.head(max_total)
    
    # Mettre en cache
    news_cache['news_data'] = df_news
    
    return df_news

def get_news_by_category(category, max_news=5):
    """
    Filtre les news par catégorie
    
    Args:
        category: Catégorie à filtrer
        max_news: Nombre maximum
    
    Returns:
        DataFrame filtré
    """
    df_news = get_all_news()
    
    if df_news.empty:
        return pd.DataFrame()
    
    filtered = df_news[df_news['categorie'].str.lower().str.contains(category.lower(), na=False)]
    return filtered.head(max_news)

def search_news(keyword, max_news=5):
    """
    Recherche dans les news par mot-clé
    
    Args:
        keyword: Mot-clé à rechercher
        max_news: Nombre maximum
    
    Returns:
        DataFrame avec résultats
    """
    df_news = get_all_news()
    
    if df_news.empty:
        return pd.DataFrame()
    
    mask = (df_news['titre'].str.contains(keyword, case=False, na=False) | 
            df_news['resume'].str.contains(keyword, case=False, na=False))
    
    return df_news[mask].head(max_news)

def get_latest_market_update():
    """
    Récupère les dernières actualités importantes du marché
    
    Returns:
        Dict avec les infos clés
    """
    df_news = get_all_news()
    
    if df_news.empty:
        return {
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'news_count': 0,
            'latest_headline': 'Aucune actualité disponible'
        }
    
    return {
        'last_update': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'news_count': len(df_news),
        'latest_headline': df_news.iloc[0]['titre'] if len(df_news) > 0 else 'N/A',
        'sources': df_news['source'].unique().tolist()
    }

# ────────────────────────────────────────────
# TEST
# ────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DU MODULE NEWS SCRAPER")
    print("=" * 60)
    
    print("\n1️⃣ Récupération des actualités...")
    df = get_all_news(force_refresh=True, max_total=10)
    
    if not df.empty:
        print(f"✅ {len(df)} actualités récupérées")
        print(f"\nDernière actualité:")
        print(f"  Source: {df.iloc[0]['source']}")
        print(f"  Titre: {df.iloc[0]['titre']}")
        print(f"  Date: {df.iloc[0]['date']}")
        print(f"  URL: {df.iloc[0]['url']}")
    else:
        print("❌ Aucune actualité récupérée")
    
    print("\n" + "=" * 60)
