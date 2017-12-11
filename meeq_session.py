"""
Session to perform MEEQ exposure transforms using the Oasis exposure management
framework in the OMDK repository

    https://github.com/OasisLMF/OMDK

Please copy this file to your directory of choice, and clone the Catrisks and
OMDK repositories, side by side, in the parent directory.

    ...
    /your/parent/directory/
    |__ meeq_session.py
    |__ Catrisks/
    |__ omdk

Also ensure that you have the necessary Python package requirements for `omdk`
and `oasis_utils`, as well as the `xtrans.exe` executable that performs the
source loc. -> canonical loc., and canonical loc. -> model loc.
transformations.

You can execute the statements in this module either by copying them into
a Python shell in the parent directory, or by running this as a script using

    python -m meeq_session.py

provided that this file is in the parent directory.

Please use recursive Git cloning to clone the two repositories.

    git clone --recursive git+ssh://git@github.com/OasisLMF/Catrisks
    git clone --recursive git+ssh://git@github.com/OasisLMF/omdk

Please ensure that you have the Catrisks MEEQ keys data, model version file
on your filesystem - you can adjust the paths of these in the call to the
`create` method of the lookup service factory class, below.
"""

import os

from oasis_utils import KeysLookupServiceFactory as klsf

model_info, meeq_kls = klsf.create(
    model_keys_data_path='Catrisks/keys_data/MEEQ',
    model_version_file_path='Catrisks/keys_data/MEEQ/ModelVersion.csv',
    lookup_service_package_path='Catrisks/src/keys_server'
)

from omdk.models import OasisModelFactory as omf

meeq_resources = {
    'lookup_service': meeq_kls,
    'output_basedirpath': os.path.abspath('omdk/Files'),
    'xtrans_path': os.path.abspath('Flamingo/xtrans/test/xtrans.exe'),
    'source_exposures_file_path': os.path.abspath('Catrisks/keys_data/MEEQ/MEEQ_loc.csv'),
    'source_exposures_validation_file_path': os.path.abspath('Catrisks/flamingo/ValidationFiles/Catrisks_SourceLoc.xsd'),
    'source_to_canonical_exposures_transformation_file_path': os.path.abspath('Catrisks/flamingo/TransformationFiles/MappingMapToCatrisks_CanLoc_A.xslt'),
    'canonical_exposures_validation_file_path': os.path.abspath('Catrisks/flamingo/ValidationFiles/Catrisks_CanLoc_B.xsd'),
    'canonical_to_model_exposures_transformation_file_path': os.path.abspath('Catrisks/flamingo/TransformationFiles/MappingMapToCatrisks_ModelLoc.xslt'),
    'canonical_exposures_profile_json_path': os.path.abspath('omdk/canonical_exposures_profiles/catrisks_canonical_profile.json')
}

meeq = omf.create(
    model_info['supplier_id'],
    model_info['model_id'],
    model_info['model_version_id'],
    resources=meeq_resources
)

from omdk.exposures import OasisExposuresManager as oem

manager = oem.create(oasis_models=[meeq])

manager.start_files_pipeline(meeq)

oasis_files = meeq.resources['oasis_files_pipeline'].oasis_files
