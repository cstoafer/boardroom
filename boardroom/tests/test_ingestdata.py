import os
import unittest
import filecmp

from boardroom.ingestdata import ticker_to_cik, write_forms_index, get_forms_index
from boardroom.tests.utils import TEST_DIRECTORY, internet_on
import boardroom.config

class TestTickerToCik(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(boardroom.config.DATA_DIR):
            os.makedirs(boardroom.config.DATA_DIR)

    @unittest.skipIf(not internet_on(), "this test requires access to www.sec.gov")
    def test_basic_case_cache(self):
        ticker = 'KO'
        output = ticker_to_cik(ticker)
        expected = u'21344'
        self.assertEqual(output, expected)

    @unittest.skipIf(not internet_on(), "this test requires access to www.sec.gov")
    def test_basic_case_no_cache(self):
        ticker = 'KO'
        output = ticker_to_cik(ticker, use_cache=False)
        expected = u'21344'
        self.assertEqual(output, expected)

    def test_bad_input(self):
        self.assertRaises(TypeError, ticker_to_cik, 123)


class TestWriteFormsIndex(unittest.TestCase):
    def setUp(self):
        self.sample_formindex_path = os.path.join(TEST_DIRECTORY, 'data_tests/sample_formindex.txt')
        self.sample_formindex = open(self.sample_formindex_path, 'r')
        self.output_dir = os.path.join(TEST_DIRECTORY, 'tmp')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.output_path = os.path.join(self.output_dir, 'test.csv')
        self.output_path345 = os.path.join(self.output_dir, 'test345.csv')

    def tearDown(self):
        self.sample_formindex.close()
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        if os.path.exists(self.output_path345):
            os.remove(self.output_path345)

    def test_basic_case(self):
        self.sample_formindex.seek(0)
        write_forms_index(self.sample_formindex, self.output_path, form_types=['4'])
        self.assertTrue(os.path.exists(self.output_path))
        path_to_expected = os.path.join(TEST_DIRECTORY, 'data_tests/sample_formindex_output.csv')
        self.assertTrue(filecmp.cmp(self.output_path, path_to_expected))

    def test_multi_forms(self):
        self.sample_formindex.seek(0)
        write_forms_index(self.sample_formindex, self.output_path345, form_types=['3','4','5'])
        self.assertTrue(os.path.exists(self.output_path345))
        path_to_expected = os.path.join(TEST_DIRECTORY, 'data_tests/sample_formindex_output345.csv')
        self.assertTrue(filecmp.cmp(self.output_path345, path_to_expected))


class TestGetFormsIndex(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(TEST_DIRECTORY, 'tmp')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def tearDown(self):
        for f in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, f)
            if os.path.isfile(file_path):
                os.unlink(file_path)

    #@unittest.skipIf(not internet_on(), "this test requires access to ftp.sec.gov")
    @unittest.skip("skipping test because of large time requirement")
    def test_basic_case(self):
        years = [2015,2016]
        get_forms_index(years, self.output_dir)
        for year in years:
            testpath = os.path.join(self.output_dir, '{}.psv'.format(year))
            self.assertTrue(os.path.exists(testpath))
        path_to_output = os.path.join(self.output_dir, '2015.psv')
        # for some reason the test only passes if file and opened and closed
        with open(path_to_output, 'r') as f:
            print(sum(1 for line in f))
        path_to_expected = os.path.join(TEST_DIRECTORY, 'data_tests/2015.psv')
        with open(path_to_expected, 'r') as f:
            print(sum(1 for line in f))
        self.assertTrue(filecmp.cmp(path_to_output, path_to_expected))

    #@unittest.skipIf(not internet_on(), "this test requires access to ftp.sec.gov")
    @unittest.skip("skipping test because of large time requirement")
    def test_overwrite(self):
        years = [2014,2016]
        get_forms_index(years, self.output_dir, overwrite=True)
        for year in years:
            testpath = os.path.join(self.output_dir, '{}.psv'.format(year))
            self.assertTrue(os.path.exists(testpath))
        path_to_output = os.path.join(self.output_dir, '2014.psv')
        path_to_expected = os.path.join(TEST_DIRECTORY, 'data_tests/2014.psv')
        self.assertTrue(filecmp.cmp(path_to_output, path_to_expected))

