#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
``run_model.py`` is an executable "master" script that can run models
end-to-end, i.e. generate losses given model resources, including keys
data, canonical exposure profiles, exposure transformation and
validation files, model data, analysis settings etc., given the
following arguments (in no particular order)

::

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
                   -m /path/to/model/data
                   [-r /path/to/model/run/directory]
                   [-s <ktools script name (without file extension)>]
                   [-n <number of ktools calculation processes to use>]

When calling the script this way paths can be given relative to the
script, in particular, file paths should include the filename and
extension. The paths to the keys data, lookup service package, model
version file, canonical exposures profile JSON, source exposures file,
transformation and validation files, and analysis settings JSON file,
will usually be located in the model keys server repository. The path to
the model run directory is optional - by default the script will create
a timestamped folder in ``omdk/runs`` with the prefix ``ProgOasis``. The
ktools script name and number of calculation processes are also optional
- by default the script will create a ktools script named
``run_tools.sh`` and set the number of calculation processes to 2.

It is also possible to run the script by defining these arguments in a
JSON configuration file and calling the script using the path to this
file using the option ``-f`` and the (relative or absolute) path to the
file.

::

    ./run_model.py -f /path/to/script/config/json/file'

The JSON file should contain the following keys (in no particular order)

::

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
    "model_data_path"
    "model_run_dir_path"
    "ktools_script_name"
    "ktools_num_processes"

and the values of the path-related keys should be string paths, given
relative to the location of the JSON file. The JSON file is usually placed in the model keys server
repository. The ``"model_run_dir_path"`` key is optional - by default
the script will create a timestamped folder in ``omdk/runs`` with the
prefix ``ProgOasis``. The ``"ktools_script_name"`` and
``"ktools_num_processes"`` keys are optional - by default the script
will create a ktools script named ``run_tools.sh`` and set the number of
calculation processes to 2.

You can define a separate JSON configuration file for each model,
provided you have the model keys server repository and other required
model resources available locally.

