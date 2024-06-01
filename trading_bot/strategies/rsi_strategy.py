import pandas as pd
import ta

class RSIStrategy:
    def __init__(self):
        self.data = pd.DataFrame()

    def add_indicators(self, data):
        data['rsi'] = ta.momentum.RSIIndicator(data['close']).rsi()
        return data

    def decide(self, market_data):
        self.data = self.data.append(market_data, ignore_index=True)
        if len(self.data) < 14:  # RSI requires at least 14 data points
            return "HOLD"

        self.data = self.add_indicators(self.data)
        latest_data = self.data.iloc[-1]

        if latest_data['rsi'] < 30:
            return "BUY"
        elif latest_data['rsi'] > 70:
            return "SELL"
        else:
            return "HOLD"
