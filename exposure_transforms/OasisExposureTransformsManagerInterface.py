#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisExposureTransformsManagerInterface'
]

from interface import Interface


class OasisExposureTransformsManagerInterface(Interface):
    """
    An interface for defining the service methods of an Oasis exposure
    transforms manager.
    """


    @classmethod
    def create(cls):
        """
        Class method that returns an instance of an Oasis exposure transforms
        manager.
        """
        pass


    def transform_source_to_canonical(self, source_exposures_file_path, supplier_id=None):
        """
        Transforms the source exposures/locations file specified in the given
        path to a canonical exposures/locations file. The transform is generic
        by default, but could be supplier specific if required.

        Returns a reference to the file object and also updates a storage dict
        to store the file as an attribute.
        """
        pass


    def transform_canonical_to_model(self, supplier_id, model_id, canonical_exposures_file_path):
        """
        Transforms the canonical exposures/locations file specified in the
        given path to a model exposures file, as expected by an Oasis keys
        lookup service.

        Returns a reference to the file object and also updates a storage dict
        to store the file as an attribute.
         """
        pass


    def transform_model_to_oasis_keys(self, supplier_id, model_id, model_exposures_file_path):
        """
        Transforms the model exposures/locations file specified in the given
        path to an Oasis keys file, as used to generate the Oasis files, using
        the lookup service factory class in ``oasis_utils``, namely
        
            ``oasis_utils.oasis_keys_lookup_service_utils.KeysLookupServiceFactory``

        Returns a reference to the file object and also updates a storage dict
        to store the file as an attribute.
        """
        pass


    def load_canonical_profile(self, canonical_exposures_profile):
        """
        Loads a JSON file representing the canonical exposures profile
        for a given supplier, which is indicated in the profile itself.

        Returns the profile as a dict, and also stores it as an attribute.
        """
        pass


    def generate_oasis_files(self, supplier_id, model_id, files=None):
        """
        Generates the standard Oasis files, namely

            ``items.csv``
            ``coverages.csv``
            ``GulSummaryXref.csv``

        The argument ``files`` can be used to specify a list of specific Oasis
        file types to generate; by default this is ``None`` so that all the 
        standard files will be generated.
        """
        pass
