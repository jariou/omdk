#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisExposureTransformsManager'
]

import io
import json
import os
import pandas as pd
import subprocess
import sys

from interface import implements

from OasisExposureTransformsManagerInterface import OasisExposureTransformsManagerInterface
from OasisExposureTransformsFilesPipeline import OasisExposureTransformsFilesPipeline

if os.getcwd().split(os.path.sep)[-1] == 'exposure_transforms':
    sys.path.insert(0, os.path.abspath(os.pardir))

from oasis_utils import (
    KeysLookupServiceFactory as klsf,
    OasisException,
    run_mono_executable,
)


class OasisExposureTransformsManager(implements(OasisExposureTransformsManagerInterface)):


    def __init__(self, keys_lookup_service_factory=None, oasis_models=None):
        """
        Class constructor - not generally to be used directly.
        """
        self._keys_lookup_service_factory = (
            keys_lookup_service_factory if keys_lookup_service_factory
            else klsf()
        )
        
        self._models = {}
        
        if oasis_models:
            for model in oasis_models:
                if 'transforms_files_pipeline' in model.resources:
                    if not model.resources['transforms_files_pipeline']:
                        model.resources['transforms_files_pipeline'] = OasisExposureTransformsFilesPipeline.create()
                else:
                    model.resources['transforms_files_pipeline'] = OasisExposureTransformsFilesPipeline.create()
                
                self._models[model.key] = model



    @classmethod
    def create(cls, keys_lookup_service_factory=None, oasis_models=None):
        """
        Class method that returns an instance of an Oasis exposure transforms
        manager. The optional ``oasis_models`` argument should be a list of
        Oasis model objects (``omdk.OasisModel.OasisModel``), and any
        additional resources can be specified in ``kwargs``.
        """
        return cls(keys_lookup_service_factory=keys_lookup_service_factory, oasis_models=oasis_models)


    @property
    def keys_lookup_service_factory(self):
        """
        Keys lookup service factory property.

            :getter: Gets the current keys lookup service factory instance
            :setter: Sets the current keys lookup service factory instance to
                     the given instance
            :deleter: Deletes the current keys lookup service factory instance
        """
        return self._keys_lookup_service_factory


    @keys_lookup_service_factory.setter
    def keys_lookup_service_factory(self, keys_lookup_service_factory):
        self._keys_lookup_service_factory = keys_lookup_service_factory


    @keys_lookup_service_factory.deleter
    def keys_lookup_service_factory(self):
        del self._keys_lookup_service_factory


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
            if 'transforms_files_pipeline' not in model.resources:
                model.resources['transforms_files_pipeline'] = OasisExposureTransformsFilesPipeline.create()
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
        Clears the exposure transforms files pipeline for the given
        ``oasis_model`` optionally using additional arguments in the ``kwargs``
        dict.
        """
        oasis_model.resources['transforms_files_pipeline'] = OasisExposureTransformsFilesPipeline.create()
        self.models[oasis_model.key] = oasis_model
        return oasis_model


    def start_files_pipeline(self, oasis_model, **kwargs):
        """
        Starts the exposure transforms pipeline for the given ``oasis_model``,
        i.e. the generation of the canonical exposures files, keys file
        and finally the Oasis files.
        """
        try:
            oasis_model = self.transform_source_to_canonical(oasis_model)
            oasis_model = self.canonical_to_model(oasis_model)
            oasis_model = self.model_to_keys(oasis_model)
            self.load_canonical_profile(oasis_model)
            self.generate_oasis_files(oasis_model)
        except OasisException as e:
            raise e

        return oasis_model


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
        omr = oasis_model.resources
        tfp = omr['transforms_files_pipeline']

        if not with_model_resources:
            xtrans_path = kwargs['xtrans_path'] if 'xtrans_path' in kwargs else None
            input_file_path = kwargs['source_exposures_file_path']  if 'source_exposures_file_path' in kwargs else None
            validation_file_path = kwargs['source_exposures_validation_file_path'] if 'source_exposures_validation_file_path' in kwargs else None
            transformation_file_path = kwargs['source_to_canonical_exposures_transformation_file_path'] if 'source_to_canonical_exposures_transformation_file_path' in kwargs else None
            output_file_path = kwargs['canonical_exposures_file_path'] if 'canonical_exposures_file_path' in kwargs else None
        else:
            xtrans_path = omr['xtrans_path'] if 'xtrans_path' in omr else None
            input_file_path = tfp.source_exposures_file.name if tfp.source_exposures_file else None
            validation_file_path = omr['source_exposures_validation_file_path'] if 'source_exposures_validation_file_path' in omr else None
            transformation_file_path = omr['source_to_canonical_exposures_transformation_file_path'] if 'source_to_canonical_exposures_transformation_file_path' in omr else None
            output_file_path = tfp.canonical_exposures_file.name if tfp.canonical_exposures_file else None

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
        tfp = omr['transforms_files_pipeline']

        if not with_model_resources:
            xtrans_path = kwargs['xtrans_path'] if 'xtrans_path' in kwargs else None
            input_file_path = kwargs['source_exposures_file_path']  if 'source_exposures_file_path' in kwargs else None
            validation_file_path = kwargs['source_exposures_validation_file_path'] if 'source_exposures_validation_file_path' in kwargs else None
            transformation_file_path = kwargs['source_to_canonical_exposures_transformation_file_path'] if 'source_to_canonical_exposures_transformation_file_path' in kwargs else None
            output_file_path = kwargs['canonical_exposures_file_path'] if 'canonical_exposures_file_path' in kwargs else None
        else:
            xtrans_path = omr['xtrans_path'] if 'xtrans_path' in omr else None
            input_file_path = tfp.canonical_exposures_file.name if tfp.canonical_exposures_file else None
            validation_file_path = omr['canonical_exposures_validation_file_path'] if 'canonical_exposures_validation_file_path' in omr else None
            transformation_file_path = omr['canonical_to_model_exposures_transformation_file_path'] if 'canonical_to_model_exposures_transformation_file_path' in omr else None
            output_file_path = tfp.model_exposures_file.name if tfp.model_exposures_file else None

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


    def get_keys_file(self, oasis_model, with_model_resources=True, **kwargs):
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
        tfp = omr['transforms_files_pipeline']        

        if not with_model_resources:
            model_exposures = kwargs['model_exposures'] if 'model_exposures' in kwargs else None
            model_exposures_file_path = kwargs['model_exposures_file_path']  if 'model_exposures_file_path' in kwargs else None
            lookup_service = kwargs['lookup_service']  if 'lookup_service' in kwargs else None
            keys_file_path = kwargs['keys_file_path']  if 'keys_file_path' in kwargs else None
        else:
            model_exposures = omr['model_exposures'] if 'model_exposures' in omr else None
            model_exposures_file_path = tfp.model_exposures_file.name if tfp.model_exposures_file else None
            lookup_service = omr['lookup_service'] if 'lookup_service' in omr else None
            keys_file_path = tfp.keys_file.name if tfp.keys_file else None

        if not any([model_exposures, model_exposures_file_path]):
            raise OasisException('No model exposures or model exposures file path provided for {}'.format(oasis_model))

        if not lookup_service:
            raise OasisException('No lookup service provided for {}'.format(oasis_model))

        if not keys_file_path:
            raise OasisException('No file path provided for the keys file for {}'.format(oasis_model))

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
        tfp = omr['transforms_files_pipeline']

        if not with_model_resources:
            canonical_exposures_profile_json = kwargs['canonical_exposures_profile_json'] if 'canonical_exposures_profile_json' in kwargs else None
            canonical_exposures_profile_json_path = kwargs['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in kwargs else None
        else:
            canonical_exposures_profile_json = omr['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in omr else None
            canonical_exposures_profile_json_path = omr['canonical_exposures_profile_json_path'] if 'canonical_exposures_profile_json_path' in omr else None

        if not any([canonical_exposures_profile_json, canonical_exposures_profile_json_path]):
            raise OasisException(
                "No canonical exposures profile JSON or JSON file path provided for {} - "
                "this must be provided either in the model object's resources dict "
                "or as optional keyword argument, using the field name / keyword name "
                "'canonical_exposures_profile_json' if providing a JSON string or "
                "'canonical_exposures_profile_json_path' if providing a full JSON file path.".
                format(str(oasis_model))
            )

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
        tfp = omr['transforms_files_pipeline']

        if not with_model_resources:
            canonical_exposures_file_path = kwargs['canonical_exposures_file_path'] if 'canonical_exposures_file_path' in kwargs else None
            keys_file_path = kwargs['keys_file_path']  if 'keys_file_path' in kwargs else None
            canonical_exposures_profile = kwargs['canonical_exposures_profile']  if 'canonical_exposures_profile' in kwargs else None
            canonical_exposures_profile_json = kwargs['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in kwargs else None
            canonical_exposures_profile_json_path = kwargs['canonical_exposures_profile_json_path'] if 'canonical_exposures_profile_json_path' in kwargs else None
        else:
            canonical_exposures_file_path = tfp.canonical_exposures_file.name if tfp.canonical_exposures_file else None
            keys_file_path = tfp.keys_file.name  if tfp.keys_file else None
            canonical_exposures_profile = omr['canonical_exposures_profile']  if 'canonical_exposures_profile' in omr else None
            canonical_exposures_profile_json = omr['canonical_exposures_profile_json']  if 'canonical_exposures_profile_json' in omr else None
            canonical_exposures_profile_json_path = omr['canonical_exposures_profile_json_path']  if 'canonical_exposures_profile_json_path' in omr else None

        if not canonical_exposures_file_path:
            raise OasisException(
                "No canonical exposures file path provided for {} - "
                "this must be provided either as an attribute of the transforms "
                "files pipeline object in the model object's resources dict, "
                "or as optional keyword argument, using the field name / keyword name "
                "'canonical_exposures_file_path'.".
                format(str(oasis_model))
            )

        if not keys_file_path:
            raise OasisException(
                "No keys file path provided for {} - "
                "this must be provided either as an attribute of the transforms "
                "files pipeline object in the model object's resources dict, "
                "or as optional keyword argument, using the field name / keyword name "
                "'keys_file_path'.".
                format(str(oasis_model))

            )

        if not any([canonical_exposures, canonical_exposures_profile_json, canonical_exposures_profile_json_path]):
            raise OasisException(
                "No canonical exposures profile dict, profile JSON or JSON file path provided for {} - "
                "this must be provided either in the model object's resources dict "
                "or as optional keyword argument, using the field name / keyword name "
                "'canonical_exposures_profile' if providing a dict, "
                "or 'canonical_exposures_profile_json' if providing a JSON string, "
                "or 'canonical_exposures_profile_json_path' if providing a JSON file path.".
                format(str(oasis_model))
            )

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
                    raise OasisException("Canonical exposures profile JSON file path invalid or file is not valid JSON for {}.".format(str(oasis_model)))

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


    def generate_coverages_file(self, oasis_model, **kwargs):
        """
        Generates a coverages file for the given ``oasis_model``.
        """
        pass


    def generate_gulsummaryxref_file(self, oasis_model, **kwargs):
        """
        Generates a gulsummaryxref file for the given ``oasis_model``.
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
