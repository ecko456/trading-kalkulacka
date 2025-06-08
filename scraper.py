import yfinance as yf
import requests
import json
import os
from datetime import datetime

# --- Funkce pro VIX (beze změny) ---
def get_vix_data():
    try:
        print("Stahuji data VIX pomocí yfinance API...")
        vix_ticker = yf.Ticker("^VIX")
        hist = vix_ticker.history(period="2mo")
        if hist.empty:
            print("yfinance nevrátil žádná data pro VIX.")
            return []
        vix_data = []
        for index, row in hist.iterrows():
            vix_data.append({ "date": index.strftime('%Y-%m-%d'), "price": round(row['Close'], 2) })
        print(f"Data VIX úspěšně stažena. Počet záznamů: {len(vix_data)}")
        return vix_data
    except Exception as e:
        print(f"Chyba při stahování VIX dat: {e}")
        return []

# --- NOVÁ FUNKCE pro zprávy z Polygon.io ---
def get_news_data():
    try:
        print("Stahuji zprávy pomocí Polygon.io API...")
        # Načtení API klíče z bezpečného prostředí (GitHub Secrets)
        API_KEY = os.getenv('POLYGON_API_KEY')
        if not API_KEY:
            print("Chyba: API klíč pro Polygon.io nebyl nalezen.")
            return []

        # Sestavení URL pro API dotaz
        URL = f"https://api.polygon.io/v2/reference/news?limit=20&apiKey={API_KEY}"
        
        response = requests.get(URL)
        response.raise_for_status()
        
        data = response.json()
        news_articles = []
        
        # Zpracování výsledků
        for article in data.get('results', []):
            news_articles.append({
                "title": article.get('title'),
                "url": article.get('article_url'),
                "source": article.get('publisher', {}).get('name'),
                "image": article.get('image_url'),
                "published_utc": article.get('published_utc')
            })
        print(f"Zprávy úspěšně staženy. Počet článků: {len(news_articles)}")
        return news_articles

    except Exception as e:
        print(f"Chyba při stahování zpráv z Polygon.io: {e}")
        return []

# --- Hlavní část skriptu ---
if __name__ == "__main__":
    # Stáhneme VIX a uložíme
    vix_data = get_vix_data()
    if vix_data:
        with open('vix_data.json', 'w') as f:
            json.dump(vix_data, f, indent=4)
        print("Soubor vix_data.json byl úspěšně vytvořen.")

    # Stáhneme zprávy a uložíme
    news_data = get_news_data()
    if news_data:
        with open('news_data.json', 'w') as f:
            json.dump(news_data, f, indent=4)
        print("Soubor news_data.json byl úspěšně vytvořen.")