**NOTE**: For a given model the JSON script configuration files for
``generate_oasis_files.py``, ``generate_losses.py`` and ``run_model.py``
should complement each other, except for ``generate_losses.py`` which
requires the path to Oasis files, not required by ``run_model.py``. You
can run any of these scripts against a single master script
configuration file, provided that the path to an actual set of Oasis
files is added in order to run ``generate_losses.py``.
"""

import argparse
import io
import json
import logging
import os
import shutil
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
        'name': 'config_file_path',
        'flag': 'f',
        'type': str,
        'help_text': 'Path for script config for model',
        'required_on_command_line': False,
        'required_for_script': False,
        'preexists': True
    },   
    'keys_data_path': {
        'name': 'keys_data_path',
        'flag': 'k',
        'type': str,
        'help_text': 'Keys data path for model keys lookup service',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'model_version_file_path': {
        'name': 'model_version_file_path',
        'flag': 'v',
        'type': str,
        'help_text': 'Model version file path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'lookup_package_path': {
        'name': 'lookup_package_path',
        'flag': 'l',
        'type': str,
        'help_text': 'Package path for model keys lookup service - usually in the `src/keys_server` folder of the relevant supplier repository',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'canonical_exposures_profile_json_path': {
        'name': 'canonical_exposures_profile_json_path',
        'flag': 'p',
        'type': str,
        'help_text': 'Path of the supplier canonical exposures profile JSON file',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'source_exposures_file_path': {
        'name': 'source_exposures_file_path',
        'flag': 'e',
        'type': str,
        'help_text': 'Source exposures file path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'source_exposures_validation_file_path': {
        'name': 'source_exposures_validation_file_path',
        'flag': 'a',
        'type': str,
        'help_text': 'Source exposures validation file (XSD) path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'source_to_canonical_exposures_transformation_file_path': {
        'name': 'source_to_canonical_exposures_transformation_file_path',
        'flag': 'b',
        'type': str,
        'help_text': 'Source -> canonical exposures transformation file (XSLT) path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'canonical_exposures_validation_file_path': {
        'name': 'canonical_exposures_validation_file_path',
        'flag': 'c',
        'type': str,
        'help_text': 'Canonical exposures validation file (XSD) path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'canonical_to_model_exposures_transformation_file_path': {
        'name': 'canonical_to_model_exposures_transformation_file_path',
        'flag': 'd',
        'type': str,
        'help_text': 'Canonical -> model exposures transformation file (XSLT) path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'xtrans_path': {
        'name': 'xtrans_path',
        'flag': 'x',
        'type': str,
        'help_text': 'Path of the xtrans executable which performs the source -> canonical and canonical -> model exposures transformations',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'analysis_settings_json_file_path': {
        'name': 'analysis_settings_json_file_path',
        'flag': 'j',
        'type': str,
        'help_text': 'Model analysis settings JSON file path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'model_data_path': {
        'name': 'model_data_path',
        'flag': 'm',
        'type': str,
        'help_text': 'Model data path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'model_run_dir_path': {
        'name': 'model_run_dir_path',
        'flag': 'r',
        'type': str,
        'help_text': 'Model run directory path',
        'required_on_command_line': False,
        'required_for_script': False,
        'preexists': False
    },
    'ktools_script_name': {
        'name': 'ktools_script_name',
        'flag': 's',
        'type': str,
        'help_text': 'Name of ktools model run script',
        'required_on_command_line': False,
        'required_for_script': False
    },
    'ktools_num_processes': {
        'name': 'ktools_num_processes',
        'flag': 'n',
        'type': str,
        'help_text': 'Number of ktools calculation processes/streams to use',
        'required_on_command_line': False,
        'required_for_script': False
    }
}


if __name__ == '__main__':

    logger = mdk_utils.set_logging()
    logger.info('MDK master script')

    logger.info('Console logging set')

    try:
        logger.info('Parsing script arguments')
        args = mdk_utils.parse_script_args(SCRIPT_ARGS_METADICT, desc='Generates ktools outputs for a given model')

        if args['config_file_path']:
            logger.info('Loading script resources from config file {}'.format(args['config_file_path']))
            args = mdk_utils.load_script_args_from_config_file(SCRIPT_ARGS_METADICT, args['config_file_path'])
        else:
            args.pop('config_file_path')

        logger.info('Script arguments: {}'.format(json.dumps(args, indent=4, sort_keys=True)))

        di = SCRIPT_ARGS_METADICT
        missing = filter(lambda arg: not args[arg] if arg in args and di[arg]['required_for_script'] else None, di)

        if missing:
            raise OasisException('Not all script resources arguments provided - missing {}'.format(missing))

        utcnow = get_utctimestamp(fmt='%Y%m%d%H%M%S')

        logger.info('Checking for model run directory')
        try:
            if 'model_run_dir_path' not in args or not args['model_run_dir_path']:
                model_run_dir_path = os.path.join(os.getcwd(), 'runs', 'ProgOasis-{}'.format(utcnow))
                logger.info('Model run directory not provided - creating one in omdk/runs')
                os.mkdir(model_run_dir_path)
            else:
                if not os.path.exists(args['model_run_dir_path']):
                    os.mkdir(args['model_run_dir_path'])

                model_run_dir_path = args['model_run_dir_path']
        except OSError as e:
            raise OasisException('Error creating model run directory: {}'.format(str(e)))

        tmp_oasis_files_path = os.path.join(model_run_dir_path, 'tmp')
        logger.info('Creating temporary folder {} for Oasis files'.format(tmp_oasis_files_path))
        os.mkdir(tmp_oasis_files_path)

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
            tmp_oasis_files_path
        )

        try:
            logger.info('Calling script `generate_oasis_files.py` - to generate Oasis input files')
            subprocess.check_call(cmd_str, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            raise OasisException("Error generating Oasis files: {}".format(str(e)))

        ktools_script_name = (
            args['ktools_script_name'] if 'ktools_script_name' in args and args['ktools_script_name']
            else 'run_ktools'
        )

        ktools_num_processes = (
            args['ktools_num_processes'] if 'ktools_num_processes' in args and args['ktools_num_processes']
            else 2
        )

        cmd_str = (
            "python generate_losses.py"
            " -o {}"
            " -j {}"
            " -m {}"
            " -r {}"
            " -s {}"
            " -n {}"
        ).format(
            tmp_oasis_files_path,
            args['analysis_settings_json_file_path'],
            args['model_data_path'],
            model_run_dir_path,
            ktools_script_name,
            ktools_num_processes
        )

        try:
            logger.info('Calling script `generate_losses.py` to generate model ktools loss outputs script')
            subprocess.check_call(cmd_str, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            raise OasisException("Error generating ktools loss outputs script: {}".format(str(e)))

        shutil.rmtree(tmp_oasis_files_path)
    except OasisException as e:
        logger.error(str(e))
        sys.exit(-1)

    sys.exit(0)
