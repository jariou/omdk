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

    The script can be executed in two ways: (1) directly by providing all the
    resources in the script call using the following syntax::

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

    or by providing the path to a JSON script config file which defines all
    the script resources - the syntax for the latter option is::

        ./oasis_files_generator.py -f '/path/to/model/resources/JSON/config/file'

    and the keys of the JSON config file should be named as follows::

        "keys_data_path"
        "model_version_file_path"
        "lookup_service_package_path"
        "canonical_exposures_profile_json_path"
        "source_exposures_file_path"
        "source_exposures_validation_file_path"
        "source_to_canonical_exposures_transformation_file_path"
        "canonical_exposures_validation_file_path"
        "canonical_to_model_exposures_transformation_file_path"
        "xtrans_path"
        "output_basedirpath"

    The file and folder paths can be relative to the path of the script. If you've cloned
    the OMDK repository then script configs for models can be placed in the `script_config`
    subfolder, and the canonical exposures profiles can be placed in the
    `canonical_exposures_profiles` subfolder.
"""

import argparse
import io
import json
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

__author__ = "Sandeep Murthy"
__copyright__ = "2017, Oasis Loss Modelling Framework"


SCRIPT_RESOURCES = {
    'config_file_path': {
        'arg_name': 'config_file_path',
        'flag': 'f',
        'type': str,
        'help_text': 'Path for script config for model',
        'directly_required': False
    },
    'keys_data_path': {
        'arg_name': 'keys_data_path',
        'flag': 'k',
        'type': str,
        'help_text': 'Keys data folder path for model keys lookup service',
        'directly_required': False
    },
    'model_version_file_path': {
        'arg_name': 'model_version_file_path',
        'flag': 'v',
        'type': str,
        'help_text': 'Model version file path',
        'directly_required': False
    },
    'lookup_service_package_path': {
        'arg_name': 'lookup_service_package_path',
        'flag': 'l',
        'type': str,
        'help_text': 'Package path for model keys lookup service - usually in the `src/keys_server` folder of the relevant supplier repository',
        'directly_required': False
    },
    'canonical_exposures_profile_json_path': {
        'arg_name': 'canonical_exposures_profile_json_path',
        'flag': 'p',
        'type': str,
        'help_text': 'Path of the supplier canonical exposures profile JSON file',
        'directly_required': False
    },
    'source_exposures_file_path': {
        'arg_name': 'source_exposures_file_path',
        'flag': 'e',
        'type': str,
        'help_text': 'Source exposures file path',
        'directly_required': False
    },
    'source_exposures_validation_file_path': {
        'arg_name': 'source_exposures_validation_file_path',
        'flag': 'a',
        'type': str,
        'help_text': 'Source exposures validation file (XSD) path',
        'directly_required': False
    },
    'source_to_canonical_exposures_transformation_file_path': {
        'arg_name': 'source_to_canonical_exposures_transformation_file_path',
        'flag': 'b',
        'type': str,
        'help_text': 'Source -> canonical exposures transformation file (XSLT) path',
        'directly_required': False
    },
    'canonical_exposures_validation_file_path': {
        'arg_name': 'canonical_exposures_validation_file_path',
        'flag': 'c',
        'type': str,
        'help_text': 'Canonical exposures validation file (XSD) path',
        'directly_required': False
    },
    'canonical_to_model_exposures_transformation_file_path': {
        'arg_name': 'canonical_to_model_exposures_transformation_file_path',
        'flag': 'd',
        'type': str,
        'help_text': 'Canonical -> model exposures transformation file (XSLT) path',
        'directly_required': False
    },
    'xtrans_path': {
        'arg_name': 'xtrans_path',
        'flag': 'x',
        'type': str,
        'help_text': 'Path of the xtrans executable which performs the source -> canonical and canonical -> model exposures transformations',
        'directly_required': False
    },
    'output_basedirpath': {
        'arg_name': 'output_basedirpath',
        'flag': 'o',
        'type': str,
        'help_text': 'Parent directory to place generated Oasis files for the model',
        'directly_required': False
    }
}


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

    di = SCRIPT_RESOURCES

    map(
        lambda res: parser.add_argument(
            '-{}'.format(di[res]['flag']),
            '--{}'.format(di[res]['arg_name']),
            type=di[res]['type'],
            required=di[res]['directly_required'],
            help=di[res]['help_text']
        ),
        di
    )

    args = parser.parse_args()

    args_dict = vars(args)

    map(
        lambda arg: args_dict.update({arg: os.path.abspath(args_dict[arg])}) if arg.endswith('path') and args_dict[arg] else None,
        args_dict
    )

    return args_dict


def load_args_from_config_file(config_file_path):
    if config_file_path.endswith('json'):
        try:
            with io.open(config_file_path, 'r', encoding='utf-8') as f:
                args = json.load(f)
        except (IOError, ValueError, TypeError) as e:
            raise OasisException('Error parsing resources config file {}: {}'.format(config_file_path, str(e)))
    elif config_file_path.endswith('yaml') or config_file_path.endswith('yml'):
        pass

    return args


if __name__ == '__main__':

    set_logging()
    logger = logging.getLogger()
    logger.info('Console logging set')
    
    try:
        logger.info('Processing script resources arguments')
        args = parse_args()

        if args['config_file_path']:
            logger.info('Loading script resources from config file {}'.format(args['config_file_path']))
            args = load_args_from_config_file(args['config_file_path'])
            logger.info('Script resources: {}'.format(args))
        else:
            args.pop('config_file_path')
            logger.info('Script resources arguments: {}'.format(args))
        
        missing = filter(lambda res: not args[res] if res in args and res != 'config_file_path' else None, SCRIPT_RESOURCES)

        if missing:
            raise OasisException('Not all script resources arguments provided - missing {}'.format(missing))

        logger.info('Getting model info and creating lookup service instance')
        model_info, model_kls = klsf.create(
            model_keys_data_path=args['keys_data_path'],
            model_version_file_path=args['model_version_file_path'],
            lookup_service_package_path=args['lookup_service_package_path']
        )
        time.sleep(3)
        logger.info('\t{}, {}'.format(model_info, model_kls))

        args['lookup_service'] = model_kls

        logger.info('Creating model object')
        model = omf.create(
            model_supplier_id=model_info['supplier_id'],
            model_id=model_info['model_id'],
            model_version_id=model_info['model_version_id']
        )
        logger.info('\t{}'.format(model))

        logger.info('Creating an Oasis exposures manager for the model')
        manager = oem(oasis_models=[model])
        logger.info('\t{}'.format(manager))

        logger.info('Adding output files directory path to `**args`')
        args['output_dirpath'] = model.resources['output_dirpath']

        logger.info('Generating Oasis files for the model')
        oasis_files = manager.start_files_pipeline(model, with_model_resources=False, **args)

        logger.info('\t{}'.format(oasis_files))
    except OasisException as e:
        logger.error(str(e))
        sys.exit(-1)
    else:
        sys.exit(0)
