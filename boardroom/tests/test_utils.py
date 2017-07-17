import os
import unittest
import json

from boardroom import utils
from boardroom.tests.utils import TEST_DIRECTORY

class TestCacheDict(unittest.TestCase):
    def setUp(self):
        self.tmpsavefile = os.path.join(TEST_DIRECTORY, 'savetest.json')
        if os.path.exists(self.tmpsavefile):
            os.remove(self.tmpsavefile)
        self.tmploadfile = os.path.join(TEST_DIRECTORY, 'loadtest.json')
        if os.path.exists(self.tmploadfile):
            os.remove(self.tmploadfile)
        self.testdict = {'a': 1, 'b': 2, 'c': 3}
        with open(self.tmploadfile, 'w') as f:
            json.dump(self.testdict, f)

    def tearDown(self):
        if os.path.exists(self.tmpsavefile):
            os.remove(self.tmpsavefile)
        if os.path.exists(self.tmploadfile):
            os.remove(self.tmploadfile)

    def test_load_cache_dict(self):
        loaddict = utils.load_cache_dict('loadtest.json', TEST_DIRECTORY)
        self.assertEqual(loaddict, self.testdict)

    def test_save_cache_dict(self):
        utils.save_cache_dict(self.testdict, 'savetest.json', TEST_DIRECTORY)
        self.assertTrue(os.path.exists(self.tmpsavefile))

    def test_load_no_file(self):
        loaddict = utils.load_cache_dict('not_a_file', TEST_DIRECTORY)
        self.assertEqual(loaddict, dict())


class TestSilentremove(unittest.TestCase):
    def setUp(self):
        self.tmpfile = os.path.join(TEST_DIRECTORY, 'testremove.csv')
        wfile = open(self.tmpfile, 'w')
        wfile.close()

    def tearDown(self):
        if os.path.exists(self.tmpfile):
            os.remove(self.tmpfile)

    def test_basic_case(self):
        self.assertTrue(os.path.exists(self.tmpfile))
        utils.silentremove(self.tmpfile)
        self.assertFalse(os.path.exists(self.tmpfile))

