#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

`generate_oasis_files.py` is an executable script that can generate Oasis files for a model, given the following arguments (in no particular order)::

    ./generate_oasis_files.py -k /path/to/keys/data
                              -v /path/to/model/version/csv/file
                              -l /path/to/lookup/service/package
                              -p /path/to/canonical/exposures/profile/JSON/file
                              -e /path/to/source/exposures/file
                              -a /path/to/source/exposures/validation/file
                              -b /path/to/source/to/canonical/exposures/transformation/file
                              -c /path/to/canonical/exposures/validation/file
                              -d /path/to/canonical/to/model/exposures/transformation/file
                              -x /path/to/xtrans/executable
                              -o /path/to/oasis/files/directory

When calling the script this way paths can be given relative to the script, in particular, file paths should include the filename and extension. The paths to the keys data, lookup service package, model version file, canonical exposures profile JSON, source exposures file, transformation and validation files, will usually be located in the model keys server repository.

It is also possible to run the script by defining these arguments in a JSON configuration file and calling the script using the path to this file using the option `-f`. In this case the paths should be given relative to the parent folder in which the model keys server repository is located.::

    ./generate_oasis_files.py -f /path/to/model/resources/JSON/config/file

The JSON file contain the following keys (in no particular order)::

    "keys_data_path"
    "model_version_file_path"
    "lookup_package_path"
    "canonical_exposures_profile_json_path"
    "source_exposures_file_path"
    "source_exposures_validation_file_path"
    "source_to_canonical_exposures_transformation_file_path"
    "canonical_exposures_validation_file_path"
    "canonical_to_model_exposures_transformation_file_path"
    "xtrans_path"
    "oasis_files_path"

