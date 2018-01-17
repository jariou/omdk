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

__author__ = "Sandeep Murthy"
__copyright__ = "2017, Oasis Loss Modelling Framework"


SCRIPT_ARGS = {
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
    'lookup_package_path': {
        'arg_name': 'lookup_package_path',
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
    'analysis_settings_json_file_path': {
        'arg_name': 'analysis_settings_json_file_path',
        'flag': 'j',
        'type': str,
        'help_text': 'Model analysis settings JSON file path',
        'directly_required': False
    },
    'ktools_script_name': {
        'arg_name': 'ktools_script_name',
        'flag': 's',
        'type': str,
        'help_text': 'Name of ktools model run script',
        'directly_required': False
    },
    'model_run_dir_path': {
        'arg_name': 'model_run_dir_path',
        'flag': 'r',
        'type': str,
        'help_text': 'Model run directory path',
        'directly_required': False
    },
    'ktools_num_processes': {
        'arg_name': 'ktools_num_processes',
        'flag': 'n',
        'type': str,
        'help_text': 'Number of ktools calculation processes/streams to use',
        'directly_required': False
    }
}


def __set_logging__():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'
    )
    return logging.getLogger()


def __parse_args__():
    """
    Parses script arguments and constructs an args dictionary.
    """
    parser = argparse.ArgumentParser(description='Generate Oasis files for a given model')

    di = SCRIPT_ARGS

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


def __load_args_from_config_file__(config_file_path):
    if config_file_path.endswith('json'):
        try:
            with io.open(config_file_path, 'r', encoding='utf-8') as f:
                args = json.load(f)
        except (IOError, ValueError, TypeError) as e:
            raise OasisException('Error parsing resources config file {}: {}'.format(config_file_path, str(e)))
        
        map(
            lambda arg: args.update({arg: os.path.abspath(args[arg])}) if arg.endswith('path') and args[arg] else None,
            args
        )
    elif config_file_path.endswith('yaml') or config_file_path.endswith('yml'):
        pass

    return args

if __name__ == '__main__':

    logger = __set_logging__()
    logger.info('MDK master script')

    try:
        logger.info('Processing script resources arguments')
        args = __parse_args__()

        if args['config_file_path']:
            logger.info('Loading script resources from config file {}'.format(args['config_file_path']))
            try:
                args = __load_args_from_config_file__(args['config_file_path'])
            except OasisException as e:
                logger.error(str(e))
                sys.exit(-1)

            logger.info('Script resources: {}'.format(args))
        else:
            args.pop('config_file_path')
            logger.info('Script resources arguments: {}'.format(args))

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
            logger.info('Calling Oasis files generator script - to generate Oasis input files')
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

        ktools_script_path = '{}.sh'.format(os.path.join(args['model_run_dir_path'], args['ktools_script_name']))
        cmd_str = (
            "python {}"
            " -a {}"
            " -p {}"
            " -o {}"
        ).format(
            os.path.join('ktools', 'kparse.py'),
            args['analysis_settings_json_file_path'],
            args['ktools_num_processes'],
            ktools_script_path
        )

        try:
            logger.info('Calling kparse - to generate model run ktools script')
            subprocess.check_call(cmd_str, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            raise OasisException("Error generating ktools script: {}".format(str(e)))

        os.chdir(args['model_run_dir_path'])
        cmd_str = "bash {}".format(ktools_script_path)
        try:
            logger.info('Running model run ktools script {}'.format(ktools_script_path))
            subprocess.check_call(cmd_str, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            raise OasisException("Error running ktools script: {}".format(str(e)))
    except OasisException as e:
        logger.error(str(e))
        sys.exit(-1)

    sys.exit(0)
