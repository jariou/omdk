"""
Session to perform MEEQ exposure transforms using the Oasis exposure management
framework in the OMDK repository

    https://github.com/OasisLMF/OMDK
"""

import io
import os
import sys

import pandas as pd

from oasis_utils import KeysLookupServiceFactory as klsf

_, meeq_kls = klsf.create('../Catrisks/keys_data/MEEQ', '../Catrisks/keys_data/MEEQ/ModelVersion.csv', '../Catrisks/src/keys_server')

from omdk.models import OasisModelFactory as omf

meeq_resources = resources = {
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

meeq = omf.create('Catrisks', 'MEEQ', '0.0.0.6', resources=resources)

from omdk.exposures import OasisExposuresManager as oem

manager = oem.create(oasis_models=[meeq])

manager.start_files_pipeline(meeq)

oasis_files = meeq.resources['oasis_files_pipeline'].oasis_files
