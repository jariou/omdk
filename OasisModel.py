#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisModel'
]

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
        model_version_id
    ):
        """
        Constructor - requires supplier ID, model ID and model version ID.
        """
        self._supplier_id = model_supplier_id
        self._model_id = model_id
        self._model_version_id = model_version_id
        self._key = '{}/{}/{}'.format(model_supplier_id, model_id, model_version_id)
        self._resources = {}


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
