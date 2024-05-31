import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from binance.client import Client
from binance.exceptions import BinanceAPIException
import config
import time

client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)

def add_indicators(df):
    df['sma'] = df['close'].rolling(window=15).mean()
    df['macd'] = df['close'].ewm(span=12, adjust=False).mean() - df['close'].ewm(span=26, adjust=False).mean()
    df['rsi'] = 100 - (100 / (1 + df['close'].diff().apply(lambda x: x if x > 0 else 0).rolling(window=14).mean() / df['close'].diff().apply(lambda x: abs(x)).rolling(window=14).mean()))
    df['stochastic'] = (df['close'] - df['low'].rolling(window=14).min()) / (df['high'].rolling(window=14).max() - df['low'].rolling(window=14).min()) * 100
    df['bb_high'] = df['close'].rolling(window=20).mean() + (df['close'].rolling(window=20).std() * 2)
    df['bb_low'] = df['close'].rolling(window=20).mean() - (df['close'].rolling(window=20).std() * 2)
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    df['ichimoku_a'] = ((df['high'].rolling(window=9).max() + df['low'].rolling(window=9).min()) / 2).shift(26)
    df['ichimoku_b'] = ((df['high'].rolling(window=52).max() + df['low'].rolling(window=52).min()) / 2).shift(26)
    return df

def fetch_data(symbol, interval, start_str):
    try:
        klines = client.get_historical_klines(symbol, interval, start_str)
        data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)
        data = data.astype(float)
        return data
    except BinanceAPIException as e:
        print(f"Error fetching data from Binance: {e}")
        return None

def train_model(df):
    df = df.dropna()
    X = df[['sma', 'macd', 'rsi', 'stochastic', 'bb_high', 'bb_low', 'obv', 'ichimoku_a', 'ichimoku_b']]
    y = df['close']
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    joblib.dump(model, 'trading_model.pkl')

def backtest(df, model):
    df = df.dropna()
    X = df[['sma', 'macd', 'rsi', 'stochastic', 'bb_high', 'bb_low', 'obv', 'ichimoku_a', 'ichimoku_b']]
    df['predicted_close'] = model.predict(X)
    df['signal'] = np.where(df['predicted_close'] > df['close'], 1, -1)
    df['strategy_returns'] = df['signal'].shift(1) * df['close'].pct_change()
    profit = df['strategy_returns'].cumsum()[-1]
    return profit

def place_order_with_risk_management(symbol, quantity, price, order_type='buy', stop_loss_pct=0.02, take_profit_pct=0.05):
    try:
        if order_type == 'buy':
            order = client.order_limit_buy(
                symbol=symbol,
                quantity=quantity,
                price=str(price)
            )
            stop_loss_price = price * (1 - stop_loss_pct)
            take_profit_price = price * (1 + take_profit_pct)
        elif order_type == 'sell':
            order = client.order_limit_sell(
                symbol=symbol,
                quantity=quantity,
                price=str(price)
            )
            stop_loss_price = price * (1 + stop_loss_pct)
            take_profit_price = price * (1 - take_profit_pct)

        print(f"{order_type.capitalize()} order placed. Stop-loss at {stop_loss_price}, Take-profit at {take_profit_price}")
        return order
    except BinanceAPIException as e:
        print(f"Error placing {order_type} order: {e}")
        return None

def bollinger_bands_strategy(df, window=20, no_of_std=2):
    df['rolling_mean'] = df['close'].rolling(window).mean()
    df['rolling_std'] = df['close'].rolling(window).std()
    df['upper_band'] = df['rolling_mean'] + (df['rolling_std'] * no_of_std)
    df['lower_band'] = df['rolling_mean'] - (df['rolling_std'] * no_of_std)
    
    df['position'] = None
    df['position'] = np.where(df['close'] > df['upper_band'], -1, df['position'])
    df['position'] = np.where(df['close'] < df['lower_band'], 1, df['position'])
    
    df['position'].fillna(method='ffill', inplace=True)
    
    df['strategy_returns'] = df['position'].shift(1) * df['close'].pct_change()
    return df

def update_model_with_new_data(symbol, interval, start_str):
    df = fetch_data(symbol, interval, start_str)
    if df is not None:
        df_with_indicators = add_indicators(df)
        train_model(df_with_indicators)
        print("Model updated with new data.")
    else:
        print("Failed to fetch new data for updating model.")

def continuous_training(symbol, interval, start_str, update_interval):
    while True:
        update_model_with_new_data(symbol, interval, start_str)
        time.sleep(update_interval)

if __name__ == "__main__":
    symbol = 'BTCUSDT'
    interval = Client.KLINE_INTERVAL_1HOUR
    start_str = '1 Jan, 2021'
    update_interval = 86400  # Mise à jour quotidienne (en secondes)
    
    # Initial model training
    df = fetch_data(symbol, interval, start_str)
    if df is not None:
        df_with_indicators = add_indicators(df)
        train_model(df_with_indicators)
        model = joblib.load('trading_model.pkl')
        
        # Apply strategies and manage risk
        df_with_bollinger = bollinger_bands_strategy(df_with_indicators)
        for index, row in df_with_bollinger.iterrows():
            if row['position'] == 1:
                place_order_with_risk_management(symbol, quantity=0.001, price=row['close'], order_type='buy')
            elif row['position'] == -1:
                place_order_with_risk_management(symbol, quantity=0.001, price=row['close'], order_type='sell')

        # Continuous training loop
        continuous_training(symbol, interval, start_str, update_interval)
    else:
        print("Failed to fetch initial data.")
