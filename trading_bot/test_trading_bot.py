import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
from unittest.mock import patch
from utils import get_market_data, execute_trade

class TestUtils(unittest.TestCase):
    @patch('utils.requests.get')
    def test_get_market_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'price': 100, 'trend': 'up'}
        
        market_data = get_market_data()
        self.assertIsNotNone(market_data)
        self.assertEqual(market_data['price'], 100)
        self.assertEqual(market_data['trend'], 'up')

    @patch('utils.requests.post')
    def test_execute_trade(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'success'}
        
        response = execute_trade('BUY', {'price': 100})
        self.assertIsNotNone(response)
        self.assertEqual(response['status'], 'success')

if __name__ == '__main__':
    unittest.main()
