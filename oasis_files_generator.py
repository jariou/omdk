#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Executable script for generating Oasis files for a given model. Requires
    that the necessary model meta information, such as the model version file,
    and resources required to create its keys lookup service, such as the
    path to the keys data folder and the lookup service source package, exist
    on the local filesystem, as well as the canonical exposures profile JSON
    file for the supplier/model, the xtrans.exe CSV conversion/ transformation
    tool for exposures files, the necessary validation and transformation files,
    and the source exposures file.

    Calling syntax (from base of ``omdk`` repository)::

        ./oasis_files_generator.py -k '/path/to/keys/data/folder'
                                   -v '/path/to/model/version/file'
                                   -l '/path/to/model/keys/lookup/service/package'
                                   -p '/path/to/canonical/exposures/profile/JSON/file'
                                   -e '/path/to/source/exposures/file'
                                   -a '/path/to/source/exposures/validation/file'
                                   -b '/path/to/source/to/canonical/exposures/transformation/file'
                                   -c '/path/to/canonical/exposures/validation/file'
                                   -d '/path/to/canonical/to/model/exposures/transformation/file'
                                   -x '/path/to/xtrans/executable'
                                   -o '/path/to/output/files/parent/directory'
"""

import argparse
import logging
import os
import sys
import time

from oasis_utils import (
    KeysLookupServiceFactory as klsf,
    OasisException,
)
from models import OasisModelFactory as omf
from exposures import OasisExposuresManager as oem


def set_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'
    )


def parse_args():
    """
    Parses script arguments and constructs an args dictionary.
    """
    parser = argparse.ArgumentParser(description='Generate Oasis files for a given model')
    
    parser.add_argument(
        '-k',
        '--keys_data_path',
        type=str,
        required=True,
        help='Keys data folder path for model keys lookup service'
    )

    parser.add_argument(
        '-v',
        '--model_version_file_path',
        type=str,
        required=True,
        help="Model version file path"
    )
    
    parser.add_argument(
        '-l',
        '--lookup_service_package_path',
        type=str,
        required=True,
        help="Package path for model keys lookup service - usually in the `src/keys_server` folder of the relevant supplier repository" 
    )

    parser.add_argument(
        '-p',
        '--canonical_exposures_profile_json_path',
        type=str,
        required=True,
        help="Path of the supplier's canonical exposures profile JSON file" 
    )

    parser.add_argument(
        '-e',
        '--source_exposures_file_path',
        type=str,
        required=True,
        help="Source exposures file path for model"
    )

    parser.add_argument(
        '-a',
        '--source_exposures_validation_file_path',
        type=str,
        required=True,
        help="Source exposures validation file path"
    )

    parser.add_argument(
        '-b',
        '--source_to_canonical_exposures_transformation_file_path',
        type=str,
        required=True,
        help="Source exposures validation file path"
    )

    parser.add_argument(
        '-c',
        '--canonical_exposures_validation_file_path',
        type=str,
        required=True,
        help="Canonical exposures validation file path"
    )

    parser.add_argument(
        '-d',
        '--canonical_to_model_exposures_transformation_file_path',
        type=str,
        required=True,
        help="Source exposures validation file path"
    )

    parser.add_argument(
        '-x',
        '--xtrans_path',
        type=str,
        required=True,
        help="Path of the `xtrans.exe` executable that performs the CSV transformations - can be compiled from the `Flamingo/xtrans/xtrans.cs` C# script"
    )

    parser.add_argument(
        '-o',
        '--output_basedirpath',
        type=str,
        required=True,
        help='Path of the parent directory where the Oasis files for the model should be generated'
    )

    args = parser.parse_args()

    args_dict = vars(args)

    map(lambda arg: args_dict.update({arg: os.path.abspath(args_dict[arg])}) if arg.endswith('path') else None, args_dict)

    return args_dict


if __name__ == '__main__':
    """
    Main block.
    """
    
    set_logging()
    logging.info('Console logging set')
    
    try:
        logging.info('Processing script arguments')
        args = parse_args()
        logging.info('Script arguments: {}'.format(args))

        logging.info('Getting model info and creating lookup service instance')
        model_info, model_kls = klsf.create(
            model_keys_data_path=args['keys_data_path'],
            model_version_file_path=args['model_version_file_path'],
            lookup_service_package_path=args['lookup_service_package_path']
        )
        time.sleep(3)
        logging.info('\t{}, {}'.format(model_info, model_kls))

        args['lookup_service'] = model_kls

        logging.info('Creating model object')
        model = omf.create(
            model_supplier_id=model_info['supplier_id'],
            model_id=model_info['model_id'],
            model_version_id=model_info['model_version_id']
        )
        logging.info('\t{}'.format(model))

        logging.info('Creating an Oasis exposures manager for the model')
        manager = oem(oasis_models=[model])
        logging.info('\t{}'.format(manager))

        logging.info('Adding output files directory path to `**args`')
        args['output_dirpath'] = model.resources['output_dirpath']

        logging.info('Generating Oasis files for the model')
        oasis_files = manager.start_files_pipeline(model, with_model_resources=False, **args)

        logging.info('\t{}'.format(oasis_files))
    except OasisException as e:
        logging.error(str(e))
        sys.exit(-1)
    else:
        sys.exit(0)
