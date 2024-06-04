import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import numpy as np
import time
import logging
import re

# Importation des stratégies
from strategies import (
    bollinger_strategy, ma_cross_strategy, macd_strategy, rsi_strategy,
    ema_cross_strategy, stochastic_oscillator_strategy, adx_strategy, ichimoku_strategy,
    volume_strategy, candlestick_strategy, obv_strategy, aroon_strategy,
    parabolic_sar_strategy, williams_r_strategy, tema_strategy, atr_strategy,
    keltner_channel_strategy, donchian_channel_strategy, rvi_strategy, momentum_strategy
)

# Configurer les logs
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Clés API Binance pour le Testnet
api_key = 'fvo67wee5dq10q00pajP2y9Rqz5Pwkdc01h2RY8m9OirvQ0oOPJhrFUW2QyKYfEJ'
api_secret = 'wvM9TmcVEG76GwNwFtPHZNx1z6W56h6VfFmUaqchkI3VpuPVbOcrxlDojXP1k29f'
client = Client(api_key, api_secret, testnet=True)

# Liste des symboles des crypto-monnaies
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'SHIBUSDT']

# Fonction pour récupérer les nouvelles données (optimisée)
def fetch_new_data(symbols):
    new_data = []
    valid_symbols = []

    for symbol in symbols:
        if re.match("^[A-Z0-9]{1,20}$", symbol):  # Vérification du format du symbole
            valid_symbols.append(symbol)
        else:
            logging.warning(f"Invalid symbol: {symbol} - Reason: Does not match regex")

    if not valid_symbols:
        logging.error("No valid symbols found.")
        return pd.DataFrame() 

    try:
        klines = client.get_klines(
            symbol=valid_symbols, 
            interval=Client.KLINE_INTERVAL_1DAY,
            limit=1 
        )

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
                'symbol': kline[0].split("USDT")[0] + "USDT" 
            })

    except BinanceAPIException as e:  # Gestion de l'erreur BinanceAPIException
        logging.error(f"Error fetching klines: {e}")
        return pd.DataFrame()  # Renvoyer un DataFrame vide en cas d'erreur

    return pd.DataFrame(new_data)

# Fonction pour gérer les risques et calculer la quantité de trade
def calculate_trade_amount(capital, current_price):
    trade_amount = (capital * 0.02) / current_price  # Risque de 2% par trade
    logging.info(f"Calculated trade amount: {trade_amount}")
    return trade_amount

# Fonction pour vérifier les stratégies
def apply_strategies(data):
    signals = {}
    for strategy in [
        # ... (liste de vos stratégies)
    ]:
        signal = strategy(data.copy()) 
        signals[strategy.__name__] = signal
    return signals

# Fonction pour prendre des décisions de trading
def trade_decision(data, capital):
    for index, row in data.iterrows():
        trade_amount = calculate_trade_amount(capital, row['Close'])
        
        # DataFrame pour les 50 dernières lignes (ou moins)
        row_df = data.iloc[max(0, index-50):index+1]
        strategies_signals = apply_strategies(row_df)

        buy_signals = sum(strategies_signals.values()) 
        sell_signals = len(strategies_signals) - buy_signals

        if buy_signals >= 3:  # Achat si au moins 2 stratégies donnent un signal d'achat
            # Exécuter l'ordre d'achat ici (code indenté)
            logging.info(f"Buy signal for {row['symbol']} at {row['Close']}")
            try:
                order = client.order_market_buy(
                    symbol=row['symbol'],
                    quantity=trade_amount
                )
                logging.info(f"Buy order placed for {row['symbol']}: {order}")
            except Exception as e:
                logging.error(f"An error occurred while placing buy order: {e}")
                
        elif sell_signals >= 3:  # Vente si au moins 2 stratégies donnent un signal de vente
            # Exécuter l'ordre de vente ici (code indenté)
            logging.info(f"Sell signal for {row['symbol']} at {row['Close']}")
            try:
                order = client.order_market_sell(
                    symbol=row['symbol'],
                    quantity=trade_amount
                )
                logging.info(f"Sell order placed for {row['symbol']}: {order}")
            except Exception as e:
                logging.error(f"An error occurred while placing sell order: {e}")
 
# Exécution du bot de trading
def run_bot():
    capital = 20 
    new_data = fetch_new_data(symbols)
    if new_data.empty:
        logging.warning("No new data fetched.")
        return

    trade_decision(new_data, capital) 

if __name__ == "__main__":
    run_bot()