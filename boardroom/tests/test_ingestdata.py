import os
import unittest

from boardroom.ingestdata import ticker_to_cik, write_forms_index, get_forms_index
from boardroom.tests.utils import TEST_DIRECTORY

class TestTickerToCik(unittest.TestCase):
    def test_basic_case_cache(self):
        ticker = 'KO'
        output = ticker_to_cik(ticker)
        expected = u'0000021344'
        self.assertEqual(output, expected)

    def test_basic_case_no_cache(self):
        ticker = 'KO'
        output = ticker_to_cik(ticker, use_cache=False)
        expected = u'0000021344'
        self.assertEqual(output, expected)

    def test_bad_input(self):
        self.assertRaises(TypeError, ticker_to_cik, 123)


class TestWriteFormsIndex(unittest.TestCase):
    def setUp(self):
        self.sample_formindex_path = os.path.join(TEST_DIRECTORY, 'data_tests/sample_formindex.txt')
        self.sample_formindex = open(self.sample_formindex_path, 'rb')
        self.output_dir = os.path.join(TEST_DIRECTORY, 'tmp')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.output_path = os.path.join(self.output_dir, 'test.csv')

    def tearDown(self):
        self.sample_formindex.close()
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_basic_case(self):
        write_forms_index(self.sample_formindex, self.output_path)
        self.assertTrue(os.path.exists(self.output_path))


class TestGetFormsIndex(unittest.TestCase):
    def setUp(self):
        self.sample_formindex_path = os.path.join(TEST_DIRECTORY, 'data_tests/sample_formindex.txt')
        self.sample_formindex = open(self.sample_formindex_path, 'rb')
        self.output_dir = os.path.join(TEST_DIRECTORY, 'tmp')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.output_path = os.path.join(self.output_dir, 'test.csv')

    def tearDown(self):
        for f in os.listdir(self.output_path):
            file_path = os.path.join(self.output_path, f)
            if os.path.isfile(file_path):
                os.unlink(file_path)
