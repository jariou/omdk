# -*- coding: utf-8 -*-

"""
Python unit tests for ::

    omdk.keys.OasisKeysLookupFactory
"""

import csv
import io
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.abspath(os.pardir))

from keys import OasisKeysLookupFactory as oklf


class OasisModelTests(unittest.TestCase):

    def setUp(self):

        self.tests_datadir = os.path.join(os.getcwd(), 'data')

    
    def test_get_model_info(self):

        test_model_info = {
            'supplier_id': 'OasisLMF',
            'model_id': 'PiWind',
            'model_version_id': '0.0.0.1'
        }
        model_version_file_path = os.path.join(self.tests_datadir, 'OasisPiWind', 'keys_data', 'PiWind', 'ModelVersion.csv')
        factory_test_model_info = oklf.get_model_info(model_version_file_path)

        self.assertEquals(test_model_info, factory_test_model_info)


    def test_get_lookup_package(self):

        lookup_package_path = os.path.join(self.tests_datadir, 'OasisPiWind', 'src', 'keys_server')

        test_lookup_package = oklf.get_lookup_package(lookup_package_path)

        self.assertIsInstance(test_lookup_package, types.ModuleType)

        self.assertEquals(test_lookup_package.__path__[0], lookup_package_path)

        self.assertIn('OasisBaseKeysLookup', dir(test_lookup_package))
        self.assertIn('PiWind', dir(test_lookup_package))
        self.assertIn('PiWindKeysLookup', dir(test_lookup_package))
        self.assertIn('AreaPerilLookup', dir(test_lookup_package))
        self.assertIn('VulnerabilityLookup', dir(test_lookup_package))


    def test_get_lookup_class_instance(self):

        lookup_package_path = os.path.join(self.tests_datadir, 'OasisPiWind', 'src', 'keys_server')

        lookup_package = oklf.get_lookup_package(lookup_package_path)

        keys_data_path = os.path.join(self.tests_datadir, 'OasisPiWind', 'keys_data', 'PiWind')

        model_info = {
            'supplier_id': 'OasisLMF',
            'model_id': 'PiWind',
            'model_version_id': '0.0.0.1'
        }

        test_lookup_class_instance = oklf.get_lookup_class_instance(lookup_package, keys_data_path, model_info)

        self.assertIsInstance(test_lookup_class_instance, types.ObjectType)

        oasis_base_keys_lookup_class_methods = [
            '_get_area_peril_id',
            '_get_area_peril_ids',
            '_get_location_record',
            '_get_vulnerability_id',
            '_get_vulnerability_ids',
            'process_locations'
        ]

        for method in oasis_base_keys_lookup_class_methods:
            self.assertIn(method, dir(test_lookup_class_instance))


if __name__ == '__main__':
    unittest.main()