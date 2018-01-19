#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Master script for end-to-end model run.

Ensure that a model run directory exists, containing the analysis settings JSON
file and also the model static data (in a subfolder named 'static'). Also ensure
that you have the ktools binaries installed on your system.

The script can then be executed in two ways: (1) directly by providing all the
resources in the script call using the following syntax::

    ./run_model.py -k '/path/to/keys/data/folder'
                   -v '/path/to/model/version/file'
                   -l '/path/to/model/keys/lookup/service/package'
                   -p '/path/to/canonical/exposures/profile/JSON/file'
                   -e '/path/to/source/exposures/file'
                   -a '/path/to/source/exposures/validation/file'
                   -b '/path/to/source/to/canonical/exposures/transformation/file'
                   -c '/path/to/canonical/exposures/validation/file'
                   -d '/path/to/canonical/to/model/exposures/transformation/file'
                   -x '/path/to/xtrans/executable'
                   -o '/path/to/oasis/files/directory'
                   -j '/path/to/analysis/settings/json/file'
                   -s '<ktools script name (without file extension)>'
                   -r '/path/to/model/run/directory'
                   -n '<number of processes to use for ktools calcs.>'

or by providing the path to a JSON script config file which defines all
the script resources - the syntax for the latter option is::

    ./run_model.py -f '/path/to/model/resources/JSON/config/file'

and the keys of the JSON config file should be named as follows::

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
    "analysis_settings_json_file_path"
    "ktools_script_name"
    "model_run_dir_path"
    "ktools_num_processes"

The file and folder paths can be relative to the path of the script. If you've cloned
the OMDK repository then script configs for models can be placed in the ``model_run_config``
subfolder, and the canonical exposures profiles can be placed in the
``canonical_exposures_profiles`` subfolder.
"""

import argparse
import io
import json
import logging
import os
import subprocess
import sys

from oasis_utils import (
    create_binary_files,
    OasisException,
    prepare_model_run_directory,
    prepare_model_run_inputs,
)

import utils as mdk_utils

__author__ = "Sandeep Murthy"
__copyright__ = "2017, Oasis Loss Modelling Framework"


SCRIPT_ARGS_METADICT = {
    'config_file_path': {
        'arg_name': 'config_file_path',
        'flag': 'f',
        'type': str,
        'help_text': 'Path for script config for model',
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
    'analysis_settings_json_file_path': {
        'arg_name': 'analysis_settings_json_file_path',
        'flag': 'j',
        'type': str,
        'help_text': 'Model analysis settings JSON file path',
        'required': False
    },
    'ktools_script_name': {
        'arg_name': 'ktools_script_name',
        'flag': 's',
        'type': str,
        'help_text': 'Name of ktools model run script',
        'required': False
    },
    'model_run_dir_path': {
        'arg_name': 'model_run_dir_path',
        'flag': 'r',
        'type': str,
        'help_text': 'Model run directory path',
        'required': False
    },
    'ktools_num_processes': {
        'arg_name': 'ktools_num_processes',
        'flag': 'n',
        'type': str,
        'help_text': 'Number of ktools calculation processes/streams to use',
        'required': False
    }
}


if __name__ == '__main__':

    logger = mdk_utils.set_logging()
    logger.info('MDK master script')

    logger.info('Console logging set')

    try:
        logger.info('Processing script resources arguments')
        args = mdk_utils.parse_script_args(SCRIPT_ARGS_METADICT, desc='Generates ktools outputs for a given model')

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

        logger.info('Preparing model run directory {}'.format(args['model_run_dir_path']))
        prepare_model_run_directory(args['model_run_dir_path'])

        args['oasis_files_path'] = os.path.join(args['model_run_dir_path'], 'input', 'csv')

        cmd_str = (
            "python generate_oasis_files.py"
              " -k {}"
              " -v {}"
              " -l {}"
              " -p {}"
              " -e {}"
              " -a {}"
              " -b {}"
              " -c {}"
              " -d {}"
              " -x {}"
              " -o {}"
        ).format(
            args['keys_data_path'],
            args['model_version_file_path'],
            args['lookup_package_path'],
            args['canonical_exposures_profile_json_path'],
            args['source_exposures_file_path'],
            args['source_exposures_validation_file_path'],
            args['source_to_canonical_exposures_transformation_file_path'],
            args['canonical_exposures_validation_file_path'],
            args['canonical_to_model_exposures_transformation_file_path'],
            args['xtrans_path'],
            args['oasis_files_path']
        )

        try:
            logger.info('Calling script `generate_oasis_files.py` - to generate Oasis input files')
            subprocess.check_call(cmd_str, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            raise OasisException("Error generating Oasis files: {}".format(str(e)))

        logger.info('Generating ktools binary files')
        create_binary_files(args['oasis_files_path'], os.path.join(args['model_run_dir_path'], 'input'))

        try:
            with io.open(args['analysis_settings_json_file_path'], 'r', encoding='utf-8') as f:
                analysis_settings = json.load(f)
                if 'analysis_settings' in analysis_settings:
                    analysis_settings = analysis_settings['analysis_settings']
        except (IOError, ValueError, TypeError) as e:
            raise OasisException("Error loading analysis settings JSON file: {}".format(str(e)))

        logger.info('Preparing model run inputs')
        prepare_model_run_inputs(analysis_settings, args['model_run_dir_path'])

        cmd_str = (
            "python kparse.py"
            " -j {}"
            " -n {}"
            " -r {}"
            " -s {}"
        ).format(
            args['analysis_settings_json_file_path'],
            args['ktools_num_processes'],
            args['model_run_dir_path'],
            args['ktools_script_name']
        )

        try:
            logger.info('Calling script `kparse.py` - to generate model run ktools script')
            subprocess.check_call(cmd_str, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            raise OasisException("Error generating ktools script: {}".format(str(e)))

        os.chdir(args['model_run_dir_path'])
        cmd_str = "bash {}.sh".format(args['ktools_script_name'])
        try:
            ktools_script_path = '{}.sh'.format(os.path.join(args['model_run_dir_path'], args['ktools_script_name']))
            logger.info('Running model run ktools script {}'.format(ktools_script_path))
            subprocess.check_call(cmd_str, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            raise OasisException("Error running ktools script: {}".format(str(e)))
    except OasisException as e:
        logger.error(str(e))
        sys.exit(-1)

    outputs_dir = os.path.join(args['model_run_dir_path'], 'output')
    logger.info('Ktools output files generated in directory {}'.format(outputs_dir))

    sys.exit(0)
