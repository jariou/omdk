#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisExposureTransformsManager'
]

from interface import implements

from OasisExposureTransformsManagerInterface import OasisExposureTransformsManagerInterface
from OasisTransformsFilesPipeline import OasisTransformsFilesPipeline

from oasis_utils.oasis_keys_lookup_service_utils import KeysLookupServiceFactory as klsf


class OasisExposureTransformsManager(implements(OasisExposureTransformsManagerInterface)):

    def __init__(self, oasis_models=None):
        """
        Class constructor - not generally to be used directly.
        """
        self.manager = {}
        self.manager['klsf'] = klsf()
        self.manager['models'] = {}
        if oasis_models:
            for model in oasis_models:
                model.resources['transforms_files_pipeline'] = OasisTransformsFilesPipeline()


    @classmethod
    def create(cls):
        """
        Class method that returns an instance of an Oasis exposure transforms
        manager.
        """
        return cls()


    def transform_source_to_canonical(self, oasis_model, *args, **kwargs):
        """
        Transforms the source exposures/locations file for a given
        ``oasis_model`` object, with the path given in the object ``resources``
        dict, optionally using additional resources specified in ``args``
        and/or ``kwargs``.

        It is up to the specific implementation of this class of how to use
        these resources to effect the transformation.
        
        The transform is generic by default, but could be supplier specific if
        required.

        Returns a reference to the file object and also stores this in the
        model object resources dict.
        """
        pass


    def transform_canonical_to_model(self, oasis_model, *args, **kwargs):
        """
        Transforms the canonical exposures/locations file for a given
        ``oasis_model``, object, with the path given in the object
        ``resources`` dict, and in the format expected by an Oasis keys lookup
        service, optionally using additional resources specified in ``args``
        and/or ``kwargs``.

        Returns a reference to the file object and also stores this in the
        model object resources dict.
         """
        pass


    def transform_model_to_oasis_keys(self, oasis_model, *args, **kwargs):
        """
        Transforms the model exposures/locations file for a given
        ``oasis_model``,  object, with the path given in the object
        ``resources`` dict, to an Oasis keys CSV file, as used to generate the
        Oasis files, using the lookup service factory class in ``oasis_utils``,
        namely
        
            ``oasis_utils.oasis_keys_lookup_service_utils.KeysLookupServiceFactory``


        optionally using additional resources specified in ``args`` and/or
        ``kwargs``.

        Returns a reference to the file object and also stores this in the
        model object resources dict.
        """
        pass


    def load_canonical_profile(self, oasis_model, *args,  **kwargs):
        """
        Loads a JSON file representing the canonical exposures profile for a
        given ``oasis_model``, optionally using any additional resources
        specified in the `args` and ``kwargs` arguments.

        Returns the profile as a dict, and also stores this in the
        model object resources dict.

        """
        pass


    def generate_oasis_files(self, oasis_model, *args, **kwargs):
        """
        For a given ``oasis_model`` generates the standard Oasis files, namely

            ``items.csv``
            ``coverages.csv``
            ``gulsummaryxref.csv``

        optionally using any additional resources specified in the `args` and
        ``kwargs` arguments.

        In addition to generating the files it also stores these in the model
        object resources dict.
        """
        pass
