import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from datetime import datetime

URL = "https://www.investing.com/indices/volatility-s-p-500-historical-data"

def get_vix_data():
    print("Spouštím Selenium WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Spustí prohlížeč bez grafického rozhraní
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("accept-language=en-US,en;q=0.9")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"Navštěvuji stránku: {URL}")
        driver.get(URL)

        # Čekáme maximálně 20 sekund, dokud se neobjeví tabulka s daty
        print("Čekám, až se tabulka s daty načte pomocí JavaScriptu...")
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table[data-test='historical-data-table']")))
        print("Tabulka nalezena!")

        # Získáme HTML obsah stránky AŽ POTÉ, co se vše načetlo
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        data_table = soup.find('table', attrs={'data-test': 'historical-data-table'})
        
        if not data_table:
            print("Chyba: Tabulka s daty nebyla nalezena ani po čekání.")
            return []

        print("Zpracovávám řádky tabulky...")
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

            historical_data.append({"date": formatted_date, "price": float(price_str)})
        
        print(f"Zpracováno {len(historical_data)} řádků.")
        return historical_data[:35]

    except Exception as e:
        print(f"Nastala chyba během běhu Selenia: {e}")
        return []
    finally:
        print("Ukončuji WebDriver.")
        driver.quit()

if __name__ == "__main__":
    vix_data = get_vix_data()
    if vix_data:
        with open('vix_data.json', 'w') as f:
            json.dump(vix_data, f, indent=4)
        print(f"Data VIX byla úspěšně stažena a uložena do vix_data.json. Počet záznamů: {len(vix_data)}")
    else:
        print("Nepodařilo se získat data VIX. Soubor vix_data.json nebyl vytvořen.")
