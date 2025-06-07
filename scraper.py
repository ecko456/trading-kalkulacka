# scraper.py

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# URL adresa, odkud budeme stahovat data
URL = "https://www.investing.com/indices/volatility-s-p-500-historical-data"

# Hlavičky, které posíláme s požadavkem. To je důležité, aby si stránka myslela,
# že jsme reálný prohlížeč, a ne robot.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9" # Požadujeme anglickou verzi pro konzistentní formát data
}

def get_vix_data():
    """
    Tato funkce navštíví stránku Investing.com, najde tabulku s historickými daty,
    extrahune je a vrátí jako seznam.
    """
    try:
        # Pošleme požadavek na stránku
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()  # Zkontroluje, zda požadavek proběhl v pořádku

        # Zpracujeme HTML obsah stránky pomocí BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Najdeme tabulku s daty podle jejího ID
        data_table = soup.find('table', {'id': 'curr_table'})
        
        if not data_table:
            print("Chyba: Tabulka s daty nebyla nalezena.")
            return []

        # Připravíme si prázdný seznam pro uložení dat
        historical_data = []
        
        # Projdeme všechny řádky <tr> v těle tabulky <tbody>
        for row in data_table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 2: continue # Přeskočíme prázdné nebo nekompletní řádky
            
            # Získáme datum a cenu
            date_str = cols[0].text.strip()
            price_str = cols[1].text.strip().replace(',', '')
            
            # Převedeme textové datum (např. "Jun 07, 2025") na standardní formát RRRR-MM-DD
            try:
                date_obj = datetime.strptime(date_str, '%b %d, %Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue

            # Uložíme data jako slovník do našeho seznamu
            historical_data.append({
                "date": formatted_date,
                "price": float(price_str)
            })

        # Vrátíme pouze posledních 35 záznamů, což bohatě stačí pro náš graf
        return historical_data[:35]

    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování stránky: {e}")
        return []
    except Exception as e:
        print(f"Nastala neočekávaná chyba: {e}")
        return []

# Hlavní část skriptu, která se spustí
if __name__ == "__main__":
    vix_data = get_vix_data()
    
    # Pokud jsme úspěšně získali data, uložíme je do souboru vix_data.json
    if vix_data:
        with open('vix_data.json', 'w') as f:
            json.dump(vix_data, f, indent=4)
        print(f"Data VIX byla úspěšně stažena. Počet záznamů: {len(vix_data)}")
    else:
        print("Nepodařilo se získat data VIX.")
