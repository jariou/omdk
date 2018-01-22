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
import logging
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

from keys import OasisKeysLookupFactory as oklf

from oasis_utils import (
    get_utctimestamp,
    OasisException,
    run_mono_executable,
)

__author__ = "Sandeep Murthy"
__copyright__ = "2017, Oasis Loss Modelling Framework"


class OasisExposuresManager(implements(OasisExposuresManagerInterface)):


    def __init__(self, oasis_models=None):
        """
        Class constructor.

        Args:
            ``oasis_models`` (``list``): a list of Oasis model objects (``omdk.OasisModel.OasisModel``)
            with resources provided in the model objects' resources dictionaries.
        """

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='w'
        )

        self.logger = logging.getLogger()

        self.logger.info('Exposures manager {} initialising'.format(self))

        self.logger.info('Creating keys lookup service factory for exposures manager {}'.format(self))
        self._keys_lookup_factory = oklf()
        self.logger.info('Created keys lookup service factory {} for exposures manager {}'.format(self._keys_lookup_factory, self))
        
        self.logger.info('Adding models')
        self._models = {}
        
        if oasis_models:
            for model in oasis_models:
                self.logger.info('Adding model {} to exposures manager {}'.format(model.key, self))

                self.add_model(model)

                self.logger.info('Added model {} to exposures manager {}'.format(model, self))
        else:
            self.logger.info('No models to add to exposures manager {}'.format(self))

        self.logger.info('Exposures manager {} finished initialising'.format(self))


    def add_model(self, oasis_model):
        """
        Adds model to the manager and sets up its resources.
        """
        omr = oasis_model.resources

        if 'oasis_files_pipeline' in omr:
            if not isinstance(omr['oasis_files_pipeline'], OasisFilesPipeline):
                raise OasisException('Oasis files pipeline object for model {} is not of type {}'.format(oasis_model, OasisFilesPipeline))
        else:
            omr['oasis_files_pipeline'] = OasisFilesPipeline.create(model_key=oasis_model.key)

        if 'oasis_files_path' in omr and omr['oasis_files_path']:
            oasis_files_path = os.path.abspath(omr['oasis_files_path'])
            if not os.path.exists(oasis_files_path):
                os.mkdir(oasis_files_path)
        else:
            oasis_files_path = os.path.join(os.getcwd(), 'Files', oasis_model.key.replace('/', '-'))
            if not os.path.exists(oasis_files_path):
                os.mkdir(oasis_files_path)
        
        omr['oasis_files_path'] = oasis_files_path

        if 'source_exposures_file_path' in omr:
            with io.open(omr['source_exposures_file_path'], 'r', encoding='utf-8') as f:
                omr['oasis_files_pipeline'].source_exposures_file = f

        if (
            'canonical_exposures_profile_json' in omr or
            'canonical_exposures_profile_json_path' in omr
        ):
            self.load_canonical_profile(oasis_model)

        self._models[oasis_model.key] = oasis_model

        return oasis_model


    def add_models(self, oasis_models):
        """
        Adds a list of Oasis model objects to the manager.
        """
        map(lambda model: self.add_model(model), oasis_models)


    def update_model(self, oasis_model):
        """
        Updates an existing Oasis model object in the manager.
        """
        omr = oasis_model.resources

        if 'source_exposures_file_path' in omr:
            with io.open(omr['source_exposures_file_path'], 'r', encoding='utf-8') as f:
                omr['oasis_files_pipeline'].source_exposures_file = f

        if (
            'canonical_exposures_profile_json' in omr or
            'canonical_exposures_profile_json_path' in omr
        ):
            self.load_canonical_profile(oasis_model)

        self._models[oasis_model.key] = oasis_model

        return oasis_model


    def update_models(self, oasis_models):
        """
        Updates a list of existing Oasis model objects in the manager.
        """
        map(lambda model: self.update_model(model), oasis_models)


    def delete_model(self, oasis_model):
        """
        Deletes an existing Oasis model object in the manager.
        """
        oasis_model.resources['oasis_files_pipeline'].clear()
        
        del self._models[oasis_model.key]


    def delete_models(self, oasis_models):
        """
        Deletes a list of existing Oasis model objects in the manager.
        """
        map(lambda model: self.delete_model(model), oasis_models)


    @property
    def keys_lookup_factory(self):
        """
        Keys lookup service factory property - getter only.

            :getter: Gets the current keys lookup service factory instance
        """
        return self._keys_lookup_factory


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
            'o': output_file_path,
            's': ''
        }

        try:
            run_mono_executable(xtrans_path, xtrans_args)
        except OasisException as e:
            raise e

        with io.open(output_file_path, 'r', encoding='utf-8') as f:
            if not with_model_resources:
                return f

            tfp.canonical_exposures_file = f
        
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
            xtrans_path = omr['xtrans_path']
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
        
        return oasis_model


    def get_keys(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Generates the Oasis keys CSV file for a given model object, with
        headers

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
            model_exposures_file_path = kwargs['model_exposures_file_path'] if 'model_exposures_file_path' in kwargs else None
            lookup = kwargs['lookup']
            keys_file_path = kwargs['keys_file_path']
        else:
            model_exposures_file_path = tfp.model_exposures_file.name if tfp.model_exposures_file else None
            lookup = omr['lookup']
            keys_file_path = tfp.keys_file.name

        (
            model_exposures_file_path,
            keys_file_path
        ) = map(os.path.abspath, [model_exposures_file_path, keys_file_path])

        oasis_keys_file, _ = self.keys_lookup_factory.save_keys(
            lookup=lookup,
            model_exposures_file_path=model_exposures_file_path,
            output_file_path=keys_file_path,
            format='oasis_keys'
        )

        if not with_model_resources:
            return oasis_keys_file

        tfp.keys_file = oasis_keys_file

        return oasis_model


    def load_canonical_profile(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Loads a JSON string or JSON file representation of the canonical
        exposures profile for a given ``oasis_model``, stores this in the
        model object's resources dict, and returns the object.
        """
        omr = oasis_model.resources

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
                raise OasisException("Canonical exposures profile JSON is invalid for {}.".format(oasis_model))
        elif canonical_exposures_profile_json_path:
            try:
                with io.open(canonical_exposures_profile_json_path, 'r', encoding='utf-8') as f:
                    canonical_exposures_profile = json.load(f)
            except (IOError, ValueError, TypeError):
                raise OasisException("Canonical exposures profile JSON file path invalid or file is not valid JSON for {}.".format(oasis_model))

        if not with_model_resources:
            return canonical_exposures_profile

        omr['canonical_exposures_profile'] = canonical_exposures_profile

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
            items_file_path = kwargs['items_file_path']
            items_timestamped_file_path = kwargs['items_timestamped_file_path']
        else:
            canonical_exposures_file_path = tfp.canonical_exposures_file.name
            keys_file_path = tfp.keys_file.name
            canonical_exposures_profile = omr['canonical_exposures_profile']  if 'canonical_exposures_profile' in omr else None
            canonical_exposures_profile_json = omr['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in omr else None
            canonical_exposures_profile_json_path = omr['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in omr else None
            items_file_path = omr['items_file_path']
            items_timestamped_file_path = omr['items_timestamped_file_path']

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
                omr['canonical_exposures_profile_json'] = canonical_exposures_profile_json
            elif canonical_exposures_profile_json_path:
                omr['canonical_exposures_profile_json_path'] = canonical_exposures_profile_json_path

            canonical_exposures_profile = self.load_canonical_profile(oasis_model, with_model_resources=with_model_resources)

        tiv_fields = sorted(map(
            lambda f: canonical_exposures_profile[f],
            filter(lambda k: canonical_exposures_profile[k]['FieldName'] == 'TIV' if 'FieldName' in canonical_exposures_profile[k] else None, canonical_exposures_profile)
        ))

        columns = ['item_id', 'coverage_id', 'areaperil_id', 'vulnerability_id', 'group_id']
        items_df = pd.DataFrame(columns=columns)

        records = []
        ii = 0
        for i in range(len(keys_df)):
            ki = keys_df.iloc[i]

            ci_df = canexp_df[canexp_df['row_id'] == ki['locid']]

            if ci_df.empty:
                raise OasisException("No matching canonical exposure item found in canonical exposures data frame for keys item {}.".format(ki))
            elif len(ci_df) > 1:
                raise OasisException("Duplicate canonical exposure items found in canonical exposures data frame for keys item {}.".format(ki))

            ci = ci_df.iloc[0]

            tiv_field = filter(
                    lambda f: f['CoverageTypeID'] == ki['coveragetype'],
                    tiv_fields
            )[0]

            if ci[tiv_field['ProfileElementName'].lower()] > 0:
                ii += 1
                rec = {
                    'item_id': ii,
                    'coverage_id': ii,
                    'areaperil_id': ki['areaperilid'],
                    'vulnerability_id': ki['vulnerabilityid'],
                    'group_id': ii
                }
                records.append(rec)

        items_df = items_df.append(records)

        items_df = items_df.astype(int)

        items_df.to_csv(
            columns=columns,
            path_or_buf=items_file_path,
            encoding='utf-8', 
            chunksize=1000,
            index=False
        )
        items_df.to_csv(
            columns=columns,
            path_or_buf=items_timestamped_file_path,
            encoding='utf-8', 
            chunksize=1000,
            index=False
        )

        with io.open(items_file_path, 'r', encoding='utf-8') as f:
            if not with_model_resources:
                return f

            tfp.items_file = f

        return oasis_model


    def generate_coverages_file(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Generates a coverages file for the given ``oasis_model``.
        """
        omr = oasis_model.resources
        tfp = omr['oasis_files_pipeline']

        if not with_model_resources:
            canonical_exposures_file_path = kwargs['canonical_exposures_file_path']
            keys_file_path = kwargs['keys_file_path']
            canonical_exposures_profile = kwargs['canonical_exposures_profile'] if 'canonical_exposures_profile' in kwargs else None
            canonical_exposures_profile_json = kwargs['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in kwargs else None
            canonical_exposures_profile_json_path = kwargs['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in kwargs else None
            coverages_file_path = kwargs['coverages_file_path']
            coverages_timestamped_file_path = kwargs['coverages_timestamped_file_path']
        else:
            canonical_exposures_file_path = tfp.canonical_exposures_file.name
            keys_file_path = tfp.keys_file.name
            canonical_exposures_profile = omr['canonical_exposures_profile']  if 'canonical_exposures_profile' in omr else None
            canonical_exposures_profile_json = omr['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in omr else None
            canonical_exposures_profile_json_path = omr['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in omr else None
            coverages_file_path = omr['coverages_file_path']
            coverages_timestamped_file_path = omr['coverages_timestamped_file_path']

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
                omr['canonical_exposures_profile_json'] = canonical_exposures_profile_json
            elif canonical_exposures_profile_json_path:
                omr['canonical_exposures_profile_json_path'] = canonical_exposures_profile_json_path

            canonical_exposures_profile = self.load_canonical_profile(oasis_model, with_model_resources=with_model_resources)

        tiv_fields = sorted(map(
            lambda f: canonical_exposures_profile[f],
            filter(lambda k: canonical_exposures_profile[k]['FieldName'] == 'TIV' if 'FieldName' in canonical_exposures_profile[k] else None, canonical_exposures_profile)
        ))

        columns = ['coverage_id', 'tiv']
        coverages_df = pd.DataFrame(columns=columns)

        records = []
        ii = 0
        for i in range(len(keys_df)):
            ki = keys_df.iloc[i]

            ci_df = canexp_df[canexp_df['row_id'] == ki['locid']]

            if ci_df.empty:
                raise OasisException("No matching canonical exposure item found in canonical exposures data frame for keys item {}.".format(ki))
            elif len(ci_df) > 1:
                raise OasisException("Duplicate canonical exposure items found in canonical exposures data frame for keys item {}.".format(ki))

            ci = ci_df.iloc[0]

            tiv_field = filter(
                    lambda f: f['CoverageTypeID'] == ki['coveragetype'],
                    tiv_fields
            )[0]

            if ci[tiv_field['ProfileElementName'].lower()] > 0:
                ii += 1
                rec = {
                    'coverage_id': ii,
                    'tiv': ci[tiv_field['ProfileElementName'].lower()]
                }
                records.append(rec)

        coverages_df = coverages_df.append(records)

        coverages_df = coverages_df.astype(int)

        coverages_df.to_csv(
            columns=columns,
            path_or_buf=coverages_file_path,
            encoding='utf-8', 
            chunksize=1000,
            index=False
        )
        coverages_df.to_csv(
            columns=columns,
            path_or_buf=coverages_timestamped_file_path,
            encoding='utf-8', 
            chunksize=1000,
            index=False
        )

        with io.open(coverages_file_path, 'r', encoding='utf-8') as f:
            if not with_model_resources:
                return f

            tfp.coverages_file = f

        return oasis_model


    def generate_gulsummaryxref_file(self, oasis_model, with_model_resources=True, **kwargs):
        """
        Generates a gulsummaryxref file for the given ``oasis_model``.
        """
        omr = oasis_model.resources
        tfp = omr['oasis_files_pipeline']

        if not with_model_resources:
            canonical_exposures_file_path = kwargs['canonical_exposures_file_path']
            keys_file_path = kwargs['keys_file_path']
            canonical_exposures_profile = kwargs['canonical_exposures_profile'] if 'canonical_exposures_profile' in kwargs else None
            canonical_exposures_profile_json = kwargs['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in kwargs else None
            canonical_exposures_profile_json_path = kwargs['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in kwargs else None
            gulsummaryxref_file_path = kwargs['gulsummaryxref_file_path']
            gulsummaryxref_timestamped_file_path = kwargs['gulsummaryxref_timestamped_file_path']
        else:
            canonical_exposures_file_path = tfp.canonical_exposures_file.name
            keys_file_path = tfp.keys_file.name
            canonical_exposures_profile = omr['canonical_exposures_profile']  if 'canonical_exposures_profile' in omr else None
            canonical_exposures_profile_json = omr['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in omr else None
            canonical_exposures_profile_json_path = omr['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in omr else None
            gulsummaryxref_file_path = omr['gulsummaryxref_file_path']
            gulsummaryxref_timestamped_file_path = omr['gulsummaryxref_timestamped_file_path']

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
                omr['canonical_exposures_profile_json'] = canonical_exposures_profile_json
            elif canonical_exposures_profile_json_path:
                omr['canonical_exposures_profile_json_path'] = canonical_exposures_profile_json_path

            canonical_exposures_profile = self.load_canonical_profile(oasis_model, with_model_resources=with_model_resources)

        tiv_fields = sorted(map(
            lambda f: canonical_exposures_profile[f],
            filter(lambda k: canonical_exposures_profile[k]['FieldName'] == 'TIV' if 'FieldName' in canonical_exposures_profile[k] else None, canonical_exposures_profile)
        ))

        columns = ['coverage_id', 'summary_id', 'summaryset_id']
        gulsummaryxref_df = pd.DataFrame(columns=columns)

        records = []
        ii = 0
        for i in range(len(keys_df)):
            ki = keys_df.iloc[i]

            ci_df = canexp_df[canexp_df['row_id'] == ki['locid']]

            if ci_df.empty:
                raise OasisException("No matching canonical exposure item found in canonical exposures data frame for keys item {}.".format(ki))
            elif len(ci_df) > 1:
                raise OasisException("Duplicate canonical exposure items found in canonical exposures data frame for keys item {}.".format(ki))

            ci = ci_df.iloc[0]

            tiv_field = filter(
                    lambda f: f['CoverageTypeID'] == ki['coveragetype'],
                    tiv_fields
            )[0]

            if ci[tiv_field['ProfileElementName'].lower()] > 0:
                ii += 1
                rec = {
                    'coverage_id': ii,
                    'summary_id': 1,
                    'summaryset_id': 1
                }
                records.append(rec)

        gulsummaryxref_df = gulsummaryxref_df.append(records)

        gulsummaryxref_df = gulsummaryxref_df.astype(int)

        gulsummaryxref_df.to_csv(
            columns=columns,
            path_or_buf=gulsummaryxref_file_path,
            encoding='utf-8', 
            chunksize=1000,
            index=False
        )
        gulsummaryxref_df.to_csv(
            columns=columns,
            path_or_buf=gulsummaryxref_timestamped_file_path,
            encoding='utf-8', 
            chunksize=1000,
            index=False
        )

        with io.open(gulsummaryxref_file_path, 'r', encoding='utf-8') as f:
            if not with_model_resources:
                return f

            tfp.gulsummaryxref_file = f

        return oasis_model


    def generate_oasis_files(
        self,
        oasis_model,
        with_model_resources=True,
        **kwargs
    ):
        """
        For a given ``oasis_model`` generates the standard Oasis files, namely

            ``items.csv``
            ``coverages.csv``
            ``gulsummaryxref.csv``

        """
        omr = oasis_model.resources
        tfp = omr['oasis_files_pipeline']

        if not with_model_resources:
            canonical_exposures_file_path = kwargs['canonical_exposures_file_path']
            keys_file_path = kwargs['keys_file_path']
            canonical_exposures_profile = kwargs['canonical_exposures_profile'] if 'canonical_exposures_profile' in kwargs else None
            canonical_exposures_profile_json = kwargs['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in kwargs else None
            canonical_exposures_profile_json_path = kwargs['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in kwargs else None
            items_file_path = kwargs['items_file_path']
            items_timestamped_file_path = kwargs['items_timestamped_file_path']
            coverages_file_path = kwargs['coverages_file_path']
            coverages_timestamped_file_path = kwargs['coverages_timestamped_file_path']
            gulsummaryxref_file_path = kwargs['gulsummaryxref_file_path']
            gulsummaryxref_timestamped_file_path = kwargs['gulsummaryxref_timestamped_file_path']
        else:
            canonical_exposures_file_path = tfp.canonical_exposures_file.name
            keys_file_path = tfp.keys_file.name
            canonical_exposures_profile = omr['canonical_exposures_profile']  if 'canonical_exposures_profile' in omr else None
            canonical_exposures_profile_json = omr['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in omr else None
            canonical_exposures_profile_json_path = omr['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in omr else None
            items_file_path = omr['items_file_path']
            items_timestamped_file_path = omr['items_timestamped_file_path']
            coverages_file_path = omr['coverages_file_path'] if 'coverages_file_path' in omr else None
            coverages_timestamped_file_path = omr['coverages_timestamped_file_path']
            gulsummaryxref_file_path = omr['gulsummaryxref_file_path']
            gulsummaryxref_timestamped_file_path = omr['gulsummaryxref_timestamped_file_path']

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
                omr['canonical_exposures_profile_json'] = canonical_exposures_profile_json
            elif canonical_exposures_profile_json_path:
                omr['canonical_exposures_profile_json_path'] = canonical_exposures_profile_json_path

            canonical_exposures_profile = self.load_canonical_profile(oasis_model, with_model_resources=with_model_resources)

        tiv_fields = sorted(map(
            lambda f: canonical_exposures_profile[f],
            filter(lambda k: canonical_exposures_profile[k]['FieldName'] == 'TIV' if 'FieldName' in canonical_exposures_profile[k] else None, canonical_exposures_profile)
        ))

        columns = [
            'item_id',
            'coverage_id',
            'tiv',
            'areaperil_id',
            'vulnerability_id',
            'group_id',
            'summary_id',
            'summaryset_id'
        ]
        master_df = pd.DataFrame(columns=columns)
        master_df

        records = []
        ii = 0
        for i in range(len(keys_df)):
            ki = keys_df.iloc[i]

            ci_df = canexp_df[canexp_df['row_id'] == ki['locid']]

            if ci_df.empty:
                raise OasisException("No matching canonical exposure item found in canonical exposures data frame for keys item {}.".format(ki))
            elif len(ci_df) > 1:
                raise OasisException("Duplicate canonical exposure items found in canonical exposures data frame for keys item {}.".format(ki))

            ci = ci_df.iloc[0]

            tiv_field = filter(
                    lambda f: f['CoverageTypeID'] == ki['coveragetype'],
                    tiv_fields
            )[0]

            if ci[tiv_field['ProfileElementName'].lower()] > 0:
                ii += 1
                rec = {
                    'item_id': ii,
                    'coverage_id': ii,
                    'tiv': ci[tiv_field['ProfileElementName'].lower()],
                    'areaperil_id': ki['areaperilid'],
                    'vulnerability_id': ki['vulnerabilityid'],
                    'group_id': ii,
                    'summary_id': 1,
                    'summaryset_id': 1
                }
                records.append(rec)

        master_df = master_df.append(records)

        columns = ['item_id', 'coverage_id', 'areaperil_id', 'vulnerability_id', 'group_id']
        for col in columns:
            master_df[col] = master_df[col].astype(int)

        master_df.to_csv(
            columns=columns,
            path_or_buf=items_file_path,
            encoding='utf-8', 
            chunksize=1000,
            index=False
        )
        master_df.to_csv(
            columns=columns,
            path_or_buf=items_timestamped_file_path,
            encoding='utf-8', 
            chunksize=1000,
            index=False
        )

        columns = ['coverage_id', 'tiv']
        master_df['coverage_id'] = master_df['coverage_id'].astype(int)

        master_df.to_csv(
            columns=columns,
            float_format='%.5f',
            path_or_buf=coverages_file_path,
            encoding='utf-8',
            chunksize=1000,
            index=False
        )
        master_df.to_csv(
            columns=columns,
            float_format='%.5f',
            path_or_buf=coverages_timestamped_file_path,
            encoding='utf-8',
            chunksize=1000,
            index=False
        )

        columns = ['coverage_id', 'summary_id', 'summaryset_id']
        for col in columns:
            master_df[col] = master_df[col].astype(int)

        master_df.to_csv(
            columns=columns,
            path_or_buf=gulsummaryxref_file_path,
            encoding='utf-8',
            chunksize=1000,
            index=False
        )
        master_df.to_csv(
            columns=columns,
            path_or_buf=gulsummaryxref_timestamped_file_path,
            encoding='utf-8',
            chunksize=1000,
            index=False
        )

        with io.open(items_file_path, 'r', encoding='utf-8') as itf:
            with io.open(coverages_file_path, 'r', encoding='utf-8') as cvf:
                with io.open(gulsummaryxref_file_path, 'r', encoding='utf-8') as gsf:
                    if not with_model_resources:
                        return itf, cvf, gsf

                    tfp.items_file = itf
                    tfp.coverages_file = cvf
                    tfp.gulsummaryxref_file = gsf

        return oasis_model


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
        oasis_model.resources['oasis_files_pipeline'].clear()

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
                self.logger.info('Checking output files directory exists for model')

                oasis_files_path = kwargs['oasis_files_path'] if 'oasis_files_path' in kwargs else None
                
                if not oasis_files_path:
                    raise OasisException(
                        "No output directory provided for {} in '**kwargs'.".format(oasis_model)
                    )
                elif not os.path.exists(oasis_files_path):
                    raise OasisException(
                        "Output directory {} for {} provided in '**kwargs' "
                        "does not exist on the filesystem.".format(oasis_files_path, oasis_model)
                    )

                self.logger.info('Output files directory {} exists'.format(oasis_files_path))

                self.logger.info('Checking for source exposures file')
                
                source_exposures_file_path = kwargs['source_exposures_file_path']

                if not source_exposures_file_path:
                    raise OasisException("No source exposures file path provided for {} in '**kwargs'.".format(oasis_model))
                elif not os.path.exists(source_exposures_file_path):
                    raise OasisException("Source exposures file path {} provided for {} in '**kwargs' is invalid.".format(source_exposures_file_path, oasis_model))
                
                self.logger.info('Source exposures file {} exists'.format(source_exposures_file_path))

                self.logger.info('Copying source exposures file to model output files directory')
                
                source_exposures_file_name = source_exposures_file_path.split(os.path.sep)[-1]
                target_file_path = os.path.join(oasis_files_path, source_exposures_file_name)
                
                if not os.path.exists(target_file_path):
                    shutil.copy(source_exposures_file_path, target_file_path)

                kwargs['source_exposures_file_path'] = target_file_path

                utcnow = get_utctimestamp(fmt='%Y%m%d%H%M%S')

                target_file_path = os.path.join(oasis_files_path, 'canexp-{}.csv'.format(utcnow))
                kwargs['canonical_exposures_file_path'] = target_file_path

                self.logger.info('Generating canonical exposures file {}'.format(target_file_path))

                canonical_exposures_file = self.transform_source_to_canonical(oasis_model, with_model_resources=False, **kwargs)
                
                target_file_path = os.path.join(oasis_files_path, 'modexp-{}.csv'.format(utcnow))
                kwargs['model_exposures_file_path'] = target_file_path

                self.logger.info('Generating model exposures file {}'.format(target_file_path))

                model_exposures_file = self.transform_canonical_to_model(oasis_model, with_model_resources=False, **kwargs)

                target_file_path = os.path.join(oasis_files_path, 'oasiskeys-{}.csv'.format(utcnow))
                kwargs['keys_file_path'] = target_file_path

                self.logger.info('Generating keys file {}'.format(target_file_path))

                keys_file = self.get_keys(oasis_model, with_model_resources=False, **kwargs)
                
                self.logger.info('Checking for canonical exposures profile source for model')

                canonical_exposures_profile_json_path = kwargs['canonical_exposures_profile_json_path']

                if not canonical_exposures_profile_json_path:
                    raise OasisException("No canonical exposures profile JSON file path provided for {} in '**kwargs'.".format(oasis_model))
                elif not os.path.exists(canonical_exposures_profile_json_path):
                    raise OasisException("Canonical exposures profile JSON file path {} provided for {} in '**kwargs' is invalid.".format(canonical_exposures_profile_json_path, oasis_model))
                
                self.logger.info('Canonical exposures profile source {} exists'.format(canonical_exposures_profile_json_path))

                self.logger.info('Loading canonical exposures profile into model resources')
                canonical_exposures_profile = self.load_canonical_profile(oasis_model, with_model_resources=False, **kwargs)
                kwargs['canonical_exposures_profile'] = canonical_exposures_profile
                self.logger.info('Loaded canonical exposures profile {} into model resources'.format(canonical_exposures_profile))

                kwargs['items_file_path'] = os.path.join(oasis_files_path, 'items.csv')
                kwargs['items_timestamped_file_path'] = os.path.join(oasis_files_path, 'items-{}.csv'.format(utcnow))
                kwargs['coverages_file_path'] = os.path.join(oasis_files_path, 'coverages.csv')
                kwargs['coverages_timestamped_file_path'] = os.path.join(oasis_files_path, 'coverages-{}.csv'.format(utcnow))
                kwargs['gulsummaryxref_file_path'] = os.path.join(oasis_files_path, 'gulsummaryxref.csv')
                kwargs['gulsummaryxref_timestamped_file_path'] = os.path.join(oasis_files_path, 'gulsummaryxref-{}.csv'.format(utcnow))

                self.logger.info('Generating Oasis files for model')
                items_file, coverages_file, gulsummaryxref_file = self.generate_oasis_files(
                    oasis_model, with_model_resources=False, **kwargs
                )

                return {
                    'items': items_file,
                    'coverages': coverages_file,
                    'gulsummaryxref': gulsummaryxref_file
                }
            else:
                omr = oasis_model.resources
                tfp = omr['oasis_files_pipeline']

                self.logger.info('Checking output files directory exists for model')

                oasis_files_path = omr['oasis_files_path'] if 'oasis_files_path' in omr else None
                if not oasis_files_path:
                    raise OasisException(
                        "No output directory provided for {} in resources dict.".format(oasis_model)
                    )
                elif not os.path.exists(oasis_files_path):
                    raise OasisException(
                        "Output directory {} for {} provided in resources dict "
                        "does not exist on the filesystem.".format(oasis_files_path, oasis_model)
                    )

                self.logger.info('Output files directory {} exists'.format(oasis_files_path))

                self.logger.info('Checking for source exposures file in the model files pipeline')

                source_exposures_file = tfp.source_exposures_file if tfp.source_exposures_file else None

                if not source_exposures_file:
                    raise OasisException("No source exposures file in the Oasis files pipeline for {}.".format(oasis_model))
                elif not os.path.exists(source_exposures_file.name):
                    raise OasisException("Source exposures file path {} provided for {} is invalid.".format(source_exposures_file.name, oasis_model))

                self.logger.info('Source exposures file {} exists'.format(source_exposures_file))

                utcnow = get_utctimestamp(fmt='%Y%m%d%H%M%S')

                target_file_path = os.path.join(oasis_files_path, 'canexp-{}.csv'.format(utcnow))
                with io.open(target_file_path, 'w', encoding='utf-8') as f:
                    tfp.canonical_exposures_file = f

                self.logger.info('Generating canonical exposures file')

                self.transform_source_to_canonical(oasis_model)

                self.logger.info('Generated canonical exposures file {}'.format(target_file_path))
                
                target_file_path = os.path.join(oasis_files_path, 'modexp-{}.csv'.format(utcnow))
                with io.open(target_file_path, 'w', encoding='utf-8') as f:
                    tfp.model_exposures_file = f

                self.logger.info('Generating model exposures file')

                self.transform_canonical_to_model(oasis_model)

                self.logger.info('Generated model exposures file {}'.format(target_file_path))

                target_file_path = os.path.join(oasis_files_path, 'oasiskeys-{}.csv'.format(utcnow))
                with io.open(target_file_path, 'w', encoding='utf-8') as f:
                    tfp.keys_file = f

                self.logger.info('Generating keys file')

                self.get_keys(oasis_model)

                self.logger.info('Generated keys file {}'.format(target_file_path))
                
                self.logger.info('Checking for canonical exposures profile for model')

                if not oasis_model.resources['canonical_exposures_profile']:
                    self.logger.info('Canonical exposures profile not found in model resources - attempting to load from source')
                    self.load_canonical_profile(oasis_model)
                    self.logger.info('Loaded canonical exposures profile {} into model resources'.format(oasis_model.resources['canonical_exposures_profile']))
                else:
                    self.logger.info('Canonical exposures profile exists for model')

                omr['items_file_path'] = os.path.join(oasis_files_path, 'items.csv')
                omr['items_timestamped_file_path'] = os.path.join(oasis_files_path, 'items-{}.csv'.format(utcnow))
                omr['coverages_file_path'] = os.path.join(oasis_files_path, 'coverages.csv')
                omr['coverages_timestamped_file_path'] = os.path.join(oasis_files_path, 'coverages-{}.csv'.format(utcnow))
                omr['gulsummaryxref_file_path'] = os.path.join(oasis_files_path, 'gulsummaryxref.csv')
                omr['gulsummaryxref_timestamped_file_path'] = os.path.join(oasis_files_path, 'gulsummaryxref-{}.csv'.format(utcnow))

                self.logger.info('Generating Oasis files for model')

                self.generate_oasis_files(oasis_model)

                self.logger.info('Generated Oasis files {}'.format(tfp.oasis_files))
        except OasisException as e:
            raise e

        return oasis_model
