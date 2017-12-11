#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Oasis exposures manager - manages the exposure management workflow for multiple
models, from loading the source exposures and canonical exposures profiles to
generating the intermediate files (canonical exposures files, model exposures
files, keys files) and finally generating the Oasis files from these.
"""

__all__ = [
    'OasisExposuresManager'
]

import io
import json
import os
import pandas as pd
import shutil
import subprocess
import sys

from datetime import datetime

from interface import implements

from OasisExposuresManagerInterface import OasisExposuresManagerInterface
from OasisFilesPipeline import OasisFilesPipeline

if os.getcwd().split(os.path.sep)[-1] == 'exposures':
    sys.path.insert(0, os.path.abspath(os.pardir))

from oasis_utils import (
    KeysLookupServiceFactory as klsf,
    OasisException,
    run_mono_executable,
)

__author__ = "Sandeep Murthy"
__copyright__ = "Oasis Loss Modelling Framework 2017"


class OasisExposuresManager(implements(OasisExposuresManagerInterface)):


    def __init__(self, oasis_models=None):
        """
        Class constructor - not generally to be used directly, instead called
        by the service method ``create``.

        Args:
            ``oasis_models`` (``list``): a list of Oasis model objects (``omdk.OasisModel.OasisModel``)
            with resources provided in the model objects' resources dictionaries.
        """
        self._keys_lookup_service_factory = klsf()
        
        self._models = {}
        
        if oasis_models:
            for model in oasis_models:
                model.resources['oasis_files_pipeline'] = OasisFilesPipeline.create(model_key=model.key)

                if 'output_basedirpath' in model.resources:
                    output_basedirpath = os.path.abspath(model.resources['output_basedirpath'])
                    if not os.path.exists(output_basedirpath):
                        raise OasisException(
                            'Output base directory {} for {} specified in resources dict but '
                            'path does not exist on the filesystem!'.format(output_basedirpath, model)
                        )
                else:
                    output_basedirpath = os.path.join(
                        os.getcwd(),
                        'Files'
                    )
                    if not os.path.exists(output_basedirpath):
                        os.mkdir(output_basedirpath)

                output_dirpath = os.path.join(
                    output_basedirpath,
                    model.key.replace('/', '-')
                )
                if not os.path.exists(output_dirpath):
                    os.mkdir(output_dirpath)
                model.resources['output_basedirpath'] = output_basedirpath
                model.resources['output_dirpath'] = output_dirpath

                if 'source_exposures_file_path' in model.resources:
                    with io.open(model.resources['source_exposures_file_path'], 'r', encoding='utf-8') as f:
                        model.resources['oasis_files_pipeline'].source_exposures_file = f

                if (
                    'canonical_exposures_profile_json' in model.resources or
                    'canonical_exposures_profile_json_path' in model.resources
                ):
                    model = self.load_canonical_profile(model)
                
                self._models[model.key] = model


    @classmethod
    def create(cls, oasis_models=None):
        """
        Service method that returns an Oasis exposures manager.

        Args:
            ``oasis_models`` (``list``): a list of Oasis model objects (``omdk.OasisModel.OasisModel``)
            with resources provided in the model objects' resources dictionaries.

        Returns:
            ``omdk.exposures.OasisExposuresManager.OasisExposuresManager``: an instance of 
            an Oasis exposures manager class
        """
        return cls(oasis_models=oasis_models)


    @property
    def keys_lookup_service_factory(self):
        """
        Keys lookup service factory property - getter only.

            :getter: Gets the current keys lookup service factory instance
        """
        return self._keys_lookup_service_factory


    @property
    def models(self, key=None):
        """
        Model objects dictionary property.

            :getter: Gets the model in the models dict using the optional
                     ``key`` argument. If ``key`` is not given then the dict
                     is returned.

            :setter: Sets the value of the optional ``key`` in the models dict
                     to ``val`` where ``val`` is assumed to be an Oasis model
                     object (``omdk.OasisModel.OasisModel``).

                     If no ``key`` is given then ``val`` is assumed to be a new
                     models dict and is used to replace the existing dict.

            :deleter: Deletes the value of the optional ``key`` in the models
                      dict. If no ``key`` is given then the entire existing
                      dict is cleared.
        """
        return self._models[key] if key else self._models


    @models.setter
    def models(self, key=None, val=None):
        if key:
            model = val
            if 'oasis_files_pipeline' not in model.resources:
                model.resources['oasis_files_pipeline'] = OasisFilesPipeline.create()
                self._models[key] = model
        else:
            self._models.clear()
            self._models.update(val)


    @models.deleter
    def models(self, key=None):
        if key:
            del self._models[key]
        else:
            self._models.clear()


    def clear_files_pipeline(self, oasis_model, **kwargs):
        """
        Clears the oasis files pipeline for the given Oasis model object.

        Args:
            ``oasis_model`` (``omdk.models.OasisModel.OasisModel``): The model object.
            
            ``**kwargs`` (arbitary keyword arguments):

        Returns:
            ``oasis_model`` (``omdk.models.OasisModel.OasisModel``): The model object with its
            Oasis files pipeline cleared.
        """
        oasis_model.resources['oasis_files_pipeline'] = OasisFilesPipeline.create()
        self.models[oasis_model.key] = oasis_model

        return oasis_model


    def start_files_pipeline(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Starts the oasis files pipeline for the given Oasis model object,
        which is the generation of the Oasis items, coverages and GUL summary
        files from the source exposures file, canonical exposures profile,
        and associated validation files and transformation files for the
        source and intermediate files (canonical exposures, model exposures).

        Args:
            ``oasis_model`` (``omdk.models.OasisModel.OasisModel``): The model object.

            ``with_model_resources``: (``bool``): Indicates whether to look for
            resources in the model object's resources dictionary or in ``**kwargs``.

            ``**kwargs`` (arbitrary keyword arguments): If ``with_model_resources``
            is ``False`` then the filesystem paths (including filename and extension)
            of the canonical exposures file, the model exposures
        """
        try:
            if not with_model_resources:
                output_dirpath = kwargs['output_dirpath'] if 'output_dirpath' in kwargs else None
                if not output_dirpath:
                    raise OasisException(
                        "No output directory provided for {} in '**kwargs'.".format(oasis_model)
                    )
                elif not os.path.exists(output_dirpath):
                    raise OasisException(
                        "Output directory {} for {} provided in '**kwargs' "
                        "does not exist on the filesystem.".format(output_dirpath, oasis_model)
                    )

                source_exposures_file_path = kwargs['source_exposures_file_path']

                if not source_exposures_file_path:
                    raise OasisException("No source exposures file path provided for {} in '**kwargs'.".format(oasis_model))
                elif not os.path.exists(source_exposures_file_path):
                    raise OasisException("Source exposures file path {} provided for {} in '**kwargs' is invalid.".format(source_exposures_file_path, oasis_model))

                source_exposures_file_name = source_exposures_file_path.split(os.path.sep)[-1]
                target_file_path = os.path.join(output_dirpath, source_exposures_file_name)
                if not os.path.exists(target_file_path):
                    shutil.copy(source_exposures_file_path, target_file_path)

                kwargs['source_exposures_file_path'] = target_file_path
                        
                utcnow = oasis_utils.get_utctimestamp(fmt='%Y%m%d%H%M%S')

                target_file_path = os.path.join(output_dirpath, 'canexp-{}.csv'.format(utcnow))
                kwargs['canonical_exposures_file_path'] = target_file_path
                canonical_exposures_file = self.transform(oasis_model, with_model_resources=False, transform_type='source_to_canonical', **kwargs)
                
                target_file_path = os.path.join(output_dirpath, 'modexp-{}.csv'.format(utcnow))
                kwargs['model_exposures_file_path'] = target_file_path
                model_exposures_file = self.transform(oasis_model, with_model_resources=False, transform_type='canonical_to_model', **kwargs)

                target_file_path = os.path.join(output_dirpath, 'oasiskeys-{}.csv'.format(utcnow))
                kwargs['keys_file_path'] = target_file_path
                keys_file = self.get_keys(oasis_model, with_model_resources=False, **kwargs)
                
                canonical_exposures_profile_json_path = kwargs['canonical_exposures_profile_json_path']

                if not canonical_exposures_profile_json_path:
                    raise OasisException("No canonical exposures profile JSON file path provided for {} in '**kwargs'.".format(oasis_model))
                elif not os.path.exists(canonical_exposures_profile_json_path):
                    raise OasisException("Canonical exposures profile JSON file path {} provided for {} in '**kwargs' is invalid.".format(canonical_exposures_profile_json_path, oasis_model))
                
                canonical_exposures_profile_json_file_name = canonical_exposures_profile_json_path.split(os.path.sep)[-1]
                target_file_path = os.path.join(output_dirpath, canonical_exposures_profile_json_file_name)
                if not os.path.exists(target_file_path):
                    shutil.copy(canonical_exposures_profile_json_path, target_file_path)

                kwargs['canonical_exposures_profile_json_path'] = target_file_path
                canonical_exposures_profile = self.load_canonical_profile(oasis_model, with_model_resources=False, **kwargs)
                kwargs['canonical_exposures_profile'] = canonical_exposures_profile

                items_file, coverages_file, gulsummaryxref_file = self.generate_oasis_files(
                    oasis_model, with_model_resources=False, **kwargs
                )

                return items_file, coverages_file, gulsummaryxref_file
            else:
                omr = oasis_model.resources
                tfp = omr['oasis_files_pipeline']

                output_dirpath = omr['output_dirpath'] if 'output_dirpath' in omr else None
                if not output_dirpath:
                    raise OasisException(
                        "No output directory provided for {} in resources dict.".format(oasis_model)
                    )
                elif not os.path.exists(output_dirpath):
                    raise OasisException(
                        "Output directory {} for {} provided in resources dict "
                        "does not exist on the filesystem.".format(output_dirpath, oasis_model)
                    )

                source_exposures_file = tfp.source_exposures_file if tfp.source_exposures_file else None

                if not source_exposures_file:
                    raise OasisException("No source exposures file in the Oasis files pipeline for {}.".format(oasis_model))
                elif not os.path.exists(source_exposures_file.name):
                    raise OasisException("Source exposures file path {} provided for {} is invalid.".format(source_exposures_file.name, oasis_model))

                self.transform(oasis_model, transform_type='source_to_canonical')
                
                self.transform(oasis_model, transform_type='canonical_to_source')

                self.get_keys(oasis_model)
                
                if not oasis_model.resources['canonical_exposures_profile']:
                    self.load_canonical_profile(oasis_model)

                self.generate_oasis_files(oasis_model)
        except OasisException as e:
            raise e

        return oasis_model


    def save_files_pipeline(self, oasis_model, **kwargs):
        """
        Saves the files in the given ``oasis_model``'s oasis files
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
        attribute of the model object's oasis files pipeline, which is in
        turn a key in the manager's models dict. The models dict is updated,
        and the model object returned.

        If not then ``with_model_resources`` should be set to ``False``, in
        which case all the resources required for the transformation should be
        present in the optional ``kwargs`` dict as named arguments. In this
        case only the generated canonical exposures file is returned.
        """
        omr = oasis_model.resources
        tfp = omr['oasis_files_pipeline']

        if not with_model_resources:
            xtrans_path = kwargs['xtrans_path']
            input_file_path = kwargs['source_exposures_file_path']
            validation_file_path = kwargs['source_exposures_validation_file_path']
            transformation_file_path = kwargs['source_to_canonical_exposures_transformation_file_path']
            output_file_path = kwargs['canonical_exposures_file_path']
        else:
            xtrans_path = omr['xtrans_path']
            input_file_path = tfp.source_exposures_file.name
            validation_file_path = omr['source_exposures_validation_file_path']
            transformation_file_path = omr['source_to_canonical_exposures_transformation_file_path']
            output_file_path = tfp.canonical_exposures_file.name

        (
            xtrans_path,
            input_file_path,
            validation_file_path,
            transformation_file_path,
            output_file_path
        ) = map(
                os.path.abspath,
                [
                    xtrans_path,
                    input_file_path,
                    validation_file_path,
                    transformation_file_path,
                    output_file_path
                ]
        )        

        xtrans_args = {
            'd': validation_file_path,
            'c': input_file_path,
            't': transformation_file_path,
            'o': output_file_path
        }

        try:
            run_mono_executable(xtrans_path, xtrans_args)
        except OasisException as e:
            raise e

        with io.open(output_file_path, 'r', encoding='utf-8') as f:
            if not with_model_resources:
                return f

            tfp.canonical_exposures_file = f
            self.models[oasis_model.key] = oasis_model
            return oasis_model


    def transform_canonical_to_model(self, oasis_model, with_model_resources=True, **kwargs):
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
        omr = oasis_model.resources
        tfp = omr['oasis_files_pipeline']

        if not with_model_resources:
            xtrans_path = kwargs['xtrans_path']
            input_file_path = kwargs['canonical_exposures_file_path']
            validation_file_path = kwargs['canonical_exposures_validation_file_path']
            transformation_file_path = kwargs['canonical_to_model_exposures_transformation_file_path']
            output_file_path = kwargs['model_exposures_file_path']
        else:
            xtrans_path = omr['xtrans_path'] if 'xtrans_path' in omr else None
            input_file_path = tfp.canonical_exposures_file.name
            validation_file_path = omr['canonical_exposures_validation_file_path']
            transformation_file_path = omr['canonical_to_model_exposures_transformation_file_path']
            output_file_path = tfp.model_exposures_file.name

        (
            xtrans_path,
            input_file_path,
            validation_file_path,
            transformation_file_path,
            output_file_path
        ) = map(
            os.path.abspath,
            [
                xtrans_path,
                input_file_path,
                validation_file_path,
                transformation_file_path,
                output_file_path
            ]
        )

        xtrans_args = {
            'd': validation_file_path,
            'c': input_file_path,
            't': transformation_file_path,
            'o': output_file_path
        }

        try:
            run_mono_executable(xtrans_path, xtrans_args)
        except OasisException as e:
            raise e

        with io.open(output_file_path, 'r', encoding='utf-8') as f:
            if not with_model_resources:
                return f

            tfp.model_exposures_file = f
            self.models[oasis_model.key] = oasis_model
            return oasis_model


    def transform(oasis_model, with_model_resources=True, transform_type=None, **kwargs):
        """
        A parent method for the individual methods which implement the

            source exposures -> canonical exposures
            canonical exposures -> model exposures
        
        transformations. If the transform_type is `source_to_canonical` then
        the ``transform_source_to_canonical`` is called, or else if the
        transform type is `canonical_to_model` then the
        ``transform_canonical_to_model`` method is called.
        """
        if transform_type == 'source_to_canonical':
            return transform_source_to_canonical(oasis_model, with_model_resources, kwargs)
        elif transform_type == 'canonical_to_model':
            return transform_canonical_to_model(oasis_model, with_model_resources, kwargs)


    def get_keys(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Generates the model exposures/locations file for a given
        ``oasis_model`` object to the Oasis keys CSV file format:

            ``LocID,PerilID,CoverageID,AreaPerilID,VulnerabilityID``

        using the lookup service defined for this model.

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
        omr = oasis_model.resources
        tfp = omr['oasis_files_pipeline']        

        if not with_model_resources:
            model_exposures = kwargs['model_exposures'] if 'model_exposures' in kwargs else None
            model_exposures_file_path = kwargs['model_exposures_file_path'] if 'model_exposures_file_path' in kwargs else None
            lookup_service = kwargs['lookup_service']
            keys_file_path = kwargs['keys_file_path']
        else:
            model_exposures = omr['model_exposures']  if 'model_exposures' in kwargs else None
            model_exposures_file_path = tfp.model_exposures_file.name if tfp.model_exposures_file else None
            lookup_service = omr['lookup_service']
            keys_file_path = tfp.keys_file.name

        (
            model_exposures_file_path,
            keys_file_path
        ) = map(os.path.abspath, [model_exposures_file_path, keys_file_path])

        oasis_keys_file, _ = self.keys_lookup_service_factory.save_keys(
            lookup_service=lookup_service,
            model_exposures=model_exposures,
            model_exposures_file_path=model_exposures_file_path,
            output_file_path=keys_file_path,
            format='oasis_keys'
        )

        if not with_model_resources:
            return oasis_keys_file

        tfp.oasis_keys_file = oasis_keys_file
        self.models[oasis_model.key] = oasis_model

        return oasis_model


    def load_canonical_profile(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Loads a JSON string or JSON file representation of the canonical
        exposures profile for a given ``oasis_model``, stores this in the
        model object's resources dict, and returns the object.
        """
        omr = oasis_model.resources
        tfp = omr['oasis_files_pipeline']

        canonical_exposures_profile = None

        if not with_model_resources:
            canonical_exposures_profile_json = kwargs['canonical_exposures_profile_json'] if 'canonical_exposures_profile_json' in kwargs else None
            canonical_exposures_profile_json_path = kwargs['canonical_exposures_profile_json_path'] if 'canonical_exposures_profile_json_path' in kwargs else None
        else:
            canonical_exposures_profile_json = omr['canonical_exposures_profile_json'] if 'canonical_exposures_profile_json' in omr else None
            canonical_exposures_profile_json_path = omr['canonical_exposures_profile_json_path'] if 'canonical_exposures_profile_json_path' in omr else None
        
        if canonical_exposures_profile_json:
            try:
                canonical_exposures_profile = json.loads(canonical_exposures_profile_json)
            except ValueError:
                raise OasisException("Canonical exposures profile JSON is invalid for {}.".format(str(oasis_model)))
        elif canonical_exposures_profile_json_path:
            try:
                with io.open(canonical_exposures_profile_json_path, 'r', encoding='utf-8') as f:
                    canonical_exposures_profile = json.load(f)
            except (IOError, ValueError):
                raise OasisException("Canonical exposures profile JSON file path invalid or file is not valid JSON for {}.".format(str(oasis_model)))

        if not with_model_resources:
            return canonical_exposures_profile

        oasis_model.resources['canonical_exposures_profile'] = canonical_exposures_profile
        self.models[oasis_model.key] = oasis_model

        return oasis_model


    def generate_items_file(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Generates an items file for the given ``oasis_model``.
        """
        omr = oasis_model.resources
        tfp = omr['oasis_files_pipeline']

        if not with_model_resources:
            canonical_exposures_file_path = kwargs['canonical_exposures_file_path']
            keys_file_path = kwargs['keys_file_path']
            canonical_exposures_profile = kwargs['canonical_exposures_profile'] if 'canonical_exposures_profile' in kwargs else None
            canonical_exposures_profile_json = kwargs['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in kwargs else None
            canonical_exposures_profile_json_path = kwargs['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in kwargs else None
        else:
            canonical_exposures_file_path = tfp.canonical_exposures_file.name
            keys_file_path = tfp.keys_file.name
            canonical_exposures_profile = omr['canonical_exposures_profile']  if 'canonical_exposures_profile' in omr else None
            canonical_exposures_profile_json = omr['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in omr else None
            canonical_exposures_profile_json_path = omr['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in omr else None

        with io.open(canonical_exposures_file_path, 'r', encoding='utf-8') as cf:
            with io.open(keys_file_path, 'r', encoding='utf-8') as kf:
                canexp_df = pd.read_csv(io.StringIO(cf.read()))
                canexp_df = canexp_df.where(canexp_df.notnull(), None)
                canexp_df.columns = map(str.lower, canexp_df.columns)

                keys_df = pd.read_csv(io.StringIO(kf.read()))
                keys_df = keys_df.rename(columns={'CoverageID': 'CoverageType'})
                keys_df = keys_df.where(keys_df.notnull(), None)
                keys_df.columns = map(str.lower, keys_df.columns)

        if not canonical_exposures_profile:
            if canonical_exposures_profile_json:
                try:
                    canonical_exposures_profile = json.loads(canonical_exposures_profile_json)
                except ValueError:
                    raise OasisException("Canonical exposures profile JSON is invalid for {}.".format(str(oasis_model)))
            else:
                try:
                    with io.open(canonical_exposures_profile_json_path, 'r', encoding='utf-8') as jp:
                        canonical_exposures_profile = json.load(jp)
                except (IOError, ValueError):
                    raise OasisException(
                        "Canonical exposures profile JSON file path is "
                        "invalid or does not exist or the file is not valid "
                        "JSON, for {}.".format(oasis_model)
                    )

        tiv_fields = sorted(map(
            lambda f: canonical_exposures_profile[f],
            filter(lambda k: canonical_exposures_profile[k]['FieldName'] == 'TIV', canonical_exposures_profile)
        ))

        items_df = pd.DataFrame(columns=['item_id', 'coverage_id', 'areaperil_id', 'vulnerability_id', 'group_id'])

        items = []
        for i in range(len(keys_df)):
            ki = keys_df.iloc[i]
            print('Processing keys item {}'.format(ki.to_json()))

            ci_df = canexp_df[canexp_df['row_id'] == ki['locid']]

            if ci_df.empty:
                raise OasisException("No matching canonical exposure item found in canonical exposures data frame for keys item {}.".format(ki))
            elif len(ci_df) > 1:
                raise OasisException("Duplicate canonical exposure items found in canonical exposures data frame for keys item {}.".format(ki))

            ci = ci_df.iloc[0]

            tiv_field = filter(
                    lambda f: f['CoverageTypeId'] == ki['coveragetype'],
                    tiv_fields
            )[0]

            if ci[tiv_field['ProfileElementName'].lower()] > 0:
                it = {
                    'item_id': ci['row_id'],
                    'coverage_id': i,
                    'areaperil_id': ki['areaperilid'],
                    'vulnerability_id': ki['vulnerabilityid'],
                    'group_id': 1
                }
                print('Appending item {}'.format(it))
                items.append(it)

        items_df = items_df.append(items)

        items_df.to_csv(path_or_buf=keys_file_path, encoding='utf-8', chunksize=1000, index=False)

        with io.open(keys_file_path, 'r', encoding='utf-8') as f:
            if not with_model_exposures:
                return f

            tfp.keys_file = f
            self.models[oasis_model.key] = oasis_model

            return oasis_model


    def generate_coverages_file(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Generates a coverages file for the given ``oasis_model``.
        """
        pass


    def generate_gulsummaryxref_file(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Generates a gulsummaryxref file for the given ``oasis_model``.
        """
        pass


    def generate_oasis_files(self, oasis_model, with_model_resources=True, **kwargs):
        """
        For a given ``oasis_model`` generates the standard Oasis files, namely

            ``items.csv``
            ``coverages.csv``
            ``gulsummaryxref.csv``

        """
        if not with_model_resources:
            items_file = self.generate_items_file(oasis_model, with_model_resources, **kwargs)
            coverages_file = self.generate_coverages_file(oasis_model, with_model_resources, **kwargs)
            gulsummaryxref_file = self.generate_gulsummaryxref_file(oasis_model, with_model_resources, **kwargs)
            return items_file, coverages_file, gulsummaryxref_file
        else:
            oasis_model = self.generate_items_file(oasis_model)
            oasis_model = self.generate_coverages_file(oasis_model)
            oasis_model = self.generate_gulsummaryxref_file(oasis_model)

            self.oasis_model[oasis_model.key] = oasis_model

            return oasis_model

