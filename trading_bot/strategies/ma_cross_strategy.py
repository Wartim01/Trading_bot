import pandas as pd
import ta

class MACrossStrategy:
    def __init__(self):
        self.data = pd.DataFrame()

    def add_indicators(self, data):
        data['ma50'] = ta.trend.SMAIndicator(data['close'], window=50).sma_indicator()
        data['ma200'] = ta.trend.SMAIndicator(data['close'], window=200).sma_indicator()
        return data

    def decide(self, market_data):
        self.data = self.data.append(market_data, ignore_index=True)
        if len(self.data) < 200:  # MA Cross requires at least 200 data points
            return "HOLD"

        self.data = self.add_indicators(self.data)
        latest_data = self.data.iloc[-1]

        if latest_data['ma50'] > latest_data['ma200']:
            return "BUY"
        elif latest_data['ma50'] < latest_data['ma200']:
            return "SELL"
        else:
            return "HOLD"
