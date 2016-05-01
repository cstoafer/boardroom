import os
import unittest

from boardroom import ingestdata
from boardroom.tests.utils import TEST_DIRECTORY

class TestTickerToCik(unittest.TestCase):
    def test_basic_case_cache(self):
        ticker = 'KO'
        output = ingestdata.ticker_to_cik(ticker)
        expected = u'0000021344'
        self.assertEqual(output, expected)

    def test_basic_case_no_cache(self):
        ticker = 'KO'
        output = ingestdata.ticker_to_cik(ticker, use_cache=False)
        expected = u'0000021344'
        self.assertEqual(output, expected)

