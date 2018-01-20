#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
`run_model.py` is an executable script that can run models end-to-end, i.e. generate ktools outputs from model resources, including keys data, model data, analysis settings etc., given the following arguments (in no particular order)::

    ./run_model.py -k /path/to/keys/data/folder
                   -v /path/to/model/version/file
                   -l /path/to/model/keys/lookup/service/package
                   -p /path/to/canonical/exposures/profile/JSON/file
                   -e /path/to/source/exposures/file
                   -a /path/to/source/exposures/validation/file
                   -b /path/to/source/to/canonical/exposures/transformation/file
                   -c /path/to/canonical/exposures/validation/file
                   -d /path/to/canonical/to/model/exposures/transformation/file
                   -x /path/to/xtrans/executable
                   -j /path/to/analysis/settings/json/file
                   -s <ktools script name (without file extension)>
                   -m /path/to/model/data
                   -r /path/to/model/run/directory
                   -n <number of ktools calculation processes to use>

When calling the script this way paths can be given relative to the script, in particular, file paths should include the filename and extension. The paths to the keys data, lookup service package, model version file, canonical exposures profile JSON, source exposures file, transformation and validation files, and analysis settings JSON file, will usually be located in the model keys server repository. The ktools script name should not contain any filename extension, and the model run directory can be placed anywhere in the parent folder common to `omdk` and the model keys server repository.

It is also possible to run the script by defining these arguments in a JSON configuration file and calling the script using the path to this file using the option `-f`. In this case the paths should be given relative to the parent folder in which the model keys server repository is located.::

    ./run_model.py -f /path/to/model/resources/JSON/config/file'

The JSON file should contain the following keys (in no particular order)::

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
    "analysis_settings_json_file_path"
    "ktools_script_name"
    "model_data_path"
    "model_run_dir_path"
    "ktools_num_processes"

and the values of the path-related keys should be string paths, given relative to the parent folder in which the model keys server repository is located. The JSON file is usually placed in the model keys server repository.

**NOTE**:  As the JSON configuration files for `generate_oasis_files.py` and `generate_loss_outputs.py` defines a subset of the resources required for `run_model.py` you can use the `run_model.py` configuration file to also run `generate_oasis_files.py`.
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
    get_utctimestamp,
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
    'model_data_path': {
        'arg_name': 'model_data_path',
        'flag': 'm',
        'type': str,
        'help_text': 'Model data folder',
        'required': False
    },    
    'keys_data_path': {
        'arg_name': 'keys_data_path',
        'flag': 'k',
        'type': str,
        'help_text': 'Keys data path for model keys lookup service',
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

        if not os.path.exists(args['model_run_dir_path']):
            os.mkdir(args['model_run_dir_path'])

        utcnow = get_utctimestamp(fmt='%Y%m%d%H%M%S')
        args['model_run_dir_path'] = os.path.join(args['model_run_dir_path'], 'ProgOasis-{}'.format(utcnow))
        os.mkdir(args['model_run_dir_path'])
        logger.info('Preparing model run directory {}'.format(args['model_run_dir_path']))
        prepare_model_run_directory(args['model_run_dir_path'], args['analysis_settings_json_file_path'])

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

        logger.info('Converting Oasis files to ktools binary files')
        create_binary_files(args['oasis_files_path'], os.path.join(args['model_run_dir_path'], 'input'))

        try:
            with io.open(args['analysis_settings_json_file_path'], 'r', encoding='utf-8') as f:
                analysis_settings = json.load(f)
                if 'analysis_settings' in analysis_settings:
                    analysis_settings = analysis_settings['analysis_settings']
        except (IOError, ValueError, TypeError) as e:
            raise OasisException("Error loading analysis settings JSON file: {}".format(str(e)))

        logger.info('Preparing model run inputs')
        prepare_model_run_inputs(analysis_settings, args['model_run_dir_path'], args['model_data_path'])

        cmd_str = (
            "python generate_loss_outputs.py"
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
    logger.info('Ktools output files generated in {}'.format(outputs_dir))

    sys.exit(0)