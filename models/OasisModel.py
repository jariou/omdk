#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisModel',
    'OasisModelFactory'
]

import os

if os.getcwd().split(os.path.sep)[-1] == 'models':
    sys.path.insert(0, os.path.abspath(os.pardir))

from oasis_utils import (
    KeysLookupServiceFactory as klsf,
    OasisException,
)

__author__ = "Sandeep Murthy"
__copyright__ = "Oasis Loss Modelling Framework 2017"


class OasisModel(object):
    """
    A simple object representation of Oasis models and their resources - an
    Oasis model is viewed as a combination of a specific supplier, model ID
    and model version, and the constructor requires these three arguments
    for creating a new Oasis model object. Each model object also has a
    resources dictionary that can be used to "attach" any resources by clients,
    e.g. a lookup service instance, a transforms files pipeline etc.
    """

    def __init__(
        self,
        model_supplier_id,
        model_id,
        model_version_id,
        resources=None
    ):
        """
        Constructor - requires supplier ID, model ID and model version ID.
        """
        self._supplier_id = model_supplier_id
        self._model_id = model_id
        self._model_version_id = model_version_id
        self._key = '{}/{}/{}'.format(model_supplier_id, model_id, model_version_id)
        self._resources = resources if resources else {}


    @property
    def key(self):
        """
        Model key - getter only. Format is

            :getter: Returns <model supplier ID>/<model ID>/<model version ID>
            :type: string
        """
        return self._key


    @property
    def supplier_id(self):
        """
        Model supplier ID property - getter only.

            :getter: Gets the model supplier ID
            :type: string
        """
        return self._supplier_id


    @property
    def model_id(self):
        """
        Model ID property - getter only.

            :getter: Gets the model ID
            :type: string
        """        
        return self._model_id


    @property
    def model_version_id(self):
        """
        Model version ID property - getter only.

            :getter: Gets the model version ID
            :type: string
        """
        return self._model_version_id

    
    @property
    def resources(self, key=None):
        """
        Model resources dictionary property.

            :getter: Gets the attached resource in the model resources dict
                     using the optional resource ``key`` argument. If ``key``
                     is not given then the entire resources dict is returned.

            :setter: Sets the value of the optional resource ``key`` in the
                     resources dict to ``val``. If no ``key`` is given then
                     ``val`` is assumed to be a new resources dict and is
                     used to replace the existing dict.

            :deleter: Deletes the value of the optional resource ``key`` in
                      the resources dict. If no ``key`` is given then the
                      entire existing dict is cleared.
        """
        return self._resources[key] if key else self._resources

    
    @resources.setter
    def resources(self, key=None, val=None):
        if key:
            self._resources.update({key: val})
        else:
            self._resources.clear()
            self._resources.update(val)


    @resources.deleter
    def resources(self, key=None):
        if key:
            del self._resources[key]
        else:
            self._resources.clear()


    def get_keys(self, model_exposures=None, model_exposures_file_path=None, success_only=True):
        """
        Generates keys lookup records to file - requires either the string
        content of a model exposures file or the path of such a file, and
        also a lookup service instance for the model attached to the model
        object's resources dict property. The optional keyword argument
        ``success_only`` indicates whether only records with successful
        lookups should be returned (default), or all records.
        """
        if not any([model_exposures, model_exposures_file_path]):
            raise OasisException('No model exposures or model exposures file path provided')

        if 'lookup_service' not in self.resources:
            raise OasisException(
                'No lookup service attached to the model '
                '- please attach a lookup service for this model in the resources dict property'
            )

        for record in klsf.get_keys(
            lookup_service=self.resources['lookup_service'],
            model_exposures=model_exposures,
            model_exposures_file_path=model_exposures_file_path,
            success_only=success_only
        ):
            yield record


    def save_keys(
        self,
        model_exposures=None,
        model_exposures_file_path=None,
        success_only=True,
        output_file_path=None,
        format='oasis_keys'
    ):
        """
        Saves keys lookup records to file - requires either the string
        content of a model exposures file or the path of such a file, a lookup
        service instance for the model attached to the model object's
        resources dict property, path of the output file to save, and 
        the format of the output file (`oasis_keys` for Oasis keys file
        format or `list_keys` for a list of JSON records).

         The optional keyword argument ``success_only`` indicates whether
         only records with successful lookups should be returned (default),
         or all records.

        Returns a pair ``(f, n)`` where ``f`` is the output file object
        and ``n`` is the number of records written to the file.
        """
        if not any([model_exposures, model_exposures_file_path]):
            raise OasisException('No model exposures or model exposures file path provided')

        if 'lookup_service' not in self.resources:
            raise OasisException(
                'No lookup service attached to the model '
                '- please attach a lookup service for this model in the resources dict property'
            )

        if not output_file_path:
            raise OasisException('No output file path provided')

        f, n = klsf.save_keys(
            lookup_service=self.resources['lookup_service'],
            model_exposures=model_exposures,
            model_exposures_file_path=model_exposures_file_path,
            success_only=success_only,
            output_file_path=output_file_path,
            format=format
        )

        return f, n


    def __str__(self):
        return '{}: {}'.format(self.__repr__(), self.key)


    def __repr__(self):
        return '{}: {}'.format(self.__class__, self.__dict__)


    def _repr_pretty_(self, p, cycle):
       p.text(str(self) if not cycle else '...')


class OasisModelFactory(object):
    """
    Factory class for creating Oasis model objects.
    """
    
    @classmethod
    def create(
        cls,
        model_supplier_id,
        model_id,
        model_version_id,
        resources=None
    ):
        """
        Service method to instantiate Oasis model objects with attached
        resource dicts.
        """
        return OasisModel(
            model_supplier_id=model_supplier_id,
            model_id=model_id,
            model_version_id=model_version_id,
            resources=resources
        )
