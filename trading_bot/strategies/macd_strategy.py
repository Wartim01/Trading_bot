
# -*- coding: utf-8 -*-
import pandas as pd
import ta

def add_indicators(data):
    data['macd'] = ta.trend.macd(data['close'])
    data['macd_signal'] = ta.trend.macd_signal(data['close'])
    return data

def generate_signals(data):
    data['signal'] = 0
    data.loc[data['macd'] > data['macd_signal'], 'signal'] = 1
    data.loc[data['macd'] < data['macd_signal'], 'signal'] = -1
    return data
