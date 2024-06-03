from binance.client import Client
import pandas as pd
import time

API_KEY = 'Cw6pBOG5Ct1GElMgwfD28PsVLKI9BW73STuVzEfJvIjSGIIPlNEB4TmDyBIWB4kT'
API_SECRET = 'i3H2TpMxndXmfDNIQf5oNA17fiy0x8QQhumIxwab1L6lMpGSt8QI7JaSZaFwkIog'

client = Client(API_KEY, API_SECRET)

# Liste des 10 premières crypto-monnaies par market cap
top_10_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'SHIBUSDT']

historical_data = []

for symbol in top_10_symbols:
    print(f"Fetching data for {symbol}")
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "100 days ago UTC")
    if not klines:
        print(f"No data found for {symbol}")
        continue
    
    df = pd.DataFrame(klines, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'Ignore'])
    df['symbol'] = symbol
    historical_data.append(df)
    time.sleep(1)  # Pour éviter de surcharger l'API

# Vérifiez si des données ont été récupérées
if not historical_data:
    print("No historical data collected.")
else:
    # Combiner toutes les données dans un seul DataFrame
    all_data = pd.concat(historical_data)
    all_data['timestamp'] = pd.to_datetime(all_data['timestamp'], unit='ms')
    all_data['Close_time'] = pd.to_datetime(all_data['Close_time'], unit='ms')

    # Réorganiser les colonnes et sauvegarder dans un fichier CSV
    all_data = all_data[['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'symbol']]
    all_data.to_csv('data/binance_historical_data.csv', index=False)
    print("Data saved to data/binance_historical_data.csv")