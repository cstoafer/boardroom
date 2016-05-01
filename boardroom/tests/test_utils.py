import os
import unittest

from boardroom import utils
from boardroom.tests.utils import TEST_DIRECTORY

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

