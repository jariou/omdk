#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'OasisExposuresManagerInterface'
]

from interface import Interface

__author__ = "Sandeep Murthy"
__copyright__ = "Oasis Loss Modelling Framework 2017"


class OasisExposuresManagerInterface(Interface):
    """
    An interface for defining the behaviour of an Oasis exposures manager.
    """

    def __init__(self, oasis_models=None):
        """
        Class constructor - not generally to be used directly.
        """
        pass


    @classmethod
    def create(cls, oasis_models=None, **kwargs):
        """
        Class method that returns an instance of an Oasis exposures
        manager. The optional ``oasis_models`` argument should be a list of
        Oasis model objects (``omdk.OasisModel.OasisModel``), and any
        additional resources can be specified in ``kwargs``.
        """
        pass


    def clear_files_pipeline(self, oasis_model, **kwargs):
        """
        Clears the exposure transforms files pipeline for the given
        ``oasis_model`` optionally using additional arguments in the ``kwargs``
        dict.

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        In the design of the exposure transform framework a model's files
        pipeline is an object value in its resources dict with the key
        ``transforms_files_pipeline`` and is thereby accessible with

            `oasis_model.resources['transforms_files_pipeline']`

        This returns an object of type

            `exposure_transforms.OasisExposureTransformsFilesPipeline`

        which stores the different files in the transformation stages for the
        model as property attributes, e.g.

            `oasis_model.resources['transforms_files_pipeline'].source_exposures_file`

        A standard implementation could either assign a new object of this
        type in the call to ``clear_files_pipeline``, or set some subset of the
        file attributes of this pipelines object to null.
        """
        pass


    def start_files_pipeline(self, oasis_model, **kwargs):
        """
        Starts the exposure transforms pipeline for the given ``oasis_model``,
        i.e. the generation of the canonical exposures files, keys file
        and finally the Oasis files.

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of a manager of whether to
        use the model object resources dict or additional optional arguments
        in ``kwargs`` for this process.

        In a standard implementation of the manager the call to
        `start_files_pipeline` should trigger calls to the individual methods for
        performing file transformations in a normal sequence, e.g.

            `transform_source_to_canonical`
            `transform_canonical_to_model`
            `transform_model_to_keys`
            `load_canonical_profile`
            `generate_oasis_files`

        and the generated files should be stored as attributes in the given
        model object's transforms files pipeline.
        """
        pass


    def save_files_pipeline(self, oasis_model, **kwargs):
        """
        Saves the files in the given ``oasis_model``'s transforms files
        pipeline to some data store, e.g. local filesystem, database etc.

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of the manager as to what type
        of store to use for saving pipelines.
        """
        pass


    def transform_source_to_canonical(self, oasis_model, **kwargs):
        """
        Transforms the source exposures/locations file for a given
        ``oasis_model`` object to a canonical/standard Oasis format.

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.
        
        The transform is generic by default, but could be supplier specific if
        required.
        """
        pass


    def transform_canonical_to_model(self, oasis_model, **kwargs):
        """
        Transforms the canonical exposures/locations file for a given
        ``oasis_model`` object to a format understood by Oasis keys lookup
        services.

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.
        """
        pass


    def get_keys(self, oasis_model, **kwargs):
        """
        Generates the model exposures/locations file for a given
        ``oasis_model`` object to the Oasis keys CSV file format:

            ``LocID,PerilID,CoverageID,AreaPerilID,VulnerabilityID``


        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.

        A "standard" implementation should use the lookup service factory
        class in ``oasis_utils`` (a submodule of `omdk`) namely
        
            ``oasis_utils.oasis_keys_lookup_service_utils.KeysLookupServiceFactory``
        """
        pass


    def load_canonical_profile(self, oasis_model, **kwargs):
        """
        Loads a JSON file representing the canonical exposures profile for a
        given ``oasis_model``.

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.
        """
        pass


    def generate_items_file(self, oasis_model, **kwargs):
        """
        Generates an items file for the given ``oasis_model``.
        """
        pass


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

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.
        """
        pass
