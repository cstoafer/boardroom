import os
import unittest
import json

from boardroom.parse_secform import (get_xml, _get_single_xml_element, _get_single_xml_value,
                                     _xpath_to_value_mapping, get_trade_holdings_dict, get_transaction_dict,
                                     get_owner_dict, get_issuer_dict, get_issuer_dict_from_xmltree, get_owner_dict_from_xmltree,
                                     get_nonderivative_info_dict_from_xmltree, get_form_dict)
from boardroom.tests.utils import TEST_DIRECTORY, internet_on

class TestGetFormDict(unittest.TestCase):
    @unittest.skipIf(not internet_on(), "this test requires access to www.sec.gov")
    def setUp(self):
        form4_dict_path = os.path.join(TEST_DIRECTORY, 'data_tests', 'form4_dict.json')
        with open(form4_dict_path, 'r') as f:
            self.form4_dict = json.load(f)

    def test_basic_case_form4(self):
        form_loc = 'edgar/data/1551138/0001144204-16-074214.txt'
        output, _ = get_form_dict(form_loc)
        self.assertEqual(output, self.form4_dict)

