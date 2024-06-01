import pandas as pd
import ta
import logging

class BollingerStrategy:
    def __init__(self):
        self.data = pd.DataFrame()

    def add_indicators(self, data):
        try:
            data['bollinger_mavg'] = ta.volatility.BollingerBands(data['close']).bollinger_mavg()
            data['bollinger_hband'] = ta.volatility.BollingerBands(data['close']).bollinger_hband()
            data['bollinger_lband'] = ta.volatility.BollingerBands(data['close']).bollinger_lband()
        except Exception as e:
            logging.error(f"Error adding indicators: {e}")
        return data

    def decide(self, market_data):
        self.data = pd.concat([self.data, market_data], ignore_index=True)
        if len(self.data) < 20:  # Bollinger Bands requires at least 20 data points
            return "HOLD"

        self.data = self.add_indicators(self.data)
        latest_data = self.data.iloc[-1]

        if latest_data['close'] < latest_data['bollinger_lband']:
            return "BUY"
        elif latest_data['close'] > latest_data['bollinger_hband']:
            return "SELL"
        else:
            return "HOLD"
