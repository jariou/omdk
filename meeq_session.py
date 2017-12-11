import io
import os
import sys

import pandas as pd

from oasis_utils import KeysLookupServiceFactory as klsf

_, meeq_kls = klsf.create('../Catrisks/keys_data/MEEQ', '../Catrisks/keys_data/MEEQ/ModelVersion.csv', '../Catrisks/src/keys_server')

from models import OasisModelFactory as omf

meeq = omf.create('Catrisks', 'MEEQ', '0.0.0.6', resources={'lookup_service': meeq_kls})

from exposures import OasisExposuresManager as oem

manager = oetm.create(oasis_models=[meeq])

meeq = manager.models[meeq.key]

meeq.resources['xtrans_path'] = os.path.abspath('../Flamingo/xtrans/test/xtrans.exe')
meeq.resources['canonical_exposures_profile_json_path'] = os.path.abspath('canonical_exposures_profiles/catrisks_canonical_profile.json')
meeq.resources['source_exposures_validation_file_path'] = os.path.abspath('../Catrisks/flamingo/ValidationFiles/Catrisks_SourceLoc.xsd')
meeq.resources['source_to_canonical_exposures_transformation_file_path'] = os.path.abspath('../Catrisks/flamingo/TransformationFiles/MappingMapToCatrisks_CanLoc_A.xslt')
meeq.resources['canonical_exposures_validation_file_path'] = os.path.abspath('../Catrisks/flamingo/ValidationFiles/Catrisks_CanLoc_B.xsd')
meeq.resources['canonical_to_model_exposures_transformation_file_path'] = os.path.abspath('../Catrisks/flamingo/TransformationFiles/MappingMapToCatrisks_ModelLoc.xslt')

with io.open('tests/data/input/Catrisks/MEEQ/test/catrisks_meeq_source_loc.csv', 'r', encoding='utf-8') as s:
    with io.open('tests/data/input/Catrisks/MEEQ/test/catrisks_meeq_can_loc.csv', 'w', encoding='utf-8') as c:
        with io.open('tests/data/input/Catrisks/MEEQ/test/catrisks_meeq_model_loc.csv', 'w', encoding='utf-8') as m:
            with io.open('tests/data/input/Catrisks/MEEQ/test/catrisks_meeq_keys.csv', 'w', encoding='utf-8') as k:
                meeq.resources['oasis_files_pipeline'].source_exposures_file = s
                meeq.resources['oasis_files_pipeline'].canonical_exposures_file = c
                meeq.resources['oasis_files_pipeline'].model_exposures_file = m
                meeq.resources['oasis_files_pipeline'].keys_file = k

