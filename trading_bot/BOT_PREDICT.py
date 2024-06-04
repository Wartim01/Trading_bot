import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
from binance.client import Client
import numpy as np
import time
from trading_bot.strategies.bollinger_strategy import check as bollinger_check
from trading_bot.strategies.ma_cross_strategy import check as ma_cross_check
from trading_bot.strategies.macd_strategy import check as macd_check
from trading_bot.strategies.rsi_strategy import check as rsi_check

# Charger les modèles
rf_model = joblib.load('models/rf_model.pkl')
nn_model = load_model('models/nn_model.h5')

# Clés API Binance
API_KEY = 'Cw6pBOG5Ct1GElMgwfD28PsVLKI9BW73STuVzEfJvIjSGIIPlNEB4TmDyBIWB4kT'
API_SECRET = 'i3H2TpMxndXmfDNIQf5oNA17fiy0x8QQhumIxwab1L6lMpGSt8QI7JaSZaFwkIog'
client = Client(API_KEY, API_SECRET)

# Liste des symboles des crypto-monnaies
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'SHIBUSDT']

# Fonction pour récupérer les nouvelles données
def fetch_new_data(symbols):
    new_data = []
    for symbol in symbols:
        print(f"Fetching data for {symbol}")
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 day ago UTC")
        if not klines:
            print(f"No data found for {symbol}")
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
    return data

# Fonction pour gérer les risques et calculer la quantité de trade
def calculate_trade_amount(capital, current_price):
    trade_amount = (capital * 0.02) / current_price
    return trade_amount

# Fonction pour vérifier les stratégies
def apply_strategies(data):
    bollinger_signal = bollinger_check(data)
    ma_cross_signal = ma_cross_check(data)
    macd_signal = macd_check(data)
    rsi_signal = rsi_check(data)
    return [bollinger_signal, ma_cross_signal, macd_signal, rsi_signal]

# Fonction pour prendre des décisions de trading
def trade_decision(data, capital):
    for index, row in data.iterrows():
        trade_amount = calculate_trade_amount(capital, row['Close'])
        strategies_signals = apply_strategies(row)
        buy_signals = strategies_signals.count(True)
        sell_signals = strategies_signals.count(False)
        
        if row['NN_Predictions'] > row['Close'] and buy_signals >= 2:
            print(f"Buy signal for {row['symbol']} at {row['Close']}")
            # Exécuter l'ordre d'achat
            try:
                order = client.order_market_buy(
                    symbol=row['symbol'],
                    quantity=trade_amount
                )
                print(f"Buy order placed for {row['symbol']}: {order}")
            except Exception as e:
                print(f"An error occurred: {e}")
            # Placer un ordre de vente limite
            sell_price = row['NN_Predictions']
            try:
                order = client.order_limit_sell(
                    symbol=row['symbol'],
                    quantity=trade_amount,
                    price=str(sell_price)
                )
                print(f"Sell limit order placed for {row['symbol']} at {sell_price}: {order}")
            except Exception as e:
                print(f"An error occurred: {e}")
        elif row['NN_Predictions'] < row['Close'] and sell_signals >= 2:
            print(f"Sell signal for {row['symbol']} at {row['Close']}")
            # Exécuter l'ordre de vente
            try:
                order = client.order_market_sell(
                    symbol=row['symbol'],
                    quantity=trade_amount
                )
                print(f"Sell order placed for {row['symbol']}: {order}")
            except Exception as e:
                print(f"An error occurred: {e}")

# Exécution du bot de trading
def run_bot():
    capital = 20  # Capital disponible en USD
    new_data = fetch_new_data(symbols)
    if new_data.empty:
        print("No new data fetched.")
        return
    predictions = make_predictions(new_data)
    trade_decision(predictions, capital)
    predictions.to_csv('data/predictions.csv', index=False)
    print("Predictions saved to data/predictions.csv")

if __name__ == "__main__":
    run_bot()
