#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
`run_keys_lookup.py` is an executable script that can generate keys records and Oasis files keys for a model, given the following arguments (in no particular order)::

    ./run_keys_lookup.py -k /path/to/keys/data
                         -v /path/to/model/version/csv/file
                         -l /path/to/lookup/service/package
                         -e /path/to/model/exposures/csv/file
                         -o /path/to/output/file
                         -f <output format - `oasis_keys` or `list_keys`>

When calling the script this way paths can be given relative to the script, in particular, file paths should include the filename and extension. The paths to the keys data, lookup service package, and model version file will usually be located in the model keys server (Git) repository, which would also contain the lookup service source code for the model (lookup service package. The lookup service package is usually located in the `src/keys_server` Python subpackage in the model keys serer repository (if it is managed by Oasis LMF).

It is also possible to run the script by defining these arguments in a JSON configuration file and calling the script using the path to this file using the option `-f`. In this case the paths should be given relative to the parent folder in which the model keys server repository is located.::

    ./run_keys_lookup.py -f /path/to/keys/script/config/file

The JSON file should contain the following keys (in no particular order)::

    "keys_data_path"
    "model_version_file_path"
    "lookup_package_path"
    "model_exposures_file_path"
    "output_file_path"
    "output_format"

and the values of these keys should be string paths, given relative to the parent folder in which the model keys server repository is located. The JSON file is usually placed in the model keys server repository.
"""

import argparse
import logging
import os
import sys

from oasis_utils import OasisException

from keys import OasisKeysLookupFactory

import utils as mdk_utils


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
        'help_text': 'Keys data folder path',
        'required': False
    },
    'model_exposures_file_path': {
        'arg_name': 'model_exposures_file_path',
        'flag': 'e',
        'type': str,
        'help_text': 'Model exposures file path',
        'required': False
    },
    'output_format': {
        'arg_name': 'output_format',
        'flag': 't',
        'type': str,
        'help_text': 'Keys records file output format: choices are `oasis_keys` and `list_keys`',
        'required': False
    },
    'lookup_package_path': {
        'arg_name': 'lookup_package_path',
        'flag': 'l',
        'type': str,
        'help_text': 'Path of the lookup service package - in the supplier repository this is usually the `src/keys_server` folder',
        'required': False
    },
    'output_file_path': {
        'arg_name': 'output_file_path',
        'flag': 'o',
        'type': str,
        'help_text': 'Keys records output file path',
        'required': False
    },
    'model_version_file_path': {
        'arg_name': 'model_version_file_path',
        'flag': 'v',
        'type': str,
        'help_text': 'Model version file path',
        'required': False
    },
}


if __name__ == '__main__':

    logger = mdk_utils.set_logging()
    logger.info('Console logging set')

    try:
        logging.info('Processing script resources arguments')
        args = mdk_utils.parse_script_args(SCRIPT_ARGS_METADICT, desc='Generate Oasis keys file for a model')
        
        if args['config_file_path']:
            logger.info('Loading script resources from config file {}'.format(args['config_file_path']))
            args = mdk_utils.load_script_args_from_config_file(args['config_file_path'])
            logger.info('Script resources: {}'.format(args))
        else:
            args.pop('config_file_path')
            logger.info('Script resources arguments: {}'.format(args))

        missing = filter(lambda res: not args[res] if res in args and res not in ['config_file_path'] else None, SCRIPT_ARGS_METADICT)

        if missing:
            raise OasisException('Not all script resources arguments provided - missing {}'.format(missing))

        logging.info('Creating Oasis keys lookup factory')
        oklf = OasisKeysLookupFactory()
        logging.info('\t{}'.format(oklf))

        logging.info('Getting model info and creating lookup service instance')
        model_info, model_klc = oklf.create(
            model_keys_data_path=args['keys_data_path'],
            model_version_file_path=args['model_version_file_path'],
            lookup_package_path=args['lookup_package_path']
        )
        logging.info('\t{}, {}'.format(model_info, model_klc))

        logging.info('Saving keys lookup records to file')
        f, n = oklf.save_keys(
            lookup=model_klc,
            model_exposures_file_path=args['model_exposures_file_path'],
            output_file_path=args['output_file_path'],
            format=args['output_format']
        )
    except OasisException as e:
        logging.error(str(e))
        sys.exit(-1)

    logging.info('{} keys lookup records saved to file {}'.format(n, f))
    sys.exit(0)
