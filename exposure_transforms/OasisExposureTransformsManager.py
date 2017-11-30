#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisExposureTransformsManager'
]

import os
import subprocess
import sys

from interface import implements

from OasisExposureTransformsManagerInterface import OasisExposureTransformsManagerInterface
from OasisExposureTransformsFilesPipeline import OasisExposureTransformsFilesPipeline

if os.getcwd().split(os.path.sep)[-1] == 'exposure_transforms':
    sys.path.insert(0, os.path.abspath('../'))

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
                model.resources['transforms_files_pipeline'] = OasisExposureTransformsFilesPipeline()
                model_key = '{}-{}-{}'.format(model.supplier_id, model.model_id, model.model_version_id)
                self.manager['models'][model_key] = model


    @classmethod
    def create(cls, oasis_models=None):
        """
        Class method that returns an instance of an Oasis exposure transforms
        manager.
        """
        return cls(oasis_models=oasis_models)


    def transform_source_to_canonical(self, oasis_model, **kwargs):
        """
        Transforms the source exposures/locations file for a given
        ``oasis_model`` object to a canonical/standard Oasis format.

        All the required resources must be provided in the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.
        
        The transform is generic by default, but could be supplier specific if
        required.

        Returns a reference to the file object and also stores this in the
        transforms files pipeline in the model object resources dict.
        """
        validation_file_path = kwargs['validation_file_path']
        transformation_file_path = kwargs['transformation_file_path']
        source_exposures_file_path = kwargs['source_exposures_file_path']
        canonical_exposures_file_path = kwargs['canonical_exposures_file_path']



    def transform_canonical_to_model(self, oasis_model, **kwargs):
        """
        Transforms the canonical exposures/locations file for a given
        ``oasis_model`` object to a format understood by Oasis keys lookup
        services.

        All the required resources must be provided in the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.

        Returns a reference to the file object and also stores this in the
        transforms files pipeline in the model object resources dict.
         """
        pass



    def transform_model_to_oasis_keys(self, oasis_model, **kwargs):
        """
        Transforms the model exposures/locations file for a given
        ``oasis_model`` object to the Oasis keys CSV file format:

            ``LocID,PerilID,CoverageID,AreaPerilID,VulnerabilityID``


        All the required resources must be provided in the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.

        A "standard" implementation should use the lookup service factory
        class in ``oasis_utils`` (a submodule of `omdk`) namely
        
            ``oasis_utils.oasis_keys_lookup_service_utils.KeysLookupServiceFactory``

        Returns a reference to the file object and also stores this in the
        transforms files pipeline in the model object resources dict.
        """
        pass

        model_exposures_file_path = os.path.abspath(kwargs['model_exposures_file_path'])
        lookup_service = kwargs['lookup_service']
        output_file_path = os.path.abspath(kwargs['output_file_path'])

        oasis_keys_file, _ = self.manager['klsf'].save_lookup_records(
            lookup_service=lookup_service,
            model_exposures_file_path=model_exposures_file_path,
            output_file_path=output_file_path,
            format='oasis_keys'
        )

        oasis_model.resources['transforms_files_pipeline'].model_exposures_file = oasis_keys_file
        return oasis_keys_file


    def load_canonical_profile(self, oasis_model, **kwargs):
        """
        Loads a JSON file representing the canonical exposures profile for a
        given ``oasis_model``.

        All the required resources must be provided in the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.

        Returns the profile as a dict, and also stores this in the transforms
        files pipeline in the model object resources dict.

        """
        pass


    def generate_oasis_files(self, oasis_model, **kwargs):
        """
        For a given ``oasis_model`` generates the standard Oasis files, namely

            ``items.csv``
            ``coverages.csv``
            ``gulsummaryxref.csv``

        All the required resources must be provided in the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.

        In addition to generating the files it also stores these in the
        transforms files pipeline in the model object resources dict.
        """
        pass
