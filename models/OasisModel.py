# -*- coding: utf-8 -*-

# BSD 3-Clause License
# 
# Copyright (c) 2017-2020, Oasis Loss Modelling Framework
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = [
    'OasisModel',
    'OasisModelFactory'
]

import os

if os.getcwd().split(os.path.sep)[-1] == 'models':
    sys.path.insert(0, os.path.abspath(os.pardir))

from oasis_utils import OasisException


class OasisModel(object):
    """
    A simple object representation of Oasis models and their resources - an
    Oasis model is identified by a triple: a specific supplier ID, model ID
    and model version. The constructor requires these three arguments
    for creating a new Oasis model object. Each model object also has a
    resources dictionary that can be used to "attach" any resources by clients,
    e.g. a lookup service instance, a transforms files pipeline, validation
    and transformation files for the source -> canonical and canonical
    -> model exposure transforms, etc.
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
