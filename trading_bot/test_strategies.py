import unittest
import pandas as pd
from strategies.macd_strategy import MACDStrategy

class TestMACDStrategy(unittest.TestCase):

    def setUp(self):
        self.strategy = MACDStrategy()
        self.market_data = pd.DataFrame({
            'close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                      11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                      21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
        })

    def test_add_indicators(self):
        data_with_indicators = self.strategy.add_indicators(self.market_data.copy())
        self.assertIn('macd', data_with_indicators.columns)
        self.assertIn('signal', data_with_indicators.columns)

    def test_decide(self):
        decision = self.strategy.decide(self.market_data)
        self.assertIn(decision, ["BUY", "SELL", "HOLD"])

if __name__ == '__main__':
    unittest.main()

import unittest
import pandas as pd
from strategies.bollinger_strategy import BollingerStrategy

class TestBollingerStrategy(unittest.TestCase):

    def setUp(self):
        self.strategy = BollingerStrategy()
        self.market_data = pd.DataFrame({
            'close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                      11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                      21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
        })

    def test_add_indicators(self):
        data_with_indicators = self.strategy.add_indicators(self.market_data.copy())
        self.assertIn('bollinger_mavg', data_with_indicators.columns)
        self.assertIn('bollinger_hband', data_with_indicators.columns)
        self.assertIn('bollinger_lband', data_with_indicators.columns)

    def test_decide(self):
        decision = self.strategy.decide(self.market_data)
        self.assertIn(decision, ["BUY", "SELL", "HOLD"])

if __name__ == '__main__':
    unittest.main()
