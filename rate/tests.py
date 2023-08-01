from decimal import Decimal
import unittest
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from rate.views import _parse_amount_string, _validate_currency


class ParseAmountStringTestCase(unittest.TestCase):
    def test_parse_amount_string_valid(self):
        amount_str = '$1,234.56'
        amount_decimal = _parse_amount_string(amount_str, 'USD')
        self.assertEqual(amount_decimal, Decimal('1234.56'))

        amount_str = '¥789.01'
        amount_decimal = _parse_amount_string(amount_str, 'JPY')
        self.assertEqual(amount_decimal, Decimal('789.01'))

        amount_str = '$1,234'
        amount_decimal = _parse_amount_string(amount_str, 'TWD')
        self.assertEqual(amount_decimal, Decimal('1234'))

    def test_parse_amount_string_invalid(self):
        amount_str = '¥100'
        with self.assertRaises(ValueError):
            _parse_amount_string(amount_str, 'USD')

        amount_str = '1234.56'
        with self.assertRaises(ValueError):
            _parse_amount_string(amount_str, 'USD')

        amount_str = '1,2,3,4.56'
        with self.assertRaises(ValueError):
            _parse_amount_string(amount_str, 'USD')

        amount_str = '$1,555.55.55'
        with self.assertRaises(ValueError):
            _parse_amount_string(amount_str, 'USD')


# Define a mock CUR_MAP for testing
MOCK_CUR_MAP = {
    'JPY': {
        'JPY': Decimal('1'),
        'USD': Decimal('0.0222'),
    },
    'USD': {
        'JPY': Decimal('11.1111'),
        'USD': Decimal('1'),
    }
}


class ValidateCurrencyTestCase(unittest.TestCase):
    @patch('rate.views._CUR_MAP', new=MOCK_CUR_MAP)
    def test_validate_currency_valid(self):
        source = 'JPY'
        target = 'USD'
        self.assertIsNone(_validate_currency(source, target))

    @patch('rate.views._CUR_MAP', new=MOCK_CUR_MAP)
    def test_validate_currency_invalid_source_currency(self):
        source = 'TWD'
        target = 'USD'
        with self.assertRaises(ValueError):
            _validate_currency(source, target)

    @patch('rate.views._CUR_MAP', new=MOCK_CUR_MAP)
    def test_validate_currency_invalid_target_currency(self):
        source = 'USD'
        target = 'CNY'
        with self.assertRaises(ValueError):
            _validate_currency(source, target)


class RateExchangeAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('rate.views._CUR_MAP', new=MOCK_CUR_MAP)
    def test_get_rate_exchange_api_valid(self):
        url = reverse('get_rate_exchange_api')
        data = {
            'source': 'USD',
            'target': 'JPY',
            'amount': '$1,234.56',
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['msg'], 'success')
        self.assertEqual(data['amount'], '¥13,717.32')

    @patch('rate.views._CUR_MAP', new=MOCK_CUR_MAP)
    def test_get_rate_exchange_api_invalid_currency(self):
        url = reverse('get_rate_exchange_api')
        data = {
            'source': 'EUR',
            'target': 'USD',
            'amount': '$100',
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.data
        self.assertEqual(data['msg'], 'error')
        self.assertEqual(data['message'], 'The source currency is not supported')

    @patch('rate.views._CUR_MAP', new=MOCK_CUR_MAP)
    def test_get_rate_exchange_api_invalid_amount(self):
        url = reverse('get_rate_exchange_api')
        data = {
            'source': 'JPY',
            'target': 'USD',
            'amount': 'abc',
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.data
        self.assertEqual(data['msg'], 'error')
        self.assertEqual(data['message'], 'Invalid amount format')

    @patch('rate.views._CUR_MAP', new=MOCK_CUR_MAP)
    def test_get_rate_exchange_api_invalid_currency_symbol(self):
        url = reverse('get_rate_exchange_api')
        data = {
            'source': 'USD',
            'target': 'JPY',
            'amount': '¥100',
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.data
        self.assertEqual(data['msg'], 'error')
        self.assertEqual(data['message'], 'Currency symbol is not match source currency')
