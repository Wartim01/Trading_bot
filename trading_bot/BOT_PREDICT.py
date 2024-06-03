import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
from binance.client import Client
import numpy as np
import time

# Charger les modèles
rf_model = joblib.load('models/rf_model.pkl')
nn_model = load_model('models/nn_model.h5')

# Clés API Binance
api_key = 'YOUR_BINANCE_API_KEY'
api_secret = 'YOUR_BINANCE_API_SECRET'
client = Client(api_key, api_secret)

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

# Fonction pour prendre des décisions de trading
def trade_decision(data, capital):
    for index, row in data.iterrows():
        trade_amount = calculate_trade_amount(capital, row['Close'])
        if row['NN_Predictions'] > row['Close']:
            print(f"Buy signal for {row['symbol']} at {row['Close']}")
            # Execute buy order (exemple)
            # client.order_market_buy(symbol=row['symbol'], quantity=trade_amount)
            # Set limit sell order
            sell_price = row['NN_Predictions']
            # client.order_limit_sell(symbol=row['symbol'], quantity=trade_amount, price=sell_price)
        else:
            print(f"Sell signal for {row['symbol']} at {row['Close']}")
            # Execute sell order (exemple)
            # client.order_market_sell(symbol=row['symbol'], quantity=trade_amount)

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
