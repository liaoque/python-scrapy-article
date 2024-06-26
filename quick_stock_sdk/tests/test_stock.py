import unittest
from quick_stock import get_stock_price, get_stock_info
from unittest.mock import patch

class TestQuickStock(unittest.TestCase):

    @patch('quick_stock.stock.requests.get')
    def test_get_stock_price(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {'price': 150.0}

        price = get_stock_price('AAPL')
        self.assertEqual(price, 150.0)

    @patch('quick_stock.stock.requests.get')
    def test_get_stock_info(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'symbol': 'AAPL',
            'companyName': 'Apple Inc.',
            'exchange': 'NASDAQ',
            'industry': 'Technology'
        }

        info = get_stock_info('AAPL')
        self.assertEqual(info['symbol'], 'AAPL')
        self.assertEqual(info['companyName'], 'Apple Inc.')
        self.assertEqual(info['exchange'], 'NASDAQ')
        self.assertEqual(info['industry'], 'Technology')

    @patch('quick_stock.stock.requests.get')
    def test_get_stock_price_failure(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 404

        with self.assertRaises(Exception) as context:
            get_stock_price('INVALID')

        self.assertTrue('无法获取股票价格' in str(context.exception))

    @patch('quick_stock.stock.requests.get')
    def test_get_stock_info_failure(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 404

        with self.assertRaises(Exception) as context:
            get_stock_info('INVALID')

        self.assertTrue('无法获取股票信息' in str(context.exception))

if __name__ == '__main__':
    unittest.main()
