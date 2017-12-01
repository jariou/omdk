#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisExposureTransformsFilesPipeline'
]

class OasisExposureTransformsFilesPipeline(object):

    def __init__(self,
        source_exposures_file=None,
        canonical_exposures_profile=None
    ):
        self._source_exposures_file = source_exposures_file
        self._canonical_exposures_profile = canonical_exposures_profile


    @classmethod
    def create(cls, source_exposures_file=None, canonical_exposures_profile=None):
        """
        Class method that returns an instance of an Oasis transforms files
        pipeline.
        """
        return cls(
            source_exposures_file=source_exposures_file,
            canonical_exposures_profile=canonical_exposures_profile
        )


    @property
    def source_exposures_file(self):
        """
        Source exposures file property.

            :getter: Gets the actual file object
            :setter: Sets the file to the specified file object
            :deleter: Deletes the file object
        """
        return self._source_exposures_file


    @source_exposures_file.setter
    def source_exposures_file(self, f):
        self._source_exposures_file = f


    @source_exposures_file.deleter
    def source_exposures_file(self):
        del self._source_exposures_file


    @property
    def canonical_exposures_profile(self):
        """
        Canonical exposures profile property.

            :getter: Gets the actual file object
            :setter: Sets the file to the specified file object
            :deleter: Deletes the file object
        """
        return self._canonical_exposures_file


    @canonical_exposures_profile.setter
    def canonical_exposures_profile(self, f):
        self._canonical_exposures_profile = f


    @canonical_exposures_profile.deleter
    def canonical_exposures_profile(self):
        del self._canonical_exposures_profile


    @property
    def model_exposures_file(self):
        """
        Model exposures file property.

            :getter: Gets the actual file object
            :setter: Sets the file to the specified file object
            :deleter: Deletes the file object
        """
        return self._model_exposures_file


    @model_exposures_file.setter
    def model_exposures_file(self, f):
        self._model_exposures_file = f


    @model_exposures_file.deleter
    def model_exposures_file(self):
        del self._model_exposures_file


    @property
    def keys_file(self):
        """
        Oasis keys file property.

            :getter: Gets the actual file object
            :setter: Sets the file to the specified file object
            :deleter: Deletes the file object
        """
        return self._keys_file


    @keys_file.setter
    def keys_file(self, f):
        self._keys_file = f


    @keys_file.deleter
    def keys_file(self):
        del self._keys_file


    @property
    def items_file(self):
        """
        Oasis items file property.

            :getter: Gets the actual file object
            :setter: Sets the file to the specified file object
            :deleter: Deletes the file object
        """
        return self._items_file


    @items_file.setter
    def items_file(self, f):
        self._items_file = f


    @items_file.deleter
    def items_file(self):
        del self._items_file


    @property
    def coverages_file(self):
        """
        Oasis coverages file property.

            :getter: Gets the actual file object
            :setter: Sets the file to the specified file object
            :deleter: Deletes the file object
        """
        return self._coverages_file


    @coverages_file.setter
    def coverages_file(self, f):
        self._coverages_file = f


    @coverages_file.deleter
    def coverages_file(self):
        del self._coverages_file


    @property
    def gulsummaryxref_file(self):
        """
        GUL summary file property.

            :getter: Gets the actual file object
            :setter: Sets the file to the specified file object
            :deleter: Deletes the file object
        """
        return self._gulsummaryxref_file


    @gulsummaryxref_file.setter
    def gulsummaryxref_file(self, f):
        self._gulsummaryxref_file = f


    @gulsummaryxref_file.deleter
    def gulsummaryxref_file(self):
        del self._gulsummaryxref_file


    @property
    def oasis_files(self):
        """
        Oasis files set property - getter only.

            :getter: Gets the complete set of generated Oasis files, including
                     ``items.csv``, ``coverages.csv``, `gulsummaryxref.csv`.
        """
        return self._oasis_files


