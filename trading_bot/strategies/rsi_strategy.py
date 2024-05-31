# -*- coding: utf-8 -*-
import pandas as pd
import ta

def add_indicators(data):
    data['rsi'] = ta.momentum.rsi(data['close'], window=14)
    data['ma50'] = ta.trend.sma_indicator(data['close'], window=50)
    data['ma200'] = ta.trend.sma_indicator(data['close'], window=200)
    data['macd'] = ta.trend.macd(data['close'])
    return data

def generate_signals(data):
    data['signal'] = 0
    data.loc[data['rsi'] < 30, 'signal'] = 1
    data.loc[data['rsi'] > 70, 'signal'] = -1
    return data


# -*- coding: utf-8 -*-
import pandas as pd
import ta

def add_indicators(data):
    data['rsi'] = ta.momentum.rsi(data['close'], window=14)
    data['ma50'] = ta.trend.sma_indicator(data['close'], window=50)
    data['ma200'] = ta.trend.sma_indicator(data['close'], window=200)
    data['macd'] = ta.trend.macd(data['close'])
    return data

def generate_signals(data):
    data['signal'] = 0
    data.loc[data['rsi'] < 30, 'signal'] = 1
    data.loc[data['rsi'] > 70, 'signal'] = -1
    return data