and the values of these keys should be string paths, given relative to the parent folder in which the model keys server repository is located. The JSON file is usually placed in the model keys server repository.
"""

import argparse
import io
import json
import logging
import os
import sys
import time

from oasis_utils import (
    OasisException,
)

import utils as mdk_utils
from models import OasisModelFactory as omf
from exposures import OasisExposuresManager as oem
from keys import OasisKeysLookupFactory as oklf

__author__ = "Sandeep Murthy"
__copyright__ = "2017, Oasis Loss Modelling Framework"


SCRIPT_ARGS_METADICT = {
    'config_file_path': {
        'arg_name': 'config_file_path',
        'flag': 'f',
        'type': str,
        'help_text': 'Model config path',
        'required': False
    },
    'keys_data_path': {
        'arg_name': 'keys_data_path',
        'flag': 'k',
        'type': str,
        'help_text': 'Keys data folder path for model keys lookup service',
        'required': False
    },
    'model_version_file_path': {
        'arg_name': 'model_version_file_path',
        'flag': 'v',
        'type': str,
        'help_text': 'Model version file path',
        'required': False
    },
    'lookup_package_path': {
        'arg_name': 'lookup_package_path',
        'flag': 'l',
        'type': str,
        'help_text': 'Package path for model keys lookup service - usually in the `src/keys_server` folder of the relevant supplier repository',
        'required': False
    },
    'canonical_exposures_profile_json_path': {
        'arg_name': 'canonical_exposures_profile_json_path',
        'flag': 'p',
        'type': str,
        'help_text': 'Path of the supplier canonical exposures profile JSON file',
        'required': False
    },
    'source_exposures_file_path': {
        'arg_name': 'source_exposures_file_path',
        'flag': 'e',
        'type': str,
        'help_text': 'Source exposures file path',
        'required': False
    },
    'source_exposures_validation_file_path': {
        'arg_name': 'source_exposures_validation_file_path',
        'flag': 'a',
        'type': str,
        'help_text': 'Source exposures validation file (XSD) path',
        'required': False
    },
    'source_to_canonical_exposures_transformation_file_path': {
        'arg_name': 'source_to_canonical_exposures_transformation_file_path',
        'flag': 'b',
        'type': str,
        'help_text': 'Source -> canonical exposures transformation file (XSLT) path',
        'required': False
    },
    'canonical_exposures_validation_file_path': {
        'arg_name': 'canonical_exposures_validation_file_path',
        'flag': 'c',
        'type': str,
        'help_text': 'Canonical exposures validation file (XSD) path',
        'required': False
    },
    'canonical_to_model_exposures_transformation_file_path': {
        'arg_name': 'canonical_to_model_exposures_transformation_file_path',
        'flag': 'd',
        'type': str,
        'help_text': 'Canonical -> model exposures transformation file (XSLT) path',
        'required': False
    },
    'xtrans_path': {
        'arg_name': 'xtrans_path',
        'flag': 'x',
        'type': str,
        'help_text': 'Path of the xtrans executable which performs the source -> canonical and canonical -> model exposures transformations',
        'required': False
    },
    'oasis_files_path': {
        'arg_name': 'oasis_files_path',
        'flag': 'o',
        'type': str,
        'help_text': 'Directory to place generated Oasis files for the model',
        'required': False
    }
}


if __name__ == '__main__':

    logger = mdk_utils.set_logging()
    logger.info('Console logging set')
    
    try:
        logger.info('Processing script resources arguments')
        args = mdk_utils.parse_script_args(SCRIPT_ARGS_METADICT, desc='Generate Oasis files for a model')

        if args['config_file_path']:
            logger.info('Loading script resources from config file {}'.format(args['config_file_path']))
            args = mdk_utils.load_script_args_from_config_file(args['config_file_path'])
            logger.info('Script resources: {}'.format(args))
        else:
            args.pop('config_file_path')
            logger.info('Script resources arguments: {}'.format(args))

        missing = filter(lambda res: not args[res] if res in args and res not in ['config_file_path', 'oasis_files_path'] else None, SCRIPT_ARGS_METADICT)

        if missing:
            raise OasisException('Not all script resources arguments provided - missing {}'.format(missing))

        logger.info('Getting model info and creating lookup service instance')
        model_info, model_klc = oklf.create(
            model_keys_data_path=args['keys_data_path'],
            model_version_file_path=args['model_version_file_path'],
            lookup_package_path=args['lookup_package_path']
        )
        time.sleep(3)
        logger.info('\t{}, {}'.format(model_info, model_klc))

        args['lookup'] = model_klc

        logger.info('Creating model object')
        model = omf.create(
            model_supplier_id=model_info['supplier_id'],
            model_id=model_info['model_id'],
            model_version_id=model_info['model_version_id']
        )
        logger.info('\t{}'.format(model))

        logger.info('Setting up Oasis files directory for model {}'.format(model.key))
        if 'oasis_files_path' in args and args['oasis_files_path']:
            if not os.path.exists(args['oasis_files_path']):
                os.mkdir(args['oasis_files_path'])
        else:
            base_dir = os.path.join(os.getcwd(), 'Files')
            logger.info('No Oasis files directory provided - creating one in {}'.format(base_dir))
            args['oasis_files_path'] = os.path.join(os.getcwd(), 'Files', model.key.replace('/', '-'))
            if not os.path.exists(args['oasis_files_path']):
                os.mkdir(args['oasis_files_path'])
        model.resources['oasis_files_path'] = args['oasis_files_path']
        logger.info('Oasis files directory {} set up for model {}'.format(model.resources['oasis_files_path'], model.key))

        logger.info('Creating an Oasis exposures manager for model')
        manager = oem(oasis_models=[model])
        logger.info('\t{}'.format(manager))

        logger.info('Generating Oasis files for model')
        oasis_files = manager.start_files_pipeline(model, with_model_resources=False, **args)

        logger.info('Generated Oasis files for model: {}'.format(oasis_files))
    except OasisException as e:
        logger.error(str(e))
        sys.exit(-1)

    sys.exit(0)
