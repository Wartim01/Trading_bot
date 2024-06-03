# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import API_KEY, API_SECRET, EXCHANGE
import pandas as pd
from binance.client import Client
import pandas as pd
import time

API_KEY = 'Cw6pBOG5Ct1GElMgwfD28PsVLKI9BW73STuVzEfJvIjSGIIPlNEB4TmDyBIWB4kT'
API_SECRET = 'i3H2TpMxndXmfDNIQf5oNA17fiy0x8QQhumIxwab1L6lMpGSt8QI7JaSZaFwkIog'

client = Client(API_KEY, API_SECRET)

# Liste des symboles des crypto-monnaies que vous voulez récupérer
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'SHIBUSDT']

new_data = []

for symbol in symbols:
    print(f"Fetching data for {symbol}")
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 day ago UTC")
    if not klines:
        print(f"No data found for {symbol}")
        continue
    
    for kline in klines:
        new_data.append({
            'Open': kline[1],
            'High': kline[2],
            'Low': kline[3],
            'Close': kline[4],
            'Volume': kline[5],
            'Quote_asset_volume': kline[7],
            'Number_of_trades': kline[8],
            'Taker_buy_base_asset_volume': kline[9],
            'Taker_buy_quote_asset_volume': kline[10],
            'symbol': symbol
        })
    time.sleep(1)  # Pour éviter de surcharger l'API

# Convertir en DataFrame
df = pd.DataFrame(new_data)

# Sauvegarder dans un fichier CSV
df.to_csv('data/new_data.csv', index=False)
print("Data saved to data/new_data.csv")