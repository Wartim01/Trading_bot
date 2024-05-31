import unittest
import pandas as pd
import numpy as np
from trading_bot import add_indicators, train_model, fetch_data, backtest

class TestTradingBot(unittest.TestCase):

    def setUp(self):
        data = {
            'timestamp': pd.date_range(start='1/1/2022', periods=500, freq='H'),
            'open': np.random.random(500) * 100,
            'high': np.random.random(500) * 100,
            'low': np.random.random(500) * 100,
            'close': np.random.random(500) * 100,
            'volume': np.random.random(500) * 1000
        }
        self.df = pd.DataFrame(data)

    def test_add_indicators(self):
        df_with_indicators = add_indicators(self.df)
        self.assertTrue('sma' in df_with_indicators.columns)
        self.assertTrue('macd' in df_with_indicators.columns)
        self.assertTrue('rsi' in df_with_indicators.columns)
        self.assertTrue('stochastic' in df_with_indicators.columns)
        self.assertTrue('bb_high' in df_with_indicators.columns)
        self.assertTrue('bb_low' in df_with_indicators.columns)
        self.assertTrue('obv' in df_with_indicators.columns)
        self.assertTrue('ichimoku_a' in df_with_indicators.columns)
        self.assertTrue('ichimoku_b' in df_with_indicators.columns)

    def test_train_model(self):
        df_with_indicators = add_indicators(self.df)
        train_model(df_with_indicators)
        model = joblib.load('trading_model.pkl')
        self.assertIsNotNone(model)

    def test_fetch_data(self):
        df = fetch_data('BTC/USDT')
        self.assertTrue(len(df) > 0)

    def test_backtest(self):
        df_with_indicators = add_indicators(self.df)
        train_model(df_with_indicators)
        model = joblib.load('trading_model.pkl')
        profit = backtest(df_with_indicators, model)
        self.assertIsInstance(profit, float)

if __name__ == '__main__':
    unittest.main()
