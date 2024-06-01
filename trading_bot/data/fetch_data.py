# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import API_KEY, API_SECRET, EXCHANGE

import ccxt
import pandas as pd

def fetch_historical_data(symbol, timeframe, start_date, end_date):
    exchange = getattr(ccxt, EXCHANGE)({
        'apiKey': API_KEY,
        'secret': API_SECRET,
    })
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=exchange.parse8601(start_date), limit=1000)
    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data
