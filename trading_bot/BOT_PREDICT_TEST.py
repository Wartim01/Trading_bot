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
from strategies.bollinger_strategy import bollinger_strategy
from strategies.ma_cross_strategy import ma_cross_strategy
from strategies.macd_strategy import macd_strategy
from strategies.rsi_strategy import rsi_strategy
from strategies.ema_cross_strategy import ema_cross_strategy
from strategies.stochastic_oscillator_strategy import stochastic_oscillator_strategy
from strategies.adx_strategy import adx_strategy
from strategies.ichimoku_strategy import ichimoku_strategy
from strategies.volume_strategy import volume_strategy
from strategies.candlestick_strategy import candlestick_strategy
from strategies.obv_strategy import obv_strategy
from strategies.aroon_strategy import aroon_strategy
from strategies.parabolic_sar_strategy import parabolic_sar_strategy
from strategies.williams_r_strategy import williams_r_strategy
from strategies.tema_strategy import tema_strategy
from strategies.atr_strategy import atr_strategy
from strategies.keltner_channel_strategy import keltner_channel_strategy
from strategies.donchian_channel_strategy import donchian_channel_strategy
from strategies.rvi_strategy import rvi_strategy
from strategies.momentum_strategy import momentum_strategy
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

    for symbol in valid_symbols:
        logging.info(f"Fetching klines for symbol: {symbol}")
        try:
            klines = client.get_klines(symbol=symbol, interval='1h')
        except BinanceAPIException as e:
            logging.error(f"Binance API error fetching klines for {symbol}: {e.message}")
            continue
        except Exception as e:
            logging.error(f"General error fetching klines for {symbol}: {e}")
            continue

        for kline in klines:
            new_data.append({
                'symbol': symbol,
                'timestamp': pd.to_datetime(kline[0], unit='ms'),
                'open': float(kline[1]),
                'high': float(kline[2]),
                'low': float(kline[3]),
                'close': float(kline[4]),
                'volume': float(kline[5]),
                'close_time': pd.to_datetime(kline[6], unit='ms'),
                'quote_asset_volume': float(kline[7]),
                'number_of_trades': int(kline[8]),
                'taker_buy_base_asset_volume': float(kline[9]),
                'taker_buy_quote_asset_volume': float(kline[10]),
                'ignore': kline[11]
            })

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
        bollinger_strategy, ma_cross_strategy, macd_strategy, rsi_strategy,
    ema_cross_strategy, stochastic_oscillator_strategy, adx_strategy, ichimoku_strategy,
    volume_strategy, candlestick_strategy, obv_strategy, aroon_strategy,
    parabolic_sar_strategy, williams_r_strategy, tema_strategy, atr_strategy,
    keltner_channel_strategy, donchian_channel_strategy, rvi_strategy, momentum_strategy
    ]:
        result = strategy(data.copy())
        if isinstance(result, dict):
            signals.update(result)  # Fusionner les dictionnaires de signaux
        else:
            signals[strategy.__name__] = result  # Ajouter le signal unique
    return signals

def trade_decision(data, capital):
    for index, row in data.iterrows():
        trade_amount = calculate_trade_amount(capital, row['close'])
        
        # DataFrame pour les 50 dernières lignes (ou moins)
        row_df = data.iloc[max(0, index-50):index+1]
        strategies_signals = apply_strategies(row_df)
        
        # Liste de tous les signaux 
        all_signals = [signal for strategy_signals in strategies_signals.values() for signal in strategy_signals.values()] 

        buy_signals = all_signals.count(True)
        sell_signals = all_signals.count(False)

        if buy_signals >= 3:  
            logging.info(f"Buy signal for {row['symbol']} at {row['close']}")
            try:
                order = client.order_market_buy(
                    symbol=row['symbol'],
                    quantity=trade_amount
                )
                logging.info(f"Buy order placed for {row['symbol']}: {order}")
            except Exception as e:
                logging.error(f"An error occurred while placing buy order: {e}")
                
        elif sell_signals >= 3:  
            logging.info(f"Sell signal for {row['symbol']} at {row['close']}")
            try:
                order = client.order_market_sell(
                    symbol=row['symbol'],
                    quantity=trade_amount
                )
                logging.info(f"Sell order placed for {row['symbol']}: {order}")
            except Exception as e:
                logging.error(f"An error occurred while placing sell order: {e}")


def run_bot():
    capital = 20 
    new_data = fetch_new_data(symbols)
    if new_data.empty:
        logging.warning("No new data fetched.")
        return

    trade_decision(new_data, capital) 

if __name__ == "__main__":
    run_bot()