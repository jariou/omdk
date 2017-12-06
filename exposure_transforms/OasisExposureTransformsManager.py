#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisExposureTransformsManager'
]

import io
import os
import subprocess
import sys

from interface import implements

from OasisExposureTransformsManagerInterface import OasisExposureTransformsManagerInterface
from OasisExposureTransformsFilesPipeline import OasisExposureTransformsFilesPipeline

if os.getcwd().split(os.path.sep)[-1] == 'exposure_transforms':
    sys.path.insert(0, os.path.abspath('../'))

from oasis_utils import (
    KeysLookupServiceFactory as klsf,
    OasisException,
    run_mono_script,
)


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
                if 'transforms_files_pipeline' in model.resources:
                    if not model.resources['transforms_files_pipeline']:
                        model.resources['transforms_files_pipeline'] = OasisExposureTransformsFilesPipeline.create()
                else:
                    model.resources['transforms_files_pipeline'] = OasisExposureTransformsFilesPipeline.create()
                
                self.manager['models'][model.key] = model


    @classmethod
    def create(cls, oasis_models=None, **kwargs):
        """
        Class method that returns an instance of an Oasis exposure transforms
        manager. The optional ``oasis_models`` argument should be a list of
        Oasis model objects (``omdk.OasisModel.OasisModel``), and any
        additional resources can be specified in ``kwargs``.
        """
        return cls(oasis_models=oasis_models)


    def clear_files_pipeline(self, oasis_model, **kwargs):
        """
        Clears the exposure transforms files pipeline for the given
        ``oasis_model`` optionally using additional arguments in the ``kwargs``
        dict.
        """
        oasis_model.resources['transforms_files_pipeline'] = OasisExposureTransformsFilesPipeline.create()
        self.manager['models'][oasis_model.key] = oasis_model


    def start_files_pipeline(self, oasis_model, **kwargs):
        """
        Starts the exposure transforms pipeline for the given ``oasis_model``,
        i.e. the generation of the canonical exposures files, keys file
        and finally the Oasis files.
        """
        pass


    def save_files_pipeline(self, oasis_model, **kwargs):
        """
        Saves the files in the given ``oasis_model``'s transforms files
        pipeline to a given data store, e.g. local filesystem, database etc.
        """
        pass


    def transform_source_to_canonical(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Transforms the source exposures/locations file for a given
        ``oasis_model`` object to a canonical/standard Oasis format.

        By default it is assumed that all the resources required for the
        transformation are present in the model object's resources dict, 
        specifically its transforms files pipeline  - this is indicated by the
        optional ``with_model_resources`` variable which is ``True`` by
        default. In this case the generated file is stored in the appropriate
        attribute of the model object's transforms files pipeline, the
        manager's model dict is updated, and the model object returned.

        If not then ``with_model_resources`` should be set to ``False``, in
        which case all the resources required for the transformation should be
        present in the optional ``kwargs`` dict as named arguments. In this
        case only the generated canonical file is returned.
        """
        if not with_model_resources:
            xtrans_path = kwargs['xtrans_path']
            source_exposures_file_path = kwargs['source_exposures_file_path']
            source_exposures_validation_file_path = kwargs['source_exposures_validation_file_path']
            source_to_canonical_exposures_transformation_file_path = kwargs['source_to_canonical_exposures_transformation_file_path']
            canonical_exposures_file_path = kwargs['canonical_exposures_file_path']
        else:
            xtrans_path = oasis_model.resources['xtrans_path']
            source_exposures_file_path = oasis_model.resources['transforms_files_pipeline'].source_exposures_file.name
            source_exposures_validation_file_path = oasis_model.resources['transforms_files_pipeline'].source_exposures_validation_file.name
            source_to_canonical_exposures_transformation_file_path = oasis_model.resources['transforms_files_pipeline'].source_to_canonical_exposures_transformation_file.name
            canonical_exposures_file_path = oasis_model.resources['transforms_files_pipeline'].canonical_exposures_file.name

        xtrans_args = {
            'd': source_exposures_validation_file_path,
            'c': source_exposures_file_path,
            't': source_to_canonical_exposures_transformation_file_path,
            'o': canonical_exposures_file_path
        }

        try:
            run_mono_script(xtrans_path, xtrans_args)
        except OasisException as e:
            raise e

        with io.open(canonical_exposures_file_path, 'r', encoding='utf-8') as f:
            if not with_model_resources:
                return f

            oasis_model.resources['transforms_files_pipeline'].canonical_exposures_file = f
            self.manager['models'][oasis_model.key] = oasis_model
            return oasis_model


    def transform_canonical_to_model(self, oasis_model, **kwargs):
        """
        Transforms the canonical exposures/locations file for a given
        ``oasis_model`` object to a format understood by Oasis keys lookup
        services.

        By default it is assumed that all the resources required for the
        transformation are present in the model object's resources dict, 
        specifically its transforms files pipeline  - this is indicated by the
        optional ``with_model_resources`` variable which is ``True`` by
        default. In this case the generated file is stored in the appropriate
        attribute of the model object's transforms files pipeline, the
        manager's model dict is updated, and the model object returned.

        If not then ``with_model_resources`` should be set to ``False``, in
        which case all the resources required for the transformation should be
        present in the optional ``kwargs`` dict as named arguments. In this
        case only the generated canonical file is returned.
        """
        if not with_model_resources:
            xtrans_path = kwargs['xtrans_path']
            canonical_exposures_file_path = kwargs['canonical_exposures_file_path']
            canonical_exposures_validation_file_path = kwargs['canonical_exposures_validation_file_path']
            canonical_to_model_exposures_transformation_file_path = kwargs['canonical_to_model_exposures_transformation_file_path']
            model_exposures_file_path = kwargs['model_exposures_file_path']
        else:
            xtrans_path = oasis_model.resources['xtrans_path']
            canonical_exposures_file_path = oasis_model.resources['transforms_files_pipeline'].canonical_exposures_file.name
            canonical_exposures_validation_file_path = oasis_model.resources['transforms_files_pipeline'].canonical_exposures_validation_file.name
            canonical_to_model_exposures_transformation_file_path = oasis_model.resources['transforms_files_pipeline'].canonical_to_model_exposures_transformation_file.name
            model_exposures_file_path = oasis_model.resources['transforms_files_pipeline'].model_exposures_file.name

        xtrans_args = {
            'd': canonical_exposures_validation_file_path,
            'c': canonical_exposures_file_path,
            't': canonical_to_model_exposures_transformation_file_path,
            'o': model_exposures_file_path
        }

        try:
            run_mono_script(xtrans_path, xtrans_args)
        except OasisException as e:
            raise e

        with io.open(model_exposures_file_path, 'r', encoding='utf-8') as f:
            if not with_model_resources:
                return f

            oasis_model.resources['transforms_files_pipeline'].model_exposures_file = f
            self.manager['models'][oasis_model.key] = oasis_model
            return oasis_model


    def transform_model_to_oasis_keys(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Transforms the model exposures/locations file for a given
        ``oasis_model`` object to the Oasis keys CSV file format:

            ``LocID,PerilID,CoverageID,AreaPerilID,VulnerabilityID``

        By default it is assumed that all the resources required for the
        transformation are present in the model object's resources dict, 
        specifically its transforms files pipeline  - this is indicated by the
        optional ``with_model_resources`` variable which is ``True`` by
        default. In this case the generated file is stored in the appropriate
        attribute of the model object's transforms files pipeline, the
        manager's model dict is updated, and the model object returned.

        If not then ``with_model_resources`` should be set to ``False``, in
        which case all the resources required for the transformation should be
        present in the optional ``kwargs`` dict as named arguments. In this
        case only the generated canonical file is returned.
        """
        if not with_model_resources:
            model_exposures_file_path = kwargs['model_exposures_file_path']
            lookup_service = kwargs['lookup_service']
            keys_file_path = kwargs['keys_file_path']
        else:
            model_exposures_file_path = oasis_model.resources['transforms_files_pipeline'].model_exposures_file.name
            lookup_service = oasis_model.resources['lookup_service']
            keys_file_path = oasis_model.resources['transforms_files_pipeline'].keys_file.name

        oasis_keys_file, _ = self.manager['klsf'].save_lookup_records(
            lookup_service=lookup_service,
            model_exposures_file_path=model_exposures_file_path,
            output_file_path=keys_file_path,
            format='oasis_keys'
        )

        if not with_model_resources:
            return oasis_keys_file

        oasis_model.resources['transforms_files_pipeline'].oasis_keys_file = oasis_keys_file
        self.manager['models'][oasis_model.key] = oasis_model

        return oasis_model


    def load_canonical_profile(self, oasis_model, **kwargs):
        """
        Loads a JSON file representing the canonical exposures profile for a
        given ``oasis_model``.

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

        In addition to generating the files it also stores these in the
        transforms files pipeline in the model object resources dict.
        """
        pass
