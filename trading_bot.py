import ccxt
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from ta.trend import SMAIndicator, MACD, IchimokuIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
import joblib
import schedule
import time
import logging

# Configuration
API_KEY = 'Cw6pBOG5Ct1GElMgwfD28PsVLKI9BW73STuVzEfJvIjSGIIPlNEB4TmDyBIWB4kT'
API_SECRET = 'i3H2TpMxndXmfDNIQf5oNA17fiy0x8QQhumIxwab1L6lMpGSt8QI7JaSZaFwkIog'
SYMBOL = 'BTC/USDT'
EXCHANGE = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})
RISK_MANAGEMENT = 0.02
INITIAL_BALANCE = 20
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fetch and prepare data
def fetch_data(symbol, timeframe='1h', limit=500):
    bars = EXCHANGE.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def add_indicators(df):
    df['sma'] = SMAIndicator(df['close'], window=20).sma_indicator()
    df['macd'] = MACD(df['close']).macd()
    df['rsi'] = RSIIndicator(df['close']).rsi()
    df['stochastic'] = StochasticOscillator(df['close']).stoch()
    bb = BollingerBands(df['close'])
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    df['obv'] = OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
    ichimoku = IchimokuIndicator(df['high'], df['low'])
    df['ichimoku_a'] = ichimoku.ichimoku_a()
    df['ichimoku_b'] = ichimoku.ichimoku_b()
    df.dropna(inplace=True)
    return df

# Train model
def train_model(df):
    X = df[['sma', 'macd', 'rsi', 'stochastic', 'bb_high', 'bb_low', 'obv', 'ichimoku_a', 'ichimoku_b']]
    y = np.where(df['close'].shift(-1) > df['close'], 1, 0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    joblib.dump(model, 'trading_model.pkl')
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logging.info(f"Model Accuracy: {accuracy}")

# Predict and trade
def predict_and_trade(df):
    model = joblib.load('trading_model.pkl')
    X = df[['sma', 'macd', 'rsi', 'stochastic', 'bb_high', 'bb_low', 'obv', 'ichimoku_a', 'ichimoku_b']].iloc[-1:].values
    prediction = model.predict(X)
    if prediction == 1:
        logging.info("Bullish signal detected. Preparing to buy.")
        potential_profit = df['close'].pct_change().iloc[-1]
        if potential_profit > 0.01:  # Example threshold for potential profit
            amount_to_invest = INITIAL_BALANCE * RISK_MANAGEMENT
            buy_price = df['close'].iloc[-1]
            logging.info(f"Buying at {buy_price}")
            # Simulate buy order
            # order = EXCHANGE.create_market_buy_order(SYMBOL, amount_to_invest)
            # Simulate sell condition
            sell_price = buy_price * (1 + potential_profit)  # Example sell logic
            logging.info(f"Selling at {sell_price}")
            # Simulate sell order
            # order = EXCHANGE.create_market_sell_order(SYMBOL, amount_to_invest)
    else:
        logging.info("No bullish signal detected.")

# Backtesting function
def backtest(df, model):
    initial_balance = INITIAL_BALANCE
    balance = initial_balance
    positions = []

    for i in range(1, len(df)):
        X = df[['sma', 'macd', 'rsi', 'stochastic', 'bb_high', 'bb_low', 'obv', 'ichimoku_a', 'ichimoku_b']].iloc[i-1:i].values
        prediction = model.predict(X)

        if prediction == 1 and not positions:
            buy_price = df['close'].iloc[i]
            positions.append(buy_price)
            logging.info(f"Backtest: Buying at {buy_price}")

        elif positions:
            current_price = df['close'].iloc[i]
            sell_price = positions[-1] * (1 + df['close'].pct_change().iloc[i])
            if current_price >= sell_price:
                balance += (current_price - positions[-1]) * (balance / positions[-1])
                positions = []
                logging.info(f"Backtest: Selling at {current_price}, Balance: {balance}")

    final_balance = balance
    profit = final_balance - initial_balance
    logging.info(f"Backtest Completed: Initial Balance: {initial_balance}, Final Balance: {final_balance}, Profit: {profit}")
    return profit

# Schedule tasks
def run_bot():
    df = fetch_data(SYMBOL)
    df = add_indicators(df)
    train_model(df)
    predict_and_trade(df)

schedule.every().hour.do(run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)
