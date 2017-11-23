#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisExposureTransformsManager'
]

from interface import implements

from OasisExposureTransformsManagerInterface import OasisExposureTransformsManagerInterface

from oasis_utils.oasis_keys_lookup_service_utils import KeysLookupServiceFactory as klsf


class OasisExposureTransformsManager(implements(OasisExposureTransformsManagerInterface)):

    def __init__(self):
        """
        Class constructor - not generally to be used directly.
        """
        self.manager = {}
        self.klsf = klsf


    @classmethod
    def create(cls):
        """
        Class method that returns an instance of an Oasis exposure transforms
        manager.
        """
        return cls()


    def transform_source_to_canonical(self, source_exposures_file_path):
        """
        Transforms the source exposures/locations file specified in the given
        path to a canonical exposures/locations file expected in the Oasis
        pipeline.

        Returns a reference to the file object and also updates a storage dict
        to store the file as an attribute.
        """
        pass


    def transform_model_to_oasis_keys(
        self,
        model_keys_data_file_path,
        model_version_file_path,
        model_git_repo_path
    ):
        """
        Transforms the model exposures/locations file specified in the given
        path to an Oasis keys file, as used to generate the Oasis files, using
        the lookup service factory class in ``oasis_utils``, namely
        
            ``oasis_utils.oasis_keys_lookup_service_utils.KeysLookupServiceFactory``

        Returns a reference to the file object and also updates a storage dict
        to store the file as an attribute.
        """
        model_info = self.klsf.get_model_info(model_version_file_path)
        # update object manager dict

        klc = self.klsf.create(
            model_keys_data_path=model_keys_data_path,
            model_version_file_path=model_version_file_path,
            model_git_repo_path=model_git_repo_path
        )

        # more stuff

