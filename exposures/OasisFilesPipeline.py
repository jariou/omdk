#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisFilesPipeline'
]

__author__ = "Sandeep Murthy"
__copyright__ = "Oasis Loss Modelling Framework 2017"


class OasisFilesPipeline(object):

    def __init__(
        self,
        model_key=None,
        source_exposures_file=None,
        canonical_exposures_file=None,
        model_exposures_file=None,
        keys_file=None
    ):
        self._model_key = model_key
        self._source_exposures_file = source_exposures_file
        self._canonical_exposures_file = canonical_exposures_file
        self._model_exposures_file = model_exposures_file
        self._keys_file = keys_file

        self._items_file = None
        self._coverages_file = None
        self._gulsummaryxref_file = None

        self._oasis_files = {
            'items': self._items_file,
            'coverages': self._coverages_file,
            'gulsummaryxref': self._gulsummaryxref_file
        }


    @classmethod
    def create(
        cls,
        model_key=None,
        source_exposures_file=None,
        canonical_exposures_file=None,
        model_exposures_file=None,
        keys_file=None
    ):
        """
        Class method that returns an instance of an Oasis files pipeline
        as used in exposures management.
        """
        return cls(
            model_key=model_key,
            source_exposures_file=source_exposures_file,
            canonical_exposures_file=canonical_exposures_file,
            model_exposures_file=model_exposures_file,
            keys_file=keys_file
        )

    @property
    def model_key(self):
        """
        Model key property - getter only.

            :getter: Gets the key of model to which the pipeline is attached.
        """
        return self._model_key


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
    def canonical_exposures_file(self):
        """
        Canonical exposures file property.

            :getter: Gets the actual file object
            :setter: Sets the file to the specified file object
            :deleter: Deletes the file object
        """
        return self._canonical_exposures_file


    @canonical_exposures_file.setter
    def canonical_exposures_file(self, f):
        self._canonical_exposures_file = f


    @canonical_exposures_file.deleter
    def canonical_exposures_file(self):
        del self._canonical_exposures_file


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
        self._items_file = self.oasis_files['items'] = f


    @items_file.deleter
    def items_file(self):
        del self._items_file
        self.oasis_files['items'] = None


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
        self._coverages_file = self.oasis_files['coverages'] = f


    @coverages_file.deleter
    def coverages_file(self):
        del self._coverages_file
        self.oasis_files['coverages'] = None


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
        self._gulsummaryxref_file = self.oasis_files['gulsummaryxref'] = f
        self.oasis_files['gulsummaryxref'] = None


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


    def clear(self):
        """
        Clears all file attributes in the pipeline.
        """
        file_attribute_names = filter(
            lambda p: p,
            map(
                lambda p: p.strip('_') if 'model_key' not in p and 'oasis_files' not in p else None,
                self.__dict__.keys()
            )
        )

        map(
            lambda f: setattr(self, f, None),
            file_attribute_names
        )


    def __str__(self):
        return '{}: {}'.format(self.__repr__(), self.model_key)


    def __repr__(self):
        return '{}: {}'.format(self.__class__, self.__dict__)


    def _repr_pretty_(self, p, cycle):
       p.text(str(self) if not cycle else '...')
