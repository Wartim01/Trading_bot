
# -*- coding: utf-8 -*-
import pandas as pd
import ta

def add_indicators(data):
    bollinger = ta.volatility.BollingerBands(data['close'])
    data['bollinger_hband'] = bollinger.bollinger_hband()
    data['bollinger_lband'] = bollinger.bollinger_lband()
    return data

def generate_signals(data):
    data['signal'] = 0
    data.loc[data['close'] < data['bollinger_lband'], 'signal'] = 1
    data.loc[data['close'] > data['bollinger_hband'], 'signal'] = -1
    return data
