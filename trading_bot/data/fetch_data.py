# -*- coding: utf-8 -*-
import ccxt
import pandas as pd
from trading_bot.config.settings import API_KEY, API_SECRET, EXCHANGE

exchange = ccxt.binance({'apiKey': API_KEY, 'secret': API_SECRET})

def fetch_historical_data(symbol, timeframe, start_date, end_date):
    since = exchange.parse8601(start_date)
    end = exchange.parse8601(end_date)
    all_ohlcv = []
    while since < end:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since)
            if not ohlcv:
                break
            since = ohlcv[-1][0] + 1
            all_ohlcv += ohlcv
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            break
    data = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    return data
