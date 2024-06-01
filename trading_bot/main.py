# main.py
import sys
import os
import time
import importlib
import logging
import ccxt
import pandas as pd
from data.fetch_data import fetch_historical_data
from config.settings import API_KEY, API_SECRET, SYMBOL, TIMEFRAME, INITIAL_CAPITAL, STRATEGY
from models.model import train_model, load_model
from strategies import Strategy
from utils import get_market_data, execute_trade  # Utiliser l'import de utils.py

logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})

def run_bot(symbol, amount, strategy_module, timeframe='1h', mode='live'):
    strategy = importlib.import_module(f'strategies.{strategy_module}')
    model = None
    if mode == 'train':
        logging.info("Training mode activated")
        data = fetch_historical_data(symbol, timeframe, '2024-01-01T00:00:00Z', '2024-01-07T00:00:00Z')
        if data.empty:
            logging.error("No data fetched for training")
            return
        data = strategy.add_indicators(data)
        model = train_model(data)
        if model is None:
            logging.error("Model training failed")
            return
    elif mode == 'live':
        logging.info("Live mode activated")
        model = load_model()
        if model is None:
            logging.error("Model not loaded")
            return
        while True:
            data = fetch_historical_data(symbol, timeframe)
            if data.empty:
                logging.warning("No new data fetched")
                time.sleep(3600)
                continue
            data = strategy.add_indicators(data)
            if data.empty or 'rsi' not in data.columns or 'ma50' not in data.columns or 'ma200' not in data.columns or 'macd' not in data.columns:
                logging.warning("Indicators not properly added")
                time.sleep(3600)
                continue
            latest_signal = model.predict(data[['open', 'high', 'low', 'close', 'volume', 'rsi', 'ma50', 'ma200', 'macd']].tail(1))
            execute_trade(latest_signal[-1], symbol, amount)
            time.sleep(3600)

if __name__ == "__main__":
    strategy_module = f"{STRATEGY}_strategy"
    mode = 'train'  # Change to 'live' to run the bot live
    run_bot(SYMBOL, INITIAL_CAPITAL, strategy_module, mode=mode)
