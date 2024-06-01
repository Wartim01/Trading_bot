import pandas as pd
import ta
import logging

class MACDStrategy:
    def __init__(self):
        self.data = pd.DataFrame()

    def add_indicators(self, data):
        try:
            data['macd'] = ta.trend.MACD(data['close']).macd()
            data['signal'] = ta.trend.MACD(data['close']).macd_signal()
        except Exception as e:
            logging.error(f"Error adding indicators: {e}")
        return data

    def decide(self, market_data):
        self.data = pd.concat([self.data, market_data], ignore_index=True)
        if len(self.data) < 26:  # MACD requires at least 26 data points
            return "HOLD"

        self.data = self.add_indicators(self.data)
        latest_data = self.data.iloc[-1]

        if latest_data['macd'] > latest_data['signal']:
            return "BUY"
        elif latest_data['macd'] < latest_data['signal']:
            return "SELL"
        else:
            return "HOLD"
