# scraper.py - verze 2 (s opraveným vyhledáváním tabulky)

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

URL = "https://www.investing.com/indices/volatility-s-p-500-historical-data"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def get_vix_data():
    """
    Tato funkce navštíví stránku Investing.com, najde tabulku s historickými daty,
    extrahune je a vrátí jako seznam.
    """
    try:
        print("Odesílám požadavek na URL:", URL)
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()
        print("Stránka úspěšně stažena. Zpracovávám obsah...")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- ZDE JE OPRAVA ---
        # Hledáme tabulku podle stabilnějšího atributu data-test
        data_table = soup.find('table', attrs={'data-test': 'historical-data-table'})
        
        if not data_table:
            print("Chyba: Tabulka s daty nebyla nalezena. (selektor: table[data-test='historical-data-table'])")
            return []

        print("Tabulka s daty úspěšně nalezena. Zpracovávám řádky...")
        historical_data = []
        
        for row in data_table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 2: continue
            
            date_str = cols[0].text.strip()
            price_str = cols[1].text.strip().replace(',', '')
            
            try:
                date_obj = datetime.strptime(date_str, '%b %d, %Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue

            historical_data.append({
                "date": formatted_date,
                "price": float(price_str)
            })

        print(f"Zpracováno {len(historical_data)} řádků.")
        return historical_data[:35]

    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování stránky: {e}")
        return []
    except Exception as e:
        print(f"Nastala neočekávaná chyba: {e}")
        return []

if __name__ == "__main__":
    vix_data = get_vix_data()
    
    if vix_data:
        with open('vix_data.json', 'w') as f:
            json.dump(vix_data, f, indent=4)
        print(f"Data VIX byla úspěšně stažena. Počet záznamů: {len(vix_data)}")
    else:
        print("Nepodařilo se získat data VIX. Soubor vix_data.json nebyl vytvořen.")
