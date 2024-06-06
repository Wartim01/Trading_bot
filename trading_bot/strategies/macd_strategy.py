import ta
import pandas as pd

def macd_strategy(data):
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < 26:  # Vérifiez si nous avons suffisamment de données
        return None

    macd = ta.trend.MACD(close=data['Close'], window_slow=26, window_fast=12, window_sign=9)
    data['macd'] = macd.macd()
    data['macd_signal'] = macd.macd_signal()

    print(f"MACD for {data['symbol'].iloc[-1]}: MACD={data['macd'].iloc[-1]}, Signal={data['macd_signal'].iloc[-1]}")

    if data['macd'].iloc[-1] > data['macd_signal'].iloc[-1] and data['macd'].iloc[-2] <= data['macd_signal'].iloc[-2]:
        return True
    elif data['macd'].iloc[-1] < data['macd_signal'].iloc[-1] and data['macd'].iloc[-2] >= data['macd_signal'].iloc[-2]:
        return False
    else:
        return None
