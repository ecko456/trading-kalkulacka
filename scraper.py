import yfinance as yf
import json
from datetime import datetime, timedelta

def get_vix_data():
    """
    Tato funkce používá knihovnu yfinance k přímému stažení dat VIX z Yahoo Finance API.
    Je to mnohem spolehlivější než web scraping.
    """
    try:
        print("Stahuji data VIX pomocí yfinance API...")
        
        # Symbol pro VIX na Yahoo Finance je ^VIX
        vix_ticker = yf.Ticker("^VIX")
        
        # Stáhneme historii za poslední 2 měsíce, abychom měli dostatek dat
        hist = vix_ticker.history(period="2mo")
        
        if hist.empty:
            print("Chyba: yfinance nevrátil žádná data.")
            return []
            
        print("Data úspěšně stažena. Zpracovávám...")
        
        # Připravíme data do formátu, který chceme: [{date: "RRRR-MM-DD", price: 12.34}, ...]
        vix_data = []
        for index, row in hist.iterrows():
            vix_data.append({
                "date": index.strftime('%Y-%m-%d'),
                "price": round(row['Close'], 2) # Použijeme uzavírací cenu
            })
            
        return vix_data

    except Exception as e:
        print(f"Nastala chyba během stahování dat z yfinance: {e}")
        return []

if __name__ == "__main__":
    data = get_vix_data()
    
    if data:
        with open('vix_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data VIX byla úspěšně uložena. Počet záznamů: {len(data)}")
    else:
        print("Nepodařilo se získat data VIX.")
