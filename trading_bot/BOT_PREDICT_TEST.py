import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
from binance.client import Client
from binance.enums import *
import numpy as np
import time
import logging

# Importation des stratégies
from trading_bot.strategies import (
    bollinger_check, ma_cross_check, macd_check, rsi_check,
    ema_cross_check, stochastic_oscillator_check, adx_check, ichimoku_check,
    volume_check, candlestick_check, obv_check, aroon_check,
    parabolic_sar_check, williams_r_check, tema_check, atr_check,
    keltner_channel_check, donchian_channel_check, rvi_check, momentum_check
)
# Configurer les logs
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Charger les modèles
rf_model = joblib.load('models/rf_model.pkl')
nn_model = load_model('models/nn_model.h5')

# Clés API Binance pour le Testnet
api_key = 'fvo67wee5dq10q00pajP2y9Rqz5Pwkdc01h2RY8m9OirvQ0oOPJhrFUW2QyKYfEJ'
api_secret = 'wvM9TmcVEG76GwNwFtPHZNx1z6W56h6VfFmUaqchkI3VpuPVbOcrxlDojXP1k29f'
client = Client(api_key, api_secret, testnet=True)

# Liste des symboles des crypto-monnaies
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'SHIBUSDT']

# Fonction pour récupérer les nouvelles données
def fetch_new_data(symbols):
    new_data = []
    for symbol in symbols:
        logging.info(f"Fetching data for {symbol}")
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 day ago UTC")
        if not klines:
            logging.warning(f"No data found for {symbol}")
            continue
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
        time.sleep(1)  # Pour éviter de surcharger l'API
    return pd.DataFrame(new_data)

# Fonction pour normaliser les données
def normalize_data(data):
    scaler = StandardScaler()
    return scaler.fit_transform(data)

# Fonction pour faire des prédictions
def make_predictions(data):
    X_new = data[['Open', 'High', 'Low', 'Close', 'Volume', 'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume']]
    X_new_scaled = normalize_data(X_new)
    rf_predictions = rf_model.predict(X_new_scaled)
    nn_predictions = nn_model.predict(X_new_scaled)
    data['RF_Predictions'] = rf_predictions
    data['NN_Predictions'] = nn_predictions
    logging.info("Predictions made using models")
    return data

# Fonction pour gérer les risques et calculer la quantité de trade
def calculate_trade_amount(capital, current_price):
    trade_amount = (capital * 0.02) / current_price
    logging.info(f"Calculated trade amount: {trade_amount}")
    return trade_amount

# Fonction pour vérifier les stratégies
def apply_strategies(data):
    signals = {}
    for strategy in [
        bollinger_check, ma_cross_check, macd_check, rsi_check,
        ema_cross_check, stochastic_oscillator_check, adx_check, ichimoku_check,
        volume_check, candlestick_check, obv_check, aroon_check,
        parabolic_sar_check, williams_r_check, tema_check, 
        keltner_channel_check, donchian_channel_check, rvi_check, momentum_check
    ]:
        signal = strategy(data.copy())  # Passer une copie des données à chaque stratégie
        signals[strategy.__name__] = signal
    return signals

# Fonction pour prendre des décisions de trading
def trade_decision(data, capital):
    for index, row in data.iterrows():
        trade_amount = calculate_trade_amount(capital, row['Close'])
        
        # Créez un DataFrame pour passer à la fonction check
        row_df = data.iloc[max(0, index-50):index+1]  # Prenez les 50 dernières lignes ou moins si moins de 50
        strategies_signals = apply_strategies(row_df)
        
        buy_signals = strategies_signals.count(True)
        sell_signals = strategies_signals.count(False)
        
        if row['NN_Predictions'] > row['Close'] and buy_signals >= 2:
            logging.info(f"Buy signal for {row['symbol']} at {row['Close']}")
            # Exécuter l'ordre d'achat
            try:
                order = client.order_market_buy(
                    symbol=row['symbol'],
                    quantity=trade_amount
                )
                logging.info(f"Buy order placed for {row['symbol']}: {order}")
            except Exception as e:
                logging.error(f"An error occurred while placing buy order: {e}")
            # Placer un ordre de vente limite
            sell_price = row['NN_Predictions']
            try:
                order = client.order_limit_sell(
                    symbol=row['symbol'],
                    quantity=trade_amount,
                    price=str(sell_price)
                )
                logging.info(f"Sell limit order placed for {row['symbol']} at {sell_price}: {order}")
            except Exception as e:
                logging.error(f"An error occurred while placing sell limit order: {e}")
        elif row['NN_Predictions'] < row['Close'] and sell_signals >= 2:
            logging.info(f"Sell signal for {row['symbol']} at {row['Close']}")
            # Exécuter l'ordre de vente
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
    capital = 20  # Capital disponible en USD
    new_data = fetch_new_data(symbols)
    if new_data.empty:
        logging.warning("No new data fetched.")
        return
    predictions = make_predictions(new_data)
    trade_decision(predictions, capital)
    predictions.to_csv('data/predictions.csv', index=False)
    logging.info("Predictions saved to data/predictions.csv")

if __name__ == "__main__":
    run_bot()