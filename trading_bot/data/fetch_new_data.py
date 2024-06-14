# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import time
import logging
import re


# Configurez logging pour stocker les messages d'erreur et d'info dans un fichier
logging.basicConfig(filename='fetch_new_data.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Client Binance
client = Client(API_KEY, API_SECRET)

# Liste des symboles à surveiller 
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'SHIBUSDT']

new_data = []

for symbol in symbols:
    logging.info(f"Fetching data for {symbol}")
    try:
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 day ago UTC")
        if not klines:
            logging.warning(f"No data found for {symbol}")
            continue  # Passe au symbole suivant si aucune donnée n'est trouvée

        for kline in klines:
            new_data.append({
                'Open': float(kline[1]),
                'High': float(kline[2]),
                'Low': float(kline[3]),
                'Close': float(kline[4]),
                'Volume': float(kline[5]),
                'Quote_asset_volume': float(kline[7]),
                'Number_of_trades': int(kline[8]),
                'Taker_buy_base_asset_volume': float(kline[9]),
                'Taker_buy_quote_asset_volume': float(kline[10]),
                'symbol': symbol
            })
    
    except (BinanceAPIException, BinanceRequestException) as e:
        # Enregistrez l'erreur dans le fichier log
        logging.error(f"Error fetching data for {symbol}: {e}")

    # Temporisation pour respecter les limites de l'API
    time.sleep(1)

# Conversion en DataFrame pandas
df = pd.DataFrame(new_data)

# Sauvegarde des nouvelles données dans un fichier CSV
if not df.empty:
    df.to_csv('new_data.csv', index=False)
    logging.info("Data saved to data/new_data.csv")
else:
    logging.warning("No new data to save.")
