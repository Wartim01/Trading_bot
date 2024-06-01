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
from utils import get_market_data, execute_trade

logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})

def get_strategy_instance(strategy_module):
    try:
        strategy = importlib.import_module(f'strategies.{strategy_module}')
        return strategy.Strategy()
    except ImportError as e:
        logging.error(f"Error importing strategy module: {e}")
        return None

def process_market_data(strategy_instance, market_data, symbol, amount):
    decision = strategy_instance.decide(market_data)
    if decision == "BUY":
        execute_trade("BUY", market_data)
    elif decision == "SELL":
        execute_trade("SELL", market_data)
    logging.info(f"Executed {decision} at {market_data['close'].iloc[-1]}")

def run_bot(symbol, amount, strategy_module, timeframe='1h', mode='live'):
    strategy_instance = get_strategy_instance(strategy_module)
    if not strategy_instance:
        return

    while True:
        market_data = get_market_data(symbol, timeframe)
        if market_data is None or market_data.empty:
            logging.warning("No new data fetched")
            time.sleep(3600)
            continue

        process_market_data(strategy_instance, market_data, symbol, amount)
        time.sleep(3600)

if __name__ == "__main__":
    strategy_module = f"{STRATEGY}_strategy"
    run_bot(SYMBOL, INITIAL_CAPITAL, strategy_module, timeframe=TIMEFRAME, mode='live')
