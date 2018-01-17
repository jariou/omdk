#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.pardir))

from oasis_utils import OasisException

from OasisKeysLookupFactory import OasisKeysLookupFactory

__author__ = "Sandeep Murthy"
__copyright__ = "2017, Oasis Loss Modelling Framework"


SCRIPT_ARGS = {
    'keys_data_path': {
        'arg_name': 'keys_data_path',
        'flag': 'd',
        'type': str,
        'help_text': 'Keys data folder path',
        'required': True
    },
    'model_exposures_file_path': {
        'arg_name': 'model_exposures_file_path',
        'flag': 'e',
        'type': str,
        'help_text': 'Model exposures file path',
        'required': True
    },
    'output_format': {
        'arg_name': 'output_format',
        'flag': 'f',
        'type': str,
        'help_text': 'Keys records file output format: choices are `oasis_keys` and `list_keys`',
        'required': True
    },
    'lookup_package_path': {
        'arg_name': 'lookup_package_path',
        'flag': 'l',
        'type': str,
        'help_text': 'Path of the lookup service package - in the supplier repository this is usually the `src/keys_server` folder',
        'required': True
    },
    'output_file_path': {
        'arg_name': 'output_file_path',
        'flag': 'o',
        'type': str,
        'help_text': 'Keys records output file path',
        'required': True
    },
    'model_version_file_path': {
        'arg_name': 'model_version_file_path',
        'flag': 'v',
        'type': str,
        'help_text': 'Model version file path',
        'required': True
    },
}


def __parse_args__():
    """
    Parses script arguments and constructs an args dictionary.
    """
    parser = argparse.ArgumentParser(description='Generate keys records / Oasis keys files from keys lookup services')
    
    di = SCRIPT_ARGS

    map(
        lambda res: parser.add_argument(
            '-{}'.format(di[res]['flag']),
            '--{}'.format(di[res]['arg_name']),
            type=di[res]['type'],
            required=di[res]['required'],
            help=di[res]['help_text']
        ),
        di
    )
        
    args = parser.parse_args()

    args_dict = vars(args)

    map(
        lambda arg: args_dict.update({arg: os.path.abspath(args_dict[arg])}) if arg.endswith('path') else None,
        args_dict
    )

    return args_dict


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'
    )

    try:
        logging.info('Processing script arguments')
        args = __parse_args__()
        logging.info('\t{}'.format(args))

        
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
        logging.info(str(e))
        sys.exit(-1)

    logging.info('{} keys lookup records saved to file {}'.format(n, f))
    sys.exit(0)
