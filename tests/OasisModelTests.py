#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python unit tests for ::

    omdk.models.OasisModel
    omdk.models.OasisModelFactory
"""

import csv
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.pardir))

from models import (
    OasisModel,
    OasisModelFactory
)


class OasisModelTests(unittest.TestCase):

    def setUp(self):

        self.tests_datadir = os.path.join(os.getcwd(), 'data')
        self.model_version_file_path = os.path.join(self.tests_datadir, 'OasisPiWind', 'keys_data', 'PiWind', 'ModelVersion.csv')

        self.test_model_supplier_id = 'OasisLMF'
        self.test_model_id = 'PiWind'
        self.test_model_version_id = '0.0.0.1'

    
    def test_model_object_creation_with_no_resources(self):

        test_model = OasisModel(
            self.test_model_supplier_id,
            self.test_model_id,
            self.test_model_version_id
        )

        self.assertIsInstance(test_model, OasisModel)

        self.assertEquals(test_model.supplier_id, self.test_model_supplier_id)
        self.assertEquals(test_model.model_id, self.test_model_id)
        self.assertEquals(test_model.model_version_id, self.test_model_version_id)


    def test_model_object_creation_with_resources(self):

        resources = {'model_version_file_path': self.model_version_file_path}
        test_model = OasisModel(
            self.test_model_supplier_id,
            self.test_model_id,
            self.test_model_version_id,
            resources=resources
        )

        self.assertIsInstance(test_model, OasisModel)

        self.assertEquals(test_model.supplier_id, self.test_model_supplier_id)
        self.assertEquals(test_model.model_id, self.test_model_id)
        self.assertEquals(test_model.model_version_id, self.test_model_version_id)

        self.assertEquals(test_model.resources, resources)


    def test_model_object_creation_with_no_resources_via_factory(self):

        test_model = OasisModelFactory.create(
            model_supplier_id=self.test_model_supplier_id,
            model_id=self.test_model_id,
            model_version_id=self.test_model_version_id
        )

        self.assertIsInstance(test_model, OasisModel)

        self.assertEquals(test_model.supplier_id, self.test_model_supplier_id)
        self.assertEquals(test_model.model_id, self.test_model_id)
        self.assertEquals(test_model.model_version_id, self.test_model_version_id)


    def test_model_object_creation_with_resources_via_factory(self):

        resources = {'model_version_file_path': self.model_version_file_path}
        test_model = OasisModelFactory.create(
            model_supplier_id=self.test_model_supplier_id,
            model_id=self.test_model_id,
            model_version_id=self.test_model_version_id,
            resources=resources
        )

        self.assertIsInstance(test_model, OasisModel)

        self.assertEquals(test_model.supplier_id, self.test_model_supplier_id)
        self.assertEquals(test_model.model_id, self.test_model_id)
        self.assertEquals(test_model.model_version_id, self.test_model_version_id)

        self.assertEquals(test_model.resources, resources)


if __name__ == '__main__':
    unittest.main()