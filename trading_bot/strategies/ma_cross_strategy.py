
# -*- coding: utf-8 -*-
import pandas as pd
import ta

def add_indicators(data):
    data['ma50'] = ta.trend.sma_indicator(data['close'], window=50)
    data['ma200'] = ta.trend.sma_indicator(data['close'], window=200)
    return data

def generate_signals(data):
    data['signal'] = 0
    data.loc[data['ma50'] > data['ma200'], 'signal'] = 1
    data.loc[data['ma50'] < data['ma200'], 'signal'] = -1
    return data
